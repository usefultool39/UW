from app.heuristic import choose_action
from app.models import ActionName, Location
from app.world import initial_world


def _agent(state, aid: str):
    return next(a for a in state.agents if a.id == aid)


def test_home_hungry_moves_to_table_instead_of_eat():
    state = initial_world()
    eugeo = _agent(state, "eugeo")
    eugeo.location = Location.home
    eugeo.hunger = 90

    action = choose_action(state, eugeo)

    assert action.name == ActionName.move
    assert action.target == Location.table.value
