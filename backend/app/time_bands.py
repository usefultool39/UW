"""昼夜与 tick 区间：与 config.TICK_PER_DAY 对齐，供 LLM 与文档单一真相源。"""

from __future__ import annotations

from .config import (
    CIRCADIAN_AFTERNOON_END,
    CIRCADIAN_EVENING_END,
    CIRCADIAN_MORNING_END,
    TICK_PER_DAY,
)


def circadian_hint_zh(tick: int) -> str:
    """与 advance_tick 后的 tick 一致：取模 TICK_PER_DAY 后分段。"""
    t = int(tick) % max(1, TICK_PER_DAY)
    if t < CIRCADIAN_MORNING_END:
        return "清晨"
    if t < CIRCADIAN_AFTERNOON_END:
        return "白昼"
    if t < CIRCADIAN_EVENING_END:
        return "傍晚"
    return "深夜（宜休息、回家）"


def circadian_band_name_en(tick: int) -> str:
    """英文 band 名，供 system prompt 与中文 user 消息一致。"""
    t = int(tick) % max(1, TICK_PER_DAY)
    if t < CIRCADIAN_MORNING_END:
        return "morning"
    if t < CIRCADIAN_AFTERNOON_END:
        return "afternoon"
    if t < CIRCADIAN_EVENING_END:
        return "evening"
    return "night"
