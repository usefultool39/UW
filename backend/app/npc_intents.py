from __future__ import annotations

from pathlib import Path

from .models import NpcIntent, WorldState


def _flag(state: WorldState, key: str) -> int:
    return int((state.flags or {}).get(key, 0))


def _done(state: WorldState, event_id: str) -> bool:
    return event_id in (state.completed_event_ids or [])


def _intent(
    *,
    state: WorldState,
    npc_id: str,
    intent_id: str,
    title: str,
    description: str,
    scene_id: str,
    tile_x: int,
    tile_y: int,
    event_id: str,
    response_ids: list[str],
    priority: int = 60,
) -> NpcIntent:
    return NpcIntent(
        id=intent_id,
        npc_id=npc_id,
        kind="npc_invite",
        title=title,
        description=description,
        scene_id=scene_id,
        map_id="novice_open",
        tile_x=tile_x,
        tile_y=tile_y,
        priority=priority,
        reason="Pre-Capture authored story node.",
        action={"type": "story_event", "event_id": event_id},
        stakes=["选择会写入关系、记忆和后续剧情回响。"],
        response_options=[
            {
                "id": response_id,
                "label": response_id.replace("_", " "),
                "hint": "",
                "once": True,
                "effects": {},
            }
            for response_id in response_ids
        ],
    )


