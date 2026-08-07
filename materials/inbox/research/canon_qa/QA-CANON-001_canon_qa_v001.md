# QA-CANON-001 — Pre-Capture 正典连续性验收包

- request_id: QA-CANON-001
- creator/source: Mavis 叙事智能体（基于 `NAR-CANON-001`、`NAR-PRECAP-001`、`WORLD-MACRO-001`、`WORLD-MICRO-001`、`CHAR-DEPTH-001`、`NAR-ADAPT-001`、`NAR-VOICE-001` 与 `materials/10_CANON_CONTINUITY_CHECKLIST.md` / `11_PRECAPTURE_EXECUTION_BRIEF.md`）
- created_at: 2026-08-06
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/
- edits: none
- intended_use: QA 校验器 / 内容校验器 / 真人盲测评审 共用的连续性验收；任何在 `data/story/events_chapter_01.json` 新增 authored 事件前必须先过本文件
- notes: 本文件**不**修改 `data/story/`、`backend/`、`frontend/`；只给"检查表 + 验收标准"层。"必须等待用户素材确认"项已在本文件 §6 单独列出。

---

## 0. 范围

- 覆盖：`NAR-PRECAP-001` N01–N10 全部 10 个 key node。
- 范围：卢利特村 + 尽头山脉；不覆盖 Centoria / 中央大教堂内部 / 整合骑士训练 / 暗黑界 / War of Underworld。
- 验收对象：未来接入 `data/story/events_chapter_01.json` 的 `ch1pc_*` 事件，以及 AI agent 在 scripted / hybrid / agent 模式下的输出。

## 1. 角色年龄 / 阶段检查

| 角色 | 项目阶段 | 官方原作阶段 | 一致性 | 来源 |
|---|---|---|---|---|
| Alice | 童年 / 少年 | 童年（Ep.1–2）/ 已被带走（Ep.3） | ✅ 一致 | https://sao-alicization.com/1st/character/ |
| Eugeo | 童年 / 少年 | 童年（Ep.1–2） | ✅ 一致 | https://sao-alicization.com/1st/character/ |
| 见习记录员 | 童年 / 少年 | 童年（Ep.1–2） | ✅ 一致 | https://sao-alicization.com/1st/character/ |
| Selka | 童年 / 少年 | 童年（Ep.3） | ✅ 一致 | https://sao-alicization.com/1st/character/ |
| 整合骑士（Deusolbert） | "远方来人" | 整合骑士第 7 位 | ✅ 一致（**不展示 Synthesis 编号**） | https://sao-alicization.com/1st/character/ |

> **不出现**：Alice Synthesis Thirty、Eugeo Synthesis Thirty-Two、Fanatio Synthesis Two、Bercouli Synthesis One、Cardinal、Administrator 的任何具体形态 / 编号 / 行动。

## 2. 地点检查

| 地点 | 项目用名 | 官方名 | 一致性 | 来源 |
|---|---|---|---|---|
| 卢利特村 | 卢利特村 | Rulid Village | ✅ | https://sao-alicization.com/1st/story/01.html |
| 巨神树（基加斯西达） | 巨神树 / 基加斯西达 | Gigas Cedar | ✅ | https://sao-alicization.com/1st/story/01.html |
| 巨神树伐木场 | 巨神树伐木场 | (未在官方原作文本中单独命名) | ⚠️ 项目原创 | `uwCanonText.js` |
| 教会书库 | 教会书库 | (未在官方原作文本中单独命名) | ⚠️ 项目原创 | `uwCanonText.js` |
| 教会回廊 | 教会回廊 | (未在官方原作文本中单独命名) | ⚠️ 项目原创 | `uwCanonText.js` |
| 北门 | 北门 | (未在官方原作文本中单独命名) | ⚠️ 项目原创 | `uwCanonText.js` |
| 尽头山脉 | 尽头山脉 | End Mountains | ✅ | https://sao-alicization.com/1st/story/01.html |
| 北方洞窟 | 北方洞窟 | North Cave | ✅（**不进入**，仅作"远方的传说"） | https://sao-alicization.com/1st/story/03.html |
| 静默线 | 静默线 | (无官方对应) | ⚠️ 项目原创 | `NAR-VOICE-001` §0.4 边界判定 |
| Centoria | Centoria | Cenotria / Centoria | ✅（**仅作远景**） | https://sao-alicization.com/1st/character/ ; https://sao-alicization.com/1st/story/03.html |
| 中央大教堂 | 中央大教堂 | Central Cathedral | ✅（**仅作远景**） | https://sao-alicization.com/1st/character/ |
| 暗黑界 | 暗黑界 | Dark Territory | ✅（**仅作"尽头山脉外侧"敬畏提及**） | https://sao-alicization.com/1st/character/ |

