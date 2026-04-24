from __future__ import annotations

import json
import os
import threading
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .session import Session

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
app = FastAPI(title="30小镇 · 日常/主线框架 API")
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


def _llm_key_configured() -> bool:
    return bool((os.getenv("ANTHROPIC_API_KEY") or os.getenv("MINIMAX_API_KEY") or "").strip())


def _provider_hint() -> str:
    model = (os.getenv("ANTHROPIC_MODEL") or "").lower()
    has_minimax_key = bool((os.getenv("MINIMAX_API_KEY") or "").strip())
    has_anthropic_key = bool((os.getenv("ANTHROPIC_API_KEY") or "").strip())

    if has_minimax_key or "minimax" in model:
        return "MiniMax"
    if has_anthropic_key:
        return "Anthropic SDK"
    return "未配置"


@app.get("/api/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "service": "30小镇-API",
        "version": "1.1.0"
    }


class RunBody(BaseModel):
    n: int = 1
    mode: str = "heuristic"


class PlayerActionBody(BaseModel):
    kind: str
    scene_id: str | None = None
    location: str | None = None
    flag_key: str | None = None
    flag_value: int | None = None
    tile_x: int | None = None
    tile_y: int | None = None


class StoryAdvanceBody(BaseModel):
    target_id: str


class StoryChooseBody(BaseModel):
    event_id: str
    choice_id: str


class DialogueBody(BaseModel):
    npc_id: str
    message: str
    context: dict | None = None


@app.get("/api/config")
def api_config():
    """供前端显示「密钥是否已被后端加载」；网页本身读不到 .env。"""
    return {
        "llm_configured": _llm_key_configured(),
        "provider_hint": _provider_hint(),
        "env_file": str(ROOT / ".env"),
    }


@app.get("/api/state")
def get_state():
    with SESSION_LOCK:
        sess = SESSION
    return sess.state.model_dump(mode="json")


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


@app.get("/api/world/regions")
def world_regions():
    """静态区域/场景表（新手村 + 日后 stub），供客户端渲染与按钮。"""
    with SESSION_LOCK:
        path = SESSION.root / "data" / "world" / "regions.json"
    if not path.is_file():
        return {"v": 1, "regions": []}
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/story/catalog")
def story_catalog():
    """主线节点定义（闸锁条件），供调试或 UI 展示。"""
    with SESSION_LOCK:
        p = SESSION.root / "data" / "story" / "main_nodes.json"
    if not p.is_file():
        return {"nodes": {}}
    return json.loads(p.read_text(encoding="utf-8"))


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
    """推荐：单步/多步日常模拟；语义上等价于旧 `/api/step`，便于客户端命名对齐。"""
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
            scene_id=body.scene_id,
            location=body.location,
            flag_key=body.flag_key,
            flag_value=body.flag_value,
            tile_x=body.tile_x,
            tile_y=body.tile_y,
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
