import pytest
import json
import re
from app.llm_agent import (
    parse_action_json,
    _strip_think_tags,
    _extract_thinking,
    build_user_message,
    _is_minimax_mode,
    _is_openai_chat_model,
    _sanitize_api_key,
)
from app.models import Action, ActionName, WorldState, Tree, AgentState, Location


class TestSanitizeApiKey:
    def test_strips_bearer(self):
        assert _sanitize_api_key("Bearer abc123") == "abc123"

    def test_strips_quotes(self):
        assert _sanitize_api_key('"abc123"') == "abc123"
        assert _sanitize_api_key("'abc123'") == "abc123"

    def test_no_change(self):
        assert _sanitize_api_key("abc123") == "abc123"


class TestIsMinimaxMode:
    def test_minimax_key_flag(self):
        assert _is_minimax_mode("gpt-4", has_minimax_key=True) is True

    def test_minimax_in_model_name(self):
        assert _is_minimax_mode("MiniMax-M2.7", has_minimax_key=False) is True

    def test_m2_her_model_name(self):
        assert _is_minimax_mode("M2-her", has_minimax_key=False) is True

    def test_m2_h_model_name(self):
        assert _is_minimax_mode("M2-H", has_minimax_key=False) is True

    def test_default_false(self):
        assert _is_minimax_mode("gpt-4", has_minimax_key=False) is False


class TestOpenAiChatModel:
    def test_m2_her_uses_openai_chat_shape(self):
        assert _is_openai_chat_model("M2-her") is True

    def test_m2_h_uses_openai_chat_shape(self):
        assert _is_openai_chat_model("M2-H") is True

    def test_m27_uses_text_generation_shape(self):
        assert _is_openai_chat_model("MiniMax-M2.7") is False


class TestStripThinkTags:
    def test_strips_reasoning_block(self):
        text = '<redacted_reasoning>some thought process</redacted_reasoning>{"name":"chop"}'
        result = _strip_think_tags(text)
        assert "redacted_reasoning" not in result
        assert '{"name":"chop"}' in result

    def test_strips_thinking_block(self):
        text = '<redacted_thinking>inner thoughts</redacted_thinking>{"name":"move","target":"bench"}'
        result = _strip_think_tags(text)
        assert "redacted_thinking" not in result
        assert '{"name":"move","target":"bench"}' in result

    def test_no_tags_unchanged(self):
        text = '{"name":"chop"}'
        assert _strip_think_tags(text) == text


class TestExtractThinking:
    def test_extracts_single_block(self):
        text = "<redacted_reasoning>think1</redacted_reasoning>extra"
        result = _extract_thinking(text)
        assert "think1" in result

    def test_extracts_multiple_blocks(self):
        text = "<redacted_thinking>t1</redacted_thinking><redacted_reasoning>t2</redacted_reasoning>"
        result = _extract_thinking(text)
        assert "t1" in result
        assert "t2" in result


class TestParseActionJson:
    def test_simple_chop(self):
        action, thinking = parse_action_json('{"name":"chop"}')
        assert action.name == ActionName.chop
        assert thinking is None

    def test_move_with_target(self):
        action, thinking = parse_action_json('{"name":"move","target":"bench"}')
        assert action.name == ActionName.move
        assert action.target == "bench"

    def test_from_code_block(self):
        text = '```json\n{"name":"chop"}\n```'
        action, thinking = parse_action_json(text)
        assert action.name == ActionName.chop

    def test_strips_think_tags(self):
        text = '<redacted_thinking>inner</redacted_thinking>{"name":"eat"}'
        action, thinking = parse_action_json(text)
        assert action.name == ActionName.eat

    def test_fallback_json_extraction(self):
        text = 'some text before {"name":"rest"} some text after'
        action, thinking = parse_action_json(text)
        assert action.name == ActionName.rest

    def test_with_thinking(self):
        text = '{"thinking":"I am tired","name":"rest"}'
        action, thinking = parse_action_json(text)
        assert action.name == ActionName.rest
        assert thinking == "I am tired"


class TestBuildUserMessage:
    def test_includes_day_and_tick(self):
        state = WorldState(
            tick=10,
            day=2,
            tree=Tree(hp=100_000_000, hp_max=100_000_000),
            agents=[
                AgentState(
                    id="alice",
                    stamina=100,
                    stamina_max=100,
                    hunger=0,
                    location=Location.at_tree,
                ),
                AgentState(
                    id="eugeo",
                    stamina=100,
                    stamina_max=100,
                    hunger=0,
                    location=Location.at_tree,
                ),
            ],
        )
        msg = build_user_message(state, "alice", [])
        assert "天数=2" in msg
        assert "回合=10" in msg

    def test_includes_tree_info(self):
        state = WorldState(
            tick=0,
            day=1,
            tree=Tree(hp=50_000_000, hp_max=100_000_000),
            agents=[
                AgentState(
                    id="alice",
                    stamina=100,
                    stamina_max=100,
                    hunger=0,
                    location=Location.at_tree,
                ),
                AgentState(
                    id="eugeo",
                    stamina=100,
                    stamina_max=100,
                    hunger=0,
                    location=Location.at_tree,
                ),
            ],
        )
        msg = build_user_message(state, "alice", [])
        assert "生命值=50000000/100000000" in msg
        assert "50.00%" in msg

    def test_includes_others_info(self):
        state = WorldState(
            tick=0,
            day=1,
            tree=Tree(hp=100_000_000, hp_max=100_000_000),
            agents=[
                AgentState(
                    id="alice",
                    stamina=50,
                    stamina_max=100,
                    hunger=0,
                    location=Location.at_tree,
                ),
                AgentState(
                    id="eugeo",
                    stamina=100,
                    stamina_max=100,
                    hunger=0,
                    location=Location.at_tree,
                ),
            ],
        )
        msg = build_user_message(state, "alice", [])
        assert "eugeo" in msg
        assert "高" in msg

    def test_stamina_band(self):
        state = WorldState(
            tick=0,
            day=1,
            tree=Tree(hp=100_000_000, hp_max=100_000_000),
            agents=[
                AgentState(
                    id="alice",
                    stamina=20,
                    stamina_max=100,
                    hunger=0,
                    location=Location.at_tree,
                ),
                AgentState(
                    id="eugeo",
                    stamina=100,
                    stamina_max=100,
                    hunger=0,
                    location=Location.at_tree,
                ),
            ],
        )
        msg = build_user_message(state, "alice", [])
        assert "低" in msg