> **检查项**：任何新增地点若不属于上表，必须先在 `WORLD-MICRO-001` / `WORLD-MACRO-001` 增补"官方固定 vs 项目原创"标注；不直接进 `data/story/`。

## 3. 时间 / 日期检查

| 检查项 | 期望 | 来源 |
|---|---|---|
| Pre-Capture 起点日期 | Day 1 上午 | `NAR-PRECAP-001` N01 |
| Pre-Capture 终点日期 | Day 4 中午 | `NAR-PRECAP-001` N10 |
| 事件总时长 | 约 96 小时游戏内时间 | `NAR-ADAPT-001` §7.1 |
| 实际游玩时长目标 | 15–25 分钟 | `NEXT_PHASE.md` P0 |
| 玩家是否可独立跳日 | 否（仅由 authored 事件 + 日结算闸推进） | `CURRENT_STATUS.md` 2026-08-05 日期推进调整 |
| 是否在 N10 之后继续推进日期 | 否（终点收束） | `NAR-PRECAP-001` §0 |

> **检查项**：N01 触发的 `d1_follow_target` flag 必须在 Day 1 上午内可写；N05 必须在 Day 2 下午可触发；N06 必须在 Day 2 夜可触发；N07 必须在 Day 3 傍晚可触发；N09 / N10 必须在 Day 4 可触发。任何超出该窗口的 `trigger.day_min` / `day_max` 视为不合格。

## 4. 术语检查

> 所有玩家面向文本必须过 `frontend/src/utils/uwCanonText.js` 与 `NAR-VOICE-001` §0.2 术语表。

| 旧译名（废弃） | 必须写成 | 来源 |
|---|---|---|
| 露茵村 | 卢利特村 | `uwCanonText.js` |
| 艾琳 | 爱丽丝 | `uwCanonText.js` / `characters/meta.json` |
| 尤里 / 悠吉欧 | 尤吉欧 | `uwCanonText.js` / `characters/meta.json` |
| 凛斗 | 见习记录员 | `uwCanonText.js` / `NAR-VOICE-001` §0.3 |
| 古誓树 | 巨神树 | `uwCanonText.js` |
| 古誓树清场 / 巨神树清场 | 巨神树伐木场 | `uwCanonText.js` |
| 北境律令 | 禁忌目录 | `uwCanonText.js` |
| 刻印术 | 神圣术 | `uwCanonText.js` |
| 村西书库 | 教会书库 | `uwCanonText.js` |
| 村西书道 | 教会回廊 | `uwCanonText.js` |
| 莉娜 | 赛尔卡 | `NAR-VOICE-001` §0.3 / §6.3 遗留项 B |
| 塞鲁卡 | 赛尔卡 | `NAR-VOICE-001` §0.3 / §6.3 遗留项 A |

> **检查项**：QA 工具（`backend/app/content_validator.py` 的 `precapture_legacy_term`）已内置上述映射；任何新写文本若触发该错误码，必须替换为规范译名。

## 5. 事件顺序 / 节点前置 / 后续回响

### 5.1 前置条件（trigger / required_flags / forbidden_flags）

