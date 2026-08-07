from __future__ import annotations

import pytest

from app.session import Session


NODES = {
    "n01": ("ch1pc_n01_rulid_daily", "warm_bond"),
    "n02": ("ch1pc_n02_gigas_calling", "steady_pace"),
    "n03": ("ch1pc_n03_talk_index_end_mountains", "deep_talk"),
    "n04": ("ch1pc_n04_travel_to_end_mountains", "pack_food"),
    "n05": ("ch1pc_n05_encounter_dark_territory_injured", "cautious_approach"),
    "n06": ("ch1pc_n06_alice_crosses_boundary", "grasp_alice_arm"),
    "n07": ("ch1pc_n07_return_to_rulid", "wait_for_alice"),
    "n08": ("ch1pc_n08_knights_arrive_village", "step_forward"),
    "n09": ("ch1pc_n09_alice_farewell", "speak_one_sentence"),
    "n10": ("ch1pc_n10_alice_captured", "record_one_phrase"),
}


def choose(sess: Session, node: str, choice: str | None = None) -> dict:
    event_id, default_choice = NODES[node]
    out = sess.choose_story_event(event_id, choice or default_choice)
    assert out["ok"] is True, (node, out)
    return out


def reach_n06(sess: Session, n06_choice: str = "grasp_alice_arm") -> None:
    choose(sess, "n01")
    choose(sess, "n02")
    choose(sess, "n03")
    assert sess.player_action(kind="rest_until_next_day")["ok"] is True
    choose(sess, "n04")
    choose(sess, "n05")
    out = sess.choose_story_event("ch1pc_n06_alice_crosses_boundary", n06_choice)
    assert out["ok"] is True, out


def reach_n10(sess: Session) -> None:
    reach_n06(sess)
    choose(sess, "n07")
    assert sess.player_action(kind="rest_until_next_day")["day_transition"]["to_day"] == 3
    choose(sess, "n08")
    choose(sess, "n09")


def test_precapture_route_runs_n01_to_n10_with_authored_time_bands():
    sess = Session(seed=7, run_id="test-precapture-full-route")

    choose(sess, "n01")
    assert sess.state.day == 1
    assert sess.state.time_band == "afternoon"
    assert sess.state.flags["precapture_mode"] == 1

    choose(sess, "n02")
    assert sess.state.time_band == "evening"
    choose(sess, "n03")
    assert sess.state.time_band == "evening"

    transition = sess.player_action(kind="rest_until_next_day")
    assert transition["day_transition"]["to_day"] == 2
    assert sess.state.time_band == "morning"

    choose(sess, "n04")
    assert sess.state.time_band == "afternoon"
    choose(sess, "n05")
    choose(sess, "n06", "grasp_alice_arm")
    assert sess.state.flags["d6_alice_crossed_instant"] == 1
    choose(sess, "n07")
    assert sess.state.time_band == "night"

    transition = sess.player_action(kind="rest_until_next_day")
    assert transition["day_transition"]["to_day"] == 3
    assert sess.state.time_band == "morning"

    choose(sess, "n08")
    assert sess.state.time_band == "afternoon"
    choose(sess, "n09")
    final = choose(sess, "n10", "record_one_phrase")

    assert sess.state.day == 3
    assert sess.state.chapter_ending_id == "alice_captured"
    assert final["ending_id"] == "alice_captured"
    assert sess.available_story_events()["events"] == []


def test_precapture_day_gates_prevent_skipping_authored_nodes():
    sess = Session(run_id="test-precapture-day-gates")
    assert sess.player_action(kind="rest_until_next_day")["error"] == "day_end_gate_incomplete"

    choose(sess, "n01")
    blocked_day_one = sess.player_action(kind="rest_until_next_day")
    assert blocked_day_one["error"] == "day_end_gate_incomplete"
    assert {item["id"] for item in blocked_day_one["missing"]} == {
        "ch1pc_n03_talk_index_end_mountains"
    }

    choose(sess, "n02")
    choose(sess, "n03")
    assert sess.player_action(kind="rest_until_next_day")["ok"] is True
    choose(sess, "n04")
    choose(sess, "n05")
    choose(sess, "n06")
    blocked_day_two = sess.player_action(kind="rest_until_next_day")
    assert blocked_day_two["error"] == "day_end_gate_incomplete"
    assert {item["id"] for item in blocked_day_two["missing"]} == {
        "ch1pc_n07_return_to_rulid"
    }

    choose(sess, "n07")
    assert sess.player_action(kind="rest_until_next_day")["day_transition"]["to_day"] == 3
    choose(sess, "n08")
    choose(sess, "n09")
    blocked_day_three = sess.player_action(kind="rest_until_next_day")
    assert blocked_day_three["error"] == "day_end_gate_incomplete"
    assert {item["id"] for item in blocked_day_three["missing"]} == {
        "ch1pc_n10_alice_captured"
    }


@pytest.mark.parametrize(
    "choice_id, expected_flag",
    [
        ("grasp_alice_arm", 1),
        ("shout_stop", 2),
        ("keep_silent", 3),
    ],
)
def test_n06_choices_all_converge_on_alice_crossing(choice_id: str, expected_flag: int):
    sess = Session(run_id=f"test-precapture-n06-{expected_flag}")
    reach_n06(sess, choice_id)

    assert sess.state.flags["d6_alice_crossed_instant"] == expected_flag
    assert sess.state.time_band == "evening"
    assert "ch1pc_n07_return_to_rulid" in {
        event["id"] for event in sess.available_story_events()["events"]
    }


@pytest.mark.parametrize("choice_id", ["record_one_phrase", "record_silence", "close_record_book"])
def test_n10_choices_all_write_the_only_precapture_endpoint(choice_id: str):
    sess = Session(run_id=f"test-precapture-n10-{choice_id}")
    reach_n10(sess)

    out = sess.choose_story_event("ch1pc_n10_alice_captured", choice_id)
    assert out["ok"] is True
    assert out["ending_id"] == "alice_captured"
    assert sess.state.chapter_ending_id == "alice_captured"


def test_capture_endpoint_rejects_all_post_capture_progression_and_writes():
    sess = Session(run_id="test-precapture-terminal-contract")
    reach_n10(sess)
    assert sess.choose_story_event("ch1pc_n10_alice_captured", "close_record_book")["ok"] is True
    frozen = sess.state.model_dump(mode="json")

    assert sess.choose_story_event("ch1pc_n10_alice_captured", "record_one_phrase")["error"] == "event_not_available"
    assert sess.player_action(kind="rest_until_next_day")["error"] == "chapter_ended"
    assert sess.player_action(kind="set_flag", flag_key="post_capture", flag_value=1)["error"] == "chapter_ended"
    assert sess.player_action(kind="scene_activity", activity_id="any_activity", activity_choice="any_choice")["error"] == "chapter_ended"
    assert sess.story_advance("mq01_tree_arc")["error"] == "chapter_ended"
    assert sess.dialogue(npc_id="alice", message="继续说下去")["error"] == "chapter_ended"
    assert sess.state.model_dump(mode="json") == frozen
