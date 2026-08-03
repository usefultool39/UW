"""NPC runtime selection shared by scripted and future model-backed brains.

The world rules, relationship state, memories and story director are identical
for every mode. A runtime only changes how an NPC chooses wording/intent.
"""

from __future__ import annotations

import os
from typing import Literal, cast

NpcRuntime = Literal["scripted", "hybrid", "agent"]
VALID_NPC_RUNTIMES = frozenset({"scripted", "hybrid", "agent"})


def _normalize(value: str | None, default: NpcRuntime = "scripted") -> NpcRuntime:
    candidate = str(value or "").strip().lower()
    if candidate in VALID_NPC_RUNTIMES:
        return cast(NpcRuntime, candidate)
    return default


def default_npc_runtime() -> NpcRuntime:
    """Offline-first by default; no API key is required for a full playthrough."""
    return _normalize(os.getenv("NPC_RUNTIME"), "scripted")


def npc_runtime_for(npc_id: str) -> NpcRuntime:
    """Allow gradual rollout, e.g. NPC_RUNTIME_ALICE=agent."""
    suffix = "".join(ch if ch.isalnum() else "_" for ch in str(npc_id).upper())
    return _normalize(os.getenv(f"NPC_RUNTIME_{suffix}"), default_npc_runtime())


def npc_runtime_meta() -> dict[str, str]:
    return {"npc_runtime": default_npc_runtime()}
