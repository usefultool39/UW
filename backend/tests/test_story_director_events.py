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
    assert sess.state.flags["clue_boundary_record"] == 1
    assert sess.state.relationships["alice"].trust > 0
    assert "ch1_d1_reading_clue" in sess.state.completed_event_ids
    profile = sess.npc_profile("alice")["profile"]
    assert profile["important_memories"]


def test_rest_until_next_day_unlocks_day_two_after_clue():
    sess = Session(run_id="test-story-day2")
    sess.choose_story_event("ch1_d1_reading_clue", "ask_alice")
    sess.player_action(kind="rest_until_next_day")
    events = sess.available_story_events()["events"]
    ids = {event["id"] for event in events}
    assert sess.state.day == 2
    assert "ch1_d2_forest_anomaly" in ids


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
    sess.choose_story_event("ch1_d2_forest_anomaly", "investigate_together")
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
