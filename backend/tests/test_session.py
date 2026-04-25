import pytest
import threading
import time
from pathlib import Path
from app.session import Session
from app.models import ActionName


class TestSessionInit:
    def test_session_initial_state(self, tmp_path):
        sess = Session(seed=42, run_id="test-run")
        assert sess.state.tick == 0
        assert sess.state.day == 1
        assert sess.state.tree.hp == 200
        assert len(sess.events) == 0
        assert sess.run_id == "test-run"

    def test_session_has_lock(self):
        sess = Session()
        assert hasattr(sess, "_lock")
        assert isinstance(sess._lock, type(threading.Lock()))


class TestSessionStep:
    def test_step_returns_events(self, tmp_path):
        sess = Session(run_id="test-step")
        events = sess.step(mode="heuristic")
        assert len(events) == 2

    def test_step_increments_tick(self, tmp_path):
        sess = Session(run_id="test-tick")
        initial_tick = sess.state.tick
        sess.step(mode="heuristic")
        assert sess.state.tick == initial_tick + 1

    def test_step_reduces_tree_hp(self, tmp_path):
        sess = Session(run_id="test-chop")
        initial_hp = sess.state.tree.hp
        sess.step(mode="heuristic")
        assert sess.state.tree.hp < initial_hp

    def test_step_appends_events(self, tmp_path):
        sess = Session(run_id="test-events")
        sess.step(mode="heuristic")
        assert len(sess.events) > 0

    def test_multiple_steps(self, tmp_path):
        sess = Session(run_id="test-multi")
        for _ in range(5):
            sess.step(mode="heuristic")
        assert len(sess.events) == 10


class TestSessionConcurrency:
    def test_concurrent_step_safety(self, tmp_path):
        sess = Session(run_id="test-concurrent")
        errors = []

        def run_steps():
            try:
                for _ in range(10):
                    sess.step(mode="heuristic")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=run_steps) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert sess.state.tick > 0
