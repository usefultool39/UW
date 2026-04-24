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
