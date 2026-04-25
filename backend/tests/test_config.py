import pytest
from app import config


class TestConfig:
    def test_tree_config(self):
        assert config.TREE_HP_MAX == 200
        assert config.CHOP_DAMAGE == 10
        assert config.CHOP_STAMINA_COST == 8

    def test_stamina_config(self):
        assert config.STAMINA_MAX == 100
        assert config.REST_RECOVER == 22

    def test_hunger_config(self):
        assert config.HUNGER_MAX == 100
        assert config.HUNGER_INCREASE == 1
        assert config.EAT_STAMINA_RECOVER == 10
        assert config.EAT_HUNGER_DECREASE == 30
        assert config.SLEEP_STAMINA_RECOVER == 50
        assert config.SLEEP_HUNGER_INCREASE == 10

    def test_tick_config(self):
        assert config.TICK_PER_DAY == 61
        assert config.TICK_LAST_IN_DAY == 60
        assert config.CIRCADIAN_EVENING_END == 52
        assert config.MEAL_TICK == 30
        assert config.RECENT_EVENTS_K == 12

    def test_scene_id(self):
        assert config.SCENE_ID == "gigas_clearing"
