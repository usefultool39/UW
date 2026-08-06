from fastapi.testclient import TestClient

from app.main import app
from app.month_plan import public_month_plan
from app.session import Session


def _finish_first_three_days(sess: Session) -> None:
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    sess.player_action(kind="rest_until_next_day")
    sess.choose_story_event("ch1_d2_forest_anomaly", "investigate_together")
    sess.player_action(kind="rest_until_next_day")
    sess.choose_story_event("ch1_d3_boundary_choice", "cross_boundary")


def _rest_to_day(sess: Session, day: int) -> None:
    while sess.state.day < day:
        sess.player_action(kind="rest_until_next_day")


def _reach_month_gate_after_vigil(sess: Session) -> None:
    _finish_first_three_days(sess)
    _rest_to_day(sess, 4)
    assert sess.choose_story_event("ch1_d4_after_boundary_debrief", "write_truth")["ok"] is True
    _rest_to_day(sess, 7)
    assert sess.choose_story_event("ch1_d7_first_boundary_drill", "mark_safe_route")["ok"] is True
    _rest_to_day(sess, 12)
    assert sess.choose_story_event("ch1_d12_village_trust", "public_patrol_board")["ok"] is True
    _rest_to_day(sess, 18)
    assert sess.choose_story_event("ch1_d18_silent_line_rehearsal", "calibrate_sacred_arts")["ok"] is True
    _rest_to_day(sess, 24)
    assert sess.choose_story_event("ch1_d24_expedition_pack", "pack_for_safety")["ok"] is True
    _rest_to_day(sess, 28)
    sess.player_action(kind="move_scene", scene_id="north_gate")
    vigil = sess.player_action(
        kind="scene_activity",
        activity_id="north_gate_month_end_vigil",
        activity_choice="review_promises",
    )
    assert vigil["ok"] is True


def test_month_plan_starts_with_opening_milestone_active():
    sess = Session(run_id="test-month-plan-start")

    plan = public_month_plan(sess.root, sess.state)

    assert plan["ok"] is True
    assert plan["title"] == "第一月：北境静默线"
    assert len(plan["weeks"]) == 4
    assert plan["current"]["active_milestone_id"] == "m01_opening_incident"
    assert plan["weeks"][0]["milestones"][0]["status"] == "active"


def test_month_plan_reflects_day_four_debrief_after_boundary_ending():
    sess = Session(run_id="test-month-plan-day4")
    _finish_first_three_days(sess)
    sess.player_action(kind="rest_until_next_day")

    plan = public_month_plan(sess.root, sess.state)
    events = sess.available_story_events()["events"]
    ids = {event["id"] for event in events}

    assert sess.state.day == 4
    assert plan["current"]["ending_path"] == "cross"
    assert plan["weeks"][0]["milestones"][0]["status"] == "completed"
    assert plan["current"]["active_milestone_id"] == "m01_debrief"
    assert "ch1_d4_after_boundary_debrief" in ids


def test_first_month_events_chain_to_week_two_drill():
    sess = Session(run_id="test-month-plan-week2")
    _finish_first_three_days(sess)
    sess.player_action(kind="rest_until_next_day")
    out = sess.choose_story_event("ch1_d4_after_boundary_debrief", "write_truth")
    assert out["ok"] is True
    assert "莉娜也能看懂" in out["choice"]["result_text"]
    assert "安全边距" in out["choice"]["result_text"]

    while sess.state.day < 7:
        sess.player_action(kind="rest_until_next_day")

    events = sess.available_story_events()["events"]
    ids = {event["id"] for event in events}
    plan = public_month_plan(sess.root, sess.state)

    assert "ch1_d7_first_boundary_drill" in ids
    assert plan["current"]["active_milestone_id"] == "m01_first_drill"


def test_first_month_event_chain_can_reach_north_gate_finale():
    sess = Session(run_id="test-month-plan-full-chain")
    _reach_month_gate_after_vigil(sess)

    blocked = sess.choose_story_event("ch1_d30_first_month_gate", "route_report_first")
    assert blocked["ok"] is True

    plan = public_month_plan(sess.root, sess.state)

    assert sess.state.flags["month01_gate_resolved"] == 1
    assert plan["weeks"][-1]["milestones"][-1]["status"] == "completed"


