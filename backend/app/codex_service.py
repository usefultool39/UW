from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .agent_registry import get_agent_profile
from .memory_store import MemoryStore
from .models import WorldState
from .scene_activities import load_scene_activities
from .story_catalog import default_catalog_path, load_main_nodes
from .story_director import load_story_events


# These are the authored, player-facing collections for the current vertical slice.
# Completion is never stored here: this catalog only gives the read-only view a
# stable order and human-readable category for authoritative state below.
ACTIVITY_CATALOG: tuple[tuple[str, str, str], ...] = (
    ("church_read_sacred_arts", "推理", "书库三步推理"),
    ("home_hearth_cooking", "烹饪", "炉火备餐"),
    ("village_square_bulletin_board", "公告柱", "村道公告柱"),
    ("west_fields_herb_gather", "采集", "西侧田野采药"),
    ("gigas_chop_rhythm", "训练", "古誓树节奏训练"),
    ("north_gate_boundary_patrol", "巡查", "北门短程巡查"),
)

FRAGMENT_CATALOG: tuple[tuple[str, str, str], ...] = (
    (
        "west_fields_stone_tablet_fragment_1",
        "石碑后的裂缝",
        "前往西侧田野，调查石碑后的裂缝。",
    ),
    (
        "west_fields_stone_tablet_fragment_2",
        "倒伏石碑的背面",
        "前往西侧田野，查看倒伏石碑的背面。",
    ),
    (
        "west_fields_stone_tablet_fragment_3",
        "田埂下的刻痕",
        "前往西侧田野，沿田埂寻找刻痕。",
    ),
)

FLAG_LABELS = {
    "prologue_reading_done": "完成书库的第一轮阅读",
    "studied_sacred_arts": "读懂刻印术笔记",
    "forest_anomaly_seen": "确认北门边境异常",
    "d1_bond": "与爱丽丝、尤吉欧的日常羁绊",
    "d3_talk_about_index": "三人谈及禁忌目录",
    "d9_farewell_choice": "告别时的承诺",
    "west_fields.stone_tablet_complete": "集齐三块石碑碎片",
    "bulletin_pass_message_done": "完成公告柱传话",
    "bulletin_deliver_supplies_done": "完成公告柱补给",
    "bulletin_check_records_done": "完成公告柱记录核对",
}


def _value(state: WorldState, key: str) -> int:
    try:
        return int((state.flags or {}).get(key, 0))
    except (TypeError, ValueError):
        return 0


def _flag_condition(key: str, expected: int = 1) -> str:
    label = FLAG_LABELS.get(str(key))
    if label:
        return label
    return "完成前置线索" if expected <= 1 else "完成更多前置线索"


def _requirements_view(state: WorldState, requirements: Any, *, include_day: bool = True) -> tuple[bool, str]:
    req = requirements if isinstance(requirements, dict) else {}
    conditions: list[str] = []
    for key, expected in (req.get("required_flags") or {}).items():
        try:
            want = int(expected)
        except (TypeError, ValueError):
            want = 1
        if _value(state, str(key)) < want:
            conditions.append(_flag_condition(str(key), want))
    required_any = req.get("required_any_flags") or {}
    if isinstance(required_any, dict) and required_any:
        if not any(_value(state, str(key)) >= int(value) for key, value in required_any.items()):
            conditions.append("完成任一前置线索")
    if include_day:
        try:
            day_min = int(req["day_min"]) if req.get("day_min") is not None else None
            day_max = int(req["day_max"]) if req.get("day_max") is not None else None
        except (TypeError, ValueError):
            day_min = day_max = None
        if day_min is not None and state.day < day_min:
            conditions.append(f"第 {day_min} 天后开放")
        if day_max is not None and state.day > day_max:
            conditions.append("当前日期已错过这段窗口")
    return not conditions, "；".join(dict.fromkeys(conditions))


