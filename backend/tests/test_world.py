import pytest
from app.world import initial_world, apply_action, advance_tick
from app.models import Action, ActionName, Location, TreeState


def _agent(state, aid: str):
    return next(a for a in state.agents if a.id == aid)


class TestInitialWorld:
    def test_initial_world_returns_valid_state(self):
        state = initial_world()
        assert state.tick == 0
        assert state.day == 1
        assert state.tree.hp == 100_000_000
        assert state.tree.state == TreeState.standing
        assert len(state.agents) == 2

    def test_agents_have_correct_ids(self):
        state = initial_world()
        agent_ids = {a.id for a in state.agents}
        assert agent_ids == {"alice", "eugeo"}

    def test_eugeo_starts_at_tree(self):
        state = initial_world()
        eugeo = _agent(state, "eugeo")
        assert eugeo.location == Location.at_tree

    def test_alice_starts_at_home(self):
        state = initial_world()
        alice = _agent(state, "alice")
        assert alice.location == Location.home

    def test_player_defaults(self):
        state = initial_world()
        assert state.player.tile_x >= 0
        assert state.player.tile_y >= 0
        assert state.player.map_id == "novice_open"
        assert state.player.scene_id in state.unlocked_scenes
        assert state.story_node_id == "mq00_tutorial"
        assert "reading_hall" in state.unlocked_scenes

    def test_initial_world_has_time_and_chapter_fields(self):
        state = initial_world()
        assert state.time_band == "morning"
        assert state.chapter_id == "chapter_01"

    def test_agents_have_map_positions(self):
        state = initial_world()
        alice = _agent(state, "alice")
        eugeo = _agent(state, "eugeo")
        assert (alice.tile_x, alice.tile_y) == (11, 27)
        assert alice.scene_id == "reading_hall"
        assert (eugeo.tile_x, eugeo.tile_y) == (54, 22)
        assert eugeo.scene_id == "gigas_clearing"


class TestApplyAction:
    def test_chop_reduces_tree_hp(self):
        state = initial_world()
        action = Action(name=ActionName.chop)
        new_state, event = apply_action(state, "eugeo", action)
        assert new_state.tree.hp == 100_000_000 - 10
        assert event.ok is True
        assert "chop" in event.detail

    def test_chop_without_axe_fails(self):
        state = initial_world()
        eugeo = _agent(state, "eugeo")
        eugeo.has_axe = False
        action = Action(name=ActionName.chop)
        _, event = apply_action(state, "eugeo", action)
        assert event.ok is False
        assert "no_axe" in event.detail

    def test_chop_insufficient_stamina_fails(self):
        state = initial_world()
        eugeo = _agent(state, "eugeo")
        eugeo.stamina = 0
        action = Action(name=ActionName.chop)
        _, event = apply_action(state, "eugeo", action)
        assert event.ok is False
        assert "not_enough_stamina" in event.detail

    def test_chop_not_at_tree_fails(self):
        state = initial_world()
        eugeo = _agent(state, "eugeo")
        eugeo.location = Location.home
        action = Action(name=ActionName.chop)
        _, event = apply_action(state, "eugeo", action)
        assert event.ok is False
        assert "chop_only_at_tree" in event.detail

    def test_move_to_valid_location(self):
        state = initial_world()
        action = Action(name=ActionName.move, target="bench")
        new_state, event = apply_action(state, "eugeo", action)
        assert _agent(new_state, "eugeo").location == Location.bench
        assert (_agent(new_state, "eugeo").tile_x, _agent(new_state, "eugeo").tile_y) == (24, 24)
        assert event.ok is True

    def test_move_to_invalid_location_fails(self):
        state = initial_world()
        action = Action(name=ActionName.move, target="invalid_place")
        _, event = apply_action(state, "eugeo", action)
        assert event.ok is False

    def test_rest_at_bench_recovers_stamina(self):
        state = initial_world()
        eugeo = _agent(state, "eugeo")
        eugeo.location = Location.bench
        eugeo.stamina = 50
        action = Action(name=ActionName.rest)
        new_state, event = apply_action(state, "eugeo", action)
        assert _agent(new_state, "eugeo").stamina == 72
        assert event.ok is True

    def test_rest_not_at_bench_fails(self):
        state = initial_world()
        action = Action(name=ActionName.rest)
        _, event = apply_action(state, "eugeo", action)
        assert event.ok is False

    def test_eat_at_table(self):
        state = initial_world()
        alice = _agent(state, "alice")
        alice.location = Location.table
        alice.hunger = 50
        action = Action(name=ActionName.eat)
        new_state, event = apply_action(state, "alice", action)
        assert _agent(new_state, "alice").hunger == 20
        assert event.ok is True

    def test_eat_not_at_table_fails(self):
        state = initial_world()
        action = Action(name=ActionName.eat)
        _, event = apply_action(state, "eugeo", action)
        assert event.ok is False

    def test_sleep_at_home(self):
        state = initial_world()
        alice = _agent(state, "alice")
        alice.location = Location.home
        action = Action(name=ActionName.sleep)
        new_state, event = apply_action(state, "alice", action)
        assert _agent(new_state, "alice").is_sleeping is True
        assert event.ok is True

    def test_sleep_not_at_home_fails(self):
        state = initial_world()
        action = Action(name=ActionName.sleep)
        _, event = apply_action(state, "eugeo", action)
        assert event.ok is False


class TestAdvanceTick:
    def test_tick_increments(self):
        state = initial_world()
        new_state = advance_tick(state)
        assert new_state.tick == 1

    def test_hunger_increases_each_tick(self):
        state = initial_world()
        alice = _agent(state, "alice")
        alice.hunger = 10
        new_state = advance_tick(state)
        assert _agent(new_state, "alice").hunger == 11

    def test_day_changes_at_tick_61(self):
        state = initial_world()
        state.tick = 60
        new_state = advance_tick(state)
        assert new_state.day == 2
        assert new_state.tick == 0
        assert new_state.time_band == "morning"

    def test_time_band_advances_with_tick(self):
        state = initial_world()
        state.tick = 14
        new_state = advance_tick(state)
        assert new_state.tick == 15
        assert new_state.time_band == "afternoon"

    def test_agents_location_not_forcibly_changed(self):
        state = initial_world()
        state.tick = 29
        initial_locations = {a.id: a.location for a in state.agents}
        new_state = advance_tick(state)
        for agent in new_state.agents:
            assert agent.location == initial_locations[agent.id]

    def test_tree_falls_when_hp_zero(self):
        state = initial_world()
        state.tree.hp = 1
        action = Action(name=ActionName.chop)
        new_state, event = apply_action(state, "eugeo", action)
        assert new_state.tree.hp == 0
        assert new_state.tree.state == TreeState.fallen
