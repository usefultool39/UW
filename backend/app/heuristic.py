from __future__ import annotations

from pathlib import Path

from .agent_registry import get_agent_profile
from .config import CHOP_STAMINA_COST, MEAL_TICK, TICK_PER_DAY
from .models import Action, ActionName, AgentState, Location, TreeState, WorldState

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _role(agent: AgentState) -> str:
    return get_agent_profile(_PROJECT_ROOT, agent.id).behavior_role


def choose_action(state: WorldState, agent: AgentState) -> Action:
    """Deterministic policy for testing without LLM."""
    if state.tree.state == TreeState.fallen or state.tree.hp <= 0:
        return Action(name=ActionName.noop)

    tick = state.tick
    is_meal_time = tick == MEAL_TICK
    is_sleep_time = tick == TICK_PER_DAY - 1

    if _role(agent) == "logistics":
        if is_meal_time and agent.location == Location.table:
            return Action(name=ActionName.eat)
        elif is_sleep_time and agent.location == Location.home:
            return Action(name=ActionName.sleep)
        elif agent.location == Location.home and not is_meal_time and not is_sleep_time:
            return Action(name=ActionName.cook)
        elif agent.location == Location.home and is_meal_time:
            return Action(name=ActionName.eat)
        else:
            return Action(name=ActionName.go_home)

    if agent.location == Location.table:
        if is_meal_time:
            return Action(name=ActionName.eat)
        elif is_sleep_time:
            return Action(name=ActionName.go_home)
        else:
            return Action(name=ActionName.noop)

    if agent.location == Location.home:
        if is_meal_time:
            return Action(name=ActionName.move, target=Location.table.value)
        elif is_sleep_time:
            return Action(name=ActionName.sleep)
        elif agent.hunger >= 80:
            return Action(name=ActionName.move, target=Location.table.value)
        else:
            return Action(name=ActionName.go_home)

    if agent.location == Location.at_tree:
        if is_sleep_time:
            return Action(name=ActionName.go_home)
        if agent.stamina < CHOP_STAMINA_COST:
            return Action(name=ActionName.move, target=Location.bench.value)
        return Action(name=ActionName.chop)

    if agent.location == Location.bench:
        if agent.stamina < agent.stamina_max - 5:
            return Action(name=ActionName.rest)
        if is_meal_time or is_sleep_time:
            return Action(name=ActionName.go_home)
        return Action(name=ActionName.move, target=Location.at_tree.value)

    return Action(name=ActionName.noop)
