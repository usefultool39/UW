import pytest
from pydantic import ValidationError
from app.models import (
    Location, TreeState, ActionName, Action, Tree, AgentState, WorldState, SimEvent
)


class TestLocation:
    def test_location_values(self):
        assert Location.at_tree.value == "at_tree"
        assert Location.bench.value == "bench"
        assert Location.home.value == "home"
        assert Location.table.value == "table"


class TestTreeState:
    def test_tree_state_values(self):
        assert TreeState.standing.value == "standing"
        assert TreeState.fallen.value == "fallen"


class TestActionName:
    def test_action_name_values(self):
        assert ActionName.noop.value == "noop"
        assert ActionName.move.value == "move"
        assert ActionName.chop.value == "chop"
        assert ActionName.rest.value == "rest"
        assert ActionName.eat.value == "eat"
        assert ActionName.sleep.value == "sleep"
        assert ActionName.go_home.value == "go_home"
        assert ActionName.cook.value == "cook"


class TestAction:
    def test_action_with_target(self):
        action = Action(name=ActionName.move, target="bench")
        assert action.name == ActionName.move
        assert action.target == "bench"

    def test_action_without_target(self):
        action = Action(name=ActionName.noop)
        assert action.name == ActionName.noop
        assert action.target is None


class TestTree:
    def test_tree_creation(self):
        tree = Tree(hp=800, hp_max=800, state=TreeState.standing)
        assert tree.hp == 800
        assert tree.hp_max == 800
        assert tree.state == TreeState.standing


class TestAgentState:
    def test_agent_creation(self):
        agent = AgentState(
            id="test_agent",
            stamina=100,
            stamina_max=100,
            hunger=0,
            location=Location.at_tree
        )
        assert agent.id == "test_agent"
        assert agent.stamina == 100
        assert agent.has_axe is True
        assert agent.is_sleeping is False
        assert agent.map_id == "novice_open"

    def test_agent_defaults(self):
        agent = AgentState(
            id="test",
            stamina=50,
            stamina_max=100,
            hunger=20,
            location=Location.home
        )
        assert agent.last_action == "init"
        assert agent.last_action_ok is True
        assert agent.scene_id == "gigas_clearing"
        assert agent.tile_x == 0
        assert agent.tile_y == 0


class TestWorldState:
    def test_world_state_requires_tree(self):
        with pytest.raises(ValidationError):
            WorldState()

    def test_world_state_with_tree(self):
        tree = Tree(hp=800, hp_max=800)
        agents = [
            AgentState(id="a1", stamina=100, stamina_max=100, hunger=0, location=Location.at_tree),
            AgentState(id="a2", stamina=100, stamina_max=100, hunger=0, location=Location.at_tree),
        ]
        state = WorldState(tree=tree, agents=agents)
        assert state.tick == 0
        assert state.day == 1
        assert state.time_band == "morning"
        assert state.chapter_id == "chapter_01"
        assert len(state.agents) == 2


class TestSimEvent:
    def test_sim_event_creation(self):
        event = SimEvent(
            tick=1,
            day=1,
            actor="eugeo",
            action='{"name":"chop"}',
            ok=True,
            detail="chop dmg=6",
            tree_hp_after=99_999_990,
            tree_state="standing",
            stamina_after={"alice": 100, "eugeo": 92},
            hunger_after={"alice": 0, "eugeo": 0}
        )
        assert event.tick == 1
        assert event.actor == "eugeo"
        assert event.ok is True
