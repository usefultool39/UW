# NAR-ADAPT-001 — 正典兼容与分支规则（v002，Pre-Capture 范围）

- request_id: NAR-ADAPT-001
- creator/source: Mavis 叙事智能体（基于用户 2026-08-06 反馈修订 v001；保留 v001 不删）
- created_at: 2026-08-06
- replaces: NAR-ADAPT-001_continuity_rules_v001
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/
- edits: v002 主要修正：
  1. 玩家可改项重写：现在玩家可改变**准备 / 对话 / 关系 / 承诺 / 最后表达**；**不可**改变爱丽丝越界、返回村庄、被整合骑士带走
  2. 玩家 = 桐人；核心三人 = 桐人 / 尤吉欧 / 爱丽丝
  3. 抓捕在村中（N08 / N09 / N10），不再在山侧
  4. 静默线 / 14.5 页 / 两息风声 / 见报名册桌 等 v001 原创核心降为可选支线（"可改但仅影响个人观察"）
  5. 三栏分类与 `NAR-CANON-001` v002 §0 对齐
- intended_use: 编剧 / AI agent / QA 校验器共用的"什么能动 / 什么不能动"硬约束；任何在 `data/story/events_chapter_01.json` 新增 authored 事件前必须先过本文件
- notes: v001 保留在 `materials/inbox/writing/continuity_rules/NAR-ADAPT-001_continuity_rules_v001.md`，MANIFEST 状态 = `changes_requested`。本文件**不**修改 `data/story/`、`backend/`、`frontend/`；只给"分支规则"层。所有"不能改"项以 `[A]` / `[B]` 标注；"可改但有约束"项以 `[C]` 标注；"未确认"项以 `[待用户确认]` 标注。

---

## 0. 玩家介入模型

- 玩家身份：**桐人**（`kirito` 内部 id；村民岗位 = 见习记录员，是职业身份，不是第 4 名角色）。
- 核心三人：**桐人 / 尤吉欧 / 爱丽丝**（不增加第 4 名）。
- 设计模式：**事实层固定 + 观察层可变**（参考 `materials/09_PRECAPTURE_STORY_TARGET.md` §二 + 用户 2026-08-06 锁定）。
  - 固定：三人童年关系、Calling、禁忌目录、爱丽丝越界、返回村庄、被整合骑士带走。
  - 可变：桐人的准备、对话、关系倾向、承诺、最后表达。
  - 可回响：NPC 对桐人的信任、记忆、承诺、紧张。
  - 不可变：爱丽丝越界 / 三人返回 / 整合骑士来村宣告 / 爱丽丝告别 / 爱丽丝被带走。

## 1. 玩家可以改变什么（5 类）

> 用户 2026-08-06 锁定的 5 类可改项。

### 1.1 准备 [C]
- N01（日常互动定位）→ 写 `d1_bond` flag
- N02（伐木节奏）→ 写 `d2_calling_pace` flag
- N04（出发前 2 选 2）→ 写 `d4_pack_food` / `d4_pack_tool` / `d4_pack_record` / `d4_bring_alice_extra` flag
- 影响：N05 接触受伤者方式、N07 返回体力基线、N08 宣告时 Eugeo 反应、N09 告别台词。

### 1.2 对话 [C]
- N01 / N02 / N03 / N04 / N05 / N06 / N07 / N08 / N09 的所有 choice 文本
- N10 的 3 个 choice 决定"最后一句话 / 最后一份记录 / 不写"
- 影响：NPC 信任度 / 紧张度 / 永久记忆 / 关系走向。

### 1.3 关系 [C]
- 玩家与 Eugeo / Alice / Selka / 加利塔 / 加斯夫特 的信任度与紧张度
- 增量区间：每节点 ±5（信任度）/ ±3（紧张度）
- 累计区间：每 NPC 全 Pre-Capture 阶段累计 +20 / -10
- 不影响：N10 触发与"爱丽丝被带走"事实

### 1.4 承诺 [C]
- N07 的 `promise_disclosure_to_knights ∈ {full, partial, none}`
- N09 的 `promise_bring_alice_back ∈ {1, 0}`
- N03 / N04 / N06 可能衍生其他 `promise_*` flag
- 每个节点 ≤ 1 个 `promise_*` 写入；同 key 不重复写

### 1.5 最后表达 [C]
- N10 的 3 个 choice 之一：
  - `record_one_phrase` 写 `final_log ≤ 15 字`
  - `record_silence` 写 `final_log = "——"`
  - `close_record_book` 不写 final_log
- 三者**都不**阻止爱丽丝被带走
- 影响：Alice 永久记忆（weight=5）+ Eugeo 永久记忆（weight=5）

> 上述 5 类**全部不**改变 F1–F10（见 §2）的 10 项不可变事实。

## 2. 玩家不能改变什么（10 项）

### 2.1 B 类原作明确（**不可改写**）

