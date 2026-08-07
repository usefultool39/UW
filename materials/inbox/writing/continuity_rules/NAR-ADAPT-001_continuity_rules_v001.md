# NAR-ADAPT-001 — 正典兼容与分支规则（Pre-Capture 范围）

- request_id: NAR-ADAPT-001
- creator/source: Mavis 叙事智能体（基于 `NAR-CANON-001`、`NAR-PRECAP-001`、`WORLD-MACRO-001`、`WORLD-MICRO-001`、`CHAR-DEPTH-001`、`NAR-VOICE-001` 与 `materials/10_CANON_CONTINUITY_CHECKLIST.md` / `08_NARRATIVE_REQUIREMENTS.md` / `11_PRECAPTURE_EXECUTION_BRIEF.md`）
- created_at: 2026-08-06
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/ ; `materials/inbox/writing/character_voice/NAR-VOICE-001_core_voice_bible_v001.md`
- edits: none
- intended_use: 编剧 / AI agent / QA 校验器共用的"什么能动 / 什么不能动"硬约束；任何在 `data/story/events_chapter_01.json` 新增 authored 事件前必须先过本文件
- notes: 本文件**不**修改 `data/story`、`backend/`、`frontend/`；只给"分支规则"层。所有"不能改"项以 `[官方固定]` 标注；"可改但有约束"项以 `[项目原创约束]` 标注。

---

## 0. 玩家介入模型

- 玩家身份：见习记录员（**显示名待用户裁决**）。
- 玩家**不**直接替代爱丽丝、尤吉欧、桐人。
- 设计模式：**事实层固定 + 观察层可变**（参考 `materials/09_PRECAPTURE_STORY_TARGET.md` §二）。
  - 固定：人物关系、年龄阶段、规则、禁忌目录、抓捕终点。
  - 可变：玩家发现的线索、关系倾向、谁先知道、临场表达、日常顺序。
  - 可回响：NPC 对玩家的信任、记忆、承诺、紧张。
  - 不可变：爱丽丝最终越界并被带走。

## 1. 玩家能改变什么（10 项）

| 序 | 可变项 | 项目约束 | 关联素材 |
|---|---|---|---|
| C1 | 跟随谁（Day 1 上午） | N01 的 4 个 `d1_follow_target` 选项；影响 N05 的基线 | N01 / N05 |
| C2 | 是否在书库做记录（第 14.5 页） | N04 的 `book14_5_recorded` 0/1；影响 N07 开场 | N04 / N07 |
| C3 | 是否把静默线证据上报 | N06 的 `d2_reported_to` ∈ {garret, elder, none}；影响 N10 整合骑士到来时的可见性 | N06 / N10 |
| C4 | 静默线标记是否压在线外 | N05 的 `silent_line_marker` ∈ {pressed, kept}；影响 N09 Alice 行为 | N05 / N09 |
| C5 | 炉边晚餐站位 | N03 的 `dinner_sided` ∈ {eugeo, alice, neutral}；影响 N07 开场 | N03 / N07 |
| C6 | 共同决定（Act 2 准备） | N07 的 `d3_plan` ∈ {direct, report_first, face_to_face}；影响 N08 | N07 / N08 |
| C7 | 准备动作（2 选 2） | N08 选 2 个 flag；影响 N09 / N10 资源基线 | N08 / N09 / N10 |
| C8 | 抵达尽头山脉的进入方式 | N09 的 `d4_entrance` ∈ {together, alice_first, retreat}；**不**改变 N10 触发 | N09 / N10 |
| C9 | Alice 越界前最后表达 | N10 的 `final_words` / `final_log` flag；改变 Alice 永久记忆 | N10 |
| C10 | 永久记忆内容（玩家可被 NPC 记下什么） | 见 `CHAR-DEPTH-001` §3.8 与各 NPC 段；不直接出现在 UI | 全部 NPC |

> 上述 10 项中，C1–C5 是 Act 0 / Act 1 的"线索 / 关系 / 信任"决定；C6–C8 是 Act 2 的"承诺 / 准备 / 入口"决定；C9–C10 是 Act 3 的"最后表达 / 永久记忆"决定。**所有 C1–C10 都不会改变 N10 的"Alice 被带走"事实**。

## 2. 玩家不能改变什么（10 项） `[官方固定]`

