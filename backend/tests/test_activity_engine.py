from app.activity_engine import ActivityValidationError, plan_scene_activity
from app.models import PlayerState


def activity(**overrides):
    base = {
        "id": "demo_activity",
        "scene_id": "reading_hall",
        "time_bands": ["morning"],
        "effects": {"stamina_cost": 10, "flag_deltas": {"clue_count": 1}},
        "repeat": "free",
        "time_cost": 2,
    }
    base.update(overrides)
    return base


def test_activity_plan_is_pure_and_returns_resource_delta():
    player = PlayerState(scene_id="reading_hall", stamina=50)
    flags = {"clue_count": 2}
    plan = plan_scene_activity(
        activity(),
        activity_id="demo_activity",
        activity_choice=None,
        scene_id="reading_hall",
        time_band="morning",
        day=1,
        flags=flags,
        player=player,
    )
    assert plan.next_flags["clue_count"] == 3
    assert plan.next_player.stamina == 40
    assert plan.resource_changes["stamina"]["delta"] == -10
    assert flags == {"clue_count": 2}
    assert player.stamina == 50


def test_activity_plan_rejects_wrong_scene_before_mutation():
    try:
        plan_scene_activity(
            activity(), activity_id="demo_activity", activity_choice=None,
            scene_id="home_hearth", time_band="morning", day=1,
            flags={}, player=PlayerState(scene_id="home_hearth"),
        )
    except ActivityValidationError as exc:
        assert exc.code == "wrong_scene"
        assert exc.details["allowed_scenes"] == ["reading_hall"]
    else:
        raise AssertionError("expected wrong_scene")


def test_once_activity_and_hp_safety_use_existing_error_contract():
    once = activity(repeat="once")
    args = dict(
        activity_id="demo_activity", activity_choice=None,
        scene_id="reading_hall", time_band="morning", day=1,
    )
    try:
        plan_scene_activity(once, flags={"activity_done.demo_activity": 1}, player=PlayerState(scene_id="reading_hall"), **args)
    except ActivityValidationError as exc:
        assert exc.code == "already_done"
    else:
        raise AssertionError("expected already_done")

    dangerous = activity(effects={"hp_cost": 10, "stamina_cost": 0})
    try:
        plan_scene_activity(dangerous, flags={}, player=PlayerState(scene_id="reading_hall", hp=10), **args)
    except ActivityValidationError as exc:
        assert exc.code == "insufficient_hp"
        assert exc.details["required"] == 11
    else:
        raise AssertionError("expected insufficient_hp")
