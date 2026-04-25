from __future__ import annotations

import json
from pathlib import Path

from .config import (
    CHOP_DAMAGE,
    CHOP_STAMINA_COST,
    EAT_HUNGER_DECREASE,
    EAT_STAMINA_RECOVER,
    HUNGER_INCREASE,
    REST_RECOVER,
    SLEEP_HUNGER_INCREASE,
    SLEEP_STAMINA_RECOVER,
    STAMINA_MAX,
    TREE_HP_MAX,
    TICK_PER_DAY,
)
from .agent_registry import initial_agent_states
from .models import (
    Action,
    ActionName,
    AgentState,
    Location,
    PlayerState,
    SimEvent,
    Tree,
    TreeState,
    WorldState,
)
from .relationship import default_relationships, ensure_relationships
from .time_bands import circadian_band_name_en
from .world_map import default_map_path, load_world_map, scene_for_tile


WEATHER_ROTATION: tuple[dict[str, str], ...] = (
    {"weather": "clear", "weather_label": "晴朗", "weather_note": "风从山脉那侧吹来，村道和麦田都很亮。"},
    {"weather": "mist", "weather_label": "薄雾", "weather_note": "薄雾贴着水渠和树根，远处的山线像被擦淡了。"},
    {"weather": "cloudy", "weather_label": "多云", "weather_note": "云影掠过屋顶，巨树清场的光线忽明忽暗。"},
    {"weather": "drizzle", "weather_label": "细雨", "weather_note": "细雨落在草叶和斧柄上，空气里有湿木头的味道。"},
)


