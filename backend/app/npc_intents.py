from __future__ import annotations

from pathlib import Path

from .models import AgentState, NpcIntent, WorldState


def _flag(state: WorldState, key: str) -> int:
    return int((state.flags or {}).get(key, 0))


def _any_flag(state: WorldState, keys: list[str]) -> bool:
    return any(_flag(state, key) >= 1 for key in keys)


def _done_today(state: WorldState, activity_id: str) -> bool:
    return _flag(state, f"activity_day.{activity_id}") == int(state.day)


def _completed(state: WorldState, event_id: str) -> bool:
    return event_id in (state.completed_event_ids or [])


def _agent(state: WorldState, npc_id: str) -> AgentState | None:
    for agent in state.agents or []:
        if agent.id == npc_id:
            return agent
    return None


def _tile(state: WorldState, npc_id: str, fallback: tuple[int, int, str]) -> tuple[int, int, str]:
    agent = _agent(state, npc_id)
    if agent is None:
        return fallback
    return int(agent.tile_x), int(agent.tile_y), str(agent.scene_id or fallback[2])


def _intent(
    *,
    state: WorldState,
    npc_id: str,
    intent_id: str,
    kind: str,
    title: str,
    description: str,
    priority: int,
    reason: str,
    action: dict,
    fallback: tuple[int, int, str],
    stakes: list[str] | None = None,
    response_options: list[dict] | None = None,
    scene_id: str | None = None,
    tile_x: int | None = None,
    tile_y: int | None = None,
) -> NpcIntent:
    ax, ay, agent_scene = _tile(state, npc_id, fallback)
    return NpcIntent(
        id=intent_id,
        npc_id=npc_id,
        kind=kind,
        title=title,
        description=description,
        scene_id=scene_id or agent_scene,
        map_id="novice_open",
        tile_x=int(tile_x if tile_x is not None else ax),
        tile_y=int(tile_y if tile_y is not None else ay),
        priority=priority,
        reason=reason,
        action=action,
        stakes=stakes or [],
        response_options=_available_response_options(
            state,
            intent_id,
            response_options or [],
        ),
    )


def _response_flag(intent_id: str, response_id: str) -> str:
    return f"npc_intent_response.{intent_id}.{response_id}"


def _available_response_options(
    state: WorldState,
    intent_id: str,
    options: list[dict],
) -> list[dict]:
    out: list[dict] = []
    for option in options:
        if not isinstance(option, dict):
            continue
        response_id = str(option.get("id") or "").strip()
        if not response_id:
            continue
        if bool(option.get("once", True)) and _flag(state, _response_flag(intent_id, response_id)) > 0:
            continue
        out.append(option)
    return out


def _social_response(
    *,
    response_id: str,
    label: str,
    hint: str,
    result_text: str,
    effects: dict,
    tone: str = "steady",
) -> dict:
    return {
        "id": response_id,
        "label": label,
        "hint": hint,
        "tone": tone,
        "result_text": result_text,
        "once": True,
        "effects": effects,
    }


