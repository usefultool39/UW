from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from .agent_registry import get_agent_profile
from .dialogue_agent import dialogue_reply
from .heuristic import choose_action
from .llm_agent import llm_choose_action
from .memory_store import MemoryStore
from .models import Location, SimEvent, WorldState
from .relationship import ensure_relationships, npc_profile
from .story_director import available_events, choose_event
from .story_catalog import can_enter_node, default_catalog_path, load_main_nodes
from .world import advance_tick, apply_action, apply_npc_schedules, initial_world
from .world_map import bfs_path, default_map_path, load_world_map, scene_for_tile


class Session:
    def __init__(self, seed: int | None = None, run_id: str = "default") -> None:
        self.root = Path(__file__).resolve().parent.parent.parent
        self.state: WorldState = ensure_relationships(initial_world(seed=seed))
        self.events: list[dict] = []
        self.seed = seed
        self.run_id = run_id
        self.memory_store = MemoryStore(self.root / "data" / "memory")
        self._pending_jsonl: list[dict] = []
        self._pending_memory: list[tuple[str, dict, str]] = []
        self._runs_dir = self.root / "runs"
        self._runs_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()

    def _append_jsonl(self, row: dict) -> None:
        self._pending_jsonl.append(row)

    def _flush_writes(self) -> None:
        if self._pending_jsonl:
            path = self._runs_dir / f"{self.run_id}.jsonl"
            with path.open("a", encoding="utf-8") as f:
                for row in self._pending_jsonl:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            self._pending_jsonl.clear()

        if self._pending_memory:
            for npc_id, event_row, run_id in self._pending_memory:
                self.memory_store.append_event(npc_id, event_row, run_id)
            self._pending_memory.clear()

    def export_save(self) -> dict:
        with self._lock:
            self.state = ensure_relationships(self.state)
            memory_summaries = {
                agent.id: self.memory_store.load_summary(agent.id)
                for agent in self.state.agents
            }
            return {
                "schema_version": 1,
                "kind": "30town_save",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "run_id": self.run_id,
                "state": self.state.model_dump(mode="json"),
                "events": list(self.events[-500:]),
                "memory_summaries": memory_summaries,
            }

    def import_save(self, payload: dict) -> dict:
        with self._lock:
            if not isinstance(payload, dict):
                return {"ok": False, "error": "invalid_save_payload"}
            if payload.get("kind") not in (None, "30town_save"):
                return {"ok": False, "error": "unsupported_save_kind"}
            raw_state = payload.get("state")
            if not isinstance(raw_state, dict):
                return {"ok": False, "error": "missing_state"}
            try:
                restored = ensure_relationships(WorldState.model_validate(raw_state))
            except Exception as exc:
                return {"ok": False, "error": f"invalid_state: {exc}"}

            self.state = restored
            raw_events = payload.get("events")
            self.events = [e for e in raw_events[-500:] if isinstance(e, dict)] if isinstance(raw_events, list) else []

            memory_summaries = payload.get("memory_summaries")
            if isinstance(memory_summaries, dict):
                known_ids = {agent.id for agent in self.state.agents}
                for npc_id, summary in memory_summaries.items():
                    if str(npc_id) in known_ids and isinstance(summary, dict):
                        self.memory_store.replace_summary(str(npc_id), summary, self.run_id)

            row = {
                "kind": "save_import",
                "tick": self.state.tick,
                "day": self.state.day,
                "imported_at": datetime.now(timezone.utc).isoformat(),
            }
            self.events.append(row)
            self._append_jsonl(row)
            self._flush_writes()
            return {"ok": True, "state": self.state.model_dump(mode="json")}

    def step(self, mode: Literal["heuristic", "llm"]) -> list[SimEvent]:
        with self._lock:
            self.state = ensure_relationships(self.state)
            out: list[SimEvent] = []
            order = sorted(self.state.agents, key=lambda a: a.id)
            for ag in order:
                llm_meta: dict | None = None
                agent_thinking: str | None = None
                if mode == "heuristic":
                    act = choose_action(self.state, ag)
                else:
                    act, agent_thinking, llm_meta = llm_choose_action(
                        self.state, ag.id, self.events, self.root
                    )
                new_state, ev = apply_action(self.state, ag.id, act)
                if agent_thinking:
                    new_state.agents = [
                        a
                        if a.id != ag.id
                        else a.model_copy(update={"thought": agent_thinking})
                        for a in new_state.agents
                    ]
                self.state = new_state
                who = get_agent_profile(self.root, ag.id)
                ev = ev.model_copy(
                    update={
                        "actor_name": who.display,
                        "actor_role": who.role,
                        "decision_mode": mode,
                        "llm_model": (llm_meta or {}).get("llm_model"),
                        "llm_prompt_system": (llm_meta or {}).get("llm_prompt_system"),
                        "llm_prompt_user": (llm_meta or {}).get("llm_prompt_user"),
                        "llm_raw": (llm_meta or {}).get("llm_raw"),
                        "llm_thinking": agent_thinking,
                    }
                )
                row = ev.model_dump(mode="json", exclude_none=True)
                self.events.append(row)
                out.append(ev)
                self._append_jsonl({"kind": "event", **row})
                self._pending_memory.append(
                    (
                        ag.id,
                        {
                            **row,
                            "action_name": act.name.value,
                        },
                        self.run_id,
                    )
                )

            self.state = advance_tick(self.state)
            self._append_jsonl(
                {
                    "kind": "tick_end",
                    "tick": self.state.tick,
                    "tree_hp": self.state.tree.hp,
                    "tree_state": self.state.tree.state.value,
                }
            )
            self._flush_writes()
            return out

    def daily_tick(self, mode: Literal["heuristic", "llm"]) -> list[SimEvent]:
        """与 `step` 等价；预留日后在 tick 前后挂日历/开放事件等钩子。"""
        return self.step(mode=mode)

    def player_action(
        self,
        *,
        kind: str,
        scene_id: str | None = None,
        location: str | None = None,
        flag_key: str | None = None,
        flag_value: int | None = None,
        tile_x: int | None = None,
        tile_y: int | None = None,
    ) -> dict:
        with self._lock:
            self.state = ensure_relationships(self.state)
            path_payload: list[dict[str, int]] | None = None
            if kind == "move_world":
                if tile_x is None or tile_y is None:
                    return {"ok": False, "error": "missing_tile"}
                wm = load_world_map(default_map_path(self.root))
                sx = self.state.player.tile_x
                sy = self.state.player.tile_y
                tx, ty = int(tile_x), int(tile_y)
                path = bfs_path(wm, sx, sy, tx, ty)
                if path is None:
                    return {"ok": False, "error": "unreachable_or_blocked"}
                path_payload = [{"x": px, "y": py} for px, py in path]
                new_scene = scene_for_tile(wm, tx, ty)
                sid = self.state.player.scene_id
                if new_scene and new_scene in self.state.unlocked_scenes:
                    sid = new_scene
                pl = self.state.player.model_copy(
                    update={"tile_x": tx, "tile_y": ty, "scene_id": sid}
                )
                self.state = self.state.model_copy(
                    update={"scene_id": sid, "player": pl}
                )
            elif kind == "move_scene":
                if not scene_id:
                    return {"ok": False, "error": "missing_scene_id"}
                if scene_id not in self.state.unlocked_scenes:
                    return {"ok": False, "error": "scene_locked"}
                pl = self.state.player.model_copy(update={"scene_id": scene_id})
                self.state = self.state.model_copy(
                    update={"scene_id": scene_id, "player": pl}
                )
            elif kind == "set_location":
                if not location:
                    return {"ok": False, "error": "missing_location"}
                try:
                    loc = Location(location)
                except ValueError:
                    return {"ok": False, "error": "invalid_location"}
                pl = self.state.player.model_copy(update={"location": loc})
                self.state = self.state.model_copy(update={"player": pl})
            elif kind == "set_flag":
                if not flag_key or flag_value is None:
                    return {"ok": False, "error": "missing_flag"}
                flags = dict(self.state.flags)
                flags[flag_key] = int(flag_value)
                self.state = self.state.model_copy(update={"flags": flags})
            elif kind == "rest_until_next_day":
                pl = self.state.player.model_copy(update={"location": Location.home})
                self.state = self.state.model_copy(
                    update={
                        "day": self.state.day + 1,
                        "tick": 0,
                        "time_band": "morning",
                        "player": pl,
                    }
                )
                self.state = apply_npc_schedules(self.state, self.root)
            else:
                return {"ok": False, "error": "unknown_action_kind"}

            row = {
                "kind": "player_action",
                "payload": {
                    "kind": kind,
                    "scene_id": scene_id,
                    "location": location,
                    "flag_key": flag_key,
                    "flag_value": flag_value,
                    "tile_x": tile_x,
                    "tile_y": tile_y,
                },
                "tick": self.state.tick,
                "day": self.state.day,
            }
            self.events.append(row)
            self._append_jsonl(row)
            self._flush_writes()
            out: dict = {"ok": True, "state": self.state.model_dump(mode="json")}
            if path_payload is not None:
                out["path"] = path_payload
            return out

    def available_story_events(self) -> dict:
        with self._lock:
            self.state = ensure_relationships(self.state)
            events = available_events(self.root, self.state)
            active_ids = [str(e.get("id")) for e in events if e.get("id")]
            self.state = self.state.model_copy(update={"active_event_ids": active_ids})
            return {
                "ok": True,
                "events": events,
                "state": self.state.model_dump(mode="json"),
            }

    def choose_story_event(self, event_id: str, choice_id: str) -> dict:
        with self._lock:
            self.state = ensure_relationships(self.state)
            next_state, result = choose_event(
                project_root=self.root,
                state=self.state,
                event_id=event_id,
                choice_id=choice_id,
            )
            if not result.get("ok"):
                return {
                    **result,
                    "state": self.state.model_dump(mode="json"),
                }

            self.state = next_state
            memory_written: list[dict] = []
            for npc_id, memory in result.pop("memory_writes", []):
                stored = self.memory_store.append_important_memory(
                    npc_id,
                    memory,
                    self.run_id,
                )
                memory_written.append({"npc_id": npc_id, **stored})

            for npc_id, text in (result.get("promises") or {}).items():
                self.memory_store.add_promise(str(npc_id), str(text), self.run_id)
            for npc_id, text in (result.get("tensions") or {}).items():
                self.memory_store.add_tension(str(npc_id), str(text), self.run_id)

            row = {
                "kind": "story_choose",
                "event_id": event_id,
                "choice_id": choice_id,
                "choice_label": result.get("choice", {}).get("label"),
                "ending_id": result.get("ending_id"),
                "relationship_changes": result.get("relationship_changes") or [],
                "memory_written": memory_written,
                "tick": self.state.tick,
                "day": self.state.day,
            }
            self.events.append(row)
            self._append_jsonl(row)
            self._flush_writes()

            available = available_events(self.root, self.state)
            self.state = self.state.model_copy(
                update={
                    "active_event_ids": [
                        str(e.get("id")) for e in available if e.get("id")
                    ]
                }
            )
            return {
                **result,
                "memory_written": memory_written,
                "available_events": available,
                "state": self.state.model_dump(mode="json"),
            }

    def npc_profile(self, npc_id: str) -> dict:
        with self._lock:
            self.state = ensure_relationships(self.state)
            npc_ids = {a.id for a in self.state.agents}
            if npc_id not in npc_ids:
                return {"ok": False, "error": "unknown_npc"}
            summary = self.memory_store.load_summary(npc_id)
            return {
                "ok": True,
                "profile": npc_profile(
                    project_root=self.root,
                    state=self.state,
                    npc_id=npc_id,
                    memory_summary=summary,
                ),
                "state": self.state.model_dump(mode="json"),
            }

    def story_advance(self, target_id: str) -> dict:
        with self._lock:
            catalog = load_main_nodes(default_catalog_path(self.root))
            raw_nodes = catalog.get("nodes") or {}
            if not isinstance(raw_nodes, dict):
                raw_nodes = {}
            ok, reason = can_enter_node(
                raw_nodes, self.state.story_node_id, target_id, self.state.flags
            )
            if not ok:
                return {
                    "ok": False,
                    "error": reason,
                    "state": self.state.model_dump(mode="json"),
                }
            prev = self.state.story_node_id
            self.state = self.state.model_copy(update={"story_node_id": target_id})
            row = {
                "kind": "story_advance",
                "from": prev,
                "to": target_id,
                "tick": self.state.tick,
                "day": self.state.day,
            }
            self.events.append(row)
            self._append_jsonl(row)
            self._flush_writes()
            return {"ok": True, "state": self.state.model_dump(mode="json")}

    def dialogue(
        self,
        *,
        npc_id: str,
        message: str,
        context: dict | None = None,
    ) -> dict:
        with self._lock:
            self.state = ensure_relationships(self.state)
            npc_ids = {a.id for a in self.state.agents}
            if npc_id not in npc_ids:
                return {
                    "ok": False,
                    "error": "unknown_npc",
                    "state": self.state.model_dump(mode="json"),
                }

            recent = self.memory_store.read_recent_events(npc_id, limit=6)
            memory_context = self.memory_store.read_important_context(npc_id, limit=6)
            relationship = (self.state.relationships or {}).get(npc_id)
            reply = dialogue_reply(
                state=self.state,
                npc_id=npc_id,
                message=message,
                project_root=self.root,
                recent_memories=recent,
                memory_context=memory_context,
                relationship=relationship,
            )
            memory_committed = False
            candidate = reply.get("memory_candidate")
            if isinstance(candidate, dict) and int(candidate.get("weight", 0)) >= 3:
                self.memory_store.append_important_memory(
                    npc_id,
                    {
                        "day": self.state.day,
                        "type": candidate.get("type") or "dialogue",
                        "summary": candidate.get("summary") or "",
                        "weight": candidate.get("weight") or 3,
                        "source_event": "dialogue",
                    },
                    self.run_id,
                )
                memory_committed = True
            row = {
                "kind": "dialogue",
                "npc_id": npc_id,
                "message": message,
                "reply": reply.get("reply"),
                "emotion": reply.get("emotion"),
                "memory_candidate": reply.get("memory_candidate"),
                "memory_committed": memory_committed,
                "context": context or {},
                "tick": self.state.tick,
                "day": self.state.day,
            }
            self.events.append(row)
            self._append_jsonl(row)
            self._pending_memory.append(
                (
                    npc_id,
                    {
                        **row,
                        "action_name": "dialogue",
                        "ok": True,
                        "detail": reply.get("reply"),
                    },
                    self.run_id,
                )
            )
            self._flush_writes()
            return {
                **reply,
                "memory_committed": memory_committed,
                "state": self.state.model_dump(mode="json"),
            }
