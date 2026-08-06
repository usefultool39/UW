from fastapi.testclient import TestClient

from app.main import app
from app.session import Session


def test_world_regions_json():
    client = TestClient(app)
    r = client.get("/api/world/regions")
    assert r.status_code == 200
    body = r.json()
    assert body.get("v") == 1
    assert "regions" in body


def test_world_scene_activities_json():
    client = TestClient(app)
    r = client.get("/api/world/scene_activities")
    assert r.status_code == 200
    body = r.json()
    assert body.get("v") == 1
    activity = next(item for item in body["activities"] if item["id"] == "gigas_chop_rhythm")
    assert activity["repeat"] == "daily"
    reading = next(item for item in body["activities"] if item["id"] == "church_read_sacred_arts")
    assert reading["preview"]["resource_costs"] == {"stamina": 5}
    assert reading["preview"]["reward_kinds"] == ["relationship", "memory", "progress"]
    assert reading["preview"]["variable_resource_cost"] is False
    village_listen = next(item for item in body["activities"] if item["id"] == "village_square_listen")
    assert "后续村道事件" in village_listen["preview"]["benefit_text"]
    patrol_board = next(item for item in body["activities"] if item["id"] == "village_patrol_board_review")
    invite_choice = next(item for item in patrol_board["choices"] if item["id"] == "invite_village_notes")
    assert invite_choice["preview"]["relationship"] == {
        "alice.trust": 1,
        "eugeo.trust": 2,
        "alice.tension": 1,
    }
    assert invite_choice["preview"]["remembered_by"] == ["eugeo"]
    assert "effects" not in invite_choice
    silent_recheck = next(item for item in body["activities"] if item["id"] == "north_gate_silent_line_recheck")
    assert "后续静默线演练" in silent_recheck["preview"]["benefit_text"]
    assert "effects" not in village_listen
    patrol = next(item for item in body["activities"] if item["id"] == "north_gate_boundary_patrol")
    assert patrol["preview"]["variable_resource_cost"] is True
    assert "effects" not in reading
    third_month = next(
        item for item in body["activities"]
        if item["id"] == "village_third_month_support_allocation"
    )
    sacred_signal = next(
        item for item in third_month["choices"]
        if item["id"] == "commit_sacred_signal"
    )
    assert sacred_signal["preview"]["resource_costs"] == {"mp": 10, "stamina": 3}
    assert "effects" not in sacred_signal


def test_world_map_by_id_default():
    client = TestClient(app)
    r = client.get("/api/world/maps/novice_open")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "novice_open"
    assert "rows" in body
    reading_desk = next(poi for poi in body["pois"] if poi["id"] == "ix_reading_desk")
    action_ids = [action["id"] for action in reading_desk["actions"]]
    assert "church_read_sacred_arts" in action_ids
    assert "read" not in action_ids


def test_world_map_by_id_rejects_path_traversal():
    client = TestClient(app)
    r = client.get("/api/world/maps/bad$id")
    assert r.status_code == 400


def test_story_catalog_json():
    client = TestClient(app)
    r = client.get("/api/story/catalog")
    assert r.status_code == 200
    assert "nodes" in r.json()


def test_dev_content_validation_endpoint_reports_current_config_ok():
    client = TestClient(app)
    r = client.get("/api/dev/content_validation")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True, body["errors"]
    assert body["warnings"] == []
    assert body["summary"]["story_events"] >= 4


def test_state_returns_time_chapter_and_agent_positions():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.get("/api/state")
    assert r.status_code == 200
    body = r.json()
    assert body["time_band"] == "morning"
    assert body["weather_label"]
    assert body["chapter_id"] == "chapter_01"
    agents = {a["id"]: a for a in body["agents"]}
    assert agents["alice"]["tile_x"] == 11
    assert agents["alice"]["tile_y"] == 27
    assert agents["eugeo"]["tile_x"] == 54
    assert agents["eugeo"]["tile_y"] == 22


