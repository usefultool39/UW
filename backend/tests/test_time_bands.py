import pytest

from app.time_bands import circadian_band_name_en, circadian_hint_zh


@pytest.mark.parametrize(
    "tick,expected_zh",
    [
        (0, "清晨"),
        (14, "清晨"),
        (15, "白昼"),
        (39, "白昼"),
        (40, "傍晚"),
        (51, "傍晚"),
        (52, "深夜（宜休息、回家）"),
        (60, "深夜（宜休息、回家）"),
        (61, "清晨"),
    ],
)
def test_circadian_hint_zh(tick, expected_zh):
    assert circadian_hint_zh(tick) == expected_zh


def test_circadian_band_name_en_edges():
    assert circadian_band_name_en(0) == "morning"
    assert circadian_band_name_en(51) == "evening"
    assert circadian_band_name_en(52) == "night"
