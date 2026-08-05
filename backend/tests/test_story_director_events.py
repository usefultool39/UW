from app.session import Session
from app.story_director import available_events


def test_available_events_start_with_day_one_choices():
    sess = Session(run_id="test-story-events")
    events = available_events(sess.root, sess.state)
    ids = {event["id"] for event in events}
    assert "ch1_d1_reading_clue" in ids
    assert "ch1_d1_training_with_eugeo" in ids


def test_choose_event_updates_flags_relationship_and_memory():
    sess = Session(run_id="test-story-choice")
    out = sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    assert out["ok"] is True
    assert "莉娜练习页" in out["choice"]["result_text"]
    assert "刻印标记" in out["choice"]["result_text"]
    assert sess.state.flags["clue_boundary_record"] == 1
    assert sess.state.relationships["alice"].trust > 0
    assert "ch1_d1_reading_clue" in sess.state.completed_event_ids
    profile = sess.npc_profile("alice")["profile"]
    assert profile["important_memories"]


def test_rest_until_next_day_unlocks_day_two_after_clue():
    sess = Session(run_id="test-story-day2")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    transition = sess.player_action(kind="rest_until_next_day")
    events = sess.available_story_events()["events"]
    ids = {event["id"] for event in events}
    assert transition["day_transition"]["from_day"] == 1
    assert transition["day_transition"]["to_day"] == 2
    assert sess.state.day == 2
    assert "ch1_d2_forest_anomaly" in ids



def test_rest_is_rejected_until_current_day_story_gate_is_complete():
    sess = Session(run_id="test-story-day-gate-blocked")
    out = sess.player_action(kind="rest_until_next_day")
    assert out["ok"] is False
    assert out["error"] == "day_end_gate_incomplete"
    assert out["state"]["day"] == 1
    assert out["missing"] == [{"type": "flag", "key": "clue_boundary_record", "expected": 1, "actual": 0}]

def test_day_two_event_reflects_day_one_eugeo_dinner_choice():
    sess = Session(run_id="test-story-day2-eugeo-variant")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    flags = {**sess.state.flags, "dinner_sided_eugeo_day1": 1}
    sess.state = sess.state.model_copy(update={"flags": flags})

    sess.player_action(kind="rest_until_next_day")
    events = sess.available_story_events()["events"]
    event = next(e for e in events if e["id"] == "ch1_d2_forest_anomaly")
    choice_ids = {choice["id"] for choice in event["choices"]}

    assert event["variant_id"] == "from_day1_eugeo_promise"
    assert "昨晚" in event["description"]
    assert "follow_eugeo_promise" in choice_ids
    assert "honor_alice_caution" not in choice_ids


def test_day_two_gated_choice_is_hidden_and_rejected_without_flag():
    sess = Session(run_id="test-story-day2-gated-choice-rejected")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    sess.player_action(kind="rest_until_next_day")

    event = next(
        e
        for e in sess.available_story_events()["events"]
        if e["id"] == "ch1_d2_forest_anomaly"
    )
    assert "follow_eugeo_promise" not in {choice["id"] for choice in event["choices"]}

    out = sess.choose_story_event("ch1_d2_forest_anomaly", "follow_eugeo_promise")

    assert out["ok"] is False
    assert out["error"] == "unknown_choice"


def test_day_two_gated_choice_applies_relationship_memory_and_flags():
    sess = Session(run_id="test-story-day2-gated-choice-applies")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    flags = {**sess.state.flags, "dinner_sided_eugeo_day1": 1}
    sess.state = sess.state.model_copy(update={"flags": flags})
    sess.player_action(kind="rest_until_next_day")

    out = sess.choose_story_event("ch1_d2_forest_anomaly", "follow_eugeo_promise")

    assert out["ok"] is True
    assert out["choice"]["id"] == "follow_eugeo_promise"
    assert sess.state.flags["honored_eugeo_promise_day2"] == 1
    assert sess.state.relationships["eugeo"].trust >= 7
    assert any(item["npc_id"] == "eugeo" for item in out["memory_written"])


