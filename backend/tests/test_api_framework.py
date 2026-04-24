from fastapi.testclient import TestClient

from app.main import app


def test_world_regions_json():
    client = TestClient(app)
    r = client.get("/api/world/regions")
    assert r.status_code == 200
    body = r.json()
    assert body.get("v") == 1
    assert "regions" in body


def test_story_catalog_json():
    client = TestClient(app)
    r = client.get("/api/story/catalog")
    assert r.status_code == 200
    assert "nodes" in r.json()


def test_state_returns_time_chapter_and_agent_positions():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.get("/api/state")
    assert r.status_code == 200
    body = r.json()
    assert body["time_band"] == "morning"
    assert body["chapter_id"] == "chapter_01"
    agents = {a["id"]: a for a in body["agents"]}
    assert agents["alice"]["tile_x"] == 11
    assert agents["alice"]["tile_y"] == 27
    assert agents["eugeo"]["tile_x"] == 54
    assert agents["eugeo"]["tile_y"] == 22


def test_story_advance_blocked_without_flags():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post("/api/story/advance", json={"target_id": "mq01_tree_arc"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert body["error"] == "requirements_not_met"


def test_story_advance_ok_after_set_flag():
    client = TestClient(app)
    client.post("/api/reset")
    client.post(
        "/api/player/action",
        json={
            "kind": "set_flag",
            "flag_key": "prologue_reading_done",
            "flag_value": 1,
        },
    )
    r = client.post("/api/story/advance", json={"target_id": "mq01_tree_arc"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["state"]["story_node_id"] == "mq01_tree_arc"


def test_player_move_scene_locked():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/player/action",
        json={"kind": "move_scene", "scene_id": "goblin_cave_stub"},
    )
    assert r.json()["ok"] is False
    assert r.json()["error"] == "scene_locked"


def test_daily_tick_same_shape_as_step():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post("/api/sim/daily_tick", json={"n": 1, "mode": "heuristic"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert len(body["events"]) == 2


def test_dialogue_returns_reply_and_memory_candidate():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/dialogue",
        json={"npc_id": "alice", "message": "北边界是不是有异常？"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["npc_id"] == "alice"
    assert body["reply"]
    assert body["source"] in {"fallback", "llm"}
    assert body["memory_candidate"]["type"] == "dialogue"


def test_dialogue_rejects_unknown_npc():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/dialogue",
        json={"npc_id": "unknown", "message": "你好"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert body["error"] == "unknown_npc"


def test_story_event_api_choose_updates_state_and_profile():
    client = TestClient(app)
    client.post("/api/reset")

    available = client.get("/api/story/available_events")
    assert available.status_code == 200
    events = available.json()["events"]
    assert any(event["id"] == "ch1_d1_reading_clue" for event in events)

    chosen = client.post(
        "/api/story/choose",
        json={"event_id": "ch1_d1_reading_clue", "choice_id": "ask_alice"},
    )
    assert chosen.status_code == 200
    body = chosen.json()
    assert body["ok"] is True
    assert body["state"]["flags"]["clue_boundary_record"] == 1

    profile = client.get("/api/npc/alice/profile")
    assert profile.status_code == 200
    data = profile.json()["profile"]
    assert data["relationship"]["trust"] > 0
    assert data["important_memories"]


def test_save_export_import_restores_world_and_memory():
    client = TestClient(app)
    client.post("/api/reset")
    client.post(
        "/api/story/choose",
        json={"event_id": "ch1_d1_reading_clue", "choice_id": "ask_alice"},
    )

    exported = client.get("/api/save/export")
    assert exported.status_code == 200
    save = exported.json()
    assert save["kind"] == "30town_save"
    assert save["state"]["flags"]["clue_boundary_record"] == 1
    assert save["memory_summaries"]["alice"]["important_memories"]

    client.post("/api/reset")
    assert "clue_boundary_record" not in client.get("/api/state").json()["flags"]

    imported = client.post("/api/save/import", json=save)
    assert imported.status_code == 200
    restored = imported.json()["state"]
    assert restored["flags"]["clue_boundary_record"] == 1

    profile = client.get("/api/npc/alice/profile").json()["profile"]
    assert profile["important_memories"]


def test_move_world_returns_path():
    client = TestClient(app)
    client.post("/api/reset")
    r = client.post(
        "/api/player/action",
        json={"kind": "move_world", "tile_x": 26, "tile_y": 24},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "path" in body
    assert isinstance(body["path"], list)
    assert len(body["path"]) >= 2
    assert body["path"][-1] == {"x": 26, "y": 24}
