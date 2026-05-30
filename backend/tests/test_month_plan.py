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