| 节点 | 前置 flag（至少 1 个） | 后续回响（读端） |
|---|---|---|
| N01 | 无（Day 1 上午首次） | N05 读 `d1_follow_target` |
| N02 | 无（与 N01 互斥或不互斥，按 `trained_with_eugeo_day1`） | N04 间接读 `eugeo_mentioned_north_tool` |
| N03 | 无（Day 1 傍晚） | N07 读 `dinner_sided` |
| N04 | 无（Day 2 上午） | N07 读 `book14_5_recorded` |
| N05 | 至少 1 个：N01 / N02 / N03 的 `d*_*` flag（**项目约束**："静默线第一证据"不应是"孤立事件"） | N09 读 `silent_line_marker` |
| N06 | `silent_line_marker ∈ {pressed, kept}`（**项目约束**：N06 不应早于静默线第一证据） | N10 读 `d2_reported_to` |
| N07 | `dinner_sided` 必填 | N08 读 `d3_plan` |
| N08 | `d3_plan` 必填 | N09 / N10 读 `pack_*` / `set_retreat` / `tell_garret_truth` |
| N09 | `d3_plan` 必填 + `pack_*` 至少 1 个 | N10 读 `d4_entrance` |
| N10 | `d4_entrance` 必填 | （**终点**） |

### 5.2 后续回响汇总（与 `NAR-PRECAP-001` §2 一致）

- E1: `d1_follow_target` → N05
- E2: `book14_5_recorded` → N07
- E3: `d2_reported_to` → N10
- E4: `silent_line_marker` → N09
- E5: `dinner_sided` → N07

> 跨节点回响总数 = **5**（≥3），验收通过。

### 5.3 关键 flag 不变量

- `precapture_endpoint: alice_captured` 在 N10 唯一存在；其他节点**不得**写该 marker。
- `effects.ending_id` 仅 N10 写 `alice_captured`（或 `precapture_alice_captured`）；其他节点**不得**写 `ending_id`。
- 任何 `effects.ending_id` 值不属于 `{alice_captured, precapture_alice_captured}` 时，QA 工具（`backend/app/content_validator.py` `precapture_endpoint_marker_must_match_choice_ending`）会报错。

## 6. 抓捕终点验收标准

| 标准 | 期望 | 验证方式 |
|---|---|---|
| `precapture_endpoint` 唯一性 | N10 是唯一含该 marker 的事件 | `check_precapture_readiness.py` `_story_report()` |
| `precapture_endpoint` 是最后一个被标记的 key node | N10 是 `marked_event_ids` 列表的最后一项 | 同上 |
| `effects.ending_id` 与 marker 一致 | N10 至少一个 choice 写 `ending_id = alice_captured` 或 `precapture_alice_captured` | 同上 |
| 标记节点数 ∈ [8, 12] | N01–N10 = 10 | 同上 |
| Act 覆盖 | `act_0` / `act_1` / `act_2` / `act_3` 全部存在 | 同上 |
| 跨节点回响 ≥ 3 | E1–E5 = 5 | 同上 |
| AI 越权边界 | AI 不写 `effects.ending_id`、不写 `precapture_*` 标记 | `backend/app/agent_budget.py` + `AI_NPC_BOUNDARY.md` |
| 玩家面向文本术语 | 过 `uwCanonText()` 与 `NAR-VOICE-001` §0.2 术语表 | `backend/app/content_validator.py` `precapture_legacy_term` |
| 剧透护栏 | 不出现 Alice Synthesis 编号 / 整合骑士神器 / 现实世界关键词 | `backend/app/content_validator.py` `precapture_spoiler_term` |

## 7. 矛盾 / 风险 / 待裁决事项

### 7.1 已识别的内部矛盾（**项目内自检**）

