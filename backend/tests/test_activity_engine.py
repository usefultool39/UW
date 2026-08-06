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


def test_authored_choice_activity_requires_explicit_choice():
    choice_activity = activity(
        choices=[
            {"id": "safe", "effects": {"flags": {"safe_route": 1}}},
            {"id": "bold", "effects": {"flags": {"bold_route": 1}}},
        ]
    )

    try:
        plan_scene_activity(
            choice_activity,
            activity_id="demo_activity",
            activity_choice=None,
            scene_id="reading_hall",
            time_band="morning",
            day=1,
            flags={},
            player=PlayerState(scene_id="reading_hall"),
        )
    except ActivityValidationError as exc:
        assert exc.code == "activity_choice_required"
        assert exc.details["choice_ids"] == ["safe", "bold"]
    else:
        raise AssertionError("expected activity_choice_required")


def test_activity_plan_enforces_authored_day_window_before_effects():
    gated = activity(requirements={"day_min": 47, "day_max": 52})
    for day in (46, 53):
        try:
            plan_scene_activity(
                gated,
                activity_id="demo_activity",
                activity_choice=None,
                scene_id="reading_hall",
                time_band="morning",
                day=day,
                flags={},
                player=PlayerState(scene_id="reading_hall"),
            )
        except ActivityValidationError as exc:
            assert exc.code == "wrong_day_range"
            assert exc.details["day"] == day
            assert exc.details["day_min"] == 47
            assert exc.details["day_max"] == 52
        else:
            raise AssertionError("expected wrong_day_range")

    plan = plan_scene_activity(
        gated,
        activity_id="demo_activity",
        activity_choice=None,
        scene_id="reading_hall",
        time_band="morning",
        day=49,
        flags={},
        player=PlayerState(scene_id="reading_hall"),
    )
    assert plan.next_flags["clue_count"] == 1


def test_activity_plan_preserves_explicit_zero_stamina_for_mp_route_choice():
    resource_choice = activity(
        effects={"stamina_cost": 0, "mp_cost": 0},
        choices=[
            {
                "id": "use_arts",
                "effects": {"stamina_cost": 0, "mp_cost": 10, "flags": {"arts_route": 1}},
            }
        ],
    )
    player = PlayerState(scene_id="reading_hall", stamina=40, mp=30)

    plan = plan_scene_activity(
        resource_choice,
        activity_id="demo_activity",
        activity_choice="use_arts",
        scene_id="reading_hall",
        time_band="morning",
        day=1,
        flags={},
        player=player,
    )

    assert plan.stamina_cost == 0
    assert plan.mp_cost == 10
    assert plan.next_player.stamina == 40
    assert plan.next_player.mp == 20
