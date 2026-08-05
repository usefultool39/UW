from __future__ import annotations

import json
import os
import threading
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .api_models import DialogueBody, PlayerActionBody, RunBody, StoryAdvanceBody, StoryChooseBody
from .content_validator import validate_project
from .llm_config import model_meta
from .month_plan import public_month_plan
from .session import Session
from .scene_activities import public_scene_activities
from .world_map import map_path_for_id

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
load_dotenv()


def _cors_allow_origins() -> list[str]:
    raw = (os.getenv("CORS_ALLOW_ORIGINS") or "").strip()
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:7456",
        "http://localhost:7456",
    ]


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="边境回声 · 日常/主线框架 API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

SESSION = Session(run_id="default")
SESSION_LOCK = threading.Lock()


@app.get("/api/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "service": "边境回声-API",
        "version": "1.1.0"
    }


@app.get("/api/config")
def api_config():
    """供前端显示「密钥是否已被后端加载」；网页本身读不到 .env。"""
    return {
        **model_meta(),
        "env_file": str(ROOT / ".env"),
    }


@app.get("/api/state")
def get_state():
    with SESSION_LOCK:
        sess = SESSION
    return sess.public_state().model_dump(mode="json")


@app.get("/api/events")
def get_events(limit: int = Query(80, ge=1, le=500)):
    with SESSION_LOCK:
        sess = SESSION
    return sess.events[-limit:]


@app.get("/api/save/export")
def save_export():
    with SESSION_LOCK:
        sess = SESSION
    return sess.export_save()


@app.post("/api/save/import")
@limiter.limit("20/minute")
def save_import(request: Request, body: dict):
    with SESSION_LOCK:
        sess = SESSION
        out = sess.import_save(body)
    if out.get("ok") is False:
        raise HTTPException(status_code=400, detail=out.get("error") or "invalid_save")
    return out


@app.get("/api/world/map")
def world_open_map():
    """开放世界格子地图（可走层、出生点、场景分区）。"""
    with SESSION_LOCK:
        path = SESSION.root / "data" / "world" / "world_map.json"
    if not path.is_file():
        return {"v": 1, "id": "empty", "width": 0, "height": 0, "rows": []}
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/world/maps/{map_id}")
def world_map_by_id(map_id: str):
    """按 map_id 读取地图。当前默认地图仍兼容 /api/world/map。"""
    with SESSION_LOCK:
        path = map_path_for_id(SESSION.root, map_id)
    if path is None:
        raise HTTPException(status_code=400, detail="invalid_map_id")
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"unknown_map_id:{map_id}")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/world/regions")
def world_regions():
    """静态区域/场景表（新手村 + 日后 stub），供客户端渲染与按钮。"""
    with SESSION_LOCK:
        path = SESSION.root / "data" / "world" / "regions.json"
    if not path.is_file():
        return {"v": 1, "regions": []}
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/world/scene_activities")
def world_scene_activities():
    """场景活动目录：用于把 POI 做成可重复的 RPG 日常玩法。"""
    with SESSION_LOCK:
        root = SESSION.root
    return public_scene_activities(root)


@app.get("/api/story/catalog")
def story_catalog():
    """主线节点定义（闸锁条件），供调试或 UI 展示。"""
    with SESSION_LOCK:
        p = SESSION.root / "data" / "story" / "main_nodes.json"
    if not p.is_file():
        return {"nodes": {}}
    return json.loads(p.read_text(encoding="utf-8"))


@app.get("/api/story/month_plan")
def story_month_plan(month_id: str = Query("month_01", min_length=1, max_length=40)):
    """第一月路线与当前进度，供日志面板展示长期目标。"""
    with SESSION_LOCK:
        sess = SESSION
        state = sess.public_state()
        root = sess.root
    return public_month_plan(root, state, month_id=month_id)


@app.get("/api/dev/content_validation")
def dev_content_validation():
    """Read-only content reference validation for story, map and activity config."""
    with SESSION_LOCK:
        root = SESSION.root
    return validate_project(root)


@app.get("/api/story/available_events")
def story_available_events():
    with SESSION_LOCK:
        sess = SESSION
        out = sess.available_story_events()
    return out


@app.get("/api/memory/{npc_id}")
def get_npc_memory(npc_id: str, limit: int = Query(20, ge=1, le=500)):
    with SESSION_LOCK:
        sess = SESSION
    npc_ids = {a.id for a in sess.state.agents}
    if npc_id not in npc_ids:
        raise HTTPException(status_code=404, detail=f"未知角色ID: {npc_id}")
    return {
        "npc_id": npc_id,
        "summary": sess.memory_store.load_summary(npc_id),
        "recent_events": sess.memory_store.read_recent_events(npc_id, limit=limit),
    }