def test_day_three_boundary_choice_reflects_day_two_joint_investigation():
    sess = Session(run_id="test-story-day3-joint-variant")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    sess.player_action(kind="rest_until_next_day")
    day_two = sess.choose_story_event("ch1_d2_forest_anomaly", "investigate_together")
    assert "刻印标记" in day_two["choice"]["result_text"]
    assert "安全距离" in day_two["choice"]["result_text"]
    sess.player_action(kind="rest_until_next_day")

    events = sess.available_story_events()["events"]
    event = next(e for e in events if e["id"] == "ch1_d3_boundary_choice")

    assert event["variant_id"] == "from_day2_together"
    assert "共同调查" in event["choices"][1]["hint"]
    assert "静默线" in event["description"]


def test_day_three_cross_boundary_sets_ending_and_memory():
    sess = Session(run_id="test-story-day3-cross-ending")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    sess.player_action(kind="rest_until_next_day")
    sess.choose_story_event("ch1_d2_forest_anomaly", "investigate_together")
    sess.player_action(kind="rest_until_next_day")

    out = sess.choose_story_event("ch1_d3_boundary_choice", "cross_boundary")

    assert out["ok"] is True
    assert out["ending_id"] == "cross"
    assert sess.state.chapter_ending_id == "cross"
    assert sess.state.flags["boundary_rule_touched"] == 1
    assert any(item["npc_id"] == "eugeo" for item in out["memory_written"])


def test_day_two_library_echo_choices_are_route_specific():
    told = Session(run_id="test-story-day2-library-echo-told")
    told.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    told.player_action(kind="rest_until_next_day")
    told_event = next(
        event
        for event in told.available_story_events()["events"]
        if event["id"] == "ch1_d2_forest_anomaly"
    )
    told_choices = {choice["id"]: choice for choice in told_event["choices"]}

    assert "use_alice_marked_record" in told_choices
    assert "confess_hidden_note" not in told_choices
    assert "昨天圈出的记录" in told_choices["use_alice_marked_record"]["label"]

    hidden = Session(run_id="test-story-day2-library-echo-hidden")
    hidden.choose_story_event("ch1_d1_reading_clue", "keep_note")
    hidden.player_action(kind="rest_until_next_day")
    hidden_event = next(
        event
        for event in hidden.available_story_events()["events"]
        if event["id"] == "ch1_d2_forest_anomaly"
    )
    hidden_choices = {choice["id"]: choice for choice in hidden_event["choices"]}

    assert "confess_hidden_note" in hidden_choices
    assert "use_alice_marked_record" not in hidden_choices
    assert "昨天隐瞒" in hidden_choices["confess_hidden_note"]["label"]


def test_day_two_marked_record_echo_applies_relationship_flag_and_memory():
    sess = Session(run_id="test-story-day2-library-echo-marked-result")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    trust_before = sess.state.relationships["alice"].trust
    sess.player_action(kind="rest_until_next_day")

    out = sess.choose_story_event("ch1_d2_forest_anomaly", "use_alice_marked_record")

    assert out["ok"] is True
    assert sess.state.flags["followed_alice_mark_day2"] == 1
    assert sess.state.relationships["alice"].trust == trust_before + 5
    alice_memory = next(item for item in out["memory_written"] if item["npc_id"] == "alice")
    assert "共同记录" in alice_memory["summary"]


def test_day_two_hidden_note_echo_repairs_trust_and_records_tension():
    sess = Session(run_id="test-story-day2-library-echo-confession-result")
    sess.choose_story_event("ch1_d1_reading_clue", "keep_note")
    trust_before = sess.state.relationships["alice"].trust
    sess.player_action(kind="rest_until_next_day")

    out = sess.choose_story_event("ch1_d2_forest_anomaly", "confess_hidden_note")

    assert out["ok"] is True
    assert sess.state.flags["confessed_hidden_note_day2"] == 1
    assert sess.state.relationships["alice"].trust == trust_before + 4
    assert "alice" in out["tensions"]
    alice_memory = next(item for item in out["memory_written"] if item["npc_id"] == "alice")
    assert "隐瞒" in alice_memory["summary"]
    assert "补全" in alice_memory["summary"]


