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
