from __future__ import annotations

import json
import threading
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryStore:
    """Phase-1 NPC memory store: JSONL events + rolling summary."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._locks_guard = threading.Lock()
        self._npc_locks: dict[str, threading.Lock] = {}

    def _npc_lock(self, npc_id: str) -> threading.Lock:
        with self._locks_guard:
            lock = self._npc_locks.get(npc_id)
            if lock is None:
                lock = threading.Lock()
                self._npc_locks[npc_id] = lock
            return lock

    def _npc_dir(self, npc_id: str) -> Path:
        d = self.root_dir / npc_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _events_path(self, npc_id: str) -> Path:
        return self._npc_dir(npc_id) / "events.jsonl"

    def _summary_path(self, npc_id: str) -> Path:
        return self._npc_dir(npc_id) / "summary.json"

    def _default_summary(self, npc_id: str) -> dict[str, Any]:
        return {
            "npc_id": npc_id,
            "total_events": 0,
            "success_count": 0,
            "fail_count": 0,
            "action_stats": {},
            "last_tick": None,
            "last_day": None,
            "last_run_id": None,
            "last_action": None,
            "last_detail": None,
            "last_updated_at": None,
            "notable_failures": [],
            "important_memories": [],
            "promises": [],
            "tensions": [],
        }

    def load_summary(self, npc_id: str) -> dict[str, Any]:
        p = self._summary_path(npc_id)
        if not p.exists():
            return self._default_summary(npc_id)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return self._default_summary(npc_id)
        default = self._default_summary(npc_id)
        for key, value in default.items():
            data.setdefault(key, value)
        return data

    def read_recent_events(self, npc_id: str, limit: int = 20) -> list[dict[str, Any]]:
        p = self._events_path(npc_id)
        if not p.exists():
            return []

        lim = max(1, min(500, int(limit)))
        tail: deque[str] = deque(maxlen=lim)
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                tail.append(line)
        out: list[dict[str, Any]] = []
        for line in tail:
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    def _save_summary(self, npc_id: str, summary: dict[str, Any]) -> None:
        p = self._summary_path(npc_id)
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(p)

    @contextmanager
    def _with_npc_lock(self, npc_id: str):
        lock = self._npc_lock(npc_id)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()

    def append_event(self, npc_id: str, event_row: dict[str, Any], run_id: str) -> None:
        payload = {
            "recorded_at": _utc_now_iso(),
            "run_id": run_id,
            **event_row,
        }
        with self._with_npc_lock(npc_id):
            events_path = self._events_path(npc_id)
            with events_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")

            summary = self.load_summary(npc_id)
            summary["total_events"] = int(summary.get("total_events", 0)) + 1
            if payload.get("ok") is True:
                summary["success_count"] = int(summary.get("success_count", 0)) + 1
            else:
                summary["fail_count"] = int(summary.get("fail_count", 0)) + 1

            action = str(payload.get("action_name") or payload.get("action") or "")
            stats = summary.get("action_stats") or {}
            stats[action] = int(stats.get(action, 0)) + 1
            summary["action_stats"] = stats

            summary["last_tick"] = payload.get("tick")
            summary["last_day"] = payload.get("day")
            summary["last_run_id"] = run_id
            summary["last_action"] = action
            summary["last_detail"] = payload.get("detail")
            summary["last_updated_at"] = payload.get("recorded_at")

            if payload.get("ok") is False:
                failures = summary.get("notable_failures") or []
                failures.append(
                    {
                        "tick": payload.get("tick"),
                        "day": payload.get("day"),
                        "detail": payload.get("detail"),
                        "action": action,
                        "run_id": run_id,
                    }
                )
                summary["notable_failures"] = failures[-20:]

            self._save_summary(npc_id, summary)

    def append_important_memory(
        self,
        npc_id: str,
        memory: dict[str, Any],
        run_id: str,
    ) -> dict[str, Any]:
        payload = {
            "recorded_at": _utc_now_iso(),
            "run_id": run_id,
            "day": memory.get("day"),
            "type": str(memory.get("type") or "choice")[:40],
            "summary": str(memory.get("summary") or "")[:180],
            "weight": max(1, min(5, int(memory.get("weight", 3)))),
            "source_event": memory.get("source_event"),
        }
        if not payload["summary"]:
            payload["summary"] = "发生了一件值得记住的事。"

        with self._with_npc_lock(npc_id):
            summary = self.load_summary(npc_id)
            memories = summary.get("important_memories") or []
            memories.append(payload)
            memories = sorted(
                memories[-30:],
                key=lambda item: (int(item.get("weight") or 0), str(item.get("recorded_at") or "")),
                reverse=True,
            )
            summary["important_memories"] = memories[:24]
            summary["last_updated_at"] = payload["recorded_at"]
            summary["last_run_id"] = run_id
            self._save_summary(npc_id, summary)
        return payload

    def add_promise(self, npc_id: str, text: str, run_id: str) -> str:
        text = str(text or "").strip()[:180]
        if not text:
            return ""
        with self._with_npc_lock(npc_id):
            summary = self.load_summary(npc_id)
            promises = summary.get("promises") or []
            if text not in promises:
                promises.append(text)
            summary["promises"] = promises[-20:]
            summary["last_updated_at"] = _utc_now_iso()
            summary["last_run_id"] = run_id
            self._save_summary(npc_id, summary)
        return text

    def add_tension(self, npc_id: str, text: str, run_id: str) -> str:
        text = str(text or "").strip()[:180]
        if not text:
            return ""
        with self._with_npc_lock(npc_id):
            summary = self.load_summary(npc_id)
            tensions = summary.get("tensions") or []
            if text not in tensions:
                tensions.append(text)
            summary["tensions"] = tensions[-20:]
            summary["last_updated_at"] = _utc_now_iso()
            summary["last_run_id"] = run_id
            self._save_summary(npc_id, summary)
        return text

    def replace_summary(
        self,
        npc_id: str,
        summary: dict[str, Any],
        run_id: str,
    ) -> dict[str, Any]:
        """Restore the compact memory profile from a save file."""
        base = self._default_summary(npc_id)
        if isinstance(summary, dict):
            for key in base:
                if key in summary:
                    base[key] = summary[key]
        base["npc_id"] = npc_id
        base["last_run_id"] = run_id
        base["important_memories"] = list(base.get("important_memories") or [])[:24]
        base["promises"] = list(base.get("promises") or [])[-20:]
        base["tensions"] = list(base.get("tensions") or [])[-20:]
        base["last_updated_at"] = _utc_now_iso()
        with self._with_npc_lock(npc_id):
            self._save_summary(npc_id, base)
        return base

    def read_important_context(self, npc_id: str, limit: int = 6) -> dict[str, Any]:
        summary = self.load_summary(npc_id)
        memories = summary.get("important_memories") or []
        return {
            "important_memories": memories[: max(1, min(20, int(limit)))],
            "promises": (summary.get("promises") or [])[-6:],
            "tensions": (summary.get("tensions") or [])[-6:],
        }
