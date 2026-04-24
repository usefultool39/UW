"""根据主线节点与旗标解析「人格阶段」，用于叠加角色 overlay 文本（原著时间线）。"""

from __future__ import annotations

from .models import WorldState

# 显式白名单：避免任意 `mq02*` 误匹配；新增央都/学院阶段时请把 story_node_id 加进此集合。
_STORIA_ACADEMY_STORY_IDS: frozenset[str] = frozenset({"mq02_future_stub"})


def persona_phase_key(state: WorldState) -> str:
    """
    返回稳定键名；对应 `characters/<agent_id>/overlay_<key>.md`（可选）。
    当前模拟锚定在卢利特村 **童年期**；后续可增 academy / integrity_knight 等阶段。
    """
    nid = (state.story_node_id or "").strip()
    flags = state.flags or {}

    if nid in _STORIA_ACADEMY_STORY_IDS:
        return "storia_academy"
    if nid.startswith("mq01") or nid == "mq01_tree_arc":
        return "childhood_mq01"
    if int(flags.get("prologue_reading_done") or 0) >= 1:
        return "childhood_post_reading"
    return "childhood_rulid"