def test_day_two_cross_route_choice_is_rejected_without_partial_write():
    sess = Session(run_id="test-story-day2-library-echo-atomic-reject")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    sess.player_action(kind="rest_until_next_day")
    sess.available_story_events()
    state_before = sess.state.model_dump(mode="json")
    memories_before = list(sess.npc_profile("alice")["profile"]["important_memories"])
    event_count_before = len(sess.events)

    out = sess.choose_story_event("ch1_d2_forest_anomaly", "confess_hidden_note")

    assert out["ok"] is False
    assert out["error"] == "unknown_choice"
    assert sess.state.model_dump(mode="json") == state_before
    assert sess.npc_profile("alice")["profile"]["important_memories"] == memories_before
    assert len(sess.events) == event_count_before
    assert "forest_anomaly_seen" not in sess.state.flags
    assert "confessed_hidden_note_day2" not in sess.state.flags


def test_day_three_variant_carries_marked_record_echo_forward():
    sess = Session(run_id="test-story-day3-library-echo-marked")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    sess.player_action(kind="rest_until_next_day")
    sess.choose_story_event("ch1_d2_forest_anomaly", "use_alice_marked_record")
    sess.player_action(kind="rest_until_next_day")

    event = next(
        event
        for event in sess.available_story_events()["events"]
        if event["id"] == "ch1_d3_boundary_choice"
    )

    assert event["variant_id"] == "from_day2_alice_record"
    assert "共同记录" in event["description"]
    cross = next(choice for choice in event["choices"] if choice["id"] == "cross_boundary")
    assert "共同记录" in cross["hint"]


def test_day_three_variant_carries_confessed_note_echo_forward():
    sess = Session(run_id="test-story-day3-library-echo-confessed")
    sess.choose_story_event("ch1_d1_reading_clue", "keep_note")
    sess.player_action(kind="rest_until_next_day")
    sess.choose_story_event("ch1_d2_forest_anomaly", "confess_hidden_note")
    sess.player_action(kind="rest_until_next_day")

    event = next(
        event
        for event in sess.available_story_events()["events"]
        if event["id"] == "ch1_d3_boundary_choice"
    )

    assert event["variant_id"] == "from_day2_confessed_note"
    assert "坦白的书页符号" in event["description"]
    hide = next(choice for choice in event["choices"] if choice["id"] == "hide_anomaly")
    assert "裂痕" in hide["hint"]


def test_day_three_cannot_advance_before_boundary_choice():
    sess = Session(run_id="test-story-day3-gate")
    sess.state = sess.state.model_copy(
        update={"day": 3, "flags": {"forest_anomaly_seen": 1}}
    )

    out = sess.player_action(kind="rest_until_next_day")

    assert out["ok"] is False
    assert out["error"] == "day_end_gate_incomplete"
    assert out["missing"] == [
        {"type": "flag", "key": "boundary_incident_resolved", "expected": 1, "actual": 0}
    ]


def test_day_four_cannot_advance_before_debrief():
    sess = Session(run_id="test-story-day4-gate")
    sess.state = sess.state.model_copy(
        update={"day": 4, "flags": {"boundary_incident_resolved": 1}}
    )

    out = sess.player_action(kind="rest_until_next_day")

    assert out["ok"] is False
    assert out["error"] == "day_end_gate_incomplete"
    assert out["missing"] == [
        {"type": "flag", "key": "month01_debrief_done", "expected": 1, "actual": 0}
    ]


