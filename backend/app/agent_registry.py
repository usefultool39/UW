from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import STAMINA_MAX
from .models import AgentState, Location


@dataclass(frozen=True)
class AgentProfile:
    id: str
    display: str
    role: str
    behavior_role: str
    initial_location: Location
    enabled: bool = True


DEFAULT_AGENT_PROFILES: dict[str, AgentProfile] = {
    "alice": AgentProfile(
        id="alice",
        display="爱丽丝",
        role="卢利特村 · 家务与照料",
        behavior_role="logistics",
        initial_location=Location.home,
    ),
    "eugeo": AgentProfile(
        id="eugeo",
        display="尤吉欧",
        role="卢利特村 · 巨神树天职与节奏",
        behavior_role="field",
        initial_location=Location.at_tree,
    ),
}


def default_agent_registry_path(project_root: Path) -> Path:
    return project_root / "characters" / "meta.json"


def _profile_from_row(row: dict[str, Any]) -> AgentProfile | None:
    agent_id = str(row.get("id") or "").strip()
    if not agent_id:
        return None
    default = DEFAULT_AGENT_PROFILES.get(agent_id)
    raw_location = row.get("initial_location") or (
        default.initial_location.value if default else Location.at_tree.value
    )
    try:
        initial_location = Location(str(raw_location))
    except ValueError:
        initial_location = default.initial_location if default else Location.at_tree
    return AgentProfile(
        id=agent_id,
        display=str(row.get("display") or (default.display if default else agent_id)),
        role=str(row.get("role") or (default.role if default else "协作者")),
        behavior_role=str(
            row.get("behavior_role") or (default.behavior_role if default else "field")
        ),
        initial_location=initial_location,
        enabled=bool(row.get("enabled", True)),
    )


def load_agent_profiles(project_root: Path) -> dict[str, AgentProfile]:
    path = default_agent_registry_path(project_root)
    if not path.is_file():
        return dict(DEFAULT_AGENT_PROFILES)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return dict(DEFAULT_AGENT_PROFILES)
    rows = raw.get("agents")
    if not isinstance(rows, list):
        return dict(DEFAULT_AGENT_PROFILES)
    profiles: dict[str, AgentProfile] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        profile = _profile_from_row(row)
        if profile is not None and profile.enabled:
            profiles[profile.id] = profile
    return profiles


def get_agent_profile(project_root: Path, agent_id: str) -> AgentProfile:
    profiles = load_agent_profiles(project_root)
    return profiles.get(
        agent_id,
        AgentProfile(
            id=agent_id,
            display=agent_id.title(),
            role="协作者",
            behavior_role="field",
            initial_location=Location.at_tree,
        ),
    )


def initial_agent_states(project_root: Path) -> list[AgentState]:
    profiles = load_agent_profiles(project_root)
    return [
        AgentState(
            id=profile.id,
            stamina=STAMINA_MAX,
            stamina_max=STAMINA_MAX,
            hunger=0,
            location=profile.initial_location,
        )
        for profile in profiles.values()
    ]