def test_day_thirty_one_month_transition_uses_first_month_route_flags():
    cases = [
        ("route_report_first", "confirm_order_route", "month02_route_order"),
        ("route_joint_expedition", "confirm_expedition_route", "month02_route_expedition"),
        ("route_quiet_probe", "confirm_quiet_route", "month02_route_quiet"),
    ]

    for month_gate_choice, day31_choice, route_flag in cases:
        sess = Session(run_id=f"test-day31-{route_flag}")
        _reach_month_gate_after_vigil(sess)
        assert sess.choose_story_event("ch1_d30_first_month_gate", month_gate_choice)["ok"] is True
        _rest_to_day(sess, 31)

        events = sess.available_story_events()["events"]
        event = next(item for item in events if item["id"] == "ch1_d31_month_transition")
        choice_ids = {choice["id"] for choice in event["choices"]}

        assert choice_ids == {day31_choice}
        out = sess.choose_story_event("ch1_d31_month_transition", day31_choice)
        assert out["ok"] is True
        assert sess.state.flags["month02_day31_entry_done"] == 1
        assert sess.state.flags[route_flag] == 1


def test_day_twenty_four_expedition_preparation_is_playable():
    sess = Session(run_id="test-month-plan-expedition-prep")
    _finish_first_three_days(sess)

    _rest_to_day(sess, 4)
    assert sess.choose_story_event("ch1_d4_after_boundary_debrief", "write_truth")["ok"] is True
    _rest_to_day(sess, 7)
    assert sess.choose_story_event("ch1_d7_first_boundary_drill", "mark_safe_route")["ok"] is True
    _rest_to_day(sess, 12)
    assert sess.choose_story_event("ch1_d12_village_trust", "public_patrol_board")["ok"] is True
    _rest_to_day(sess, 18)
    assert sess.choose_story_event("ch1_d18_silent_line_rehearsal", "calibrate_sacred_arts")["ok"] is True
    _rest_to_day(sess, 24)

    sess.state = sess.state.model_copy(update={"time_band": "evening"})
    sess.player_action(kind="move_scene", scene_id="home_hearth")
    intents = {item.id: item for item in sess.public_state().npc_intents}
    assert intents["alice_sets_expedition_bridge_talk"].action == {
        "type": "scene_activity",
        "activity_id": "home_expedition_bridge_talk",
    }
    bridge = sess.player_action(kind="scene_activity", activity_id="home_expedition_bridge_talk")
    assert bridge["ok"] is True
    assert bridge["state"]["flags"]["month01_expedition_bridge_talk"] == 1
    assert any(item["npc_id"] == "alice" for item in bridge["memory_written"])

    sess.state = sess.state.model_copy(update={"time_band": "morning"})
    intents = {item.id: item for item in sess.public_state().npc_intents}
    assert intents["alice_checks_expedition_pack"].action == {
        "type": "scene_activity",
        "activity_id": "home_expedition_pack_review",
    }
    pack_review = sess.player_action(
        kind="scene_activity",
        activity_id="home_expedition_pack_review",
        activity_choice="review_safe_pack",
    )
    assert pack_review["ok"] is True
    assert pack_review["activity_result"]["activity_choice"]["id"] == "review_safe_pack"
    assert pack_review["state"]["flags"]["month01_pack_reviewed"] == 1
    assert any(item["npc_id"] == "alice" for item in pack_review["memory_written"])

    assert sess.choose_story_event("ch1_d24_expedition_pack", "pack_for_safety")["ok"] is True
    assert sess.state.flags["month01_expedition_ready"] == 1

    sess.state = sess.state.model_copy(update={"day": 25, "time_band": "afternoon"})
    sess.player_action(kind="move_scene", scene_id="village_square")
    intents = {item.id: item for item in sess.public_state().npc_intents}
    assert intents["eugeo_brings_pack_to_square"].action == {
        "type": "scene_activity",
        "activity_id": "village_expedition_sendoff",
    }
    sendoff = sess.player_action(kind="scene_activity", activity_id="village_expedition_sendoff")
    assert sendoff["ok"] is True
    assert sendoff["state"]["flags"]["month01_village_sendoff_done"] == 1
    assert any(item["npc_id"] == "eugeo" for item in sendoff["memory_written"])

    sess.state = sess.state.model_copy(update={"day": 28, "time_band": "evening"})
    sess.player_action(kind="move_scene", scene_id="north_gate")
    intents = {item.id: item for item in sess.public_state().npc_intents}
    assert intents["alice_marks_month_gate_vigil"].action == {
        "type": "scene_activity",
        "activity_id": "north_gate_month_end_vigil",
    }
    vigil = sess.player_action(
        kind="scene_activity",
        activity_id="north_gate_month_end_vigil",
        activity_choice="review_promises",
    )
    assert vigil["ok"] is True
    assert vigil["state"]["flags"]["month01_gate_vigil_done"] == 1
    assert vigil["state"]["flags"]["month01_gate_promises_reviewed"] == 1
    assert any(item["npc_id"] == "alice" for item in vigil["memory_written"])