def build_npc_intents(project_root: Path, state: WorldState) -> list[NpcIntent]:
    _ = project_root
    intents: list[NpcIntent] = []
    day = int(state.day)
    band = state.time_band

    if day == 1 and band in {"morning", "afternoon"}:
        if _flag(state, "prologue_reading_done") < 1:
            intents.append(
                _intent(
                    state=state,
                    npc_id="alice",
                    intent_id="alice_invites_reading",
                    kind="npc_invite",
                    title="艾琳想让你先看旧记录",
                    description="她在书库那边留了记号，等你把刻印术笔记和边界旧记录拼起来。",
                    priority=96,
                    reason="Day 1 的第一步应让玩家自然进入书库调查。",
                    action={"type": "scene_activity", "activity_id": "church_read_sacred_arts"},
                    stakes=[
                        "艾琳想确认你会不会把旧记录当成普通作业。",
                        "回应她会提前改变她对你是否可靠的判断。",
                    ],
                    response_options=[
                        _social_response(
                            response_id="accept_reading_note",
                            label="告诉艾琳：我会先查旧记录",
                            hint="给她一个明确回应，建立基础信任。",
                            result_text="艾琳把书签推到你手边，声音放轻了一点：她相信你至少会把旧记录看完。",
                            tone="reassure",
                            effects={
                                "flags": {"alice_reading_invite_ack": 1},
                                "relationship": {"alice.trust": 2},
                                "memory": {
                                    "alice": {
                                        "type": "npc_intent_response",
                                        "summary": "玩家回应艾琳的提醒，答应先去查书库旧记录。",
                                        "weight": 3,
                                    }
                                },
                            },
                        ),
                        _social_response(
                            response_id="ask_why_worried",
                            label="追问艾琳：你为什么这么在意？",
                            hint="让她知道你注意到了她的异常担心。",
                            result_text="艾琳没有直接回答，只说旧记录里有些边角字迹不像是普通抄写。她开始意识到你会追问。",
                            tone="probe",
                            effects={
                                "flags": {"alice_worry_noticed": 1},
                                "relationship": {"alice.trust": 1, "alice.tension": 1},
                                "memory": {
                                    "alice": {
                                        "type": "npc_intent_response",
                                        "summary": "玩家没有只接任务，而是追问艾琳为什么在意旧记录。",
                                        "weight": 3,
                                    }
                                },
                            },
                        ),
                    ],
                    fallback=(14, 14, "reading_hall"),
                    scene_id="reading_hall",
                    tile_x=14,
                    tile_y=14,
                )
            )
        elif _flag(state, "clue_boundary_record") < 1 and not _completed(state, "ch1_d1_reading_clue"):
            intents.append(
                _intent(
                    state=state,
                    npc_id="alice",
                    intent_id="alice_reacts_to_boundary_record",
                    kind="npc_reaction",
                    title="艾琳注意到你的书库线索",
                    description="她想知道你读到的静默线到底意味着什么，告诉她或暂时隐瞒都会被记住。",
                    priority=98,
                    reason="玩家完成读书玩法后，NPC 应主动接住线索。",
                    action={"type": "story_event", "event_id": "ch1_d1_reading_clue"},
                    stakes=[
                        "艾琳已经察觉你读到了异常，但还不知道你准备怎么处理。",
                        "你先安抚、直接说出或继续试探，会改变她的紧张来源。",
                    ],
                    response_options=[
                        _social_response(
                            response_id="calm_before_telling",
                            label="先安抚艾琳：我不会一个人靠近北边",
                            hint="降低她的戒备，再进入线索事件。",
                            result_text="艾琳的肩膀松了一点。她还在担心，但愿意听你把书页上的话说完。",
                            tone="reassure",
                            effects={
                                "flags": {"alice_reassured_before_boundary_record": 1},
                                "relationship": {"alice.trust": 2, "alice.tension": -1},
                                "memory": {
                                    "alice": {
                                        "type": "npc_intent_response",
                                        "summary": "玩家在说出边界记录前先向艾琳保证不会独自冒险。",
                                        "weight": 4,
                                    }
                                },
                            },
                        ),
                        _social_response(
                            response_id="press_for_truth",
                            label="直接问：你是不是早就知道静默线？",
                            hint="推进真相感，但会让她感到被逼问。",
                            result_text="艾琳握紧书脊。她没有否认，只提醒你：有些线索一旦说出口，就会牵动所有人。",
                            tone="pressure",
                            effects={
                                "flags": {"pressed_alice_about_silence_line": 1},
                                "relationship": {"alice.trust": 1, "alice.tension": 2},
                                "memory": {
                                    "alice": {
                                        "type": "npc_intent_response",
                                        "summary": "玩家在书库里直接追问艾琳是否早就知道静默线。",
                                        "weight": 4,
                                    }
                                },
                            },
                        ),
                    ],
                    fallback=(14, 14, "reading_hall"),
                    scene_id="reading_hall",
                    tile_x=14,
                    tile_y=14,
                )
            )

        if _flag(state, "prologue_reading_done") >= 1 and not _done_today(state, "church_ask_alice_lunch"):
            intents.append(
                _intent(
                    state=state,
                    npc_id="alice",
                    intent_id="alice_lunch_basket_choice",
                    kind="npc_prompt",
                    title="艾琳在等你决定午餐篮",
                    description="午餐怎么分，会让她和尤里都看出你更在意什么。",
                    priority=72,
                    reason="用日常选择把关系变化从剧情事件带回生活。",
                    action={"type": "scene_activity", "activity_id": "church_ask_alice_lunch"},
                    stakes=[
                        "午餐不是资源管理，而是两人判断你是否会照顾别人。",
                        "回应艾琳会影响她之后如何解读你的餐桌态度。",
                    ],
                    response_options=[
                        _social_response(
                            response_id="ask_who_needs_more",
                            label="问艾琳：今天谁更需要这份午餐？",
                            hint="把日常选择交给关系判断。",
                            result_text="艾琳看了一眼巨树方向，说尤里不会主动说累，但斧柄上的水迹已经说明很多。",
                            effects={
                                "flags": {"asked_alice_about_lunch_needs": 1},
                                "relationship": {"alice.affinity": 1, "alice.trust": 1},
                                "memory": {
                                    "alice": {
                                        "type": "npc_intent_response",
                                        "summary": "玩家在分午餐前询问艾琳谁更需要照顾。",
                                        "weight": 3,
                                    }
                                },
                            },
                        ),
                    ],
                    fallback=(14, 14, "reading_hall"),
                    scene_id="reading_hall",
                    tile_x=14,
                    tile_y=14,
                )
            )

        if _flag(state, "trained_with_eugeo") < 1 and not _completed(state, "ch1_d1_training_with_eugeo"):
            intents.append(
                _intent(
                    state=state,
                    npc_id="eugeo",
                    intent_id="eugeo_invites_training",
                    kind="npc_invite",
                    title="尤里示意你来巨树旁训练",
                    description="他把训练看成确认世界仍按规则运转的方式，也会听见你对北边的追问。",
                    priority=90,
                    reason="Day 1 必须让尤里用行动邀请玩家，而不是只等事件按钮。",
                    action={"type": "story_event", "event_id": "ch1_d1_training_with_eugeo"},
                    stakes=[
                        "尤里用训练试探你是否能跟上他的节奏。",
                        "回应他的邀约，会影响他把你当作旁观者还是并肩者。",
                    ],
                    response_options=[
                        _social_response(
                            response_id="match_training_rhythm",
                            label="回应尤里：我跟你的节奏来",
                            hint="先建立并肩感，再开始训练。",
                            result_text="尤里点了点头，把第一下挥斧的节奏放慢到你能接住的位置。",
                            tone="bond",
                            effects={
                                "flags": {"eugeo_training_invite_ack": 1},
                                "relationship": {"eugeo.affinity": 2, "eugeo.trust": 1},
                                "memory": {
                                    "eugeo": {
                                        "type": "npc_intent_response",
                                        "summary": "玩家回应尤里的训练邀约，表示愿意按他的节奏来。",
                                        "weight": 3,
                                    }
                                },
                            },
                        ),
                        _social_response(
                            response_id="ask_tree_as_rule",
                            label="问尤里：巨树训练真的能证明规则还在吗？",
                            hint="把日常训练和世界异常连起来。",
                            result_text="尤里的斧头在半空停了一下。他说如果连每天最固定的事都变了，那北边就不只是传闻。",
                            tone="probe",
                            effects={
                                "flags": {"eugeo_tree_rule_questioned": 1},
                                "relationship": {"eugeo.trust": 2, "eugeo.tension": 1},
                                "memory": {
                                    "eugeo": {
                                        "type": "npc_intent_response",
                                        "summary": "玩家把巨树训练和世界规则是否稳定联系起来问尤里。",
                                        "weight": 4,
                                    }
                                },
                            },
                        ),
                    ],
                    fallback=(54, 22, "gigas_clearing"),
                    scene_id="gigas_clearing",
                    tile_x=54,
                    tile_y=22,
                )
            )

    if day == 1 and band in {"evening", "night"} and not _done_today(state, "home_evening_meal"):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_evening_meal_prompt",
                kind="npc_prompt",
                title="炉火边的晚餐还在等你表态",
                description="今天的读书、训练和隐瞒都会在餐桌边变成关系变化。",
                priority=82,
                reason="用晚餐把 Day 1 的关系线收束到日结算前。",
                action={"type": "scene_activity", "activity_id": "home_evening_meal"},
                stakes=[
                    "晚餐会把今天的读书、训练和隐瞒汇总成关系判断。",
                    "先回应艾琳的担心，会改变餐桌选择的情绪底色。",
                ],
                response_options=[
                    _social_response(
                        response_id="name_the_tension",
                        label="先说出口：今天大家都在担心北边",
                        hint="让晚餐分歧变得更坦诚。",
                        result_text="炉火轻轻响了一下。艾琳没有反驳，尤里也没有低头，这让晚餐前的沉默短了一些。",
                        tone="honest",
                        effects={
                            "flags": {"named_evening_boundary_tension": 1},
                            "relationship": {"alice.trust": 1, "eugeo.trust": 1},
                            "memory": {
                                "alice": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家在晚餐前主动说出大家都在担心北边。",
                                    "weight": 3,
                                },
                                "eugeo": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家没有回避晚餐前的紧张，而是先把北边的担心说出口。",
                                    "weight": 3,
                                },
                            },
                        },
                    ),
                ],
                fallback=(11, 27, "home_hearth"),
                scene_id="home_hearth",
                tile_x=11,
                tile_y=27,
            )
        )

    if day == 2 and band in {"morning", "afternoon"} and _flag(state, "clue_boundary_record") >= 1 and _flag(state, "forest_anomaly_seen") < 1:
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_points_to_forest_anomaly",
                kind="npc_concern",
                title="尤里想确认森林忽然安静的原因",
                description="Day 1 留下的线索已经变成现实，他想和你一起去古誓树附近确认。",
                priority=94,
                reason="让 Day 2 的异常从 NPC 行动自然冒出来。",
                action={"type": "story_event", "event_id": "ch1_d2_forest_anomaly"},
                stakes=[
                    "尤里把 Day 1 的线索当成现实异常，而不是普通传闻。",
                    "你是否约定不独自行动，会改变两人对 Day 2 调查的信任。",
                ],
                response_options=[
                    _social_response(
                        response_id="promise_not_alone",
                        label="答应尤里：我们一起确认，不单独越线",
                        hint="把调查推进和安全边界同时说清楚。",
                        result_text="尤里看向古誓树后方，点头很慢。这个承诺让调查像一件可以一起承担的事。",
                        tone="promise",
                        effects={
                            "flags": {"promised_eugeo_not_alone_day2": 1},
                            "relationship": {"eugeo.trust": 3, "alice.tension": -1},
                            "promises": {
                                "eugeo": "玩家在 Day 2 森林异常前答应和尤里一起确认，不单独越线。"
                            },
                            "memory": {
                                "eugeo": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家在森林异常前答应尤里一起确认，不单独越线。",
                                    "weight": 4,
                                }
                            },
                        },
                    ),
                ],
                fallback=(54, 22, "gigas_clearing"),
                scene_id="gigas_clearing",
                tile_x=54,
                tile_y=22,
            )
        )

    if (
        4 <= day <= 6
        and band in {"morning", "afternoon"}
        and _flag(state, "boundary_incident_resolved") >= 1
        and _flag(state, "month01_debrief_done") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_calls_boundary_debrief",
                kind="npc_invite",
                title="艾琳想把边界事件写成记录",
                description="边界前的风声没有随着回村消失。艾琳已经摊开记录本，等你决定这件事该如何留下。",
                priority=92,
                reason="Day 4-6 需要由 NPC 主动把玩家带回书库复盘，而不是只依赖事件列表。",
                action={"type": "story_event", "event_id": "ch1_d4_after_boundary_debrief"},
                stakes=[
                    "这份记录会决定后续巡查是公开、保守，还是继续追查异常源头。",
                    "艾琳在意安全流程，尤里在意异常真相；你的写法会影响两人的判断。",
                ],
                response_options=[
                    _social_response(
                        response_id="promise_complete_record",
                        label="答应艾琳：这次把事实写完整",
                        hint="先稳住记录流程，再进入第四天复盘。",
                        result_text="艾琳把空白页推到你面前，神情放松了一点。她不要求你立刻下结论，只要求你不要再让关键细节消失。",
                        tone="steady",
                        effects={
                            "flags": {"alice_debrief_record_promised": 1},
                            "relationship": {"alice.trust": 2, "eugeo.trust": 1},
                            "memory": {
                                "alice": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家在第四天复盘前答应艾琳，会把边界事件写成完整记录。",
                                    "weight": 4,
                                }
                            },
                        },
                    )
                ],
                fallback=(14, 14, "church_library"),
                scene_id="church_library",
                tile_x=14,
                tile_y=14,
            )
        )

    if (
        5 <= day <= 6
        and band in {"morning", "afternoon"}
        and _flag(state, "month01_debrief_done") >= 1
        and _flag(state, "month01_drill_done") < 1
        and _flag(state, "activity_done.north_gate_drill_walkthrough") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_offers_route_walkthrough",
                kind="npc_invite",
                title="尤里想先走一遍北门退路",
                description="正式演练前还有时间。尤里提议先把撤退点、听风位置和轮换手势走熟，让第七天不是第一次面对这条路线。",
                priority=76,
                reason="Day 5-6 需要一个可选准备活动，把书库复盘连接到第七天北门演练。",
                action={"type": "scene_activity", "activity_id": "north_gate_drill_walkthrough"},
                stakes=[
                    "标撤退点更稳妥，轮换听风更强调三人协作。",
                    "这次选择会写入同伴记忆，并在正式演练前留下准备路线。",
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    if (
        7 <= day <= 10
        and band in {"morning", "afternoon"}
        and _flag(state, "month01_debrief_done") >= 1
        and _flag(state, "month01_drill_done") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_pushes_north_gate_drill",
                kind="npc_prompt",
                title="尤里想把复盘变成北门演练",
                description="复盘已经写下来了，但尤里不想让它停在纸上。他在北门等你，把路线、风声和撤退信号走一遍。",
                priority=90,
                reason="Day 7-10 的第一次北门演练应该由同伴主动提出，形成从记录到行动的过渡。",
                action={"type": "story_event", "event_id": "ch1_d7_first_boundary_drill"},
                stakes=[
                    "演练会决定后续巡查更偏向安全流程，还是更偏向三人协作。",
                    "如果一直拖延，北门异常会停留在记录里，缺少可执行的队伍规则。",
                ],
                response_options=[
                    _social_response(
                        response_id="agree_to_walk_route",
                        label="告诉尤里：先走一遍撤退路线",
                        hint="把主动调查压进安全流程里。",
                        result_text="尤里把斧柄往肩上一搭，点头说先走退路也算前进。北门那边的风声像是在等你们靠近。",
                        tone="promise",
                        effects={
                            "flags": {"eugeo_drill_route_agreed": 1},
                            "relationship": {"eugeo.trust": 2, "alice.trust": 1},
                            "promises": {
                                "eugeo": "玩家在第一次北门演练前答应尤里，先走一遍撤退路线。"
                            },
                            "memory": {
                                "eugeo": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家同意和尤里把北门撤退路线先演练一遍。",
                                    "weight": 4,
                                }
                            },
                        },
                    )
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    if (
        8 <= day <= 11
        and band in {"morning", "afternoon", "evening"}
        and _flag(state, "month01_drill_done") >= 1
        and _flag(state, "month01_village_trust") < 1
        and _flag(state, "activity_done.village_patrol_board_review") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_opens_patrol_board_review",
                kind="npc_invite",
                title="艾琳把空白巡查板放到了广场",
                description="第十二天作出村务决定前，你可以先公开安全流程，或邀请村民补充他们见过的异常。",
                priority=78,
                reason="Day 8-11 需要一个可选村务准备，让日常活动真实进入 Day 12 与 Day 18 的回响。",
                action={"type": "scene_activity", "activity_id": "village_patrol_board_review"},
                stakes=[
                    "公开安全流程会降低艾琳压力。",
                    "邀请村民记录会扩大线索来源，也会提高信息公开带来的紧张。",
                ],
                fallback=(28, 25, "village_square"),
                scene_id="village_square",
                tile_x=28,
                tile_y=25,
            )
        )

    if (
        12 <= day <= 16
        and band in {"morning", "afternoon", "evening"}
        and _flag(state, "month01_drill_done") >= 1
        and _flag(state, "month01_village_trust") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_guides_village_trust",
                kind="npc_invite",
                title="艾琳想把巡查变成村务",
                description="北门演练不能只留在三个人之间。艾琳在村广场整理巡查板，等你决定要公开多少。",
                priority=88,
                reason="Day 12-16 需要 NPC 主动把玩家从小队调查带到村务信任阶段。",
                action={"type": "story_event", "event_id": "ch1_d12_village_trust"},
                stakes=[
                    "公开巡查能提高村内信任，也会让更多人意识到北门异常。",
                    "低调筹备能推进调查，但艾琳会要求你把补给和路线交给她复核。",
                ],
                response_options=[
                    _social_response(
                        response_id="offer_patrol_summary",
                        label="先把北门演练写成村民能看懂的记录",
                        hint="把调查语言转成村务语言。",
                        result_text="艾琳把巡查板上的空格让给你。她说如果村里要一起承担这件事，第一行就不能只写给你们三个人看。",
                        tone="steady",
                        effects={
                            "flags": {"alice_village_board_summary_started": 1},
                            "relationship": {"alice.trust": 2, "eugeo.affinity": 1},
                            "memory": {
                                "alice": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家在村务信任阶段前，答应先把北门演练写成村民能看懂的记录。",
                                    "weight": 4,
                                }
                            },
                        },
                    )
                ],
                fallback=(28, 25, "village_square"),
                scene_id="village_square",
                tile_x=28,
                tile_y=25,
            )
        )

    if (
        13 <= day <= 17
        and band in {"morning", "afternoon"}
        and _flag(state, "month01_village_trust") >= 1
        and _flag(state, "month01_silent_line_rehearsed") < 1
        and _flag(state, "activity_done.north_gate_silent_line_recheck") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_requests_silent_line_recheck",
                kind="npc_concern",
                title="尤里听见静默线又靠近了一次",
                description="正式演练前，尤里想用巡查记录或三人判定先复核一次靠近距离。",
                priority=79,
                reason="Day 13-17 需要一个可选复核活动，把村务信任连接到第十八天静默线演练。",
                action={"type": "scene_activity", "activity_id": "north_gate_silent_line_recheck"},
                stakes=[
                    "按记录校准会让流程更可靠。",
                    "三人共同判定会强化羁绊，并把最终判断交给队伍。",
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    if (
        18 <= day <= 22
        and band in {"morning", "afternoon"}
        and _flag(state, "month01_village_trust") >= 1
        and _flag(state, "month01_silent_line_rehearsed") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_calls_silent_line_rehearsal",
                kind="npc_concern",
                title="尤里想复核静默线",
                description="巡查板已经贴出去，北门的风声却又断了一次。尤里想趁记录还新，把静默线复核成真正的队伍流程。",
                priority=86,
                reason="Day 18-22 需要从村务信任自然推进到静默线演练。",
                action={"type": "story_event", "event_id": "ch1_d18_silent_line_rehearsal"},
                stakes=[
                    "这次复核会决定规则、同伴判断和撤退路线能否同时成立。",
                    "如果复核失败，远征包准备会缺少最关键的安全依据。",
                ],
                response_options=[
                    _social_response(
                        response_id="ask_for_three_person_verdict",
                        label="告诉尤里：这次三个人一起下判定",
                        hint="强化共同复核，而不是让任何一个人独自承担。",
                        result_text="尤里把听风位置重新画了一遍，留下最后一格给艾琳的记录。你们都明白，这次不能靠一个人的直觉。",
                        tone="cooperate",
                        effects={
                            "flags": {"eugeo_three_person_verdict_agreed": 1},
                            "relationship": {"eugeo.trust": 2, "alice.trust": 1},
                            "promises": {
                                "eugeo": "玩家在静默线演练前答应尤里，这次由三个人共同下判定。"
                            },
                            "memory": {
                                "eugeo": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家答应尤里在静默线演练中让三个人共同复核最终判定。",
                                    "weight": 4,
                                }
                            },
                        },
                    )
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    if (
        23 <= day <= 27
        and band in {"evening", "night"}
        and _flag(state, "month01_silent_line_rehearsed") >= 1
        and _flag(state, "month01_expedition_bridge_talk") < 1
        and _flag(state, "month01_expedition_ready") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_sets_expedition_bridge_talk",
                kind="npc_concern",
                title="艾琳想把远征前夜说清楚",
                description="静默线复核结束后，艾琳不想让远征包只剩物品清单。她想在炉火边确认退路、记录本和停步信号。",
                priority=84,
                reason="Day 23-27 需要从静默线演练自然过渡到远征包准备。",
                action={"type": "scene_activity", "activity_id": "home_expedition_bridge_talk"},
                stakes=[
                    "远征前夜会决定第二月远征是带着共同分工出发，还是只靠临时判断。",
                    "如果不先说清楚，远征包准备会缺少情感和安全铺垫。",
                ],
                response_options=[
                    _social_response(
                        response_id="agree_to_hearth_review",
                        label="答应艾琳：先在炉火边把分工过一遍",
                        hint="把远征前的问题从物品清单拉回同伴分工。",
                        result_text="艾琳把记录本放到桌中央。她没有要求你立刻决定路线，只要求每个人先知道谁负责停下。",
                        tone="cautious",
                        effects={
                            "flags": {"alice_expedition_bridge_agreed": 1},
                            "relationship": {"alice.trust": 2, "eugeo.trust": 1},
                            "memory": {
                                "alice": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家答应艾琳先在炉火边确认远征前的退路、记录本和停步信号。",
                                    "weight": 4,
                                }
                            },
                        },
                    )
                ],
                fallback=(11, 27, "home_hearth"),
                scene_id="home_hearth",
                tile_x=11,
                tile_y=27,
            )
        )

    if (
        24 <= day <= 27
        and band in {"morning", "afternoon", "evening"}
        and _flag(state, "month01_silent_line_rehearsed") >= 1
        and _flag(state, "month01_pack_reviewed") < 1
        and _flag(state, "month01_expedition_ready") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_checks_expedition_pack",
                kind="npc_plan",
                title="艾琳要复核远征包",
                description="绳索、记录本和标记粉已经摆在桌上。艾琳想先确认这不是一次冲动出发，而是一套能撤回来的准备。",
                priority=87,
                reason="Day 24-27 需要把远征包从计划文字落实为小屋中的可操作活动。",
                action={"type": "scene_activity", "activity_id": "home_expedition_pack_review"},
                stakes=[
                    "远征包的取舍会影响艾琳对路线安全性的判断。",
                    "这一步会给正式的远征包剧情事件提供清晰的物品和情绪铺垫。",
                ],
                response_options=[
                    _social_response(
                        response_id="start_pack_review",
                        label="让艾琳先检查退路和记录本",
                        hint="偏向稳妥准备，让远征包先变得可靠。",
                        result_text="艾琳没有急着装包，只先把记录本翻到空白页。她说只要退路写清楚，出发就不再只是胆量问题。",
                        tone="steady",
                        effects={
                            "flags": {"alice_pack_review_started": 1},
                            "relationship": {"alice.trust": 2, "alice.tension": -1},
                            "memory": {
                                "alice": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家让艾琳先检查远征包中的退路、记录本和安全标记。",
                                    "weight": 4,
                                }
                            },
                        },
                    )
                ],
                fallback=(11, 27, "home_hearth"),
                scene_id="home_hearth",
                tile_x=11,
                tile_y=27,
            )
        )

    if (
        24 <= day <= 27
        and band in {"morning", "afternoon", "evening"}
        and _flag(state, "month01_expedition_ready") >= 1
        and _flag(state, "month01_village_sendoff_done") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_brings_pack_to_square",
                kind="npc_plan",
                title="尤里想把远征信号留给村里",
                description="远征包已经压好，尤里却停在村道广场边。他想让村里至少知道安全距离和撤退信号，而不是只看着你们离开。",
                priority=82,
                reason="Day 24-27 完成远征包后，需要把准备结果连接到村庄共同记忆。",
                action={"type": "scene_activity", "activity_id": "village_expedition_sendoff"},
                stakes=[
                    "送行活动会把远征从三人秘密扩展成村庄可理解的安全流程。",
                    "如果不做这一步，Day 28-30 的北门前夜会缺少村庄侧反馈。",
                ],
                response_options=[
                    _social_response(
                        response_id="leave_signal_with_square",
                        label="同意尤里：把撤退信号留在广场",
                        hint="让村民知道最少必要的安全信息。",
                        result_text="尤里把手势画在巡查板边缘，没有写下静默线的全部细节。这样够少，也够让人看懂。",
                        tone="open",
                        effects={
                            "flags": {"eugeo_sendoff_signal_agreed": 1},
                            "relationship": {"eugeo.trust": 2, "alice.trust": 1},
                            "memory": {
                                "eugeo": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家同意尤里在村道广场留下远征前的安全距离和撤退信号。",
                                    "weight": 4,
                                }
                            },
                        },
                    )
                ],
                fallback=(28, 25, "village_square"),
                scene_id="village_square",
                tile_x=28,
                tile_y=25,
            )
        )

    if (
        28 <= day <= 30
        and band in {"morning", "afternoon", "evening", "night"}
        and _flag(state, "month01_expedition_ready") >= 1
        and _flag(state, "month01_gate_resolved") < 1
        and _flag(state, "activity_done.north_gate_month_end_vigil") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_marks_month_gate_vigil",
                kind="npc_plan",
                title="艾琳想在北门前复核第一月承诺",
                description="远征包已经准备好，但艾琳没有急着让你选择路线。她把记录本带到北门，想先确认撤退线、村里支持和每个人没说出口的担心。",
                priority=89,
                reason="Day 28-30 的第一月收束需要同伴主动把玩家带入北门仪式，而不是只点击路线选择。",
                action={"type": "scene_activity", "activity_id": "north_gate_month_end_vigil"},
                stakes=[
                    "这一步会把第一月的记录、远征包和村内支持重新汇合到北门场景。",
                    "如果跳过，第二月路线选择会更像普通菜单，缺少告别第一月的情绪重量。",
                ],
                response_options=[
                    _social_response(
                        response_id="agree_to_gate_vigil",
                        label="答应艾琳：先把第一个月复核完",
                        hint="在路线选择前补上记录、撤退线和同伴担心。",
                        result_text="艾琳合上记录本，语气比平时更轻：「那就先确认能回来，再决定要往哪里走。」",
                        tone="steady",
                        effects={
                            "flags": {"alice_gate_vigil_agreed": 1},
                            "relationship": {"alice.trust": 2, "eugeo.trust": 1},
                            "memory": {
                                "alice": {
                                    "type": "npc_intent_response",
                                    "summary": "玩家答应艾琳，在第一月收束路线选择前先到北门复核记录、撤退线和远征承诺。",
                                    "weight": 4,
                                }
                            },
                        },
                    )
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    if (
        day == 32
        and band in {"morning", "afternoon", "evening", "night"}
        and _flag(state, "month02_day31_entry_done") >= 1
        and _flag(state, "month02_route_order") >= 1
        and _flag(state, "activity_done.church_month02_briefing") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_introduces_month02_duty",
                kind="npc_plan",
                title="艾琳在书库等你整理第二月稳守简报",
                description="第二月已经从稳守北门展开。艾琳把记录本摊在书桌上，等你把巡查公开度、补给线和撤退信号整理成村务能执行的第一步。",
                priority=86,
                reason="Day 32 order route should turn the month route flag into a concrete scene action.",
                action={"type": "scene_activity", "activity_id": "church_month02_briefing"},
                stakes=[
                    "这一步会把第二月稳守路线接到村务协同，而不是停留在第一月末的选择结果。",
                    "如果不做，order 路线缺少第一个玩家可执行动作。",
                ],
                response_options=[
                    _social_response(
                        response_id="write_order_briefing",
                        label="和艾琳整理第二月稳守简报",
                        hint="把稳守路线拆成巡查、补给和撤退信号。",
                        result_text="艾琳点头，把空白页留给你写下第二月第一周的执行顺序。",
                        tone="steady",
                        effects={
                            "flags": {"alice_month02_order_briefing_agreed": 1},
                            "relationship": {"alice.trust": 1},
                        },
                    )
                ],
                fallback=(42, 18, "reading_hall"),
                scene_id="reading_hall",
                tile_x=42,
                tile_y=18,
            )
        )

    if (
        day == 32
        and band in {"morning", "afternoon", "evening"}
        and _flag(state, "month02_day31_entry_done") >= 1
        and _flag(state, "month02_route_expedition") >= 1
        and _flag(state, "activity_done.north_gate_expedition_check") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_suggests_month02_expedition",
                kind="npc_plan",
                title="尤里想复核第二月第一段远征线",
                description="第二月远征路线已经定下。尤里带着测距粉在北门等你，想先把第一段路线和撤退标记复核清楚。",
                priority=86,
                reason="Day 32 expedition route should create a concrete north gate follow-up activity.",
                action={"type": "scene_activity", "activity_id": "north_gate_expedition_check"},
                stakes=[
                    "这一步会把远征路线转成可重复的路线复核，而不是直接跳到越界冒险。",
                    "如果不做，expedition 路线缺少安全节拍。",
                ],
                response_options=[
                    _social_response(
                        response_id="walk_expedition_check",
                        label="和尤里复核北门远征路线",
                        hint="先走第一段路线和撤退标记。",
                        result_text="尤里把测距粉递给你，等你确认第一段路线从哪里开始。",
                        tone="cooperate",
                        effects={
                            "flags": {"eugeo_month02_expedition_check_agreed": 1},
                            "relationship": {"eugeo.trust": 1},
                        },
                    )
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    if (
        day == 32
        and band in {"morning", "afternoon", "evening", "night"}
        and _flag(state, "month02_day31_entry_done") >= 1
        and _flag(state, "month02_route_quiet") >= 1
        and _flag(state, "activity_done.reading_hall_silent_record") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_raises_silent_line_recheck",
                kind="npc_plan",
                title="艾琳要求把静默线频率写成记录",
                description="静默观察路线需要先能复查。艾琳在书桌旁等你，把异常频率、风声断点和见证人都写清楚。",
                priority=86,
                reason="Day 32 quiet route should reduce ambiguity with a concrete record activity.",
                action={"type": "scene_activity", "activity_id": "reading_hall_silent_record"},
                stakes=[
                    "这一步会把静默路线从暗线判断转成可复查记录。",
                    "如果不做，quiet 路线容易继续变成信息不对称。",
                ],
                response_options=[
                    _social_response(
                        response_id="write_silent_record",
                        label="和艾琳整理静默线频率",
                        hint="把异常频率、位置和见证人写清楚。",
                        result_text="艾琳没有反驳你的判断，只要求每一次沉默都能被复查。",
                        tone="careful",
                        effects={
                            "flags": {"alice_month02_silent_record_agreed": 1},
                            "relationship": {"alice.trust": 1, "alice.tension": -1},
                        },
                    )
                ],
                fallback=(42, 18, "reading_hall"),
                scene_id="reading_hall",
                tile_x=42,
                tile_y=18,
            )
        )

    if (
        39 <= day <= 45
        and band in {"morning", "afternoon", "evening"}
        and _flag(state, "month02_order_briefing_done") >= 1
        and _flag(state, "activity_done.village_month02_patrol_standby") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_formalizes_month02_patrol_board",
                kind="npc_plan",
                title="艾琳要把第二月巡逻板交给村务执行",
                description=(
                    "第二月入口已经选择公开完整轮值。艾琳在村道广场等你，把新增村民记录、撤退信号和异常上报变成真正能运行的公开巡逻板。"
                    if _flag(state, "month02_order_open_rotation") >= 1
                    else "第二月入口先建立了受训巡逻核心。艾琳在村道广场等你，把固定轮值、撤退信号和分级上报写成不会被传闻冲散的流程。"
                    if _flag(state, "month02_order_trained_core") >= 1
                    else "稳守线已经从书库简报走到中段。艾琳在村道广场等你，把北门巡逻、撤退信号和异常上报整理成村民能照着执行的轮值表。"
                ),
                priority=85,
                reason="Week 06 order route needs a concrete village-operation follow-up after the Day 32 briefing.",
                action={"type": "scene_activity", "activity_id": "village_month02_patrol_standby"},
                stakes=[
                    "这一步会让稳守线从三人的计划变成全村可执行的村务流程。",
                    "如果不做，第二月稳守线会停在简报层，缺少 Day 39-45 的玩家可执行目标。",
                ],
                response_options=[
                    _social_response(
                        response_id="formalize_patrol_board",
                        label="和艾琳把巡逻板交给村务执行",
                        hint="公开轮值、撤退信号和异常上报格式。",
                        result_text="艾琳把轮值栏钉到木牌上，等你确认哪些信号可以公开，哪些只写给巡逻队。",
                        tone="steady",
                        effects={
                            "flags": {"alice_month02_patrol_board_agreed": 1},
                            "relationship": {"alice.trust": 1},
                        },
                    )
                ],
                fallback=(28, 25, "village_square"),
                scene_id="village_square",
                tile_x=28,
                tile_y=25,
            )
        )

    if (
        39 <= day <= 45
        and band in {"morning", "afternoon", "evening"}
        and _flag(state, "month02_expedition_check_done") >= 1
        and _flag(state, "activity_done.north_gate_expedition_supply_review") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_reviews_expedition_supplies",
                kind="npc_plan",
                title="尤吉欧要复核第二月远征补给",
                description=(
                    "第一段远征优先加固了回撤标记。尤吉欧在北门等你，准备按每个撤退点重新分配干粮、标记粉和绳结。"
                    if _flag(state, "month02_expedition_return_markers") >= 1
                    else "第一段远征已经把测距推进到下一个岔路。尤吉欧在北门等你，补足新增距离需要的干粮、标记粉和备用绳结。"
                    if _flag(state, "month02_expedition_range_extended") >= 1
                    else "远征线已经确认第一段路线。尤吉欧在北门等你，把干粮、标记粉、绳结和撤退口令重新点清，避免下一次越界只靠临场判断。"
                ),
                priority=85,
                reason="Week 06 expedition route needs a supply review after the Day 32 route confirmation.",
                action={"type": "scene_activity", "activity_id": "north_gate_expedition_supply_review"},
                stakes=[
                    "这一步会让远征线从路线复核进入补给确认，降低后续越界行动的风险。",
                    "如果不做，远征线缺少 Day 39-45 的准备节奏，容易直接跳到高风险探索。",
                ],
                response_options=[
                    _social_response(
                        response_id="confirm_supply_list",
                        label="和尤吉欧复核远征补给",
                        hint="点清干粮、标记粉、绳结和撤退口令。",
                        result_text="尤吉欧把补给袋打开，等你决定哪些东西必须带，哪些东西只会拖慢撤退。",
                        tone="cooperate",
                        effects={
                            "flags": {"eugeo_month02_supply_review_agreed": 1},
                            "relationship": {"eugeo.trust": 1},
                        },
                    )
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    if (
        39 <= day <= 45
        and band in {"morning", "afternoon", "evening", "night"}
        and _flag(state, "month02_quiet_record_done") >= 1
        and _flag(state, "activity_done.reading_hall_quiet_frequency_crosscheck") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_conducts_quiet_frequency_crosscheck",
                kind="npc_plan",
                title="艾琳要复核静默线频率的第二周数据",
                description=(
                    "第一周已经补全见证人链。艾琳在书桌等你，把第二周的新断点逐条对回时间、位置和见证人，确认是否有人看见同一个方向。"
                    if _flag(state, "month02_quiet_witness_chain") >= 1
                    else "第一周优先隔离了重复信号模式。艾琳在书桌等你，确认第二周是否再次出现相同时段和风声断点。"
                    if _flag(state, "month02_quiet_signal_pattern") >= 1
                    else "上次整理的频率记录已经过了一周。艾琳在书桌等你，把新见到的风声断点与第一周记录对照，确认异常是在靠近还是在漂移。"
                ),
                priority=85,
                reason="Week 06 quiet route needs a frequency crosscheck after the Day 32 record.",
                action={"type": "scene_activity", "activity_id": "reading_hall_quiet_frequency_crosscheck"},
                stakes=[
                    "这一步会把静默线从单周记录推进到两周对比。",
                    "如果不做，静默线缺少 Day 39-45 的可执行目标，后续判断会继续停在猜测层。",
                ],
                response_options=[
                    _social_response(
                        response_id="crosscheck_frequency_table",
                        label="和艾琳复核两周频率记录",
                        hint="对比风声断点、时间带和见证人。",
                        result_text="艾琳把两页记录并排摊开，等你把新的静默点标到上一周频率表旁边。",
                        tone="careful",
                        effects={
                            "flags": {"alice_month02_quiet_crosscheck_agreed": 1},
                            "relationship": {"alice.trust": 1, "alice.tension": -1},
                        },
                    )
                ],
                fallback=(42, 18, "reading_hall"),
                scene_id="reading_hall",
                tile_x=42,
                tile_y=18,
            )
        )

    if (
        46 <= day <= 52
        and band in {"morning", "afternoon", "evening", "night"}
        and _any_flag(
            state,
            [
                "month02_order_patrol_standby_done",
                "month02_expedition_supply_review_done",
                "month02_quiet_frequency_crosscheck_done",
            ],
        )
        and _flag(state, "activity_done.boundary_anomaly_convergence") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_calls_anomaly_convergence",
                kind="npc_plan",
                title="艾琳要把三条路线的异常信号合到同一张记录上",
                description="第二月中段的发现开始指向同一个方向。艾琳在书库等你，把村务报告、远征补给和静默频率表并排核对，确认异常是否正在靠近北门。",
                priority=87,
                reason="Week 07 needs a shared convergence objective after any Week 06 route slice is completed.",
                action={"type": "scene_activity", "activity_id": "boundary_anomaly_convergence"},
                stakes=[
                    "这一步会把三条路线从平行推进收束到同一个边境异常核心。",
                    "如果不做，第二月 Week 07 会缺少玩家可执行的共同目标。",
                ],
                response_options=[
                    _social_response(
                        response_id="compare_route_records",
                        label="和艾琳核对三条路线的异常信号",
                        hint="把村务、远征和静默记录放到同一张表里。",
                        result_text="艾琳把三份记录推到桌面中央，等你指出哪些信号其实来自同一个方向。",
                        tone="careful",
                        effects={
                            "flags": {"alice_month02_convergence_agreed": 1},
                            "relationship": {"alice.trust": 1},
                        },
                    )
                ],
                fallback=(42, 18, "reading_hall"),
                scene_id="reading_hall",
                tile_x=42,
                tile_y=18,
            )
        )

    if (
        47 <= day <= 52
        and band in {"morning", "afternoon", "evening"}
        and _flag(state, "month02_shared_map_published") >= 1
        and _flag(state, "activity_done.village_shared_map_hearing") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_hosts_shared_map_hearing",
                kind="npc_plan",
                title="爱丽丝要把共同异常地图带到村道广场",
                description="共同异常地图已经公开，但爱丽丝不想让传闻替代证据。她请你到村道广场，决定先收集村民亲历，还是先审核证据簿的公开口径。",
                priority=88,
                reason="The public-map route needs a playable Day 47-52 follow-up before the Day 53 result.",
                action={"type": "scene_activity", "activity_id": "village_shared_map_hearing"},
                stakes=[
                    "这一步会决定正式听证更依赖村民证词，还是更严格的证据口径。",
                    "Day 49 会阻止玩家跳过这项公开地图后续行动。",
                ],
                response_options=[
                    _social_response(
                        response_id="bring_map_to_square",
                        label="和爱丽丝把共同地图带到广场",
                        hint="主持一次可复查的听证准备，而不是直接宣布源头答案。",
                        result_text="爱丽丝卷起地图，先提醒你：要让每个人说清自己亲眼看见了什么。",
                        tone="open",
                        effects={
                            "flags": {"alice_shared_map_hearing_agreed": 1},
                            "relationship": {"alice.trust": 1},
                        },
                    )
                ],
                fallback=(28, 25, "village_square"),
                scene_id="village_square",
                tile_x=28,
                tile_y=25,
            )
        )

    if (
        47 <= day <= 52
        and band in {"morning", "afternoon", "evening"}
        and _flag(state, "month02_source_held_by_team") >= 1
        and _flag(state, "activity_done.north_gate_team_source_probe") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_prepares_team_source_probe",
                kind="npc_plan",
                title="尤吉欧在北门排好三人试探的回撤标记",
                description="异常源头仍留在三人记录里。尤吉欧想再验证一枚刻印的方向，爱丽丝则带来了可随时交给村务的密封副本。",
                priority=88,
                reason="The held-source route needs a playable Day 47-52 follow-up before the Day 53 result.",
                action={"type": "scene_activity", "activity_id": "north_gate_team_source_probe"},
                stakes=[
                    "继续推进会更接近源头，但增加同伴压力。",
                    "先完成密封副本会降低失联风险，并兑现对爱丽丝的承诺。",
                ],
                response_options=[
                    _social_response(
                        response_id="meet_at_north_gate_probe",
                        label="和尤吉欧在北门确认试探节拍",
                        hint="在继续推进与先封存副本之间作出明确选择。",
                        result_text="尤吉欧把绳标递给你，等三个人都确认停步信号后才准备越过北门。",
                        tone="careful",
                        effects={
                            "flags": {"eugeo_team_source_probe_agreed": 1},
                            "relationship": {"eugeo.trust": 1, "alice.trust": 1},
                        },
                    )
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    if (
        day == 53
        and band in {"morning", "afternoon", "evening", "night"}
        and _any_flag(state, ["month02_shared_map_hearing_done", "month02_team_source_probe_done"])
        and _flag(state, "month02_second_month_result_done") < 1
    ):
        public_route = _flag(state, "month02_shared_map_hearing_done") >= 1
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_calls_second_month_result",
                kind="story_event",
                title="爱丽丝请你在书库写下第二月的答案",
                description=(
                    "共同地图已经经过村务听证准备。爱丽丝在书库等你决定：举行正式边界听证，还是只公开警告与退路。"
                    if public_route
                    else "三人源头试探已经留下回撤线与可交代的记录。爱丽丝在书库等你决定：继续三人追查，还是先交出密封副本。"
                ),
                priority=92,
                reason="Day 53 must surface the route-specific second-month result as a clear authored event.",
                action={"type": "story_event", "event_id": "ch1_d53_second_month_result"},
                stakes=[
                    "选择会写入第三月路线入口。",
                    "关系、紧张、承诺和长期记忆会根据第二月结果结算。",
                ],
                response_options=[
                    _social_response(
                        response_id="review_second_month_result",
                        label="和爱丽丝复核第二月结果",
                        hint="进入只显示当前路线结果的第五十三天事件。",
                        result_text="爱丽丝把两页空白分别留给公开边界与源头追查，等你写下真正要承担的那一页。",
                        tone="steady",
                        effects={
                            "flags": {"alice_second_month_result_agreed": 1},
                            "relationship": {"alice.trust": 1},
                        },
                    )
                ],
                fallback=(42, 18, "reading_hall"),
                scene_id="reading_hall",
                tile_x=42,
                tile_y=18,
            )
        )

    tail_routes = [
        {
            "required_flag": "month02_result_formal_hearing",
            "done_flag": "activity_done.village_formal_hearing_followthrough",
            "npc_id": "alice",
            "intent_id": "alice_lands_formal_hearing_rules",
            "title": "爱丽丝要把正式听证写成可轮值的村务规则",
            "description": "听证已经给出公开方向，但村民还需要知道谁记录、谁复核、谁发出撤退信号。爱丽丝把空白轮值板带到广场，等你决定建立双人复核还是说明小队。",
            "activity_id": "village_formal_hearing_followthrough",
            "scene_id": "village_square",
            "tile_x": 28,
            "tile_y": 25,
            "response_id": "land_formal_hearing_rules",
            "response_label": "和爱丽丝把听证规则落到轮值板",
            "response_hint": "让公开决定变成三人不在场时也能执行的村务。",
            "response_text": "爱丽丝把听证簿和轮值板并排放好，等你决定先训练记录人还是说明员。",
        },
        {
            "required_flag": "month02_result_warning_only",
            "done_flag": "activity_done.village_warning_route_drill",
            "npc_id": "eugeo",
            "intent_id": "eugeo_drills_guarded_warning_route",
            "title": "尤吉欧想验证只公开警告是否真的够用",
            "description": "村里知道异常时段和退路，却不知道未经确认的源头。尤吉欧请你到广场，选择演练三段钟声或可移动路线卡，确认克制的信息也能保护人。",
            "activity_id": "village_warning_route_drill",
            "scene_id": "village_square",
            "tile_x": 28,
            "tile_y": 25,
            "response_id": "drill_guarded_warning",
            "response_label": "和尤吉欧演练分层警告",
            "response_hint": "不公布源头答案，也要让村民知道下一步。",
            "response_text": "尤吉欧先敲了一次集合信号，等你决定接下来用固定钟声还是移动路线卡。",
        },
        {
            "required_flag": "month02_result_team_probe_continues",
            "done_flag": "activity_done.north_gate_source_pursuit_calibration",
            "npc_id": "eugeo",
            "intent_id": "eugeo_calibrates_source_pursuit",
            "title": "尤吉欧要在第三月前校准源头追查节拍",
            "description": "三人暗线会继续，但下一段不能只靠勇气。尤吉欧在北门等你验证回撤标记，爱丽丝则要求完整演练一次失联与中止协议。",
            "activity_id": "north_gate_source_pursuit_calibration",
            "scene_id": "north_gate",
            "tile_x": 67,
            "tile_y": 24,
            "response_id": "calibrate_source_pursuit",
            "response_label": "和尤吉欧校准第三月追查节拍",
            "response_hint": "在主动推进与完整中止协议之间决定优先级。",
            "response_text": "尤吉欧把下一枚回撤标记和中止协议放在一起，等三个人都确认后才开始。",
        },
        {
            "required_flag": "month02_result_sealed_copy_handed_over",
            "done_flag": "activity_done.reading_hall_sealed_copy_protocol",
            "npc_id": "alice",
            "intent_id": "alice_writes_sealed_copy_protocol",
            "title": "爱丽丝要把密封副本的开启条件写清",
            "description": "密封副本已经交出，但托管人、开启条件和通知顺序仍需落成协议。爱丽丝在书库等你选择双人托管，或由她保管一把受审计的钥匙。",
            "activity_id": "reading_hall_sealed_copy_protocol",
            "scene_id": "reading_hall",
            "tile_x": 42,
            "tile_y": 18,
            "response_id": "write_sealed_copy_protocol",
            "response_label": "和爱丽丝写下密封副本协议",
            "response_hint": "让暗线信息的每次开启都有责任边界。",
            "response_text": "爱丽丝把木匣放到桌面中央，只在外页写下三个问题：谁保管、何时打开、先通知谁。",
        },
    ]
    if 54 <= day <= 60 and band in {"morning", "afternoon", "evening", "night"}:
        for route in tail_routes:
            if _flag(state, route["required_flag"]) < 1 or _flag(state, route["done_flag"]) >= 1:
                continue
            intents.append(
                _intent(
                    state=state,
                    npc_id=route["npc_id"],
                    intent_id=route["intent_id"],
                    kind="npc_plan",
                    title=route["title"],
                    description=route["description"],
                    priority=89,
                    reason="Day 54-60 must make the selected Day 53 result playable before the third-month bridge.",
                    action={"type": "scene_activity", "activity_id": route["activity_id"]},
                    stakes=[
                        "这一步会把第二月结果变成可执行规则，而不只是月末文本。",
                        "Day 58 会阻止玩家跳过对应尾声活动。",
                    ],
                    response_options=[
                        _social_response(
                            response_id=route["response_id"],
                            label=route["response_label"],
                            hint=route["response_hint"],
                            result_text=route["response_text"],
                            tone="steady",
                            effects={
                                "flags": {f"{route['intent_id']}_agreed": 1},
                                "relationship": {f"{route['npc_id']}.trust": 1},
                            },
                        )
                    ],
                    fallback=(route["tile_x"], route["tile_y"], route["scene_id"]),
                    scene_id=route["scene_id"],
                    tile_x=route["tile_x"],
                    tile_y=route["tile_y"],
                )
            )

    if (
        day == 61
        and band in {"morning", "afternoon", "evening", "night"}
        and _flag(state, "month02_tail_feedback_done") >= 1
        and _flag(state, "month03_departure_ready") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="alice",
                intent_id="alice_calls_third_month_departure",
                kind="story_event",
                title="爱丽丝和尤吉欧在北门等你写下第三月准则",
                description="第二月结果已经真正落地。两名同伴把轮值板、路线卡、回撤标记或密封协议带到北门，等你决定第三月第一条行动准则。",
                priority=94,
                reason="Day 61 needs a visible route-specific bridge into the third month.",
                action={"type": "story_event", "event_id": "ch1_d61_third_month_departure"},
                stakes=[
                    "事件只显示当前第二月结果对应的两个第三月入口。",
                    "选择会写入第三月路线、关系、承诺和长期记忆。",
                ],
                response_options=[
                    _social_response(
                        response_id="review_third_month_departure",
                        label="和两名同伴复核第三月出发准则",
                        hint="进入第六十一天路线专属选择。",
                        result_text="爱丽丝摊开记录，尤吉欧按住路线标记，等你写下第三月真正要承担的第一步。",
                        tone="steady",
                        effects={
                            "flags": {"third_month_departure_review_agreed": 1},
                            "relationship": {"alice.trust": 1, "eugeo.trust": 1},
                        },
                    )
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    month03_families = [
        {
            "route_flags": [
                "month03_public_council_trial",
                "month03_public_scout_assembly",
                "month03_warning_bell_network",
                "month03_mobile_watch_route",
            ],
            "done_flag": "activity_done.village_third_month_support_allocation",
            "npc_id": "alice",
            "intent_id": "alice_allocates_third_month_support",
            "title": "爱丽丝要你决定第三月第一次行动的资源投入",
            "description": "公开议事、侦察说明、警告钟和移动守望都需要真实资源。爱丽丝把村务板带到广场，等你在人力轮值和神圣术信号之间分配体力与神圣力。",
            "activity_id": "village_third_month_support_allocation",
            "scene_id": "village_square",
            "tile_x": 28,
            "tile_y": 25,
            "label": "和爱丽丝分配村务支持",
            "hint": "在人力投入与神圣术信号之间选择真实资源代价。",
        },
        {
            "route_flags": ["month03_source_depart_dawn", "month03_source_wait_for_signal"],
            "done_flag": "activity_done.north_gate_third_month_expedition_loading",
            "npc_id": "eugeo",
            "intent_id": "eugeo_loads_third_month_expedition",
            "title": "尤吉欧在北门等你分配第三月追查负载",
            "description": "第一次源头行动不能同时拥有最重的回撤补给和最多的远距刻印。尤吉欧请你在高体力负载与高神圣力消耗之间选择。",
            "activity_id": "north_gate_third_month_expedition_loading",
            "scene_id": "north_gate",
            "tile_x": 67,
            "tile_y": 24,
            "label": "和尤吉欧分配边境负载",
            "hint": "在完整回撤补给与远距刻印之间选择。",
        },
        {
            "route_flags": ["month03_shared_custody_record", "month03_alice_custody_key"],
            "done_flag": "activity_done.reading_hall_third_month_intelligence_budget",
            "npc_id": "alice",
            "intent_id": "alice_budgets_third_month_intelligence",
            "title": "爱丽丝要把第三月情报托管写进资源预算",
            "description": "密封副本已经有责任边界，但多重校验会消耗神圣力，轻量托管又会增加人为风险。爱丽丝在书库等你决定第一次情报预算。",
            "activity_id": "reading_hall_third_month_intelligence_budget",
            "scene_id": "reading_hall",
            "tile_x": 42,
            "tile_y": 18,
            "label": "和爱丽丝决定情报托管预算",
            "hint": "在多重审计与轻量托管之间权衡可靠性和资源。",
        },
    ]
    if 62 <= day <= 68 and band in {"morning", "afternoon", "evening", "night"}:
        for family in month03_families:
            if not _any_flag(state, family["route_flags"]) or _flag(state, family["done_flag"]) >= 1:
                continue
            intents.append(
                _intent(
                    state=state,
                    npc_id=family["npc_id"],
                    intent_id=family["intent_id"],
                    kind="npc_plan",
                    title=family["title"],
                    description=family["description"],
                    priority=91,
                    reason="Day 62-68 must turn the third-month route into a real stamina/MP resource decision.",
                    action={"type": "scene_activity", "activity_id": family["activity_id"]},
                    stakes=[
                        "不同做法会真实扣除体力和神圣力。",
                        "Day 69 路线测试只显示所选资源方法对应的两个结果。",
                    ],
                    response_options=[
                        _social_response(
                            response_id=f"review_{family['intent_id']}",
                            label=family["label"],
                            hint=family["hint"],
                            result_text="同伴把资源清单和行动目标放在一起，等待你确认这次真正愿意花掉什么。",
                            tone="careful",
                            effects={
                                "flags": {f"{family['intent_id']}_agreed": 1},
                                "relationship": {f"{family['npc_id']}.trust": 1},
                            },
                        )
                    ],
                    fallback=(family["tile_x"], family["tile_y"], family["scene_id"]),
                    scene_id=family["scene_id"],
                    tile_x=family["tile_x"],
                    tile_y=family["tile_y"],
                )
            )

    if (
        69 <= day <= 74
        and band in {"morning", "afternoon", "evening", "night"}
        and _flag(state, "month03_preparation_done") >= 1
        and _flag(state, "month03_route_test_done") < 1
    ):
        intents.append(
            _intent(
                state=state,
                npc_id="eugeo",
                intent_id="eugeo_calls_first_third_month_test",
                kind="story_event",
                title="尤吉欧请你把第一次资源投入带到北门测试",
                description="人力、神圣力、回撤补给或审计封印已经准备好。尤吉欧在北门等你决定扩大成果，还是保留后备并接受较小范围。",
                priority=95,
                reason="Day 69-74 must close the first third-month resource loop with a route-specific authored result.",
                action={"type": "story_event", "event_id": "ch1_d69_third_month_route_test"},
                stakes=[
                    "事件只显示当前资源方法对应的两个选择。",
                    "结果会写入关系、长期记忆，并可能留下承诺或紧张点。",
                ],
                response_options=[
                    _social_response(
                        response_id="review_first_third_month_test",
                        label="和尤吉欧复核第一次路线测试",
                        hint="把已投入资源用于真实边界行动。",
                        result_text="尤吉欧把准备清单折到只剩两种可执行结果，等你决定扩大成果还是保留后备。",
                        tone="steady",
                        effects={
                            "flags": {"third_month_route_test_review_agreed": 1},
                            "relationship": {"eugeo.trust": 1, "alice.trust": 1},
                        },
                    )
                ],
                fallback=(67, 24, "north_gate"),
                scene_id="north_gate",
                tile_x=67,
                tile_y=24,
            )
        )

    return sorted(intents, key=lambda item: (-int(item.priority), item.id))


def attach_npc_intents(project_root: Path, state: WorldState) -> WorldState:
    return state.model_copy(update={"npc_intents": build_npc_intents(project_root, state)})