| 序 | 矛盾 | 影响 | 处置 |
|---|---|---|---|
| M1 | 旧译名（露茵村 / 艾琳 / 尤里 / 凛斗 / 古誓树 / 北境律令 / 刻印术 / 村西书库）仍出现在 `data/story/events_chapter_01.json` 等老文件中 | 玩家面向文本可能被错误渲染 | `uwCanonText()` 兜底；建议后续 PR 做源文件级清理（见 `NAR-VOICE-001` §6.3 遗留项 D） |
| M2 | `characters/alice/persona.md` 仍把 Alice 妹妹写为"莉娜" | 与 `meta.json` / `selka/persona.md` 冲突 | `NAR-VOICE-001` §6.3 遗留项 B；建议清理 persona 文件 |
| M3 | `characters/garret/persona.md` 与 `characters/rulid_elder/persona.md` 仍使用旧译名（露茵村 / 北境律令） | 与 `meta.json` display 值冲突 | 与 M1 一起清理 |
| M4 | `characters/kirito/README.md` 与 `characters/kirito/persona.md` 把玩家角色写为"凛斗" | 与 `NAR-VOICE-001` §0.3 冲突 | 与 M1 一起清理；显示名问题保持开放（见 `CHAR-DEPTH-001` §3.0） |
| M5 | `kirito` 内部 id 在 `characters/meta.json` 未挂载为可玩 agent | 与本项目"玩家操作 kirito"事实不一致 | 建议在主线收束后挂载为可玩 agent（参考 `characters/kirito/README.md` 后续可选方向 1） |

### 7.2 已识别的外部风险

| 序 | 风险 | 影响 | 处置 |
|---|---|---|---|
| R1 | "End of World" 是否为独立官方正传电影 | 若有官方页面/书页明确指向另一作品，本项目对"混称"的解释需要更新 | 等待用户返还明确素材后再定（见 §6 / §8） |
| R2 | 整合骑士在 N10 的具体台词是否触发"复刻官方台词" | 玩家面向文本可能因台词过近而被识别为搬运 | 整合骑士 N10 台词必须原创；本项目已锁定"3 句对话上限 + 不透露 Synthesis 编号 + 不复刻官方台词" |
| R3 | AI agent 在 hybrid / agent 模式下越权改写 `effects.ending_id` | 终点被改写 | `NAR-ADAPT-001` §4 + `AI_NPC_BOUNDARY.md` 锁定 |
| R4 | NPC 主动入口在不同玩家路径下数量爆炸 | 分支膨胀 | `NAR-ADAPT-001` §6.4 限制每节点 ≤ 1 个 NPC 主动入口 |
| R5 | `data/story/events_chapter_01.json` 老事件（`ch1_d*_`）与本文件 `ch1pc_*` 共存导致内容校验冲突 | QA 工具可能误报 | 旧 `ch1_d*_` 事件保留为"系统验证 + 候选内容库"；本文件 `ch1pc_*` 事件由后续 PR 增量补入；不在本文件范围直接修改 |

### 7.3 概念性风险（**软风险**）

| 序 | 风险 | 处置 |
|---|---|---|
| C1 | 玩家无法在 N10 真正"阻止"Alice 被带走 → 部分玩家可能感到"无意义" | N10 提供 3 种"最后表达"选择；让玩家保留"我的反应"而非"我的结果" |
| C2 | 越界前的"准备"差异不显著 → 部分玩家感觉"准备动作白做" | N10 的"最后表达"路径直接读取 N08 的 `pack_record` / `set_retreat` / `tell_garret_truth` |
| C3 | `N10` 的整合骑士出现可能"过于突然" | `WORLD-MACRO-001` §2.3 + `NAR-PRECAP-001` N10 注明"不可预警"；UI 上以"压感"代替角色对话预警 |

## 8. **必须等待用户素材确认**的内容（独立列出）

> 下列 6 项在用户返还明确素材前，**不得**在玩家面向文本中写死。每项均给出"等待用户素材类型"。