| 序 | 不可变项 | 原因 |
|---|---|---|
| F1 | 卢利特村是三人童年生活的核心地点 | 官方 Ep.1 "raised in Rulid village" |
| F2 | 爱丽丝、尤吉欧、见习记录员之间的童年关系 | 官方 Ep.1 固定三人组合 |
| F3 | 巨神树（基加斯西达）是天职 | 官方 Ep.1 "This is their Calling" |
| F4 | 禁忌目录是世界规则，不是普通法律 | 官方 Ep.1 "the Taboo Index, the laws of their world" |
| F5 | 尽头山脉是"规则边界"的空间化表达 | 官方 Ep.1 "the fabled cave in the End Mountains"；本项目原创"规则边界"映射 |
| F6 | 越界即触发禁忌目录执行 | 官方 Ep.3 后续 "Alice's departure"（被 Axiom Church 带走） |
| F7 | 爱丽丝被整合骑士带走 | 官方 Ep.3 "taken away by the Axiom Church" + 角色页 Deusolbert 描述 |
| F8 | 玩家不能让 Alice 永久逃脱 | 与 F7 一致；`N10` 的所有 choice 都 `effects.ending_id = alice_captured` |
| F9 | 玩家不能阻止整合骑士到来 | 越界即触发，不可延迟 |
| F10 | 玩家不能让 Alice 提前进入整合骑士人格（Synthesis 三十） | 剧透护栏：`NAR-VOICE-001` §0.4；本项目 Pre-Capture 阶段禁止出现 Alice 的整合骑士形态 |

## 3. 玩家可以延后揭示的内容（5 项） `[项目原创约束]`

- D1：北方洞窟的 Blue Rose Sword — 仅在 Eugeo 提及"北方工具"时轻提，**不展开**。
- D2：中央大教堂内部政治 — 仅作"远端存在"被敬畏提及，**不展开**。
- D3：Cardinal 自治程序 — **不出现**（属 War of Underworld 之后阶段）。
- D4：整合骑士的 Synthesis 编号 — **不出现**（属 Pre-Capture 之后阶段）。
- D5：玩家在现实世界的记忆缺口 — **只表现为停顿 + 撤回**，不出现 SAO / 现实世界 / 桐人等任何具体内容（剧透护栏）。

> 上述 5 项在 `N10` 之后**仍不可揭示**（属后续阶段）。

## 4. 固定终点如何保持不变

- `N10` 是唯一一个 `precapture_endpoint: alice_captured` 的事件，且必须是**最后一个**被标记的 key node。
- `N10` 至少一个 choice 写 `effects.ending_id = alice_captured`（与 marker 一致）。
- 任何在 `N10` 之后新增的 key node 必须取消 `precapture_key_node` 标记或迁移到 Pre-Capture 之后的新阶段。
- AI agent（包括 NPC 意图 agent、AI 对话 agent）**不得**改写 `effects.ending_id`；该字段由 authored JSON 锁定（参考 `docs/architecture/AI_NPC_BOUNDARY.md`）。
- 跨节点回响（`NAR-PRECAP-001` §2 中 5 条）**均不**影响终点触发；只影响 N10 的"最后表达"选项内容。
- scripted / hybrid / agent 三种模式共用同一份 authored `data/story/events_chapter_01.json`；AI 失败时回退 scripted（参考 `docs/architecture/AI_PROVIDER_ADAPTER.md`）。

## 5. 选择如何影响线索 / 关系 / 承诺 / 准备 / 最后表达

| 选择类别 | 影响通道 | 影响幅度上限 | 例 |
|---|---|---|---|
| 线索掌握 | `d*_follow_target` / `book14_5_recorded` / `silent_line_marker` | 0/1 状态 + 1 个 memory | N05 的 `marker_pressed` 让 N09 Alice 默认把标记压在外侧 |
| 关系变化 | `*.trust` / `*.affinity` / `*.tension` 增量 | 每节点 +5 / -3 区间 | N07 `side_alice_plan` → `alice.trust +3, eugeo.trust +1, eugeo.tension +2` |
| 承诺 | `promise_*` flag；一次性；进入长期记忆 | 1 个 / 节点 | N07 `promise_d4_face_check` |
| 准备 | `pack_*` / `set_retreat` / `tell_garret_truth` | 0/1 + 资源基线 | N08 选 `pack_record` → N10 `speak_log` 可用 |
| 最后表达 | `final_words` / `final_log` flag；只写入永久记忆 | ≤8 字 / ≤25 字 | N10 `speak_one_sentence` 写 ≤8 字 |

## 6. 如何避免分支膨胀

### 6.1 数值收束
- 信任度区间：每节点 ±5；紧张度区间：每节点 ±3；超过区间时由 `Session.player_action` 钳制。
- 关系度总量：每个 NPC 全 Pre-Capture 阶段累计增量 ≤ +20 / -10（防止单 NPC 数值过快突破）。
- 承诺：每节点 ≤ 1 个 `promise_*` 写入；同 key 不重复写。

### 6.2 节点数收束
- key node 总数 ∈ [8, 12]（本项目目标 10）。
- 跨节点回响总数 ≤ 5（项目目标 3 主 + 2 次）。
- 每个事件 choice 数量 ≤ 3（2–3 优先）。

