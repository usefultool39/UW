from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Location(str, Enum):
    at_tree = "at_tree"
    bench = "bench"
    home = "home"
    table = "table"


class TreeState(str, Enum):
    standing = "standing"
    fallen = "fallen"


class ActionName(str, Enum):
    noop = "noop"
    move = "move"
    chop = "chop"
    rest = "rest"
    eat = "eat"
    sleep = "sleep"
    go_home = "go_home"
    cook = "cook"


class Action(BaseModel):
    name: ActionName
    target: str | None = None  # move: "at_tree"|"bench"|"home"|"table"


class Tree(BaseModel):
    hp: int
    hp_max: int
    state: TreeState = TreeState.standing


class PlayerState(BaseModel):
    """主角状态（与 AI 同伴 AgentState 分离）。"""

    scene_id: str = "gigas_clearing"
    location: Location = Location.at_tree
    map_id: str = "novice_open"
    tile_x: int = 4
    tile_y: int = 10
    hp: int = 100
    max_hp: int = 100
    mp: int = 100
    max_mp: int = 100
    stamina: int = 100
    max_stamina: int = 100


class AgentState(BaseModel):
    id: str
    stamina: int
    stamina_max: int
    hunger: int
    hunger_max: int = 100
    location: Location
    scene_id: str = "gigas_clearing"
    map_id: str = "novice_open"
    tile_x: int = 0
    tile_y: int = 0
    has_axe: bool = True
    last_action_ok: bool = True
    last_action: str = "init"
    is_sleeping: bool = False
    mood: int = 50
    thought: str | None = None
    daily_contribution: int = 0
    motivation: float = 1.0
    current_goal: str | None = None


class RelationshipState(BaseModel):
    affinity: int = 0
    trust: int = 0
    tension: int = 0
    mood_note: str = "平稳"


class NpcIntent(BaseModel):
    id: str
    npc_id: str
    kind: str
    title: str
    description: str = ""
    scene_id: str
    map_id: str = "novice_open"
    tile_x: int
    tile_y: int
    priority: int = 50
    reason: str = ""
    action: dict[str, Any] = Field(default_factory=dict)
    stakes: list[str] = Field(default_factory=list)
    response_options: list[dict[str, Any]] = Field(default_factory=list)
    expires_at_tick: int | None = None


class WorldState(BaseModel):
    tick: int = 0
    day: int = 1
    time_band: Literal["morning", "afternoon", "evening", "night"] = "morning"
    weather: str = "clear"
    weather_label: str = "晴朗"
    weather_note: str = "清亮的风穿过北境村道。"
    chapter_id: str = "chapter_01"
    scene_id: str = "gigas_clearing"
    tree: Tree
    agents: list[AgentState] = Field(default_factory=list)
    timeline_mode: Literal["daily", "story"] = "daily"
    story_node_id: str = "mq00_tutorial"
    story_sub_id: str | None = None
    flags: dict[str, int] = Field(default_factory=dict)
    # Item counts are intentionally a flat map for save/API compatibility.
    # Unknown item ids remain valid so authored content can add materials
    # without requiring a model migration.
    inventory: dict[str, int] = Field(default_factory=dict)
    relationships: dict[str, RelationshipState] = Field(default_factory=dict)
    active_event_ids: list[str] = Field(default_factory=list)
    completed_event_ids: list[str] = Field(default_factory=list)
    chapter_ending_id: str | None = None
    player: PlayerState = Field(default_factory=PlayerState)
    npc_intents: list[NpcIntent] = Field(default_factory=list)
    unlocked_scenes: list[str] = Field(
        default_factory=lambda: [
            "reading_hall",
            "church_library",
            "home_hearth",
            "village_square",
            "gigas_clearing",
            "north_gate",
            "west_fields",
        ]
    )


class SimEvent(BaseModel):
    tick: int
    day: int
    actor: str
    action: str
    ok: bool
    detail: str
    tree_hp_after: int
    tree_state: str
    stamina_after: dict[str, int]
    hunger_after: dict[str, int]
    actor_name: str | None = None
    actor_role: str | None = None
    decision_mode: str | None = None
    llm_model: str | None = None
    llm_prompt_system: str | None = None
    llm_prompt_user: str | None = None
    llm_raw: str | None = None
    llm_thinking: str | None = None
    ai_budget: dict[str, Any] | None = None
    agent_mood_after: int | None = None
    agent_motivation_after: float | None = None
