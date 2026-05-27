from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class RunBody(BaseModel):
    n: int = 1
    mode: Literal["heuristic", "llm"] | str = "heuristic"


class PlayerActionBody(BaseModel):
    kind: str
    map_id: str | None = None
    entry_point: str | None = None
    scene_id: str | None = None
    poi_id: str | None = None
    location: str | None = None
    flag_key: str | None = None
    flag_value: int | None = None
    activity_id: str | None = None
    activity_choice: str | None = None
    intent_id: str | None = None
    response_id: str | None = None
    tile_x: int | None = None
    tile_y: int | None = None
    n: int | None = None
    daily_n: int | None = None


class StoryAdvanceBody(BaseModel):
    target_id: str


class StoryChooseBody(BaseModel):
    event_id: str
    choice_id: str


class DialogueBody(BaseModel):
    npc_id: str
    message: str
    context: dict[str, Any] | None = None


class CameraEnvelope(BaseModel):
    mode: str = "follow_player"
    focus_tile: dict[str, int]
    map_id: str
    scene_id: str


class SceneUpdateEnvelope(BaseModel):
    changed: bool
    reason: str
    map_id: str
    scene_id: str
    region: dict[str, Any] | None = None


class PlayerActionResult(BaseModel):
    ok: bool
    state: dict[str, Any]
    events: list[dict[str, Any]]
    camera: CameraEnvelope
    scene_update: SceneUpdateEnvelope
    path: list[dict[str, int]] | None = None
    activity_result: dict[str, Any] | None = None
    intent_result: dict[str, Any] | None = None
    relationship_changes: list[dict[str, Any]] | None = None
    memory_written: list[dict[str, Any]] | None = None
    error: str | None = None