def test_day_seven_cannot_advance_before_first_boundary_drill():
    sess = Session(run_id="test-story-day7-gate")
    sess.state = sess.state.model_copy(
        update={"day": 7, "flags": {"month01_debrief_done": 1}}
    )

    out = sess.player_action(kind="rest_until_next_day")

    assert out["ok"] is False
    assert out["error"] == "day_end_gate_incomplete"
    assert out["missing"] == [
        {"type": "flag", "key": "month01_drill_done", "expected": 1, "actual": 0}
    ]


def test_day_twelve_cannot_advance_before_village_trust_event():
    sess = Session(run_id="test-story-day12-gate")
    sess.state = sess.state.model_copy(
        update={"day": 12, "flags": {"month01_drill_done": 1}}
    )

    out = sess.player_action(kind="rest_until_next_day")

    assert out["ok"] is False
    assert out["error"] == "day_end_gate_incomplete"
    assert out["missing"] == [
        {"type": "flag", "key": "month01_village_trust", "expected": 1, "actual": 0}
    ]


def test_later_month_milestones_also_require_their_authored_event():
    cases = [
        (18, {"month01_village_trust": 1}, "month01_silent_line_rehearsed"),
        (24, {"month01_silent_line_rehearsed": 1}, "month01_expedition_ready"),
        (28, {"month01_expedition_ready": 1}, "month01_gate_vigil_done"),
    ]
    for day, flags, missing_key in cases:
        sess = Session(run_id=f"test-story-day-gate-{day}")
        sess.state = sess.state.model_copy(update={"day": day, "flags": flags})

        out = sess.player_action(kind="rest_until_next_day")

        assert out["ok"] is False
        assert out["error"] == "day_end_gate_incomplete"
        assert out["missing"][0]["key"] == missing_key


def test_day_twelve_event_reflects_optional_village_short_loop():
    sess = Session(run_id="test-story-day12-activity-feedback")
    sess.state = sess.state.model_copy(
        update={"day": 12, "flags": {"month01_drill_done": 1}}
    )
    sess.player_action(kind="move_scene", scene_id="village_square")
    activity = sess.player_action(
        kind="scene_activity",
        activity_id="village_patrol_board_review",
        activity_choice="publish_safe_summary",
    )
    assert activity["ok"] is True
    assert sess.state.flags["village_patrol_board_reviewed"] == 1

    event = next(
        item for item in sess.available_story_events()["events"]
        if item["id"] == "ch1_d12_village_trust"
    )

    assert event["variant_id"] == "after_patrol_board_review"
    public_choice = next(item for item in event["choices"] if item["id"] == "public_patrol_board")
    assert "木牌已经有人开始补充" in public_choice["hint"]


def test_day_eighteen_event_reflects_village_route_feedback():
    sess = Session(run_id="test-story-day18-route-feedback")
    sess.state = sess.state.model_copy(
        update={
            "day": 18,
            "flags": {
                "month01_village_trust": 1,
                "village_safe_summary_published": 1,
            },
        }
    )

    event = next(
        item for item in sess.available_story_events()["events"]
        if item["id"] == "ch1_d18_silent_line_rehearsal"
    )

    assert event["variant_id"] == "after_safe_summary"
    calibrate = next(item for item in event["choices"] if item["id"] == "calibrate_sacred_arts")
    assert "公开的安全流程" in calibrate["hint"]


def test_day_eighteen_event_uses_rumor_feedback_when_no_board_route_exists():
    sess = Session(run_id="test-story-day18-rumor-feedback")
    sess.state = sess.state.model_copy(
        update={
            "day": 18,
            "flags": {
                "month01_village_trust": 1,
                "heard_village_rumor": 1,
            },
        }
    )

    event = next(
        item for item in sess.available_story_events()["events"]
        if item["id"] == "ch1_d18_silent_line_rehearsal"
    )

    assert event["variant_id"] == "after_village_rumor"
    companion = next(item for item in event["choices"] if item["id"] == "trust_companion_call")
    assert "传闻与风声" in companion["hint"]
