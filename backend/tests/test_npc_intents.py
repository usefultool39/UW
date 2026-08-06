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
    assert intents["alice_calls_boundary_debrief"].scene_id == "church_library"


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
                "month02_order_open_rotation": 1,
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
    assert "公开完整轮值" in intents["alice_formalizes_month02_patrol_board"].description


def test_day_thirty_nine_expedition_supply_intent_guides_player_to_north_gate():
    sess = Session(run_id="test-day39-expedition-supply")
    sess.state = sess.state.model_copy(
        update={
            "day": 39,
            "time_band": "morning",
            "flags": {
                "month02_day31_entry_done": 1,
                "month02_route_expedition": 1,
                "month02_expedition_check_done": 1,
                "month02_expedition_return_markers": 1,
            },
        }
    )

    intents = {item.id: item for item in sess.public_state().npc_intents}

    assert intents["eugeo_reviews_expedition_supplies"].scene_id == "north_gate"
    assert intents["eugeo_reviews_expedition_supplies"].action == {
        "type": "scene_activity",
        "activity_id": "north_gate_expedition_supply_review",
    }
    assert intents["eugeo_reviews_expedition_supplies"].response_options
    assert "回撤标记" in intents["eugeo_reviews_expedition_supplies"].description


def test_day_thirty_nine_quiet_frequency_intent_guides_player_to_reading_hall():
    sess = Session(run_id="test-day39-quiet-crosscheck")
    sess.state = sess.state.model_copy(
        update={
            "day": 39,
            "time_band": "morning",
            "flags": {
                "month02_day31_entry_done": 1,
                "month02_route_quiet": 1,
                "month02_quiet_record_done": 1,
                "month02_quiet_witness_chain": 1,
            },
        }
    )

    intents = {item.id: item for item in sess.public_state().npc_intents}

    assert intents["alice_conducts_quiet_frequency_crosscheck"].scene_id == "reading_hall"
    assert intents["alice_conducts_quiet_frequency_crosscheck"].action == {
        "type": "scene_activity",
        "activity_id": "reading_hall_quiet_frequency_crosscheck",
    }
    assert intents["alice_conducts_quiet_frequency_crosscheck"].response_options
    assert "见证人链" in intents["alice_conducts_quiet_frequency_crosscheck"].description


def test_day_forty_six_shared_convergence_intent_appears_after_any_week_six_route():
    cases = [
        "month02_order_patrol_standby_done",
        "month02_expedition_supply_review_done",
        "month02_quiet_frequency_crosscheck_done",
    ]

    for flag in cases:
        sess = Session(run_id=f"test-day46-convergence-{flag}")
        sess.state = sess.state.model_copy(
            update={
                "day": 46,
                "time_band": "morning",
                "flags": {
                    "month02_day31_entry_done": 1,
                    flag: 1,
                },
            }
        )

        intents = {item.id: item for item in sess.public_state().npc_intents}

        assert intents["alice_calls_anomaly_convergence"].scene_id == "reading_hall"
        assert intents["alice_calls_anomaly_convergence"].action == {
            "type": "scene_activity",
            "activity_id": "boundary_anomaly_convergence",
        }
        assert intents["alice_calls_anomaly_convergence"].response_options


def test_day_forty_six_shared_convergence_intent_stays_locked_without_week_six_route():
    sess = Session(run_id="test-day46-convergence-locked")
    sess.state = sess.state.model_copy(
        update={
            "day": 46,
            "time_band": "morning",
            "flags": {"month02_day31_entry_done": 1},
        }
    )

    intents = {item.id: item for item in sess.public_state().npc_intents}

    assert "alice_calls_anomaly_convergence" not in intents


def test_optional_first_month_choice_activities_have_authored_npc_entries():
    cases = [
        (
            5,
            {"month01_debrief_done": 1},
            "north_gate",
            "eugeo_offers_route_walkthrough",
            "north_gate_drill_walkthrough",
        ),
        (
            8,
            {"month01_drill_done": 1},
            "village_square",
            "alice_opens_patrol_board_review",
            "village_patrol_board_review",
        ),
        (
            13,
            {"month01_village_trust": 1},
            "north_gate",
            "eugeo_requests_silent_line_recheck",
            "north_gate_silent_line_recheck",
        ),
    ]
    for day, flags, scene_id, intent_id, activity_id in cases:
        sess = Session(run_id=f"test-optional-intent-{day}")
        sess.state = sess.state.model_copy(
            update={"day": day, "time_band": "morning", "flags": flags}
        )

        intents = {item.id: item for item in sess.public_state().npc_intents}

        assert intents[intent_id].scene_id == scene_id
        assert intents[intent_id].action == {
            "type": "scene_activity",
            "activity_id": activity_id,
        }


def test_optional_first_month_activity_intent_disappears_after_completion():
    sess = Session(run_id="test-optional-intent-complete")
    sess.state = sess.state.model_copy(
        update={
            "day": 8,
            "time_band": "morning",
            "flags": {
                "month01_drill_done": 1,
                "activity_done.village_patrol_board_review": 1,
            },
        }
    )

    intent_ids = {item.id for item in sess.public_state().npc_intents}

    assert "alice_opens_patrol_board_review" not in intent_ids