def test_story_advance_blocked_without_flags():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post("/api/story/advance", json={"target_id": "mq01_tree_arc"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert body["error"] == "requirements_not_met"


def test_story_advance_ok_after_set_flag():
    client = TestClient(app)
    client.post("/api/reset")
    client.post(
        "/api/player/action",
        json={
            "kind": "set_flag",
            "flag_key": "prologue_reading_done",
            "flag_value": 1,
        },
    )
    r = client.post("/api/story/advance", json={"target_id": "mq01_tree_arc"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["state"]["story_node_id"] == "mq01_tree_arc"


def test_player_action_set_day_refreshes_runtime_state():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post("/api/player/action", json={"kind": "set_day", "day": 46})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["state"]["day"] == 46
    assert body["state"]["time_band"] == "morning"
    assert body["events"][0]["type"] == "day_set"


def test_player_move_scene_locked():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/player/action",
        json={"kind": "move_scene", "scene_id": "goblin_cave_stub"},
    )
    assert r.json()["ok"] is False
    assert r.json()["error"] == "scene_locked"
    assert r.json()["events"][0]["type"] == "action_rejected"


def test_daily_tick_same_shape_as_step():
    client = TestClient(app)
    client.post("/api/reset")
    before = client.get("/api/state").json()
    r = client.post("/api/sim/daily_tick", json={"n": 1, "mode": "heuristic"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert len(body["events"]) == len(before["agents"])


def test_dialogue_returns_reply_and_memory_candidate():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/dialogue",
        json={"npc_id": "alice", "message": "北边界是不是有异常？"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["npc_id"] == "alice"
    assert body["reply"]
    assert body["source"] in {"fallback", "llm"}
    assert body["memory_candidate"]["type"] == "dialogue"


def test_dialogue_rejects_unknown_npc():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/dialogue",
        json={"npc_id": "unknown", "message": "你好"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert body["error"] == "unknown_npc"


def test_story_event_api_choose_updates_state_and_profile():
    client = TestClient(app)
    client.post("/api/reset")

    available = client.get("/api/story/available_events")
    assert available.status_code == 200
    events = available.json()["events"]
    assert any(event["id"] == "ch1_d1_reading_clue" for event in events)

    chosen = client.post(
        "/api/story/choose",
        json={"event_id": "ch1_d1_reading_clue", "choice_id": "ask_alice"},
    )
    assert chosen.status_code == 200
    body = chosen.json()
    assert body["ok"] is True
    assert body["state"]["flags"]["clue_boundary_record"] == 1

    profile = client.get("/api/npc/alice/profile")
    assert profile.status_code == 200
    data = profile.json()["profile"]
    assert data["relationship"]["trust"] > 0
    assert data["important_memories"]


def test_save_export_import_restores_world_and_memory():
    client = TestClient(app)
    client.post("/api/reset")
    client.post(
        "/api/story/choose",
        json={"event_id": "ch1_d1_reading_clue", "choice_id": "ask_alice"},
    )

    exported = client.get("/api/save/export")
    assert exported.status_code == 200
    save = exported.json()
    assert save["kind"] == "30town_save"
    assert save["state"]["flags"]["clue_boundary_record"] == 1
    assert save["memory_summaries"]["alice"]["important_memories"]

    client.post("/api/reset")
    assert "clue_boundary_record" not in client.get("/api/state").json()["flags"]

    imported = client.post("/api/save/import", json=save)
    assert imported.status_code == 200
    restored = imported.json()["state"]
    assert restored["flags"]["clue_boundary_record"] == 1

    profile = client.get("/api/npc/alice/profile").json()["profile"]
    assert profile["important_memories"]


def test_save_import_preserves_month_two_required_any_flags_for_day_forty_six():
    client = TestClient(app)
    client.post("/api/reset")
    for flag in [
        "month02_day31_entry_done",
        "month02_route_quiet",
        "month02_quiet_frequency_crosscheck_done",
    ]:
        r = client.post(
            "/api/player/action",
            json={"kind": "set_flag", "flag_key": flag, "flag_value": 1},
        )
        assert r.status_code == 200
        assert r.json()["ok"] is True
    client.post("/api/player/action", json={"kind": "set_day", "day": 46})
    client.post("/api/player/action", json={"kind": "move_scene", "scene_id": "reading_hall"})

    save = client.get("/api/save/export").json()

    client.post("/api/reset")
    locked = client.post(
        "/api/player/action",
        json={"kind": "scene_activity", "activity_id": "boundary_anomaly_convergence"},
    ).json()
    assert locked["ok"] is False

    imported = client.post("/api/save/import", json=save)
    assert imported.status_code == 200
    restored = imported.json()["state"]
    assert restored["day"] == 46
    assert restored["flags"]["month02_quiet_frequency_crosscheck_done"] == 1
    intents = {item["id"]: item for item in restored["npc_intents"]}
    assert "alice_calls_anomaly_convergence" in intents

    done = client.post(
        "/api/player/action",
        json={
            "kind": "scene_activity",
            "activity_id": "boundary_anomaly_convergence",
            "activity_choice": "publish_shared_anomaly_map",
        },
    ).json()
    assert done["ok"] is True
    assert done["state"]["flags"]["month02_anomaly_convergence_done"] == 1
    assert done["state"]["flags"]["month02_anomaly_source_documented"] == 1


def test_move_world_returns_path():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/player/action",
        json={"kind": "move_world", "tile_x": 26, "tile_y": 24},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "path" in body
    assert isinstance(body["path"], list)
    assert len(body["path"]) >= 2
    assert body["path"][-1] == {"x": 26, "y": 24}
    assert body["camera"]["mode"] == "follow_player"
    assert body["scene_update"]["map_id"] == "novice_open"


def test_move_map_alias_returns_unified_envelope():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/player/action",
        json={"kind": "move_map", "map_id": "novice_open", "tile_x": 26, "tile_y": 24},
    )
    body = r.json()
    assert body["ok"] is True
    assert body["events"][0]["type"] == "player_moved"
    assert body["camera"]["focus_tile"] == {"x": 26, "y": 24}
    assert "scene_update" in body


def test_move_map_rejects_blocked_terrain():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/player/action",
        json={"kind": "move_map", "map_id": "novice_open", "tile_x": 67, "tile_y": 23},
    )
    body = r.json()
    assert body["ok"] is False
    assert body["error"] == "unreachable_or_blocked"
    assert body["events"][0]["type"] == "action_rejected"


def test_enter_scene_alias_updates_scene():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/player/action",
        json={"kind": "enter_scene", "scene_id": "home_hearth"},
    )
    body = r.json()
    assert body["ok"] is True
    assert body["state"]["player"]["scene_id"] == "home_hearth"
    assert body["events"][0]["type"] == "scene_entered"


def test_interact_with_hub_runs_scene_activity():
    client = TestClient(app)
    client.post("/api/reset")
    client.post("/api/player/action", json={"kind": "enter_scene", "scene_id": "gigas_clearing"})
    r = client.post(
        "/api/player/action",
        json={
            "kind": "interact_with_hub",
            "poi_id": "ix_gigas_tree",
            "activity_id": "gigas_chop_rhythm",
        },
    )
    body = r.json()
    assert body["ok"] is True
    assert body["activity_result"]["tree_damage"] == 8
    assert body["events"][0]["type"] == "scene_activity_completed"


def test_compound_sleep_keeps_player_home_and_advances_time():
    client = TestClient(app)
    client.post("/api/reset")
    before = client.get("/api/state").json()
    r = client.post(
        "/api/player/action",
        json={"kind": "compound_sleep", "daily_n": 2},
    )
    body = r.json()
    assert body["ok"] is True
    assert body["state"]["player"]["location"] == "home"
    assert body["state"]["tick"] == before["tick"] + 2


def test_set_location_updates_player_map_anchor():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/player/action",
        json={"kind": "set_location", "location": "home"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["state"]["player"]["location"] == "home"
    assert body["state"]["player"]["scene_id"] == "home_hearth"
    assert body["state"]["player"]["tile_x"] == 11
    assert body["state"]["player"]["tile_y"] == 27


def test_scene_activity_updates_time_tree_relationship_and_memory():
    client = TestClient(app)
    client.post("/api/reset")
    client.post("/api/player/action", json={"kind": "move_scene", "scene_id": "gigas_clearing"})
    before = client.get("/api/state").json()
    r = client.post(
        "/api/player/action",
        json={"kind": "scene_activity", "activity_id": "gigas_chop_rhythm"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["activity_result"]["tree_damage"] == 8
    assert body["state"]["tick"] == before["tick"] + 3
    assert body["state"]["tree"]["hp"] == before["tree"]["hp"] - 8
    assert body["state"]["flags"]["activity_day.gigas_chop_rhythm"] == before["day"]
    assert body["relationship_changes"]
    assert body["memory_written"][0]["npc_id"] == "eugeo"

    repeated = client.post(
        "/api/player/action",
        json={"kind": "scene_activity", "activity_id": "gigas_chop_rhythm"},
    ).json()
    assert repeated["ok"] is False
    assert repeated["error"] == "already_done_today"


def test_scene_activity_choice_effects_update_flags_relationship_and_memory():
    client = TestClient(app)
    client.post("/api/reset")
    client.post("/api/player/action", json={"kind": "move_scene", "scene_id": "reading_hall"})
    before = client.get("/api/state").json()

    r = client.post(
        "/api/player/action",
        json={
            "kind": "scene_activity",
            "activity_id": "church_ask_alice_lunch",
            "activity_choice": "support_eugeo",
        },
    )

    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["activity_result"]["activity_choice"]["id"] == "support_eugeo"
    assert body["state"]["flags"]["lunch_packed_for_eugeo"] == 1
    assert body["state"]["tick"] == before["tick"] + 1
    assert any(item["npc_id"] == "eugeo" for item in body["memory_written"])
    assert any(item["npc_id"] == "eugeo" for item in body["relationship_changes"])


def test_scene_activity_tree_damage_can_fell_tree():
    session = Session(run_id="test_scene_activity_tree_damage")
    session.player_action(kind="move_scene", scene_id="gigas_clearing")
    session.state = session.state.model_copy(
        update={"tree": session.state.tree.model_copy(update={"hp": 5})}
    )

    out = session.player_action(kind="scene_activity", activity_id="gigas_chop_rhythm")

    assert out["ok"] is True
    assert out["state"]["tree"]["hp"] == 0
    assert out["state"]["tree"]["state"] == "fallen"


def test_scene_activity_rejects_wrong_time_band():
    client = TestClient(app)
    client.post("/api/reset")
    client.post("/api/player/action", json={"kind": "move_scene", "scene_id": "reading_hall"})
    r = client.post(
        "/api/player/action",
        json={"kind": "scene_activity", "activity_id": "home_evening_meal"},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is False
    assert r.json()["error"] == "wrong_time_band"


def test_scene_activity_sleep_resets_day_and_environment():
    client = TestClient(app)
    client.post("/api/reset")
    client.post("/api/sim/daily_tick", json={"n": 40, "mode": "heuristic"})
    before = client.get("/api/state").json()
    assert before["time_band"] == "evening"
    client.post("/api/player/action", json={"kind": "move_scene", "scene_id": "home_hearth"})
    client.post("/api/player/action", json={"kind": "set_flag", "flag_key": "clue_boundary_record", "flag_value": 1})

    r = client.post(
        "/api/player/action",
        json={"kind": "scene_activity", "activity_id": "home_sleep_until_morning"},
    )

    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["state"]["day"] == before["day"] + 1
    assert body["state"]["tick"] == 0
    assert body["state"]["time_band"] == "morning"
    assert body["state"]["weather_label"]
    assert body["state"]["player"]["scene_id"] == "home_hearth"
    assert body["state"]["player"]["tile_x"] == 11
    assert body["state"]["player"]["tile_y"] == 27


def test_boundary_patrol_applies_resources_and_incremental_rewards():
    session = Session(run_id="test_boundary_patrol_resources")
    session.state = session.state.model_copy(
        update={"flags": {**session.state.flags, "forest_anomaly_seen": 1}}
    )
    session.player_action(kind="move_scene", scene_id="north_gate")
    before = session.state.player

    out = session.player_action(
        kind="scene_activity",
        activity_id="north_gate_boundary_patrol",
        activity_choice="scraped_clear",
    )

    assert out["ok"] is True
    assert out["state"]["player"]["hp"] == before.hp - 8
    assert out["state"]["player"]["mp"] == before.mp - 5
    assert out["state"]["player"]["stamina"] == before.stamina - 20
    assert out["state"]["flags"]["boundary_marks"] == 2
    assert out["state"]["flags"]["boundary_patrol_clears"] == 1
    assert out["activity_result"]["resource_changes"]["hp"]["delta"] == -8
    assert out["activity_result"]["flag_deltas"]["boundary_marks"] == 2


def test_boundary_patrol_rejection_is_transactional_when_hp_is_too_low():
    session = Session(run_id="test_boundary_patrol_transaction")
    session.state = session.state.model_copy(
        update={
            "flags": {**session.state.flags, "forest_anomaly_seen": 1},
            "player": session.state.player.model_copy(update={"hp": 10}),
        }
    )
    session.player_action(kind="move_scene", scene_id="north_gate")
    before_flags = dict(session.state.flags)
    before_relationships = session.state.relationships

    out = session.player_action(
        kind="scene_activity",
        activity_id="north_gate_boundary_patrol",
        activity_choice="forced_retreat",
    )

    assert out["ok"] is False
    assert out["error"] == "insufficient_hp"
    assert out["state"]["flags"] == before_flags
    assert out["state"]["relationships"] == {
        key: value.model_dump(mode="json") for key, value in before_relationships.items()
    }


def test_scene_activity_sleep_is_blocked_until_day_gate_is_complete():
    client = TestClient(app)
    client.post("/api/reset")
    client.post("/api/sim/daily_tick", json={"n": 40, "mode": "heuristic"})
    client.post("/api/player/action", json={"kind": "move_scene", "scene_id": "home_hearth"})

    r = client.post(
        "/api/player/action",
        json={"kind": "scene_activity", "activity_id": "home_sleep_until_morning"},
    )

    body = r.json()
    assert body["ok"] is False
    assert body["error"] == "day_end_gate_incomplete"
    assert body["state"]["day"] == 1


def test_rest_until_next_day_restores_all_player_resources():
    session = Session(run_id="test_rest_all_resources")
    session.state = session.state.model_copy(
        update={
            "flags": {**session.state.flags, "clue_boundary_record": 1},
            "player": session.state.player.model_copy(update={"hp": 37, "mp": 21, "stamina": 12}),
        }
    )

    out = session.player_action(kind="rest_until_next_day")

    assert out["ok"] is True
    assert out["state"]["player"]["hp"] == out["state"]["player"]["max_hp"]
    assert out["state"]["player"]["mp"] == out["state"]["player"]["max_mp"]
    assert out["state"]["player"]["stamina"] == out["state"]["player"]["max_stamina"]


def test_npc_intent_proposal_is_preview_only():
    client = TestClient(app)
    client.post("/api/reset")
    before = client.get("/api/state").json()

    r = client.post("/api/npc/alice/intent/propose")

    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["decision"]["accepted"] is True
    assert body["source"] == "fallback"
    assert body["state"]["day"] == before["day"]
    assert body["state"]["tick"] == before["tick"]
