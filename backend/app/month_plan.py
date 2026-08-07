from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import WorldState


def default_month_plan_path(project_root: Path, month_id: str = "month_01") -> Path:
    safe_id = "".join(ch for ch in month_id if ch.isalnum() or ch in {"_", "-"})
    if not safe_id:
        safe_id = "month_01"
    return project_root / "data" / "story" / f"{safe_id}_plan.json"


def load_month_plan(project_root: Path, month_id: str = "month_01") -> dict[str, Any]:
    path = default_month_plan_path(project_root, month_id)
    if not path.is_file():
        return {"v": 1, "id": month_id, "weeks": []}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {"v": 1, "id": month_id, "weeks": []}


def _flag_value(state: WorldState, key: str) -> int:
    return int((state.flags or {}).get(str(key), 0))


def _requirements_met(state: WorldState, requirements: dict[str, Any] | None) -> tuple[bool, str]:
    if not requirements:
        return True, ""

    for key, expected in (requirements.get("required_flags") or {}).items():
        if _flag_value(state, str(key)) < int(expected):
            return False, f"需要先完成：{key}"

    required_any = requirements.get("required_any_flags") or {}
    if isinstance(required_any, dict) and required_any:
        if not any(_flag_value(state, str(key)) >= int(expected) for key, expected in required_any.items()):
            return False, "需要先完成任一前置线索"

    for key, value in (requirements.get("forbidden_flags") or {}).items():
        if _flag_value(state, str(key)) >= int(value):
            return False, f"已被状态锁定：{key}"

    endings = requirements.get("required_endings")
    if isinstance(endings, list) and endings:
        current = state.chapter_ending_id or "unresolved"
        if current not in {str(item) for item in endings}:
            return False, "需要对应的第三天选择"

    return True, ""


def _day_range(raw: Any) -> tuple[int, int]:
    if isinstance(raw, list) and len(raw) >= 2:
        return int(raw[0]), int(raw[1])
    if isinstance(raw, int):
        return raw, raw
    return 1, 30


def _is_completed(state: WorldState, milestone: dict[str, Any]) -> bool:
    flag = str(milestone.get("completed_flag") or "")
    if flag and _flag_value(state, flag) > 0:
        return True
    event_id = str(milestone.get("related_event_id") or "")
    if event_id and event_id in (state.completed_event_ids or []):
        return True
    related_ids = milestone.get("related_event_ids")
    if isinstance(related_ids, list) and related_ids:
        return all(str(item) in (state.completed_event_ids or []) for item in related_ids)
    return False


def _status_label(status: str) -> str:
    return {
        "completed": "已完成",
        "active": "可推进",
        "upcoming": "未到日期",
        "locked": "待解锁",
        "overdue": "可补做",
    }.get(status, status)


def _month_ending_path(state: WorldState, month_id: str) -> str:
    _ = month_id
    return state.chapter_ending_id or "unresolved"


def _milestone_view(state: WorldState, raw: dict[str, Any]) -> dict[str, Any]:
    start, end = _day_range(raw.get("day_range"))
    completed = _is_completed(state, raw)
    requirements_ok, blocked_reason = _requirements_met(state, raw.get("requirements"))

    if completed:
        status = "completed"
    elif not requirements_ok:
        status = "locked"
    elif state.day < start:
        status = "upcoming"
    elif state.day > end:
        status = "overdue"
    else:
        status = "active"

    return {
        **raw,
        "day_start": start,
        "day_end": end,
        "day_label": f"Day {start}" if start == end else f"Day {start}-{end}",
        "completed": completed,
        "unlocked": requirements_ok,
        "status": status,
        "status_label": _status_label(status),
        "blocked_reason": blocked_reason,
    }


def public_month_plan(
    project_root: Path,
    state: WorldState,
    month_id: str = "month_01",
) -> dict[str, Any]:
    plan = load_month_plan(project_root, month_id)
    weeks_out: list[dict[str, Any]] = []
    current_week_id = ""
    active_milestone: dict[str, Any] | None = None

    for week in plan.get("weeks") if isinstance(plan.get("weeks"), list) else []:
        if not isinstance(week, dict):
            continue
        start, end = _day_range(week.get("day_range"))
        milestones = [
            _milestone_view(state, item)
            for item in (week.get("milestones") or [])
            if isinstance(item, dict)
        ]
        if start <= state.day <= end:
            current_week_id = str(week.get("id") or "")
        if active_milestone is None:
            active_milestone = next(
                (item for item in milestones if item["status"] in {"active", "overdue"}),
                None,
            )
        if milestones and all(item["status"] == "completed" for item in milestones):
            week_status = "completed"
        elif any(item["status"] in {"active", "overdue"} for item in milestones):
            week_status = "active"
        elif state.day < start:
            week_status = "upcoming"
        else:
            week_status = "locked"

        weeks_out.append(
            {
                **week,
                "day_start": start,
                "day_end": end,
                "day_label": f"Day {start}" if start == end else f"Day {start}-{end}",
                "status": week_status,
                "status_label": _status_label(week_status),
                "milestones": milestones,
            }
        )

    if not current_week_id and weeks_out:
        current_week_id = str(weeks_out[-1 if state.day > int(weeks_out[-1]["day_end"]) else 0].get("id") or "")

    ending_path = _month_ending_path(state, str(plan.get("id") or month_id))
    ending_notes = plan.get("ending_paths") if isinstance(plan.get("ending_paths"), dict) else {}

    return {
        "ok": True,
        "id": plan.get("id") or month_id,
        "title": plan.get("title") or "第一月路线",
        "subtitle": plan.get("subtitle") or "",
        "summary": plan.get("summary") or "",
        "day_range": plan.get("day_range") or [1, 30],
        "current": {
            "day": state.day,
            "time_band": state.time_band,
            "week_id": current_week_id,
            "ending_path": ending_path,
            "ending_note": ending_notes.get(ending_path) or ending_notes.get("unresolved") or "",
            "active_milestone_id": active_milestone.get("id") if active_milestone else "",
        },
        "weeks": weeks_out,
    }