def test_month_plan_endpoint_returns_current_route():
    client = TestClient(app)
    client.post("/api/reset")

    r = client.get("/api/story/month_plan")

    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["id"] == "month_01"
    assert body["current"]["day"] == 1
    assert body["weeks"][0]["milestones"][0]["status"] == "active"


def test_month_two_plan_exposes_route_specific_day32_entry():
    sess = Session(run_id="test-month-two-plan")
    sess.state = sess.state.model_copy(
        update={
            "day": 32,
            "time_band": "morning",
            "flags": {
                "month02_day31_entry_done": 1,
                "month02_route_order": 1,
            },
        }
    )

    plan = public_month_plan(sess.root, sess.state, month_id="month_02")
    week = plan["weeks"][0]
    milestones = {item["id"]: item for item in week["milestones"]}

    assert plan["ok"] is True
    assert plan["id"] == "month_02"
    assert plan["current"]["ending_path"] == "order"
    assert plan["current"]["active_milestone_id"] == "m02_order_briefing"
    assert week["status"] == "active"
    assert milestones["m02_order_briefing"]["status"] == "active"
    assert milestones["m02_expedition_check"]["status"] == "locked"
    assert milestones["m02_quiet_record"]["status"] == "locked"


def test_month_two_plan_marks_day32_route_activity_completed():
    sess = Session(run_id="test-month-two-plan-completed")
    sess.state = sess.state.model_copy(
        update={
            "day": 32,
            "time_band": "morning",
            "flags": {
                "month02_day31_entry_done": 1,
                "month02_route_expedition": 1,
                "month02_expedition_check_done": 1,
            },
        }
    )

    plan = public_month_plan(sess.root, sess.state, month_id="month_02")
    milestones = {item["id"]: item for item in plan["weeks"][0]["milestones"]}

    assert plan["current"]["ending_path"] == "expedition"
    assert milestones["m02_expedition_check"]["status"] == "completed"


def test_month_two_week_six_order_patrol_milestone_is_active_and_completes():
    sess = Session(run_id="test-month-two-week-six-order")
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

    plan = public_month_plan(sess.root, sess.state, month_id="month_02")
    week = next(item for item in plan["weeks"] if item["id"] == "week_06")
    milestones = {item["id"]: item for item in week["milestones"]}

    assert plan["current"]["week_id"] == "week_06"
    assert plan["current"]["active_milestone_id"] == "m02_order_patrol_standby"
    assert milestones["m02_order_patrol_standby"]["status"] == "active"

    sess.state = sess.state.model_copy(
        update={"flags": {**sess.state.flags, "month02_order_patrol_standby_done": 1}}
    )
    completed = public_month_plan(sess.root, sess.state, month_id="month_02")
    completed_week = next(item for item in completed["weeks"] if item["id"] == "week_06")
    completed_milestones = {item["id"]: item for item in completed_week["milestones"]}

    assert completed_milestones["m02_order_patrol_standby"]["status"] == "completed"


