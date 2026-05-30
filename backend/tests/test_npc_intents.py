from fastapi.testclient import TestClient

from app.main import app
from app.session import Session


def test_state_exposes_day1_npc_intents():
    client = TestClient(app)
    client.post("/api/reset")

    state = client.get("/api/state").json()
    intents = {item["id"]: item for item in state["npc_intents"]}

    assert "alice_invites_reading" in intents
    assert "eugeo_invites_training" in intents
    assert intents["alice_invites_reading"]["action"] == {
        "type": "scene_activity",
        "activity_id": "church_read_sacred_arts",
    }
    assert intents["alice_invites_reading"]["response_options"]
    assert intents["alice_invites_reading"]["stakes"]
    assert intents["eugeo_invites_training"]["action"] == {
        "type": "story_event",
        "event_id": "ch1_d1_training_with_eugeo",
    }


def test_reading_activity_changes_alice_intent_to_reaction():
    client = TestClient(app)
    client.post("/api/reset")
    client.post("/api/player/action", json={"kind": "move_scene", "scene_id": "reading_hall"})
    client.post(
        "/api/player/action",
        json={
            "kind": "scene_activity",
            "activity_id": "church_read_sacred_arts",
            "activity_choice": "trace_silence",
        },
    )

    state = client.get("/api/state").json()
    intents = {item["id"]: item for item in state["npc_intents"]}

    assert "alice_invites_reading" not in intents
    assert intents["alice_reacts_to_boundary_record"]["action"] == {
        "type": "story_event",
        "event_id": "ch1_d1_reading_clue",
    }
    assert any(opt["id"] == "calm_before_telling" for opt in intents["alice_reacts_to_boundary_record"]["response_options"])


def test_responding_to_npc_intent_writes_relationship_memory_and_hides_once_option():
    client = TestClient(app)
    client.post("/api/reset")

    r = client.post(
        "/api/player/action",
        json={
            "kind": "respond_npc_intent",
            "intent_id": "alice_invites_reading",
            "response_id": "accept_reading_note",
        },
    )

    body = r.json()
    assert body["ok"] is True
    assert body["intent_result"]["kind"] == "npc_intent_response"
    assert body["events"][0]["type"] == "npc_intent_responded"
    assert body["state"]["flags"]["alice_reading_invite_ack"] == 1
    assert body["state"]["flags"]["npc_intent_response.alice_invites_reading.accept_reading_note"] == 1
    assert any(item["npc_id"] == "alice" and item["field"] == "trust" for item in body["relationship_changes"])
    assert any(item["npc_id"] == "alice" for item in body["memory_written"])

    state = client.get("/api/state").json()
    intent = next(item for item in state["npc_intents"] if item["id"] == "alice_invites_reading")
    assert all(opt["id"] != "accept_reading_note" for opt in intent["response_options"])


def test_npc_profile_exposes_mind_snapshot():
    client = TestClient(app)
    client.post("/api/reset")

    profile = client.get("/api/npc/alice/profile").json()["profile"]

    assert profile["mind"]["current_goal"]
    assert profile["mind"]["active_focus"] == "艾琳想让你先看旧记录"
    assert isinstance(profile["mind"]["beliefs"], list)


def test_day_four_debrief_intent_guides_player_back_to_library():
    sess = Session(run_id="test-day4-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 4,
            "time_band": "morning",
            "flags": {"boundary_incident_resolved": 1},
        }
    )

    state = sess.public_state()
    intents = {item.id: item for item in state.npc_intents}

    assert intents["alice_calls_boundary_debrief"].action == {
        "type": "story_event",
        "event_id": "ch1_d4_after_boundary_debrief",
    }
    assert intents["alice_calls_boundary_debrief"].response_options
    assert intents["alice_calls_boundary_debrief"].scene_id == "reading_hall"


def test_day_seven_drill_intent_guides_player_to_north_gate():
    sess = Session(run_id="test-day7-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 7,
            "time_band": "afternoon",
            "flags": {"month01_debrief_done": 1},
        }
    )

    state = sess.public_state()
    intents = {item.id: item for item in state.npc_intents}

    assert intents["eugeo_pushes_north_gate_drill"].action == {
        "type": "story_event",
        "event_id": "ch1_d7_first_boundary_drill",
    }
    assert intents["eugeo_pushes_north_gate_drill"].scene_id == "north_gate"


def test_day_twelve_village_intent_guides_player_to_square():
    sess = Session(run_id="test-day12-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 12,
            "time_band": "evening",
            "flags": {"month01_drill_done": 1},
        }
    )

    state = sess.public_state()
    intents = {item.id: item for item in state.npc_intents}

    assert intents["alice_guides_village_trust"].action == {
        "type": "story_event",
        "event_id": "ch1_d12_village_trust",
    }
    assert intents["alice_guides_village_trust"].scene_id == "village_square"


