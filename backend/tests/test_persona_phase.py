from app.models import WorldState
from app.persona_phase import persona_phase_key
from app.world import initial_world


def test_persona_phase_default_childhood():
    st = initial_world()
    assert persona_phase_key(st) == "childhood_rulid"


def test_persona_phase_after_reading_flag():
    st = initial_world()
    st = st.model_copy(update={"flags": {"prologue_reading_done": 1}})
    assert persona_phase_key(st) == "childhood_post_reading"


def test_persona_phase_mq01_overrides_reading_flag():
    st = initial_world()
    st = st.model_copy(
        update={
            "flags": {"prologue_reading_done": 1},
            "story_node_id": "mq01_tree_arc",
        }
    )
    assert persona_phase_key(st) == "childhood_mq01"


def test_persona_phase_mq02_stub():
    st = initial_world()
    st = st.model_copy(update={"story_node_id": "mq02_future_stub"})
    assert persona_phase_key(st) == "storia_academy"


def test_persona_phase_mq02_prefix_not_in_whitelist_stays_childhood():
    st = initial_world()
    st = st.model_copy(update={"story_node_id": "mq02_not_academy"})
    assert persona_phase_key(st) == "childhood_rulid"