| 序 | 待裁决项 | 等待用户素材类型 |
|---|---|---|
| W1 | 玩家面向显示名："见习记录员" / "桐人" / "凛斗" / 其他 | 明确显示名（可附 `uwCanonText.js` 映射建议） |
| W2 | "End of World" 是否为独立官方正传电影 | 官方页面 / 影像 / 书页链接；若为另一作品，提供带来源的标题与时间 |
| W3 | 整合骑士在 N10 的具体台词（"你已越过规则边界"等是否被接受） | 接受 / 改写建议 / 新的台词模板 |
| W4 | 整合骑士的"3 名 Pre-Capture 投影"是否被接受（Deusolbert + 2 名次级骑士） | 接受 / 改为只出现 1 名主骑士 / 改为完全匿名 |
| W5 | Alice 父亲（`rulid_chief` 占位 id）是否在 Act 2 后段出场 | 接受 `rulid_elder`（加斯夫特）代行村务 / 让 Alice 父亲本人出场 |
| W6 | 北方洞窟的"前人划痕"细节（在 N10 石板下方）是否被接受 | 接受 / 改为完全无痕迹 / 改为不同形态 |

> 上述 6 项在 `materials/05_WORKFLOW_AND_REVIEW.md` 的"评审 → 返工"流程中处理；在用户返还素材前，本项目主线收束不强行写死。

## 9. 与既有 QA 工具的对应

| QA 工具 / 错误码 | 本文件对应检查项 |
|---|---|
| `backend/app/content_validator.py` `invalid_precapture_act` | §5.1 中 N01–N10 的 `precapture_act` ∈ {act_0, act_1, act_2, act_3} |
| `backend/app/content_validator.py` `invalid_precapture_key_node` | §5.1 中 N01–N10 的 `precapture_key_node: true` |
| `backend/app/content_validator.py` `invalid_precapture_endpoint` | §6 中 N10 的 `precapture_endpoint: alice_captured` |
| `backend/app/content_validator.py` `precapture_endpoint_not_key_node` | §6 中 N10 同时 `precapture_key_node: true` |
| `backend/app/content_validator.py` `precapture_endpoint_marker_must_match_choice_ending` | §6 中 N10 `effects.ending_id = alice_captured` |
| `backend/app/content_validator.py` `precapture_legacy_term` | §4 术语表 |
| `backend/app/content_validator.py` `precapture_spoiler_term` | §6 剧透护栏 |
| `materials/tools/check_precapture_readiness.py` | §6 全部标准 |

## 10. 盲测评审清单（首次玩家前最后一遍）

- [ ] 3 名陌生玩家在 15–25 分钟内能完成四幕。
- [ ] 玩家能复述三人为什么前往尽头山脉。
- [ ] 玩家能解释禁忌目录意味着什么。
- [ ] 玩家能解释抓捕为什么不可避免。
- [ ] 玩家能说出至少一次"自己改变了关系 / 线索 / 准备 / 最后表达"的体验。
- [ ] 玩家在 N10 后不感到"被骗"或"突然"，而感到"它确实要发生，只是我多说了什么 / 多做了什么"。

> 上述 6 项是 `materials/11_PRECAPTURE_EXECUTION_BRIEF.md` §6 完成定义的精简版；详细测试方法见 `docs/delivery/PLAYTEST.md` 与 `docs/delivery/PLAYTEST_ROUND_01_TRACKER_20260806.md`。

## 11. 完成定义

- ✅ 覆盖时间线 / 年龄阶段 / 角色语气 / 世界规则 / 事件闸门 / 固定抓捕终点 / 素材来源检查。
- ✅ 每个 key node 的前置条件与后续影响列出。
- ✅ 抓捕终点验收标准（§6）齐备。
- ✅ 矛盾、风险、待裁决事项分别列出（§7.1 / §7.2 / §7.3）。
- ✅ **"必须等待用户素材确认"内容**（§8）6 项独立列出。
- ✅ 不直接修改 `data/story/`、`backend/`、`frontend/`。