def environment_for(day: int, tick: int) -> dict[str, str]:
    band = circadian_band_name_en(tick)
    if band == "night":
        return {
            "weather": "night",
            "weather_label": "夜色",
            "weather_note": "炉火和窗光变得显眼，村外的树林只剩下暗轮廓。",
        }
    item = WEATHER_ROTATION[(int(day) * 3 + int(tick) // 9) % len(WEATHER_ROTATION)]
    return dict(item)


def apply_environment(state: WorldState) -> WorldState:
    return state.model_copy(update=environment_for(state.day, state.tick))


LOCATION_MAP_ANCHORS: dict[Location, dict[str, object]] = {
    Location.at_tree: {
        "tile_x": 54,
        "tile_y": 22,
        "scene_id": "gigas_clearing",
        "current_goal": "清理巨树旁的日常劳动",
    },
    Location.bench: {
        "tile_x": 24,
        "tile_y": 24,
        "scene_id": "village_square",
        "current_goal": "在村道旁短暂休息",
    },
    Location.home: {
        "tile_x": 11,
        "tile_y": 27,
        "scene_id": "home_hearth",
        "current_goal": "在小屋整理与休息",
    },
    Location.table: {
        "tile_x": 15,
        "tile_y": 15,
        "scene_id": "home_hearth",
        "current_goal": "准备一起用餐",
    },
}


def sync_agent_map_position(agent: AgentState) -> None:
    anchor = LOCATION_MAP_ANCHORS.get(agent.location)
    if not anchor:
        return
    agent.tile_x = int(anchor["tile_x"])
    agent.tile_y = int(anchor["tile_y"])
    agent.scene_id = str(anchor["scene_id"])
    agent.map_id = "novice_open"
    agent.current_goal = str(anchor["current_goal"])


def default_schedules_path(project_root: Path) -> Path:
    return project_root / "data" / "world" / "schedules.json"


def load_schedules(project_root: Path) -> dict:
    path = default_schedules_path(project_root)
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return raw if isinstance(raw, dict) else {}


def apply_npc_schedules(state: WorldState, project_root: Path | None = None) -> WorldState:
    root = project_root or Path(__file__).resolve().parent.parent.parent
    schedules = load_schedules(root)
    if not schedules:
        return state
    st = state.model_copy(deep=True)
    for agent in st.agents:
        per_agent = schedules.get(agent.id)
        if not isinstance(per_agent, dict):
            continue
        table = per_agent.get("default")
        if not isinstance(table, dict):
            continue
        entry = table.get(st.time_band)
        if not isinstance(entry, dict):
            continue
        agent.scene_id = str(entry.get("scene_id") or agent.scene_id)
        agent.map_id = str(entry.get("map_id") or agent.map_id or "novice_open")
        agent.tile_x = int(entry.get("tile_x", agent.tile_x))
        agent.tile_y = int(entry.get("tile_y", agent.tile_y))
        agent.current_goal = str(entry.get("goal") or agent.current_goal or "")
    return st


def calculate_mood(agent: AgentState, all_agents: list[AgentState]) -> int:
    base = 50

    if agent.hunger > 80:
        base -= 20
    elif agent.hunger > 60:
        base -= 10

    if agent.stamina < 20:
        base -= 15
    elif agent.stamina < 40:
        base -= 8

    for other in all_agents:
        if other.id == agent.id:
            continue
        if other.stamina < 20:
            base -= 8
        elif other.stamina < 40:
            base -= 4
        if other.hunger > 80:
            base -= 5
        elif other.hunger > 60:
            base -= 2

    if agent.daily_contribution > 20:
        base += 10
    elif agent.daily_contribution > 10:
        base += 5

    if agent.mood > 70 and agent.stamina > 70:
        base += 5

    return max(0, min(100, base))


def calculate_motivation(mood: int, hunger: int, stamina: int) -> float:
    m = 1.0

    if mood > 85:
        m += 0.3
    elif mood > 70:
        m += 0.2
    elif mood < 15:
        m -= 0.2
    elif mood < 30:
        m -= 0.3

    if hunger > 80:
        m -= 0.15
    if stamina < 30:
        m -= 0.15

    return max(0.5, min(1.5, m))


def initial_world(seed: int | None = None) -> WorldState:
    _ = seed
    root = Path(__file__).resolve().parent.parent.parent
    wm = load_world_map(default_map_path(root))
    sp = wm.get("spawn") or {}
    px, py = int(sp.get("x", 4)), int(sp.get("y", 10))
    mid = str(wm.get("id", "novice_open"))
    sid = scene_for_tile(wm, px, py) or "gigas_clearing"

    tree = Tree(hp=TREE_HP_MAX, hp_max=TREE_HP_MAX, state=TreeState.standing)
    agents = initial_agent_states(root)
    for agent in agents:
        sync_agent_map_position(agent)
    state = WorldState(
        tick=0,
        day=1,
        time_band=circadian_band_name_en(0),
        chapter_id="chapter_01",
        scene_id=sid,
        tree=tree,
        agents=agents,
        relationships=default_relationships([agent.id for agent in agents]),
        player=PlayerState(
            scene_id=sid,
            location=Location.at_tree,
            map_id=mid,
            tile_x=px,
            tile_y=py,
            stamina=STAMINA_MAX,
            max_stamina=STAMINA_MAX,
        ),
    )
    return apply_npc_schedules(apply_environment(state), root)


def _agent_by_id(state: WorldState, aid: str) -> AgentState:
    for a in state.agents:
        if a.id == aid:
            return a
    raise KeyError(aid)


def apply_action(
    state: WorldState, agent_id: str, action: Action
) -> tuple[WorldState, SimEvent]:
    st = state.model_copy(deep=True)
    agent = _agent_by_id(st, agent_id)
    ok = True
    detail = ""

    if action.name == ActionName.noop:
        detail = "noop"
    elif action.name == ActionName.move:
        dest = action.target
        valid_locs = [loc.value for loc in Location]
        if dest not in valid_locs:
            ok = False
            detail = "invalid_move_target"
        else:
            agent.location = Location(dest)
            detail = f"move->{dest}"
    elif action.name == ActionName.rest:
        if agent.location != Location.bench:
            ok = False
            detail = "rest_only_at_bench"
        else:
            agent.stamina = min(agent.stamina_max, agent.stamina + REST_RECOVER)
            detail = f"rest+{REST_RECOVER}"
    elif action.name == ActionName.chop:
        if agent.location != Location.at_tree:
            ok = False
            detail = "chop_only_at_tree"
        elif not agent.has_axe:
            ok = False
            detail = "no_axe"
        elif agent.stamina < CHOP_STAMINA_COST:
            ok = False
            detail = "not_enough_stamina"
        elif st.tree.state != TreeState.standing or st.tree.hp <= 0:
            ok = False
            detail = "tree_already_down"
        else:
            actual_damage = int(CHOP_DAMAGE * agent.motivation)
            agent.stamina -= CHOP_STAMINA_COST
            st.tree.hp = max(0, st.tree.hp - actual_damage)
            agent.daily_contribution += 1
            if st.tree.hp <= 0:
                st.tree.state = TreeState.fallen
            detail = f"chop dmg={actual_damage} (mot={agent.motivation:.2f})"
    elif action.name == ActionName.eat:
        if agent.location != Location.table:
            ok = False
            detail = "eat_only_at_table"
        else:
            agent.stamina = min(agent.stamina_max, agent.stamina + EAT_STAMINA_RECOVER)
            agent.hunger = max(0, agent.hunger - EAT_HUNGER_DECREASE)
            detail = f"eat stamina+{EAT_STAMINA_RECOVER} hunger-{EAT_HUNGER_DECREASE}"
    elif action.name == ActionName.sleep:
        if agent.location != Location.home:
            ok = False
            detail = "sleep_only_at_home"
        elif not agent.is_sleeping:
            agent.is_sleeping = True
            agent.stamina = min(
                agent.stamina_max, agent.stamina + SLEEP_STAMINA_RECOVER
            )
            agent.hunger = min(agent.hunger_max, agent.hunger + SLEEP_HUNGER_INCREASE)
            detail = (
                f"sleep stamina+{SLEEP_STAMINA_RECOVER} hunger+{SLEEP_HUNGER_INCREASE}"
            )
        else:
            ok = False
            detail = "already_sleeping"
    elif action.name == ActionName.go_home:
        agent.location = Location.home
        detail = "go_home"
    elif action.name == ActionName.cook:
        if agent.location != Location.home:
            ok = False
            detail = "cook_only_at_home"
        else:
            detail = "cooking"
    else:
        ok = False
        detail = "unknown_action"

    agent.last_action_ok = ok
    agent.last_action = action.name.value
    sync_agent_map_position(agent)

    stamina_after = {a.id: a.stamina for a in st.agents}
    hunger_after = {a.id: a.hunger for a in st.agents}
    ev = SimEvent(
        tick=st.tick,
        day=st.day,
        actor=agent_id,
        action=action.model_dump_json(),
        ok=ok,
        detail=detail,
        tree_hp_after=st.tree.hp,
        tree_state=st.tree.state.value,
        stamina_after=stamina_after,
        hunger_after=hunger_after,
        agent_mood_after=agent.mood,
        agent_motivation_after=agent.motivation,
    )
    return st, ev


def advance_tick(state: WorldState) -> WorldState:
    st = ensure_relationships(state).model_copy(deep=True)
    st.tick += 1
    for agent in st.agents:
        agent.hunger = min(agent.hunger_max, agent.hunger + HUNGER_INCREASE)
        if agent.is_sleeping:
            agent.is_sleeping = False
        agent.mood = calculate_mood(agent, st.agents)
        agent.motivation = calculate_motivation(agent.mood, agent.hunger, agent.stamina)

    if st.tick >= TICK_PER_DAY:
        st.tick = 0
        st.day += 1
        for agent in st.agents:
            agent.daily_contribution = 0

    st.time_band = circadian_band_name_en(st.tick)  # type: ignore[assignment]
    return apply_npc_schedules(apply_environment(st))
