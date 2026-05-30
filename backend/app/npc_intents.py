from __future__ import annotations

from pathlib import Path

from .models import AgentState, NpcIntent, WorldState


def _flag(state: WorldState, key: str) -> int:
    return int((state.flags or {}).get(key, 0))


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
                fallback=(14, 14, "reading_hall"),
                scene_id="reading_hall",
                tile_x=14,
                tile_y=14,
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
                title="艾丽丝要把第二月巡逻板交给村务执行",
                description="稳守线已经从书库简报走到中段。艾丽丝在村道广场等你，把北门巡逻、撤退信号和异常上报整理成村民能照着执行的轮值表。",
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
                        label="和艾丽丝把巡逻板交给村务执行",
                        hint="公开轮值、撤退信号和异常上报格式。",
                        result_text="艾丽丝把轮值栏钉到木牌上，等你确认哪些信号可以公开，哪些只写给巡逻队。",
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
                description="远征线已经确认第一段路线。尤吉欧在北门等你，把干粮、标记粉、绳结和撤退口令重新点清，避免下一次越界只靠临场判断。",
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
                title="艾丽丝要复核静默线频率的第二周数据",
                description="上次整理的频率记录已经过了一周。艾丽丝在书桌等你，把新见到的风声断点与第一周记录对照，确认异常是在靠近还是在漂移。",
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
                        label="和艾丽丝复核两周频率记录",
                        hint="对比风声断点、时间带和见证人。",
                        result_text="艾丽丝把两页记录并排摊开，等你把新的静默点标到上一周频率表旁边。",
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

    return sorted(intents, key=lambda item: (-int(item.priority), item.id))


def attach_npc_intents(project_root: Path, state: WorldState) -> WorldState:
    return state.model_copy(update={"npc_intents": build_npc_intents(project_root, state)})