def test_month_two_week_six_expedition_supply_milestone_is_active_and_completes():
    sess = Session(run_id="test-month-two-week-six-expedition")
    sess.state = sess.state.model_copy(
        update={
            "day": 39,
            "time_band": "morning",
            "flags": {
                "month02_day31_entry_done": 1,
                "month02_route_expedition": 1,
                "month02_expedition_check_done": 1,
            },
        }
    )

    plan = public_month_plan(sess.root, sess.state, month_id="month_02")
    week = next(item for item in plan["weeks"] if item["id"] == "week_06")
    milestones = {item["id"]: item for item in week["milestones"]}

    assert plan["current"]["week_id"] == "week_06"
    assert plan["current"]["active_milestone_id"] == "m02_expedition_supply_check"
    assert milestones["m02_order_patrol_standby"]["status"] == "locked"
    assert milestones["m02_expedition_supply_check"]["status"] == "active"

    sess.state = sess.state.model_copy(
        update={"flags": {**sess.state.flags, "month02_expedition_supply_review_done": 1}}
    )
    completed = public_month_plan(sess.root, sess.state, month_id="month_02")
    completed_week = next(item for item in completed["weeks"] if item["id"] == "week_06")
    completed_milestones = {item["id"]: item for item in completed_week["milestones"]}

    assert completed_milestones["m02_expedition_supply_check"]["status"] == "completed"


def test_month_two_week_six_quiet_frequency_milestone_is_active_and_completes():
    sess = Session(run_id="test-month-two-week-six-quiet")
    sess.state = sess.state.model_copy(
        update={
            "day": 39,
            "time_band": "morning",
            "flags": {
                "month02_day31_entry_done": 1,
                "month02_route_quiet": 1,
                "month02_quiet_record_done": 1,
            },
        }
    )

    plan = public_month_plan(sess.root, sess.state, month_id="month_02")
    week = next(item for item in plan["weeks"] if item["id"] == "week_06")
    milestones = {item["id"]: item for item in week["milestones"]}

    assert plan["current"]["week_id"] == "week_06"
    assert plan["current"]["active_milestone_id"] == "m02_quiet_frequency_crosscheck"
    assert milestones["m02_order_patrol_standby"]["status"] == "locked"
    assert milestones["m02_expedition_supply_check"]["status"] == "locked"
    assert milestones["m02_quiet_frequency_crosscheck"]["status"] == "active"

    sess.state = sess.state.model_copy(
        update={"flags": {**sess.state.flags, "month02_quiet_frequency_crosscheck_done": 1}}
    )
    completed = public_month_plan(sess.root, sess.state, month_id="month_02")
    completed_week = next(item for item in completed["weeks"] if item["id"] == "week_06")
    completed_milestones = {item["id"]: item for item in completed_week["milestones"]}

    assert completed_milestones["m02_quiet_frequency_crosscheck"]["status"] == "completed"


def test_month_two_week_seven_convergence_milestone_accepts_any_week_six_route():
    cases = [
        "month02_order_patrol_standby_done",
        "month02_expedition_supply_review_done",
        "month02_quiet_frequency_crosscheck_done",
    ]

    for flag in cases:
        sess = Session(run_id=f"test-month-two-week-seven-{flag}")
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

        plan = public_month_plan(sess.root, sess.state, month_id="month_02")
        week = next(item for item in plan["weeks"] if item["id"] == "week_07")
        milestones = {item["id"]: item for item in week["milestones"]}

        assert plan["current"]["week_id"] == "week_07"
        assert plan["current"]["active_milestone_id"] == "m02_anomaly_convergence"
        assert milestones["m02_anomaly_convergence"]["status"] == "active"


def test_month_two_week_seven_convergence_activity_requires_any_week_six_route():
    sess = Session(run_id="test-month-two-week-seven-activity")
    sess.state = sess.state.model_copy(update={"day": 46, "time_band": "morning"})
    sess.player_action(kind="move_scene", scene_id="reading_hall")

    locked = sess.player_action(kind="scene_activity", activity_id="boundary_anomaly_convergence")
    assert locked["ok"] is False
    assert locked["error"] == "requirements_not_met"

    sess.state = sess.state.model_copy(
        update={"flags": {**sess.state.flags, "month02_order_patrol_standby_done": 1}}
    )
    done = sess.player_action(
        kind="scene_activity",
        activity_id="boundary_anomaly_convergence",
        activity_choice="publish_shared_anomaly_map",
    )

    assert done["ok"] is True
    assert done["state"]["flags"]["month02_anomaly_convergence_done"] == 1
    assert done["state"]["flags"]["month02_anomaly_source_documented"] == 1