### 6.3 AI 介入收束
- 单局 AI 调用预算：action 12 / dialogue 12 / intent 6（参考 `docs/architecture/AI_NPC_BOUNDARY.md` 与 `backend/app/agent_budget.py`）。
- AI 越权边界：不写 `effects.ending_id`、不写 flag deltas 中的 `precapture_*`、不写阶段日期。
- AI 候选必须过 `backend/app/memory_policy.py` 的确定性筛选。

### 6.4 文案与素材收束
- 玩家面向文本必须过 `uwCanonText()` 与 `NAR-VOICE-001` 第 0.2 节术语表。
- 玩家面向文本不得包含剧透护栏中的"整合骑士 Synthesis 编号 / 神器 / 现实世界"等内容。
- 每个 key node 的 NPC 主动入口 ≤ 1；其余入口在活动目录中作为"可选准备"出现，不在主事件里。

## 7. 如何将长剧情压缩为紧凑、可重复游玩的短循环

### 7.1 时长与日期
- 起点 = Day 1 上午；终点 = Day 4 中午（**约 96 小时游戏内时间**）。
- 玩家实际游玩时长目标：15–25 分钟（参考 `NEXT_PHASE.md` §P0）。
- 日期推进：只由 authored 事件与日结算闸推进，玩家**没有**独立跳日入口（参考 `CURRENT_STATUS.md` 2026-08-05 日期推进调整）。

### 7.2 资源回收
- 体力：每节点 1 档；不恢复跨日。
- 神圣力：仅 Alice / Selka 持有；每节点最多 1 次"做标记"消耗。
- 天命（HP/MP）：不在本阶段显示具体数值，只在 N10 整合骑士出现时出现一次"压感"。

### 7.3 可重复游玩差异
- **关系走向**：C1 + C3 + C5 + C6 决定 Alice / Eugeo 的信任度与紧张度终值。
- **线索掌握**：C2 + C4 决定 N10 `speak_log` 路径的可用素材。
- **承诺履行**：C6 + C8 决定 `promise_*` flag 在 N10 是否兑现。
- **最后表达**：C9 决定 N10 `final_words` / `final_log` 内容（≤8 字 / ≤25 字）。
- **不差异**：F1–F10、N10 触发、整合骑士到来。

### 7.4 失败与重玩
- 玩家在 N09 选 `turn_back`：**不**取消 N10 触发；只让 Alice 独自先行（`d4_entrance=alice_first`），让玩家"没有陪她走到最后一步"。
- 玩家在 N06 选 `keep_silent`：**不**取消 N10 触发；让玩家手上的"已上报"证据为空。
- 玩家在 N08 选错两项：让 N09 / N10 资源基线降低（体力归零 / 撤退失败 / 记录本丢失），**不**取消 N10 触发。
- 重玩：从 Day 1 上午重新开始；所有 `d*_*` flag 重置；`promise_*` 累计清空。

## 8. 与既有 `data/story/events_chapter_01.json` 的关系

- 既有 `ch1_d*_` 事件保留为"系统验证 + 候选内容库"；不直接进 Pre-Capture 主线（参考 `NEXT_PHASE.md`）。
- 本文件 N01–N10 的 `precapture_act` / `precapture_key_node` / `precapture_endpoint` 标记由后续 PR 在用户返还素材后接入 `data/story/events_chapter_01.json`。
- 本文件**不直接修改** `data/story/`、`backend/`、`frontend/`。

## 9. 与 `AI_NPC_BOUNDARY.md` / `NAR-VOICE-001` 的硬约束对照

| 约束 | 引用 |
|---|---|
| AI 不改写 `effects.ending_id` | `docs/architecture/AI_NPC_BOUNDARY.md` |
| AI 不改写 `precapture_*` 标记 | `docs/architecture/AI_NPC_BOUNDARY.md` |
| AI 候选过 `memory_policy.py` | `backend/app/memory_policy.py` |
| AI 单局预算 24 次 | `backend/app/agent_budget.py` |
| 玩家面向文本术语过 `uwCanonText()` | `frontend/src/utils/uwCanonText.js` |
| 剧透护栏 | `NAR-VOICE-001` §0.4 |

## 10. 完成定义

- ✅ 玩家能改变 / 不能改变 / 可以延后揭示三类清楚分开。
- ✅ 固定终点 `precapture_endpoint: alice_captured` 的保持方式明确。
- ✅ 5 条跨节点回响列出（≥3）。
- ✅ 分支膨胀防护（数值 / 节点 / AI / 文案）四类齐备。
- ✅ 长剧情 → 紧凑短循环的对应规则（时长 / 资源 / 重玩 / 失败）齐备。
- ✅ 不直接修改 `data/story/`、`backend/`、`frontend/`。
