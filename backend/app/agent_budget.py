"""Per-playthrough budget for optional model calls.

Budgets protect local development and paid provider quotas. A denied call is
always expected to fall back to the scripted/heuristic path.
"""

from __future__ import annotations

import os
from typing import Any

_DEFAULT_TOTAL = 24
_DEFAULT_LIMITS = {"action": 12, "dialogue": 12, "intent": 6}


def _env_int(name: str, default: int) -> int:
    try:
        return max(0, min(1000, int(os.getenv(name, str(default)))))
    except (TypeError, ValueError):
        return default


class AgentBudget:
    def __init__(self) -> None:
        self.total_limit = _env_int("AI_MAX_CALLS_PER_RUN", _DEFAULT_TOTAL)
        self.limits = {
            kind: _env_int(f"AI_MAX_{kind.upper()}_CALLS_PER_RUN", default)
            for kind, default in _DEFAULT_LIMITS.items()
        }
        self.counts: dict[str, int] = {kind: 0 for kind in self.limits}

    def reserve(self, kind: str, *, enabled: bool = True) -> dict[str, Any]:
        kind = str(kind or "unknown")
        used = int(self.counts.get(kind, 0))
        limit = int(self.limits.get(kind, self.total_limit))
        total_used = sum(self.counts.values())
        if not enabled:
            return self._decision(kind, False, "not_requested", used, limit, total_used)
        if total_used >= self.total_limit:
            return self._decision(kind, False, "total_budget_exhausted", used, limit, total_used)
        if used >= limit:
            return self._decision(kind, False, "purpose_budget_exhausted", used, limit, total_used)
        self.counts[kind] = used + 1
        return self._decision(kind, True, "reserved", used + 1, limit, total_used + 1)

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_used": sum(self.counts.values()),
            "total_limit": self.total_limit,
            "by_purpose": {
                kind: {"used": int(self.counts.get(kind, 0)), "limit": int(limit)}
                for kind, limit in self.limits.items()
            },
        }

    def _decision(
        self,
        kind: str,
        allowed: bool,
        reason: str,
        used: int,
        limit: int,
        total_used: int,
    ) -> dict[str, Any]:
        return {
            "kind": kind,
            "allowed": allowed,
            "reason": reason,
            "used": used,
            "limit": limit,
            "total_used": total_used,
            "total_limit": self.total_limit,
        }