def build_npc_intents(project_root: Path, state: WorldState) -> list[NpcIntent]:
    _ = project_root
    intents: list[NpcIntent] = []
    day = int(state.day)
    band = state.time_band

    if day == 1 and band == "morning" and not _done(state, "ch1pc_n01_rulid_daily"):
        intents.append(_intent(
            state=state,
            npc_id="alice",
            intent_id="alice_precapture_n01",
            title="爱丽丝想先确认今天的日程",
            description="巨神树伐木场的日常还没有结束，爱丽丝带着食物过来了。",
            scene_id="gigas_clearing",
            tile_x=54,
            tile_y=22,
            event_id="ch1pc_n01_rulid_daily",
            response_ids=["warm_bond", "neutral_bond", "distant_bond"],
        ))
    if day == 1 and band == "afternoon" and not _done(state, "ch1pc_n02_gigas_calling"):
        intents.append(_intent(
            state=state,
            npc_id="eugeo",
            intent_id="eugeo_precapture_n02",
            title="尤吉欧想一起完成今天的伐木节奏",
            description="下午的风穿过巨神树清场，天职的压力还挂在尤吉欧肩上。",
            scene_id="gigas_clearing",
            tile_x=54,
            tile_y=22,
            event_id="ch1pc_n02_gigas_calling",
            response_ids=["steady_pace", "push_pace", "slow_pace"],
        ))
    if day == 1 and band == "evening" and not _done(state, "ch1pc_n03_talk_index_end_mountains"):
        intents.append(_intent(
            state=state,
            npc_id="alice",
            intent_id="alice_precapture_n03",
            title="爱丽丝想谈谈尽头山脉的传闻",
            description="炉边的晚餐把三个人重新聚到一起，禁忌目录的话题摆在桌面上。",
            scene_id="home_hearth",
            tile_x=11,
            tile_y=27,
            event_id="ch1pc_n03_talk_index_end_mountains",
            response_ids=["casual_talk", "deep_talk", "avoid_talk"],
        ))
    if day == 2 and band == "morning" and not _done(state, "ch1pc_n04_travel_to_end_mountains"):
        intents.append(_intent(
            state=state,
            npc_id="eugeo",
            intent_id="eugeo_precapture_n04",
            title="尤吉欧在检查出发的补给",
            description="从住家到北门再到尽头山脉洞窟，今天只能带走有限的准备。",
            scene_id="north_gate",
            tile_x=67,
            tile_y=24,
            event_id="ch1pc_n04_travel_to_end_mountains",
            response_ids=["pack_food", "pack_tool", "pack_record", "bring_alice_extra"],
        ))
    if day == 2 and band == "afternoon" and not _done(state, "ch1pc_n05_encounter_dark_territory_injured"):
        intents.append(_intent(
            state=state,
            npc_id="alice",
            intent_id="alice_precapture_n05",
            title="爱丽丝发现边界另一侧有人受伤",
            description="三人抵达洞窟外侧，边界另一侧存在受伤的陌生生命。",
            scene_id="north_gate",
            tile_x=67,
            tile_y=24,
            event_id="ch1pc_n05_encounter_dark_territory_injured",
            response_ids=["cautious_approach", "helping_approach", "observing_approach"],
        ))
    if day == 2 and band == "afternoon" and _flag(state, "d5_approach") > 0 and not _done(state, "ch1pc_n06_alice_crosses_boundary"):
        intents.append(_intent(
            state=state,
            npc_id="alice",
            intent_id="alice_precapture_n06",
            title="爱丽丝决定靠近边界",
            description="规则和眼前的伤势正在冲突，她需要确认自己看到的事实。",
            scene_id="north_gate",
            tile_x=67,
            tile_y=24,
            event_id="ch1pc_n06_alice_crosses_boundary",
            response_ids=["grasp_alice_arm", "shout_stop", "keep_silent"],
            priority=70,
        ))
    if day == 2 and band == "evening" and _flag(state, "d6_alice_crossed_instant") > 0 and not _done(state, "ch1pc_n07_return_to_rulid"):
        intents.append(_intent(
            state=state,
            npc_id="eugeo",
            intent_id="eugeo_precapture_n07",
            title="尤吉欧想讨论回到村子后怎么说",
            description="爱丽丝刚越过边界，三人带着这份事实返回卢利特。",
            scene_id="north_gate",
            tile_x=67,
            tile_y=24,
            event_id="ch1pc_n07_return_to_rulid",
            response_ids=["tell_truth_now", "wait_for_alice", "keep_secret"],
        ))
    if day == 3 and band == "morning" and not _done(state, "ch1pc_n08_knights_arrive_village"):
        intents.append(_intent(
            state=state,
            npc_id="eugeo",
            intent_id="eugeo_precapture_n08",
            title="整合骑士来到村中",
            description="广场上的公告把爱丽丝的越界变成必须面对的罪名。",
            scene_id="village_square",
            tile_x=24,
            tile_y=24,
            event_id="ch1pc_n08_knights_arrive_village",
            response_ids=["step_forward", "stand_with_eugeo", "stay_back_observe"],
            priority=80,
        ))
    if day == 3 and band == "afternoon" and _done(state, "ch1pc_n08_knights_arrive_village") and not _done(state, "ch1pc_n09_alice_farewell"):
        intents.append(_intent(
            state=state,
            npc_id="alice",
            intent_id="alice_precapture_n09",
            title="爱丽丝想和家人、桐人、尤吉欧告别",
            description="被带走前，她有一段短暂的告别时间。",
            scene_id="village_square",
            tile_x=24,
            tile_y=24,
            event_id="ch1pc_n09_alice_farewell",
            response_ids=["speak_one_sentence", "pass_record_book", "stand_silently_with_eugeo"],
            priority=85,
        ))
    if day == 3 and _done(state, "ch1pc_n09_alice_farewell") and not _done(state, "ch1pc_n10_alice_captured"):
        intents.append(_intent(
            state=state,
            npc_id="alice",
            intent_id="alice_precapture_n10",
            title="爱丽丝被带向北门外",
            description="固定终点已经靠近；玩家只能留下最后一份记录。",
            scene_id="north_gate",
            tile_x=67,
            tile_y=24,
            event_id="ch1pc_n10_alice_captured",
            response_ids=["record_one_phrase", "record_silence", "close_record_book"],
            priority=95,
        ))
    return intents


def attach_npc_intents(project_root: Path, state: WorldState) -> WorldState:
    return state.model_copy(update={"npc_intents": build_npc_intents(project_root, state)})