@app.get("/api/npc/{npc_id}/profile")
def get_npc_profile(npc_id: str):
    with SESSION_LOCK:
        sess = SESSION
        out = sess.npc_profile(npc_id)
    if out.get("ok") is False:
        raise HTTPException(status_code=404, detail=f"未知角色ID: {npc_id}")
    return out


@app.post("/api/reset")
@limiter.limit("30/minute")
def reset(request: Request, seed: int | None = None):
    global SESSION
    rid = uuid.uuid4().hex[:12]
    with SESSION_LOCK:
        SESSION = Session(seed=seed, run_id=rid)
        sess = SESSION
    return {"ok": True, "run_id": rid, "state": sess.state.model_dump(mode="json")}


@app.post("/api/step")
@limiter.limit("60/minute")
def step(request: Request, body: RunBody | None = None):
    b = body or RunBody()
    mode = b.mode if b.mode in ("heuristic", "llm") else "heuristic"
    n = max(1, min(200, int(b.n)))
    with SESSION_LOCK:
        sess = SESSION
    all_ev: list[dict] = []
    for _ in range(n):
        try:
            evs = sess.step(mode=mode)  # type: ignore[arg-type]
        except Exception as e:
            return {"ok": False, "error": str(e), "state": sess.state.model_dump(mode="json")}
        all_ev.extend([e.model_dump(mode="json") for e in evs])
    return {"ok": True, "events": all_ev, "state": sess.state.model_dump(mode="json")}


@app.post("/api/sim/daily_tick")
@limiter.limit("60/minute")
def daily_tick(request: Request, body: RunBody | None = None):
    """自动模拟：单步/多步日常 tick；只推进时间段和 NPC 状态，不绕过剧情闸跨日。"""
    b = body or RunBody()
    mode = b.mode if b.mode in ("heuristic", "llm") else "heuristic"
    n = max(1, min(200, int(b.n)))
    with SESSION_LOCK:
        sess = SESSION
    all_ev: list[dict] = []
    for _ in range(n):
        try:
            evs = sess.daily_tick(mode=mode)  # type: ignore[arg-type]
        except Exception as e:
            return {"ok": False, "error": str(e), "state": sess.state.model_dump(mode="json")}
        all_ev.extend([e.model_dump(mode="json") for e in evs])
    return {"ok": True, "events": all_ev, "state": sess.state.model_dump(mode="json")}


@app.post("/api/player/action")
@limiter.limit("120/minute")
def player_action(request: Request, body: PlayerActionBody):
    with SESSION_LOCK:
        sess = SESSION
        out = sess.player_action(
            kind=body.kind,
            map_id=body.map_id,
            entry_point=body.entry_point,
            scene_id=body.scene_id,
            poi_id=body.poi_id,
            location=body.location,
            flag_key=body.flag_key,
            flag_value=body.flag_value,
            activity_id=body.activity_id,
            activity_choice=body.activity_choice,
            intent_id=body.intent_id,
            response_id=body.response_id,
            tile_x=body.tile_x,
            tile_y=body.tile_y,
            day=body.day,
            n=body.n,
            daily_n=body.daily_n,
        )
    return out


@app.post("/api/story/advance")
@limiter.limit("30/minute")
def story_advance(request: Request, body: StoryAdvanceBody):
    with SESSION_LOCK:
        sess = SESSION
        out = sess.story_advance(body.target_id)
    return out


@app.post("/api/story/choose")
@limiter.limit("60/minute")
def story_choose(request: Request, body: StoryChooseBody):
    with SESSION_LOCK:
        sess = SESSION
        out = sess.choose_story_event(body.event_id, body.choice_id)
    return out


@app.post("/api/npc/{npc_id}/intent/propose")
@limiter.limit("30/minute")
def propose_npc_intent(request: Request, npc_id: str):
    """Ask the optional NPC agent for a safe, preview-only intent recommendation."""
    with SESSION_LOCK:
        sess = SESSION
        out = sess.propose_npc_intent(npc_id)
    if out.get("ok") is False:
        raise HTTPException(status_code=404, detail=out.get("error") or "unknown_npc")
    return out


@app.post("/api/dialogue")
@limiter.limit("60/minute")
def dialogue(request: Request, body: DialogueBody):
    with SESSION_LOCK:
        sess = SESSION
        out = sess.dialogue(
            npc_id=body.npc_id,
            message=body.message,
            context=body.context,
        )
    return out