def test_day_thirty_two_route_choice_is_required_and_unlocks_day_thirty_three():
    sess = Session(run_id="test-month-two-day32-choice-gate")
    sess.state = sess.state.model_copy(
        update={
            "day": 32,
            "time_band": "morning",
            "flags": {
                "month02_day31_entry_done": 1,
                "month02_route_order": 1,
            },
        }
    )
    sess.player_action(kind="move_scene", scene_id="reading_hall")

    missing_choice = sess.player_action(
        kind="scene_activity",
        activity_id="church_month02_briefing",
    )
    assert missing_choice["ok"] is False
    assert missing_choice["error"] == "activity_choice_required"
    assert "month02_order_briefing_done" not in sess.state.flags

    chosen = sess.player_action(
        kind="scene_activity",
        activity_id="church_month02_briefing",
        activity_choice="publish_full_rotation",
    )
    assert chosen["ok"] is True
    assert chosen["state"]["flags"]["month02_order_briefing_done"] == 1
    assert chosen["state"]["flags"]["month02_order_open_rotation"] == 1
    assert any(item["npc_id"] == "alice" for item in chosen["memory_written"])

    advanced = sess.player_action(kind="rest_until_next_day")
    assert advanced["ok"] is True
    assert advanced["state"]["day"] == 33


def test_month_two_public_map_followup_requires_day_window_and_choice():
    sess = Session(run_id="test-month-two-shared-map-hearing")
    sess.state = sess.state.model_copy(
        update={
            "day": 46,
            "time_band": "morning",
            "flags": {
                "month02_anomaly_convergence_done": 1,
                "month02_shared_map_published": 1,
            },
        }
    )
    sess.player_action(kind="move_scene", scene_id="village_square")

    early = sess.player_action(
        kind="scene_activity",
        activity_id="village_shared_map_hearing",
        activity_choice="invite_village_testimony",
    )
    assert early["ok"] is False
    assert early["error"] == "wrong_day_range"
    assert "month02_shared_map_hearing_done" not in sess.state.flags

    sess.state = sess.state.model_copy(update={"day": 47})
    missing = sess.player_action(
        kind="scene_activity",
        activity_id="village_shared_map_hearing",
    )
    assert missing["ok"] is False
    assert missing["error"] == "activity_choice_required"

    chosen = sess.player_action(
        kind="scene_activity",
        activity_id="village_shared_map_hearing",
        activity_choice="invite_village_testimony",
    )
    assert chosen["ok"] is True
    assert chosen["state"]["flags"]["month02_shared_map_hearing_done"] == 1
    assert chosen["state"]["flags"]["month02_village_testimony_gathered"] == 1
    assert {row["npc_id"] for row in chosen["memory_written"]} == {"alice", "eugeo"}


def test_month_two_team_probe_followup_records_sealed_copy_route():
    sess = Session(run_id="test-month-two-team-source-probe")
    sess.state = sess.state.model_copy(
        update={
            "day": 49,
            "time_band": "morning",
            "flags": {
                "month02_anomaly_convergence_done": 1,
                "month02_source_held_by_team": 1,
            },
        }
    )
    sess.player_action(kind="move_scene", scene_id="north_gate")

    chosen = sess.player_action(
        kind="scene_activity",
        activity_id="north_gate_team_source_probe",
        activity_choice="prepare_sealed_duplicate",
    )

    assert chosen["ok"] is True
    assert chosen["state"]["flags"]["month02_team_source_probe_done"] == 1
    assert chosen["state"]["flags"]["month02_sealed_duplicate_ready"] == 1
    assert any(row["npc_id"] == "alice" for row in chosen["memory_written"])


