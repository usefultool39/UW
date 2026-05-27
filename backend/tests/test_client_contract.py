from app.api_models import PlayerActionBody, PlayerActionResult
from app.player_actions import normalize_player_action_kind
from app.session import Session


def test_player_action_body_keeps_wire_shape():
    body = PlayerActionBody(
        kind="move_map",
        map_id="novice_open",
        tile_x=26,
        tile_y=24,
    )

    assert body.model_dump(exclude_none=True) == {
        "kind": "move_map",
        "map_id": "novice_open",
        "tile_x": 26,
        "tile_y": 24,
    }


def test_player_action_result_model_accepts_move_envelope():
    sess = Session(run_id="contract-move")
    out = sess.player_action(kind="move_map", map_id="novice_open", tile_x=26, tile_y=24)

    parsed = PlayerActionResult.model_validate(out)

    assert parsed.ok is True
    assert parsed.path
    assert parsed.camera.focus_tile == {"x": 26, "y": 24}
    assert parsed.scene_update.map_id == "novice_open"


def test_interact_with_activity_normalizes_to_scene_activity():
    original, normalized = normalize_player_action_kind(
        "interact_with_hub",
        activity_id="gigas_chop_rhythm",
    )

    assert original == "interact_with_hub"
    assert normalized == "scene_activity"


def test_player_action_body_accepts_npc_intent_response_fields():
    body = PlayerActionBody(
        kind="respond_npc_intent",
        intent_id="alice_invites_reading",
        response_id="accept_reading_note",
    )

    assert body.model_dump(exclude_none=True) == {
        "kind": "respond_npc_intent",
        "intent_id": "alice_invites_reading",
        "response_id": "accept_reading_note",
    }