def _activity_events(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        if not isinstance(row, dict) or row.get("kind") != "player_action":
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        activity_id = str(payload.get("activity_id") or "").strip()
        if not activity_id:
            continue
        completed = any(
            isinstance(item, dict)
            and item.get("type") == "scene_activity_completed"
            for item in (row.get("events") or [])
        )
        if completed:
            by_id[activity_id].append(row)
    return by_id


def _choice_label(activity: dict[str, Any], choice_id: str) -> str:
    for choice in activity.get("choices") or []:
        if isinstance(choice, dict) and str(choice.get("id") or "") == choice_id:
            return str(choice.get("label") or choice_id)
    return choice_id


def _activity_view(
    state: WorldState,
    activity: dict[str, Any],
    category: str,
    display_title: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    activity_id = str(activity.get("id") or "")
    repeat = str(activity.get("repeat") or "free")
    requirements_ok, condition = _requirements_view(state, activity.get("requirements"))
    scene_ids = activity.get("scene_ids") if isinstance(activity.get("scene_ids"), list) else [activity.get("scene_id")]
    scene_ids = [str(item) for item in scene_ids if item]
    scene_unlocked = not scene_ids or any(scene in (state.unlocked_scenes or []) for scene in scene_ids)
    completed = bool(records) or _value(state, f"activity_done.{activity_id}") > 0
    if completed:
        status = "completed"
    elif not requirements_ok or not scene_unlocked:
        status = "locked"
        condition = condition or "先解锁对应场景"
    else:
        status = "available"
        condition = condition or "前往对应地点尝试一次"
    choices: list[str] = []
    for row in records[-6:]:
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        choice_id = str(payload.get("activity_choice") or "").strip()
        if choice_id:
            label = _choice_label(activity, choice_id)
            if label not in choices:
                choices.append(label)
    last_day = None
    if records:
        last_day = records[-1].get("day")
    elif _value(state, f"activity_day.{activity_id}") > 0:
        last_day = _value(state, f"activity_day.{activity_id}")
    return {
        "id": activity_id,
        "category": category,
        "title": display_title or activity.get("title") or activity_id,
        "description": activity.get("description") or activity.get("label") or "",
        "status": status,
        "completed": completed,
        "count": len(records),
        "last_day": last_day,
        "choices": choices,
        "condition": condition,
        "repeat": repeat,
        "scene_ids": scene_ids,
    }


def _mainline_view(state: WorldState, project_root: Path) -> list[dict[str, Any]]:
    completed = set(str(item) for item in (state.completed_event_ids or []))
    active = set(str(item) for item in (state.active_event_ids or []))
    rows: list[dict[str, Any]] = []
    for event in load_story_events(project_root, state.chapter_id):
        event_id = str(event.get("id") or "")
        if not event_id:
            continue
        trigger = event.get("trigger") if isinstance(event.get("trigger"), dict) else {}
        requirements_ok, condition = _requirements_view(state, trigger)
        if event_id in completed:
            status = "completed"
        elif event_id in active and requirements_ok:
            status = "available"
        else:
            status = "locked"
            condition = condition or "完成前一个主线节点"
        rows.append(
            {
                "id": event_id,
                "title": event.get("title") or event_id,
                "description": event.get("description") or "",
                "status": status,
                "completed": event_id in completed,
                "condition": condition,
                "day": trigger.get("day_min"),
                "participants": list(event.get("participants") or []),
            }
        )
    return rows


def _fragment_view(state: WorldState, project_root: Path) -> list[dict[str, Any]]:
    del project_root  # reserved for future authored collection catalogs
    done_flags = state.flags or {}
    inventory_count = max(0, int((state.inventory or {}).get("stone_tablet_fragment", 0)))
    rows: list[dict[str, Any]] = []
    for index, (activity_id, title, condition) in enumerate(FRAGMENT_CATALOG):
        collected = _value(state, f"activity_done.{activity_id}") > 0
        # Imported/older saves may only carry the aggregate item count. Use that
        # authoritative count as a compatibility fallback, never browser state.
        if not collected and index < inventory_count:
            collected = True
        rows.append(
            {
                "id": activity_id,
                "title": title,
                "description": "石碑碎片，拼合后才能读出完整刻痕。",
                "collected": collected,
                "status": "collected" if collected else "hidden",
                "condition": "已写入行囊" if collected else condition,
            }
        )
    return rows


def _relationship_milestones(state: WorldState, npc_id: str) -> list[dict[str, Any]]:
    rel = (state.relationships or {}).get(npc_id)
    values = {
        "affinity": int(getattr(rel, "affinity", 0)) if rel is not None else 0,
        "trust": int(getattr(rel, "trust", 0)) if rel is not None else 0,
        "tension": int(getattr(rel, "tension", 0)) if rel is not None else 0,
    }
    definitions = (
        ("trust_10", "trust", 10, "愿意把小计划交给你"),
        ("trust_25", "trust", 25, "愿意把重要记录交给你"),
        ("affinity_10", "affinity", 10, "愿意分享更多村中日常"),
        ("affinity_25", "affinity", 25, "把你视作可以并肩行动的人"),
        ("tension_10", "tension", 10, "开始认真留意你的冒险倾向"),
        ("tension_18", "tension", 18, "关系进入明显戒备区"),
    )
    return [
        {
            "id": f"{npc_id}:{milestone_id}",
            "dimension": dimension,
            "threshold": threshold,
            "label": label,
            "unlocked": values[dimension] >= threshold,
            "value": values[dimension],
            "condition": f"{dimension_label(dimension)}达到 {threshold}",
        }
        for milestone_id, dimension, threshold, label in definitions
    ]


def dimension_label(dimension: str) -> str:
    return {"affinity": "好感", "trust": "信任", "tension": "紧张"}.get(dimension, dimension)


def build_codex(
    *,
    state: WorldState,
    project_root: Path,
    events: list[dict[str, Any]],
    memory_store: MemoryStore,
) -> dict[str, Any]:
    activity_defs = {
        str(item.get("id")): item
        for item in (load_scene_activities(project_root).get("activities") or [])
        if isinstance(item, dict) and item.get("id")
    }
    records = _activity_events(events)
    activities: list[dict[str, Any]] = []
    for activity_id, category, title in ACTIVITY_CATALOG:
        activity = activity_defs.get(activity_id)
        if activity is not None:
            activities.append(_activity_view(state, activity, category, title, records.get(activity_id, [])))

    npc_rows: list[dict[str, Any]] = []
    recent_memories: list[dict[str, Any]] = []
    for agent in state.agents:
        npc_id = str(agent.id)
        profile = get_agent_profile(project_root, npc_id)
        summary = memory_store.load_summary(npc_id)
        memories = [item for item in (summary.get("important_memories") or []) if isinstance(item, dict)]
        memories = memories[:8]
        for memory in memories:
            recent_memories.append(
                {
                    "npc_id": npc_id,
                    "npc": profile.display,
                    "summary": memory.get("summary") or "",
                    "day": memory.get("day"),
                    "type": memory.get("type") or "choice",
                    "weight": memory.get("weight") or 0,
                }
            )
        rel = (state.relationships or {}).get(npc_id)
        relationship = {
            "affinity": int(getattr(rel, "affinity", 0)) if rel is not None else 0,
            "trust": int(getattr(rel, "trust", 0)) if rel is not None else 0,
            "tension": int(getattr(rel, "tension", 0)) if rel is not None else 0,
        }
        npc_rows.append(
            {
                "npc_id": npc_id,
                "npc": profile.display,
                "relationship": relationship,
                "memories": memories,
                "promises": list((summary.get("promises") or [])[-6:]),
                "tensions": list((summary.get("tensions") or [])[-6:]),
                "milestones": _relationship_milestones(state, npc_id),
            }
        )

    mainline = _mainline_view(state, project_root)
    fragments = _fragment_view(state, project_root)
    completed_count = sum(1 for item in mainline if item["completed"])
    completed_count += sum(1 for item in fragments if item["collected"])
    completed_count += sum(1 for item in activities if item["completed"])
    total_count = len(mainline) + len(fragments) + len(activities)
    return {
        "version": 1,
        "source": "server_authoritative",
        "progress": {
            "completed": completed_count,
            "total": total_count,
            "percent": round((completed_count / total_count) * 100) if total_count else 0,
        },
        "mainline": mainline,
        "fragments": fragments,
        "activities": activities,
        "npcs": npc_rows,
        "recent_memories": recent_memories[:24],
    }