| 序 | 不可变项 | 分类 | 原因 |
|---|---|---|---|
| F1 | 卢利特村是三人童年生活的核心地点 | A | 官方 Ep.1 "raised in Rulid village" |
| F2 | 桐人、尤吉欧、爱丽丝的童年关系是核心三人 | A + B | 官方 Ep.1 固定三人组合 |
| F3 | 巨神树（基加斯西达）是 Calling | A | 官方 Ep.1 "This is their Calling" |
| F4 | 禁忌目录是世界规则，不是普通法律 | A | 官方 Ep.1 "the Taboo Index, the laws of their world" |
| F5 | 尽头山脉是 End Mountains，洞窟是其内 | A | 官方 Ep.1 "the fabled cave in the End Mountains" |
| F6 | 三人前往 End Mountains 洞窟附近 | B | 原作·动画明确 |
| F7 | 三人接触暗黑界一侧的受伤者 | B | 原作·动画明确 |
| F8 | 爱丽丝因施援受伤者而触碰 / 越过边界 | B | 原作·动画明确 |
| F9 | 三人返回卢利特村 | B | 原作·动画明确 |
| F10 | 整合骑士来到村中宣告罪名 | B | 原作·动画明确 |

### 2.2 A 类官方明确（**不可改写**）

| 序 | 不可变项 | 原因 |
|---|---|---|
| F11 | 爱丽丝与家人、桐人、尤吉欧告别 | 官方角色页 Deusolbert 描述"arrested Alice … took her to the Central Cathedral" + 原作·动画明确 |
| F12 | 爱丽丝被整合骑士从村中带走 | A + B |
| F13 | 桐人具有"既视感"（童年阶段表现为停顿 + 撤回，**不**给出具体来源） | 原作·动画明确 |
| F14 | 玩家不能让 Alice 永久逃脱 | 与 F11/F12 一致 |
| F15 | 玩家不能让 Alice 提前进入整合骑士人格（Synthesis 三十） | 剧透护栏 |
| F16 | 玩家不能阻止整合骑士到来 | F10 / F11 / F12 一致 |
| F17 | 玩家不能阻止三人前往 End Mountains 洞窟 | F6 |
| F18 | 玩家不能阻止爱丽丝施援受伤者 | F8 |
| F19 | 玩家不能阻止三人返回 | F9 |
| F20 | 玩家不能阻止整合骑士宣告 | F10 |

> 玩家可改项 = §1 的 5 类；不可改项 = F1–F20。**F11 / F12 是 capture 终点**。

## 3. 玩家可以延后揭示的内容（5 项）`[B + C]`

- D1：北方洞窟的 Blue Rose Sword — 仅在 Eugeo 提及"北方工具"时轻提，**不**展开（B：剧透护栏）。
- D2：中央大教堂内部政治 — 仅作"远端存在"被敬畏提及，**不**展开。
- D3：Cardinal 自治程序 — **不**出现（属后续阶段）。
- D4：整合骑士的 Synthesis 编号 — **不**出现（属 Pre-Capture 之后阶段）。
- D5：桐人的"既视感"的具体来源（现实世界 / SAO / 死亡游戏）— **不**出现（剧透护栏）。

> 上述 5 项在 `N10` 之后**仍不可揭示**（属后续阶段）。

## 4. 固定终点如何保持不变

- `N10` 是唯一一个 `precapture_endpoint: alice_captured` 的事件，且必须是**最后一个**被标记的 key node。
- `N10` 至少一个 choice 写 `effects.ending_id = alice_captured`（与 marker 一致）。
- 任何在 `N10` 之后新增的 key node 必须取消 `precapture_key_node` 标记或迁移到 Pre-Capture 之后的新阶段。
- AI agent（包括 NPC 意图 agent、AI 对话 agent）**不得**改写 `effects.ending_id`；该字段由 authored JSON 锁定（参考 `docs/architecture/AI_NPC_BOUNDARY.md`）。
- 跨节点回响（`NAR-PRECAP-001` v002 §2 中 5 条）**均不**影响 F11 / F12；只影响 N08 / N09 / N10 的台词语气与最后表达内容。
- scripted / hybrid / agent 三种模式共用同一份 authored `data/story/events_chapter_01.json`；AI 失败时回退 scripted（参考 `docs/architecture/AI_PROVIDER_ADAPTER.md`）。

## 5. 选择如何影响准备 / 对话 / 关系 / 承诺 / 最后表达

| 选择类别 | 影响通道 | 影响幅度上限 | 例 |
|---|---|---|---|
| 准备 | `d*_bond` / `d*_calling_pace` / `d*_pack_*` flag | 0/1 状态 + 1 个 memory | N04 选 `pack_food` 让 N07 体力 +1 |
| 对话 | choice 文本 + flag | 不定量 | N03 `deep_talk` → `alice.trust +3, eugeo.tension +1` |
| 关系 | `*.trust` / `*.affinity` / `*.tension` 增量 | 每节点 ±5（信任度）/ ±3（紧张度） | N07 `wait_for_alice` → `alice.trust +3, eugeo.trust +1` |
| 承诺 | `promise_*` flag；一次性；进入长期记忆 | 1 个 / 节点 | N09 `promise_bring_alice_back=1` |
| 最后表达 | `final_log` flag；只写入永久记忆 | ≤15 字 / "——" / 不写 | N10 `record_one_phrase` 写 ≤15 字 |