def test_day_eighteen_silent_line_intent_guides_player_to_north_gate():
    sess = Session(run_id="test-day18-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 18,
            "time_band": "morning",
            "flags": {"month01_village_trust": 1},
        }
    )

    state = sess.public_state()
    intents = {item.id: item for item in state.npc_intents}

    assert intents["eugeo_calls_silent_line_rehearsal"].action == {
        "type": "story_event",
        "event_id": "ch1_d18_silent_line_rehearsal",
    }
    assert intents["eugeo_calls_silent_line_rehearsal"].scene_id == "north_gate"


def test_day_twenty_four_pack_intent_guides_player_home():
    sess = Session(run_id="test-day24-pack-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 24,
            "time_band": "morning",
            "flags": {"month01_silent_line_rehearsed": 1},
        }
    )

    state = sess.public_state()
    intents = {item.id: item for item in state.npc_intents}

    assert intents["alice_checks_expedition_pack"].action == {
        "type": "scene_activity",
        "activity_id": "home_expedition_pack_review",
    }
    assert intents["alice_checks_expedition_pack"].scene_id == "home_hearth"


def test_day_twenty_four_bridge_intent_guides_evening_hearth_talk():
    sess = Session(run_id="test-day24-bridge-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 24,
            "time_band": "evening",
            "flags": {"month01_silent_line_rehearsed": 1},
        }
    )

    state = sess.public_state()
    intents = {item.id: item for item in state.npc_intents}

    assert intents["alice_sets_expedition_bridge_talk"].action == {
        "type": "scene_activity",
        "activity_id": "home_expedition_bridge_talk",
    }
    assert intents["alice_sets_expedition_bridge_talk"].scene_id == "home_hearth"


def test_day_twenty_five_sendoff_intent_guides_player_to_square():
    sess = Session(run_id="test-day25-sendoff-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 25,
            "time_band": "afternoon",
            "flags": {"month01_expedition_ready": 1},
        }
    )

    state = sess.public_state()
    intents = {item.id: item for item in state.npc_intents}

    assert intents["eugeo_brings_pack_to_square"].action == {
        "type": "scene_activity",
        "activity_id": "village_expedition_sendoff",
    }
    assert intents["eugeo_brings_pack_to_square"].scene_id == "village_square"


def test_day_twenty_eight_gate_vigil_intent_guides_player_to_north_gate():
    sess = Session(run_id="test-day28-gate-vigil-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 28,
            "time_band": "evening",
            "flags": {"month01_expedition_ready": 1},
        }
    )

    state = sess.public_state()
    intents = {item.id: item for item in state.npc_intents}

    assert intents["alice_marks_month_gate_vigil"].action == {
        "type": "scene_activity",
        "activity_id": "north_gate_month_end_vigil",
    }
    assert intents["alice_marks_month_gate_vigil"].scene_id == "north_gate"


def test_day_thirty_two_month_two_route_intents_are_route_specific():
    cases = [
        (
            "month02_route_order",
            "alice_introduces_month02_duty",
            "reading_hall",
            {"type": "scene_activity", "activity_id": "church_month02_briefing"},
        ),
        (
            "month02_route_expedition",
            "eugeo_suggests_month02_expedition",
            "north_gate",
            {"type": "scene_activity", "activity_id": "north_gate_expedition_check"},
        ),
        (
            "month02_route_quiet",
            "alice_raises_silent_line_recheck",
            "reading_hall",
            {"type": "scene_activity", "activity_id": "reading_hall_silent_record"},
        ),
    ]

    for route_flag, intent_id, scene_id, action in cases:
        sess = Session(run_id=f"test-day32-{route_flag}")
        sess.state = sess.state.model_copy(
            update={
                "day": 32,
                "time_band": "morning",
                "flags": {
                    "month02_day31_entry_done": 1,
                    route_flag: 1,
                },
            }
        )

        intents = {item.id: item for item in sess.public_state().npc_intents}

        assert intents[intent_id].scene_id == scene_id
        assert intents[intent_id].action == action
        assert intents[intent_id].response_options


def test_day_thirty_nine_order_patrol_board_intent_guides_player_to_square():
    sess = Session(run_id="test-day39-order-patrol")
    sess.state = sess.state.model_copy(
        update={
            "day": 39,
            "time_band": "morning",
            "flags": {
                "month02_day31_entry_done": 1,
                "month02_route_order": 1,
                "month02_order_briefing_done": 1,
            },
        }
    )

    intents = {item.id: item for item in sess.public_state().npc_intents}

    assert intents["alice_formalizes_month02_patrol_board"].scene_id == "village_square"
    assert intents["alice_formalizes_month02_patrol_board"].action == {
        "type": "scene_activity",
        "activity_id": "village_month02_patrol_standby",
    }
    assert intents["alice_formalizes_month02_patrol_board"].response_options
