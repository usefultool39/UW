import json

from app.agent_registry import initial_agent_states, load_agent_profiles
from app.models import Location


def test_agent_registry_loads_profiles_from_characters_meta(tmp_path):
    root = tmp_path
    chars = root / "characters"
    chars.mkdir()
    (chars / "meta.json").write_text(
        json.dumps(
            {
                "agents": [
                    {
                        "id": "mina",
                        "display": "米娜",
                        "role": "测试村 · 药师",
                        "behavior_role": "logistics",
                        "initial_location": "home",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    profiles = load_agent_profiles(root)

    assert profiles["mina"].display == "米娜"
    assert profiles["mina"].behavior_role == "logistics"
    assert profiles["mina"].initial_location == Location.home


def test_initial_agent_states_are_data_driven(tmp_path):
    root = tmp_path
    chars = root / "characters"
    chars.mkdir()
    (chars / "meta.json").write_text(
        json.dumps(
            {
                "agents": [
                    {
                        "id": "scout",
                        "display": "侦察员",
                        "role": "测试村 · 巡逻",
                        "behavior_role": "field",
                        "initial_location": "bench",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    agents = initial_agent_states(root)

    assert [agent.id for agent in agents] == ["scout"]
    assert agents[0].location == Location.bench


def test_disabled_agents_are_not_spawned(tmp_path):
    root = tmp_path
    chars = root / "characters"
    chars.mkdir()
    (chars / "meta.json").write_text(
        json.dumps(
            {
                "agents": [
                    {
                        "id": "hidden",
                        "display": "隐藏角色",
                        "enabled": False,
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert initial_agent_states(root) == []