def test_day_forty_seven_route_followup_intents_are_exclusive():
    cases = [
        (
            {"month02_shared_map_published": 1},
            "alice_hosts_shared_map_hearing",
            "village_square",
            "village_shared_map_hearing",
        ),
        (
            {"month02_source_held_by_team": 1},
            "eugeo_prepares_team_source_probe",
            "north_gate",
            "north_gate_team_source_probe",
        ),
    ]
    all_route_intents = {
        "alice_hosts_shared_map_hearing",
        "eugeo_prepares_team_source_probe",
    }
    for flags, expected_id, scene_id, activity_id in cases:
        sess = Session(run_id=f"test-day47-route-followup-{expected_id}")
        sess.state = sess.state.model_copy(
            update={"day": 47, "time_band": "morning", "flags": flags}
        )

        intents = {item.id: item for item in sess.public_state().npc_intents}

        assert expected_id in intents
        assert intents[expected_id].scene_id == scene_id
        assert intents[expected_id].action == {
            "type": "scene_activity",
            "activity_id": activity_id,
        }
        assert not (all_route_intents - {expected_id}) & set(intents)


def test_day_fifty_three_result_intent_reads_current_route():
    cases = [
        ({"month02_shared_map_hearing_done": 1}, "正式边界听证"),
        ({"month02_team_source_probe_done": 1}, "继续三人追查"),
    ]
    for flags, expected_text in cases:
        sess = Session(run_id=f"test-day53-result-{expected_text}")
        sess.state = sess.state.model_copy(
            update={"day": 53, "time_band": "morning", "flags": flags}
        )

        intents = {item.id: item for item in sess.public_state().npc_intents}
        intent = intents["alice_calls_second_month_result"]

        assert intent.scene_id == "reading_hall"
        assert intent.action == {
            "type": "story_event",
            "event_id": "ch1_d53_second_month_result",
        }
        assert expected_text in intent.description


def test_day_fifty_four_tail_intent_matches_day_fifty_three_result():
    cases = [
        ("month02_result_formal_hearing", "alice_lands_formal_hearing_rules", "village_formal_hearing_followthrough"),
        ("month02_result_warning_only", "eugeo_drills_guarded_warning_route", "village_warning_route_drill"),
        ("month02_result_team_probe_continues", "eugeo_calibrates_source_pursuit", "north_gate_source_pursuit_calibration"),
        ("month02_result_sealed_copy_handed_over", "alice_writes_sealed_copy_protocol", "reading_hall_sealed_copy_protocol"),
    ]
    all_ids = {item[1] for item in cases}
    for flag, expected_id, activity_id in cases:
        sess = Session(run_id=f"test-day54-tail-intent-{expected_id}")
        sess.state = sess.state.model_copy(
            update={"day": 54, "time_band": "morning", "flags": {flag: 1}}
        )

        intents = {item.id: item for item in sess.public_state().npc_intents}

        assert expected_id in intents
        assert intents[expected_id].action == {
            "type": "scene_activity",
            "activity_id": activity_id,
        }
        assert not (all_ids - {expected_id}) & set(intents)


def test_day_sixty_one_departure_intent_appears_after_tail_feedback():
    sess = Session(run_id="test-day61-departure-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 61,
            "time_band": "morning",
            "flags": {"month02_tail_feedback_done": 1},
        }
    )

    intents = {item.id: item for item in sess.public_state().npc_intents}
    intent = intents["alice_calls_third_month_departure"]

    assert intent.scene_id == "north_gate"
    assert intent.action == {
        "type": "story_event",
        "event_id": "ch1_d61_third_month_departure",
    }


def test_day_sixty_two_resource_intent_matches_third_month_family():
    cases = [
        ("month03_public_council_trial", "alice_allocates_third_month_support", "village_third_month_support_allocation"),
        ("month03_source_depart_dawn", "eugeo_loads_third_month_expedition", "north_gate_third_month_expedition_loading"),
        ("month03_shared_custody_record", "alice_budgets_third_month_intelligence", "reading_hall_third_month_intelligence_budget"),
    ]
    all_ids = {item[1] for item in cases}
    for route_flag, expected_id, activity_id in cases:
        sess = Session(run_id=f"test-day62-resource-intent-{expected_id}")
        sess.state = sess.state.model_copy(
            update={"day": 62, "time_band": "morning", "flags": {route_flag: 1}}
        )

        intents = {item.id: item for item in sess.public_state().npc_intents}

        assert expected_id in intents
        assert intents[expected_id].action == {
            "type": "scene_activity",
            "activity_id": activity_id,
        }
        assert not (all_ids - {expected_id}) & set(intents)


def test_day_sixty_nine_route_test_intent_requires_resource_preparation():
    sess = Session(run_id="test-day69-route-test-intent")
    sess.state = sess.state.model_copy(
        update={
            "day": 69,
            "time_band": "morning",
            "flags": {"month03_preparation_done": 1},
        }
    )

    intents = {item.id: item for item in sess.public_state().npc_intents}

    assert intents["eugeo_calls_first_third_month_test"].action == {
        "type": "story_event",
        "event_id": "ch1_d69_third_month_route_test",
    }