## 6. 如何避免分支膨胀

### 6.1 数值收束
- 信任度区间：每节点 ±5；紧张度区间：每节点 ±3；超过区间时由 `Session.player_action` 钳制。
- 关系度总量：每个 NPC 全 Pre-Capture 阶段累计增量 ≤ +20 / -10（防止单 NPC 数值过快突破）。
- 承诺：每节点 ≤ 1 个 `promise_*` 写入；同 key 不重复写。

### 6.2 节点数收束
- key node 总数 ∈ [8, 12]（本项目目标 10）。
- 跨节点回响总数 ≤ 5（E1–E5）。
- 每个事件 choice 数量 ≤ 3（2–3 优先）。

### 6.3 AI 介入收束
- 单局 AI 调用预算：action 12 / dialogue 12 / intent 6（参考 `docs/architecture/AI_NPC_BOUNDARY.md` 与 `backend/app/agent_budget.py`）。
- AI 越权边界：不写 `effects.ending_id`、不写 flag deltas 中的 `precapture_*`、不写阶段日期。
- AI 候选必须过 `backend/app/memory_policy.py` 的确定性筛选。

### 6.4 文案与素材收束
- 玩家面向文本必须过 `uwCanonText()` 与 `NAR-VOICE-001` 第 0.2 节术语表。
- 玩家面向文本不得包含剧透护栏中的"整合骑士 Synthesis 编号 / 神器 / 现实世界 / SAO / 死亡游戏"等内容。
- 每个 key node 的 NPC 主动入口 ≤ 1；其余入口在活动目录中作为"可选准备"出现，不在主事件里。

### 6.5 C 类可选支线（v001 核心降级）
- 静默线 / 14.5 页 / 两息风声 / 见报名册桌 = C 类项目原创补充，**不**进关键节点表。
- 玩家触发这些支线时**不**影响 F1–F20，只影响个人观察 / 信任度 / 紧张度。

## 7. 如何将长剧情压缩为紧凑、可重复游玩的短循环

### 7.1 时长与日期
- 起点 = Day 1 上午；终点 = Day 3 下午（**约 60 小时游戏内时间**）。
- 玩家实际游玩时长目标：15–25 分钟（参考 `NEXT_PHASE.md` §P0）。
- 日期推进：只由 authored 事件与日结算闸推进，玩家**没有**独立跳日入口。

### 7.2 资源回收
- 体力：每节点 1 档；不恢复跨日。
- 神圣力：仅 Alice / Selka 持有；每节点最多 1 次"做标记"消耗。
- 天命（HP/MP）：不在本阶段显示具体数值。

### 7.3 可重复游玩差异（5 类可改项的全部差异）
- **准备走向**：C1 + C2 + C4 决定 Alice / Eugeo / 桐人 在 N05 / N07 的基线。
- **对话差异**：C2 全部 choice 文本改变 NPC 信任度终值。
- **关系差异**：C3 决定 Alice / Eugeo / 桐人 在 N10 之前的信任度终值。
- **承诺差异**：C4 决定 `promise_disclosure_to_knights` / `promise_bring_alice_back` 在 N08 / N10 的兑现情况。
- **最后表达差异**：C5 决定 N10 `final_log` 内容。
- **不差异**：F1–F20、N08 / N10 触发、整合骑士到来。

### 7.4 失败与重玩
- 玩家在 N07 选 `keep_secret`：**不**取消 N08 触发；只让 N08 / N09 台词更紧。
- 玩家在 N04 选错两项：让 N05 / N07 资源基线降低，**不**取消 N10 触发。
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
| 剧透护栏（不出现 SAO / 现实世界 / Synthesis 编号 / 神器） | `NAR-VOICE-001` §0.4 |

## 10. 完成定义

- ✅ 玩家可改 5 类（准备 / 对话 / 关系 / 承诺 / 最后表达）。
- ✅ 玩家不可改 20 项（F1–F20，全部 A + B 类）。
- ✅ 玩家可延后揭示 5 项（D1–D5）。
- ✅ 固定终点 `precapture_endpoint: alice_captured` 的保持方式明确（在村中 N10 触发）。
- ✅ 5 条跨节点回响列出（≥3）。
- ✅ 分支膨胀防护（数值 / 节点 / AI / 文案 / C 类支线）齐备。
- ✅ 长剧情 → 紧凑短循环的对应规则齐备。
- ✅ 不直接修改 `data/story/`、`backend/`、`frontend/`。