def test_month_two_week_seven_route_milestones_are_exclusive_and_track_completion():
    public = Session(run_id="test-month-two-week-seven-public")
    public.state = public.state.model_copy(
        update={
            "day": 47,
            "flags": {
                "month02_anomaly_convergence_done": 1,
                "month02_shared_map_published": 1,
            },
        }
    )
    public_plan = public_month_plan(public.root, public.state, month_id="month_02")
    week = next(item for item in public_plan["weeks"] if item["id"] == "week_07")
    milestones = {item["id"]: item for item in week["milestones"]}
    assert milestones["m02_shared_map_hearing"]["status"] == "active"
    assert milestones["m02_team_source_probe"]["status"] == "locked"

    public.state = public.state.model_copy(
        update={"flags": {**public.state.flags, "month02_shared_map_hearing_done": 1}}
    )
    completed = public_month_plan(public.root, public.state, month_id="month_02")
    week = next(item for item in completed["weeks"] if item["id"] == "week_07")
    milestones = {item["id"]: item for item in week["milestones"]}
    assert milestones["m02_shared_map_hearing"]["status"] == "completed"


def test_month_two_day_fifty_four_tail_activities_are_route_specific_and_playable():
    cases = [
        (
            "month02_result_formal_hearing",
            "village_square",
            "village_formal_hearing_followthrough",
            "rotate_testimony_clerks",
            "month02_formal_hearing_followthrough_done",
        ),
        (
            "month02_result_warning_only",
            "village_square",
            "village_warning_route_drill",
            "drill_warning_bells",
            "month02_warning_route_drill_done",
        ),
        (
            "month02_result_team_probe_continues",
            "north_gate",
            "north_gate_source_pursuit_calibration",
            "rehearse_abort_protocol",
            "month02_source_pursuit_calibration_done",
        ),
        (
            "month02_result_sealed_copy_handed_over",
            "reading_hall",
            "reading_hall_sealed_copy_protocol",
            "create_paired_custody_log",
            "month02_sealed_copy_protocol_done",
        ),
    ]
    for route_flag, scene_id, activity_id, choice_id, done_flag in cases:
        sess = Session(run_id=f"test-month-two-tail-{activity_id}")
        sess.state = sess.state.model_copy(
            update={"day": 54, "time_band": "morning", "flags": {route_flag: 1}}
        )
        sess.player_action(kind="move_scene", scene_id=scene_id)

        out = sess.player_action(
            kind="scene_activity",
            activity_id=activity_id,
            activity_choice=choice_id,
        )

        assert out["ok"] is True
        assert out["state"]["flags"]["month02_tail_feedback_done"] == 1
        assert out["state"]["flags"][done_flag] == 1
        assert out["memory_written"]


def test_month_two_result_summary_prefers_day_fifty_three_outcome():
    cases = [
        ("month02_result_formal_hearing", "formal_hearing", "正式边界听证"),
        ("month02_result_warning_only", "guarded_warning", "分层警告"),
        ("month02_result_team_probe_continues", "source_pursuit", "三人源头追查"),
        ("month02_result_sealed_copy_handed_over", "accountable_probe", "密封副本托管"),
    ]
    for flag, expected_path, expected_note in cases:
        sess = Session(run_id=f"test-month-two-result-summary-{expected_path}")
        sess.state = sess.state.model_copy(
            update={
                "day": 54,
                "flags": {"month02_route_order": 1, flag: 1},
            }
        )

        plan = public_month_plan(sess.root, sess.state, month_id="month_02")

        assert plan["current"]["ending_path"] == expected_path
        assert expected_note in plan["current"]["ending_note"]


def test_month_two_week_eight_tracks_tail_and_departure_milestones():
    sess = Session(run_id="test-month-two-week-eight-tail")
    sess.state = sess.state.model_copy(
        update={
            "day": 54,
            "flags": {
                "month02_result_formal_hearing": 1,
                "month02_second_month_result_done": 1,
            },
        }
    )

    plan = public_month_plan(sess.root, sess.state, month_id="month_02")
    week = next(item for item in plan["weeks"] if item["id"] == "week_08")
    milestones = {item["id"]: item for item in week["milestones"]}

    assert milestones["m02_formal_hearing_followthrough"]["status"] == "active"
    assert milestones["m02_warning_route_drill"]["status"] == "locked"
    assert milestones["m02_third_month_departure"]["status"] == "locked"
