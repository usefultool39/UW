from fastapi.testclient import TestClient

from app.codex_service import build_codex
from app.main import app
from app.memory_store import MemoryStore
from app.session import Session


def test_codex_endpoint_exposes_read_only_authoritative_contract():
    client = TestClient(app)
    response = client.get('/api/codex')
    assert response.status_code == 200
    body = response.json()
    assert body['version'] == 1
    assert body['source'] == 'server_authoritative'
    assert set(body) >= {'progress', 'mainline', 'fragments', 'activities', 'npcs', 'recent_memories'}
    assert body['progress']['total'] >= 1
    assert any(item['id'] == 'west_fields_stone_tablet_fragment_1' for item in body['fragments'])
    assert any(item['id'] == 'church_read_sacred_arts' for item in body['activities'])


def test_codex_completion_comes_from_state_flags_inventory_events_and_memory(tmp_path):
    session = Session(run_id='codex-unit')
    session.memory_store = MemoryStore(tmp_path / 'memory')
    state = session.state.model_copy(
        update={
            'completed_event_ids': ['ch1pc_n01_rulid_daily'],
            'active_event_ids': [],
            'flags': {
                'activity_done.west_fields_stone_tablet_fragment_1': 1,
                'activity_done.church_read_sacred_arts': 1,
                'activity_day.south_lake_fishing': 2,
            },
            'inventory': {'stone_tablet_fragment': 1},
        }
    )
    session.state = state
    session.events = [
        {
            'kind': 'player_action',
            'day': 2,
            'payload': {
                'activity_id': 'south_lake_fishing',
                'activity_choice': 'catch_rare_fish',
            },
            'events': [{'type': 'scene_activity_completed'}],
        }
    ]
    session.memory_store.append_important_memory(
        'alice',
        {'day': 2, 'summary': '玩家把共同记录带回书库', 'weight': 4},
        session.run_id,
    )

    body = build_codex(
        state=session.state,
        project_root=session.root,
        events=session.events,
        memory_store=session.memory_store,
    )
    mainline = next(item for item in body['mainline'] if item['id'] == 'ch1pc_n01_rulid_daily')
    fragment = next(item for item in body['fragments'] if item['id'].endswith('_1'))
    reading = next(item for item in body['activities'] if item['id'] == 'church_read_sacred_arts')
    fishing = next(item for item in body['activities'] if item['id'] == 'south_lake_fishing')
    alice = next(item for item in body['npcs'] if item['npc_id'] == 'alice')

    assert mainline['completed'] is True
    assert fragment['collected'] is True
    assert reading['completed'] is True
    assert fishing['completed'] is True
    assert fishing['choices'] == ['收线：雾银鱼（稀有）']
    assert alice['memories'][0]['summary'] == '玩家把共同记录带回书库'
    assert body['source'] == 'server_authoritative'
