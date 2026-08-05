from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .activity_engine import ActivityValidationError, plan_scene_activity
from .agent_registry import get_agent_profile
from .dialogue_agent import dialogue_reply
from .heuristic import choose_action
from .llm_agent import llm_choose_action
from .memory_store import MemoryStore
from .models import Location, SimEvent, TreeState, WorldState
from .npc_intents import attach_npc_intents
from .player_actions import (
    PLAYER_ACTIONS,
    camera_for_player as _camera_for_player,
    normalize_player_action_kind,
    player_at_location as _player_at_location,
    poi_by_id as _poi_by_id,
    rejected_action_envelope,
    zone_for_scene as _zone_for_scene,
)
from .relationship import apply_relationship_effects, ensure_relationships, npc_profile
from .scene_activities import find_scene_activity
from .story_director import available_events, choose_event, day_gate_status
from .story_catalog import can_enter_node, default_catalog_path, load_main_nodes
from .world import (
    advance_tick,
    apply_action,
    apply_environment,
    apply_npc_schedules,
    initial_world,
)
from .world_map import bfs_path, is_blocked_zone, load_world_map, map_path_for_id, scene_for_tile, zone_for_tile


class Session:
    def __init__(self, seed: int | None = None, run_id: str = "default") -> None:
        self.root = Path(__file__).resolve().parent.parent.parent
        self.state: WorldState = ensure_relationships(initial_world(seed=seed))
        self.events: list[dict] = []
        self.seed = seed
        self.run_id = run_id
        safe_run_id = "".join(
            ch if ch.isalnum() or ch in {"-", "_"} else "_"
            for ch in str(run_id or "default")
        )[:80] or "default"
        # Memories belong to a playthrough. A new game must never inherit a
        # previous run's Day 3 secrets; imported saves restore their own summary.
        self.memory_store = MemoryStore(self.root / "data" / "memory" / safe_run_id)
        self._pending_jsonl: list[dict] = []
        self._pending_memory: list[tuple[str, dict, str]] = []
        self._runs_dir = self.root / "runs"
        self._runs_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self.state = attach_npc_intents(self.root, self.state)

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

    def _refresh_runtime_views(self) -> None:
        self.state = attach_npc_intents(self.root, ensure_relationships(self.state))

    def public_state(self) -> WorldState:
        with self._lock:
            self._refresh_runtime_views()
            return self.state

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
            self._refresh_runtime_views()
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
            self._refresh_runtime_views()
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

    def _resolve_day_transition(self, *, reason: str, trigger_event_id: str | None = None) -> dict[str, Any] | None:
        status = day_gate_status(self.root, self.state)
        if not status.get("ready"):
            return None
        gate = status.get("gate") if isinstance(status.get("gate"), dict) else {}
        before_day = int(self.state.day)
        target_day = int(gate.get("advance_to") or (before_day + 1))
        player = _player_at_location(self.state.player, Location.home).model_copy(
            update={"stamina": self.state.player.max_stamina, "hp": self.state.player.max_hp, "mp": self.state.player.max_mp}
        )
        updates: dict[str, Any] = {
            "day": target_day,
            "tick": 0,
            "time_band": "morning",
            "scene_id": player.scene_id,
            "player": player,
        }
        next_node = gate.get("next_story_node_id")
        if next_node:
            updates["story_node_id"] = str(next_node)
        self.state = self.state.model_copy(update=updates)
        self.state = apply_npc_schedules(apply_environment(self.state), self.root)
        transition = {
            "from_day": before_day,
            "to_day": target_day,
            "reason": reason,
            "trigger_event_id": trigger_event_id,
            "settlement_title": gate.get("settlement_title"),
            "next_goal": gate.get("next_goal") or {},
        }
        self._append_jsonl({"kind": "day_transition", **transition})
        return transition

    def _day_gate_error(self) -> dict[str, Any]:
        status = day_gate_status(self.root, self.state)
        return {
            "missing": status.get("missing") or [],
            "day": self.state.day,
            "gate": status.get("gate"),
        }

    def player_action(
        self,
        *,
        kind: str,
        map_id: str | None = None,
        entry_point: str | None = None,
        scene_id: str | None = None,
        poi_id: str | None = None,
        location: str | None = None,
        flag_key: str | None = None,
        flag_value: int | None = None,
        activity_id: str | None = None,
        activity_choice: str | None = None,
        intent_id: str | None = None,
        response_id: str | None = None,
        tile_x: int | None = None,
        tile_y: int | None = None,
        day: int | None = None,
        n: int | None = None,
        daily_n: int | None = None,
    ) -> dict:
        with self._lock:
            self.state = ensure_relationships(self.state)
            self._refresh_runtime_views()
            original_kind, kind = normalize_player_action_kind(kind, activity_id=activity_id)
            before_player = self.state.player
            action_events: list[dict[str, Any]] = []
            path_payload: list[dict[str, int]] | None = None
            activity_result: dict | None = None
            intent_result: dict | None = None
            relationship_changes: list[dict] = []
            memory_written: list[dict] = []
            day_transition: dict[str, Any] | None = None

            def current_map() -> tuple[dict[str, Any] | None, str | None]:
                mid = map_id or self.state.player.map_id or "novice_open"
                path = map_path_for_id(self.root, mid)
                if path is None:
                    return None, "invalid_map_id"
                if not path.is_file():
                    return None, "unknown_map_id"
                return load_world_map(path), None

            def response_scene_update(changed: bool, reason: str | None = None) -> dict[str, Any]:
                wm, _ = current_map()
                zone = _zone_for_scene(wm or {}, self.state.player.scene_id)
                return {
                    "changed": changed,
                    "reason": reason or kind,
                    "map_id": self.state.player.map_id,
                    "scene_id": self.state.player.scene_id,
                    "region": zone,
                }

            def fail(error: str, **extra: Any) -> dict:
                return rejected_action_envelope(
                    state=self.state,
                    original_kind=original_kind,
                    normalized_kind=kind,
                    error=error,
                    scene_update=response_scene_update(False, error),
                    extra=extra,
                )

            if kind not in PLAYER_ACTIONS:
                return fail("unknown_action_kind")

            if kind in {"move_world", "move_map"}:
                did_map_migration = False
                if tile_x is None or tile_y is None:
                    if kind == "move_map" and map_id:
                        wm, err = current_map()
                        if err or wm is None:
                            return fail(err or "unknown_map_id")
                        points = wm.get("entry_points") or {}
                        entry = points.get(entry_point or "default") if isinstance(points, dict) else None
                        spawn = entry if isinstance(entry, dict) else wm.get("spawn") or {}
                        tx = int(spawn.get("x", 0))
                        ty = int(spawn.get("y", 0))
                        sid = str(spawn.get("scene_id") or scene_for_tile(wm, tx, ty) or self.state.player.scene_id)
                        if sid not in self.state.unlocked_scenes:
                            return fail("scene_locked")
                        pl = self.state.player.model_copy(
                            update={"map_id": map_id, "tile_x": tx, "tile_y": ty, "scene_id": sid}
                        )
                        self.state = self.state.model_copy(update={"scene_id": sid, "player": pl})
                        path_payload = [{"x": tx, "y": ty}]
                        did_map_migration = True
                        action_events.append(
                            {"type": "map_changed", "map_id": map_id, "scene_id": sid, "tile": {"x": tx, "y": ty}}
                        )
                    else:
                        return fail("missing_tile")
                else:
                    wm, err = current_map()
                    if err or wm is None:
                        return fail(err or "unknown_map_id")
                if not did_map_migration:
                    sx = self.state.player.tile_x
                    sy = self.state.player.tile_y
                    tx, ty = int(tile_x), int(tile_y)
                    target_zone = zone_for_tile(wm, tx, ty)
                    if is_blocked_zone(target_zone):
                        return fail("zone_locked", zone=target_zone)
                    path = bfs_path(wm, sx, sy, tx, ty)
                    if path is None:
                        return fail("unreachable_or_blocked")
                    path_payload = [{"x": px, "y": py} for px, py in path]
                    new_scene = scene_for_tile(wm, tx, ty)
                    sid = self.state.player.scene_id
                    if new_scene and new_scene in self.state.unlocked_scenes:
                        sid = new_scene
                    pl = self.state.player.model_copy(
                        update={"map_id": map_id or self.state.player.map_id, "tile_x": tx, "tile_y": ty, "scene_id": sid}
                    )
                    self.state = self.state.model_copy(
                        update={"scene_id": sid, "player": pl}
                    )
                    action_events.append(
                        {"type": "player_moved", "map_id": pl.map_id, "scene_id": sid, "tile": {"x": tx, "y": ty}}
                    )
            elif kind == "move_scene":
                if not scene_id:
                    return fail("missing_scene_id")
                if scene_id not in self.state.unlocked_scenes:
                    return fail("scene_locked")
                updates: dict[str, Any] = {"scene_id": scene_id}
                wm, err = current_map()
                if err is None and wm:
                    zone = _zone_for_scene(wm, scene_id)
                    entries = zone.get("entry_points") if isinstance(zone, dict) else None
                    picked = None
                    if isinstance(entries, list) and entries:
                        if entry_point:
                            picked = next((p for p in entries if isinstance(p, dict) and p.get("id") == entry_point), None)
                        picked = picked or next((p for p in entries if isinstance(p, dict)), None)
                    if isinstance(picked, dict) and {"x", "y"} <= set(picked):
                        updates.update({"tile_x": int(picked["x"]), "tile_y": int(picked["y"])})
                pl = self.state.player.model_copy(update=updates)
                self.state = self.state.model_copy(
                    update={"scene_id": scene_id, "player": pl}
                )
                action_events.append({"type": "scene_entered", "scene_id": scene_id})
            elif kind == "interact_with_hub":
                if scene_id:
                    if scene_id not in self.state.unlocked_scenes:
                        return fail("scene_locked")
                    pl = self.state.player.model_copy(update={"scene_id": scene_id})
                    self.state = self.state.model_copy(update={"scene_id": scene_id, "player": pl})
                    action_events.append({"type": "scene_entered", "scene_id": scene_id})
                elif poi_id:
                    wm, err = current_map()
                    if err or wm is None:
                        return fail(err or "unknown_map_id")
                    poi = _poi_by_id(wm, poi_id)
                    if not poi:
                        return fail("unknown_poi")
                    px, py = int(poi.get("tile_x", self.state.player.tile_x)), int(poi.get("tile_y", self.state.player.tile_y))
                    sid = str(poi.get("scene_id") or scene_for_tile(wm, px, py) or self.state.player.scene_id)
                    action_events.append({"type": "hub_ready", "poi_id": poi_id, "scene_id": sid})
                else:
                    return fail("missing_interaction_target")
            elif kind == "set_location":
                if not location:
                    return fail("missing_location")
                try:
                    loc = Location(location)
                except ValueError:
                    return fail("invalid_location")
                pl = _player_at_location(self.state.player, loc)
                self.state = self.state.model_copy(
                    update={"player": pl, "scene_id": pl.scene_id}
                )
                action_events.append({"type": "location_changed", "location": loc.value, "scene_id": pl.scene_id})
            elif kind == "set_flag":
                if not flag_key or flag_value is None:
                    return fail("missing_flag")
                flags = dict(self.state.flags)
                flags[flag_key] = int(flag_value)
                self.state = self.state.model_copy(update={"flags": flags})
                action_events.append({"type": "flag_set", "key": flag_key, "value": int(flag_value)})
            elif kind == "set_day":
                if day is None:
                    return fail("missing_day")
                target_day = max(1, min(999, int(day)))
                self.state = self.state.model_copy(
                    update={"day": target_day, "tick": 0, "time_band": "morning"}
                )
                self.state = apply_npc_schedules(apply_environment(self.state), self.root)
                action_events.append({"type": "day_set", "day": target_day, "time_band": self.state.time_band})
            elif kind == "respond_npc_intent":
                if not intent_id or not response_id:
                    return fail("missing_npc_intent_response")
                self._refresh_runtime_views()
                intent = next(
                    (item for item in self.state.npc_intents if item.id == intent_id),
                    None,
                )
                if intent is None:
                    return fail("unknown_npc_intent")
                option: dict[str, Any] | None = None
                for raw_option in intent.response_options or []:
                    row = dict(raw_option)
                    if str(row.get("id") or "") == response_id:
                        option = row
                        break
                if option is None:
                    return fail("unknown_npc_intent_response")

                response_flag = f"npc_intent_response.{intent_id}.{response_id}"
                if bool(option.get("once", True)) and int(self.state.flags.get(response_flag, 0)) > 0:
                    return fail("npc_intent_response_already_done")

                effects = option.get("effects") if isinstance(option.get("effects"), dict) else {}
                flags = dict(self.state.flags)
                for key, val in (effects.get("flags") or {}).items():
                    flags[str(key)] = int(val)
                flags[response_flag] = int(self.state.day)
                self.state = self.state.model_copy(update={"flags": flags})

                self.state, relationship_changes = apply_relationship_effects(
                    self.state,
                    effects.get("relationship") if isinstance(effects.get("relationship"), dict) else {},
                )

                for npc_id, memory in (effects.get("memory") or {}).items():
                    if not isinstance(memory, dict):
                        continue
                    stored = self.memory_store.append_important_memory(
                        str(npc_id),
                        {
                            "day": self.state.day,
                            "type": memory.get("type") or "npc_intent_response",
                            "summary": memory.get("summary") or "",
                            "weight": memory.get("weight") or 3,
                            "source_event": f"{intent_id}:{response_id}",
                        },
                        self.run_id,
                    )
                    memory_written.append({"npc_id": str(npc_id), **stored})

                promises = effects.get("promises") if isinstance(effects.get("promises"), dict) else {}
                tensions = effects.get("tensions") if isinstance(effects.get("tensions"), dict) else {}
                for npc_id, text in promises.items():
                    self.memory_store.add_promise(str(npc_id), str(text), self.run_id)
                for npc_id, text in tensions.items():
                    self.memory_store.add_tension(str(npc_id), str(text), self.run_id)

                intent_result = {
                    "kind": "npc_intent_response",
                    "event_title": intent.title,
                    "npc_id": intent.npc_id,
                    "intent_id": intent.id,
                    "choice": {
                        "id": option.get("id"),
                        "label": option.get("label") or "回应 NPC",
                        "result_text": option.get("result_text") or intent.description,
                    },
                    "result_text": option.get("result_text") or intent.description or "你的回应被对方记住了。",
                    "relationship_changes": relationship_changes,
                    "memory_written": memory_written,
                    "promises": promises,
                    "tensions": tensions,
                }
                action_events.append(
                    {
                        "type": "npc_intent_responded",
                        "intent_id": intent.id,
                        "response_id": response_id,
                        "npc_id": intent.npc_id,
                    }
                )
            elif kind == "daily_tick":
                steps = max(1, min(24, int(n or daily_n or 1)))
                for _ in range(steps):
                    self.state = advance_tick(self.state)
                action_events.append({"type": "time_advanced", "ticks": steps})
            elif kind == "compound_sleep":
                pl = _player_at_location(self.state.player, Location.home)
                player = pl.model_copy(
                    update={"stamina": pl.max_stamina, "hp": pl.max_hp, "mp": pl.max_mp}
                )
                self.state = self.state.model_copy(update={"player": player, "scene_id": pl.scene_id})
                steps = max(1, min(24, int(daily_n or n or 1)))
                for _ in range(steps):
                    self.state = advance_tick(self.state)
                action_events.append({"type": "rested", "location": "home", "ticks": steps})
            elif kind == "scene_activity":
                if not activity_id:
                    return fail("missing_activity_id")
                activity = find_scene_activity(self.root, activity_id)
                if not activity:
                    return fail("unknown_activity")

                try:
                    plan = plan_scene_activity(
                        activity,
                        activity_id=activity_id,
                        activity_choice=activity_choice,
                        scene_id=self.state.player.scene_id,
                        time_band=self.state.time_band,
                        day=self.state.day,
                        flags=self.state.flags,
                        player=self.state.player,
                    )
                except ActivityValidationError as exc:
                    return fail(exc.code, **exc.details)

                effects = plan.effects
                selected_choice = plan.selected_choice
                choice_id = str(activity_choice or "").strip()
                if effects.get("sleep_until_morning") is True:
                    candidate_state = self.state.model_copy(update={"flags": plan.next_flags})
                    candidate_status = day_gate_status(self.root, candidate_state)
                    if not candidate_status.get("ready"):
                        return fail("day_end_gate_incomplete", **self._day_gate_error())
                if plan.next_flags != self.state.flags:
                    self.state = self.state.model_copy(update={"flags": plan.next_flags})

                self.state, relationship_changes = apply_relationship_effects(
                    self.state,
                    effects.get("relationship") if isinstance(effects.get("relationship"), dict) else {},
                )
                self.state = self.state.model_copy(update={"player": plan.next_player})
                resource_changes = plan.resource_changes
                tree_damage = plan.tree_damage
                time_cost = plan.time_cost
                if tree_damage:
                    next_hp = max(0, self.state.tree.hp - tree_damage)
                    tree = self.state.tree.model_copy(
                        update={
                            "hp": next_hp,
                            "state": TreeState.fallen if next_hp <= 0 else self.state.tree.state,
                        }
                    )
                    self.state = self.state.model_copy(update={"tree": tree})

                for npc_id, memory in (effects.get("memory") or {}).items():
                    if not isinstance(memory, dict):
                        continue
                    stored = self.memory_store.append_important_memory(
                        str(npc_id),
                        {
                            "day": self.state.day,
                            "type": memory.get("type") or "scene_activity",
                            "summary": memory.get("summary") or "",
                            "weight": memory.get("weight") or 3,
                            "source_event": f"{activity_id}:{choice_id}" if choice_id else activity_id,
                        },
                        self.run_id,
                    )
                    memory_written.append({"npc_id": str(npc_id), **stored})

                promises = effects.get("promises") if isinstance(effects.get("promises"), dict) else {}
                tensions = effects.get("tensions") if isinstance(effects.get("tensions"), dict) else {}
                for npc_id, text in promises.items():
                    self.memory_store.add_promise(str(npc_id), str(text), self.run_id)
                for npc_id, text in tensions.items():
                    self.memory_store.add_tension(str(npc_id), str(text), self.run_id)

                if effects.get("sleep_until_morning") is True:
                    day_transition = self._resolve_day_transition(
                        reason="day_end_gate_completed",
                        trigger_event_id=activity_id,
                    )
                    action_events.append({
                        "type": "day_reset",
                        "day": self.state.day,
                        "time_band": self.state.time_band,
                        "reason": "day_end_gate_completed",
                    })

                for _ in range(time_cost):
                    self.state = advance_tick(self.state)

                activity_result = {
                    "activity": {
                        "id": activity.get("id"),
                        "title": activity.get("title"),
                        "label": activity.get("label"),
                    },
                    "activity_choice": {
                        "id": selected_choice.get("id"),
                        "label": selected_choice.get("label"),
                        "hint": selected_choice.get("hint"),
                    } if selected_choice else None,
                    "result_text": (
                        (selected_choice or {}).get("result_text")
                        or effects.get("result_text")
                        or activity.get("result_text")
                        or "这段日常被今天记住了。"
                    ),
                    "time_cost": time_cost,
                    "tree_damage": tree_damage,
                    "stamina_cost": plan.stamina_cost,
                    "hp_cost": plan.hp_cost,
                    "mp_cost": plan.mp_cost,
                    "resource_changes": resource_changes,
                    "flag_deltas": effects.get("flag_deltas") if isinstance(effects.get("flag_deltas"), dict) else {},
                    "repeat": plan.repeat,
                    "relationship_changes": relationship_changes,
                    "memory_written": memory_written,
                    "promises": promises,
                    "tensions": tensions,
                }
                action_events.append(
                    {
                        "type": "scene_activity_completed",
                        "activity_id": activity_id,
                        "time_cost": time_cost,
                        "tree_damage": tree_damage,
                    }
                )
            elif kind == "rest_until_next_day":
                status = day_gate_status(self.root, self.state)
                if not status.get("ready"):
                    return fail("day_end_gate_incomplete", **self._day_gate_error())
                day_transition = self._resolve_day_transition(
                    reason="day_end_gate_completed",
                    trigger_event_id="rest_until_next_day",
                )
                action_events.append({
                    "type": "day_reset",
                    "day": self.state.day,
                    "time_band": self.state.time_band,
                    "reason": "day_end_gate_completed",
                })

            row = {
                "kind": "player_action",
                "payload": {
                    "kind": original_kind,
                    "normalized_kind": kind,
                    "map_id": map_id,
                    "entry_point": entry_point,
                    "scene_id": scene_id,
                    "poi_id": poi_id,
                    "location": location,
                    "flag_key": flag_key,
                    "flag_value": flag_value,
                    "activity_id": activity_id,
                    "activity_choice": activity_choice,
                    "intent_id": intent_id,
                    "response_id": response_id,
                    "tile_x": tile_x,
                    "tile_y": tile_y,
                    "n": n,
                    "daily_n": daily_n,
                },
                "activity_result": activity_result,
                "intent_result": intent_result,
                "events": action_events,
                "tick": self.state.tick,
                "day": self.state.day,
            }
            self.events.append(row)
            self._append_jsonl(row)
            self._flush_writes()
            self._refresh_runtime_views()
            scene_changed = (
                before_player.map_id != self.state.player.map_id
                or before_player.scene_id != self.state.player.scene_id
            )
            out: dict = {
                "ok": True,
                "state": self.state.model_dump(mode="json"),
                "events": action_events,
                "camera": _camera_for_player(self.state.player),
                "scene_update": response_scene_update(scene_changed),
            }
            if path_payload is not None:
                out["path"] = path_payload
            if activity_result is not None:
                out["activity_result"] = activity_result
                out["relationship_changes"] = relationship_changes
                out["memory_written"] = memory_written
            if intent_result is not None:
                out["intent_result"] = intent_result
                out["relationship_changes"] = relationship_changes
                out["memory_written"] = memory_written
            if day_transition is not None:
                out["day_transition"] = day_transition
            return out

    def available_story_events(self) -> dict:
        with self._lock:
            self.state = ensure_relationships(self.state)
            events = available_events(self.root, self.state)
            active_ids = [str(e.get("id")) for e in events if e.get("id")]
            self.state = self.state.model_copy(update={"active_event_ids": active_ids})
            self._refresh_runtime_views()
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
            self._refresh_runtime_views()
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
            self._refresh_runtime_views()
            return {
                **result,
                "memory_written": memory_written,
                "available_events": available,
                "state": self.state.model_dump(mode="json"),
            }

    def npc_profile(self, npc_id: str) -> dict:
        with self._lock:
            self.state = ensure_relationships(self.state)
            self._refresh_runtime_views()
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
            self._refresh_runtime_views()
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
