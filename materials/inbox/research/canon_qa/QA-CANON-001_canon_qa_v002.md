# QA-CANON-001 — Pre-Capture 正典连续性验收包（v002）

- request_id: QA-CANON-001
- creator/source: Mavis 叙事智能体（基于用户 2026-08-06 反馈修订 v001；保留 v001 不删）
- created_at: 2026-08-06
- replaces: QA-CANON-001_canon_qa_v001
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/
- edits: v002 主要修正：
  1. 三栏事实分类与 `NAR-CANON-001` v002 §0 对齐：A 官方明确 / B 原作·动画明确但当前官方网页摘要未覆盖 / C 项目原创补充
  2. 修复 v001 全部内部矛盾（M1–M5）：包括"显示名问题"在 v002 闭合、"整合骑士在山侧出现"修正为"仅在 N08/N09/N10 在村中"、"静默线/14.5 页/两息风声/见报名册桌"降为 C 类可选支线
  3. 10 节点表按用户 2026-08-06 锁定的 10 步顺序重新设计
  4. 6 项 W 待裁决按 v002 状态重新列出（W1 闭合 / W2 未确认 / W3–W6 调整）
- intended_use: QA 校验器 / 内容校验器 / 真人盲测评审 共用的连续性验收；任何在 `data/story/events_chapter_01.json` 新增 authored 事件前必须先过本文件
- notes: 上一轮被退回的修订已从工作树删除，可通过 Git 历史追溯。本文件**不**修改 `data/story/`、`backend/`、`frontend/`；只给"检查表 + 验收标准"层。

---

## 0. 范围

- 覆盖：`NAR-PRECAP-001` v002 N01–N10 全部 10 个 key node。
- 范围：卢利特村 + 尽头山脉外侧；不覆盖 Centoria / 中央大教堂内部 / 整合骑士训练 / 暗黑界 / War of Underworld。
- 验收对象：未来接入 `data/story/events_chapter_01.json` 的 `ch1pc_*` 事件，以及 AI agent 在 scripted / hybrid / agent 模式下的输出。

## 1. 角色年龄 / 阶段检查

| 角色 | 项目阶段 | 官方原作阶段 | 分类 | 一致性 |
|---|---|---|---|---|
| 桐人（玩家） | 童年 / 少年 | 童年（Ep.1–2） | A + B | ✅ 一致；"既视感"按 B 类表达 |
| Alice | 童年 / 少年 | 童年（Ep.1–2）/ 已被带走（Ep.3） | A + B | ✅ 一致；"施援受伤者越界"按 B 类表达 |
| Eugeo | 童年 / 少年 | 童年（Ep.1–2） | A + B | ✅ 一致；Blue Rose Sword **不出现**（B 保护） |
| Selka | 童年 / 少年 | 童年（Ep.3） | A | ✅ 一致；N09 / N10 出现 |
| 整合骑士（Deusolbert） | "远方来人" / 在村中宣告与带走 | 整合骑士第 7 位 | A + B | ✅ 一致；**仅 N08 / N09 / N10 在村中**；N10 之前不展示 Synthesis 编号 |

> **不出现**（B 类剧透保护）：Alice Synthesis Thirty、Eugeo Synthesis Thirty-Two、Fanatio Synthesis Two、Bercouli Synthesis One、Cardinal、Administrator 的任何具体形态 / 编号 / 行动。

## 2. 地点检查

| 地点 | 项目用名 | 官方名 | 分类 | 一致性 |
|---|---|---|---|---|
| 卢利特村 | 卢利特村 | Rulid Village | A | ✅ |
| 巨神树（基加斯西达） | 巨神树 / 基加斯西达 | Gigas Cedar | A | ✅ |
| 巨神树伐木场 | 巨神树伐木场 | (无官方单独命名) | C | ⚠️ 项目原创 |
| 教会书库 | 教会书库 | (无官方单独命名) | C | ⚠️ 项目原创 |
| 教会回廊 | 教会回廊 | (无官方单独命名) | C | ⚠️ 项目原创 |
| 北门 | 北门 | (无官方单独命名) | C | ⚠️ 项目原创 |
| 尽头山脉 | 尽头山脉 | End Mountains | A | ✅ |
| 尽头山脉洞窟 | 尽头山脉洞窟 | "the fabled cave in the End Mountains" | A | ✅ |
| 北方洞窟 | 北方洞窟 | North Cave | A | ✅（**不进入**，仅作"远方的传说"） |
| 静默线 / 规则边界 | 静默线 | (无官方单独命名) | B + C | ⚠️ B 类原作明确（"北门不越过"边界）+ C 类具体物理形态 |
| Centoria | Centoria | Cenotria / Centoria | A | ✅（**仅作远景**） |
| 中央大教堂 | 中央大教堂 | Central Cathedral | A | ✅（**仅作远景**） |
| 暗黑界 | 暗黑界 | Dark Territory | A | ✅（**仅作"尽头山脉外侧"敬畏提及**） |

> **检查项**：任何新增地点若不属于上表，必须先在 `WORLD-MICRO-001` / `WORLD-MACRO-001` 增补"A/B/C 三类"标注；不直接进 `data/story/`。

## 3. 时间 / 日期检查

| 检查项 | 期望 | 来源 |
|---|---|---|
| Pre-Capture 起点日期 | Day 1 上午 | `NAR-PRECAP-001` v002 N01 |
| Pre-Capture 终点日期 | Day 3 下午 | `NAR-PRECAP-001` v002 N10 |
| 事件总时长 | 约 60 小时游戏内时间 | `NAR-ADAPT-001` v002 §7.1 |
| 实际游玩时长目标 | 15–25 分钟 | `docs/PLAN.md` P0 |
| 玩家是否可独立跳日 | 否 | `docs/PLAN.md` 的当前剧情推进规则 |
| 是否在 N10 之后继续推进日期 | 否（终点收束） | `NAR-PRECAP-001` v002 §0 |

> **检查项**：N01 触发的 `d1_bond` flag 必须在 Day 1 上午内可写；N05 必须在 Day 2 下午可触发；N07 必须在 Day 2 傍晚可触发；N08 必须在 Day 3 上午可触发；N10 必须在 Day 3 下午可触发。

## 4. 术语检查

> 所有玩家面向文本必须过 `frontend/src/utils/uwCanonText.js` 与 `NAR-VOICE-001` §0.2 术语表。

| 旧译名（废弃） | 必须写成 | 来源 |
|---|---|---|
| 露茵村 | 卢利特村 | `uwCanonText.js` |
| 艾琳 | 爱丽丝 | `uwCanonText.js` / `characters/meta.json` |
| 尤里 / 悠吉欧 | 尤吉欧 | `uwCanonText.js` / `characters/meta.json` |
| 凛斗 | 桐人（**v002 闭合**显示名问题） | 用户 2026-08-06 |
| 古誓树 | 巨神树 | `uwCanonText.js` |
| 古誓树清场 / 巨神树清场 | 巨神树伐木场 | `uwCanonText.js` |
| 北境律令 | 禁忌目录 | `uwCanonText.js` |
| 刻印术 | 神圣术 | `uwCanonText.js` |
| 村西书库 | 教会书库 | `uwCanonText.js` |
| 村西书道 | 教会回廊 | `uwCanonText.js` |
| 莉娜 | 赛尔卡 | `NAR-VOICE-001` §0.3 / §6.3 遗留项 B |
| 塞鲁卡 | 赛尔卡 | `NAR-VOICE-001` §0.3 / §6.3 遗留项 A |

> **检查项**：QA 工具（`backend/app/content_validator.py` 的 `precapture_legacy_term`）已内置上述映射；任何新写文本若触发该错误码，必须替换为规范译名。
> **v002 关键闭合**："凛斗" → "桐人" 在玩家面向文本中**完全闭合**（不再视为"待用户裁决"）。

## 5. 事件顺序 / 节点前置 / 后续回响

### 5.1 10 节点（v002 主线）— 严格按用户 2026-08-06 锁定的 10 步

| 节点 | 对应步骤 | 分类 | 关键事实 |
|---|---|---|---|
| N01 | 1. 卢利特村三人日常 | A + C | 三人童年关系（A）+ 日常细节（C） |
| N02 | 2. 尤吉欧的巨神树天职 | A + C | Gigas Cedar Calling（A）+ 伐木节奏（C） |
| N03 | 3. 三人谈及禁忌目录与尽头山脉 | A + C | 讨论 Taboo Index 与 End Mountains（A）+ 讨论深度（C） |
| N04 | 4. 前往尽头山脉洞窟 | A + C | 三人决定出发（A）+ 准备选择（C） |
| N05 | 5. 接触暗黑界一侧及受伤者 | B + C | 原作明确"接触受伤者"（B）+ 接触方式（C） |
| N06 | 6. 爱丽丝为救人触碰/越过边界 | B | 原作明确"爱丽丝越界救人"（B）；玩家**不能**阻止 |
| N07 | 7. 三人返回卢利特村 | B + C | 原作明确"返回"（B）+ 返回方式（C） |
| N08 | 8. 整合骑士来到村中宣告罪名 | B | 原作明确"骑士来村中宣告"（B）；**不**在山侧出现 |
| N09 | 9. 爱丽丝与家人、桐人、尤吉欧告别 | B + C | 原作明确"告别"（B）+ 告别具体方式（C） |
| N10 | 10. 爱丽丝被带走 | A + B | Deusolbert 描述（A）+ 原作明确（B）；**村中**带走 |

### 5.2 前置条件（trigger / required_flags / forbidden_flags）

| 节点 | 前置 flag（至少 1 个） | 后续回响（读端） |
|---|---|---|
| N01 | 无（Day 1 上午首次） | N05 读 `d1_bond` |
| N02 | 可选：`d1_bond` | N08 读 `d2_calling_pace` |
| N03 | 可选：`d1_bond` | N06 读 `d3_talk_about_index` |
| N04 | `d3_talk_about_index` 必填 | N07 读 `d4_pack_*` |
| N05 | `d4_pack_*` 至少 1 个 + `d1_bond` | N06 读 `d5_approach` |
| N06 | `d5_approach` 必填 | N07 读 `d6_alice_crossed_instant` |
| N07 | `d4_pack_*` 至少 1 个 + `d6_alice_crossed_instant` | N08 / N09 读 `d7_return_disclosure` |
| N08 | `d7_return_disclosure` 必填 | N09 读 `d8_knight_arrival_posture` |
| N09 | `d8_knight_arrival_posture` 必填 | N10 读 `d9_farewell_choice` |
| N10 | `d9_farewell_choice` 必填 | （**终点**） |

### 5.3 跨节点回响汇总（与 `NAR-PRECAP-001` v002 §2 一致）

- E1: `d1_bond` → N05
- E2: `d2_calling_pace` → N08
- E3: `d3_talk_about_index` → N06
- E4: `d4_pack_*` → N07
- E5: `d5_approach` → N06

> 跨节点回响总数 = **5**（≥3），验收通过。

### 5.4 关键 flag 不变量

- `precapture_endpoint: alice_captured` 在 N10 唯一存在；其他节点**不得**写该 marker。
- `effects.ending_id` 仅 N10 写 `alice_captured`（或 `precapture_alice_captured`）；其他节点**不得**写 `ending_id`。
- 任何 `effects.ending_id` 值不属于 `{alice_captured, precapture_alice_captured}` 时，QA 工具会报错。

## 6. 抓捕终点验收标准

| 标准 | 期望 | 验证方式 |
|---|---|---|
| `precapture_endpoint` 唯一性 | N10 是唯一含该 marker 的事件 | `check_precapture_readiness.py` `_story_report()` |
| `precapture_endpoint` 是最后一个被标记的 key node | N10 是 `marked_event_ids` 列表的最后一项 | 同上 |
| `effects.ending_id` 与 marker 一致 | N10 至少一个 choice 写 `ending_id = alice_captured` | 同上 |
| 标记节点数 ∈ [8, 12] | N01–N10 = 10 | 同上 |
| Act 覆盖 | `act_0` / `act_1` / `act_2` / `act_3` 全部存在 | 同上 |
| 跨节点回响 ≥ 3 | E1–E5 = 5 | 同上 |
| AI 越权边界 | AI 不写 `effects.ending_id`、不写 `precapture_*` 标记 | `backend/app/agent_budget.py` + `AI_NPC_BOUNDARY.md` |
| 玩家面向文本术语 | 过 `uwCanonText()` 与 `NAR-VOICE-001` §0.2 术语表 | `backend/app/content_validator.py` `precapture_legacy_term` |
| 剧透护栏 | 不出现 Alice Synthesis 编号 / 整合骑士神器 / 现实世界 / SAO / 死亡游戏 | `backend/app/content_validator.py` `precapture_spoiler_term` |
| **抓捕地点** | 在卢利特村（N08 / N09 / N10）；**不**在山侧 | 人工 + QA 工具 |

## 7. 矛盾 / 风险 / 待裁决事项

### 7.1 v001 内部矛盾修复（来自用户 2026-08-06 反馈）

| 序 | v001 矛盾 | v002 修正 |
|---|---|---|
| K1 | v001 把"在 End Mountains 越界后立即被整合骑士在山侧带走"作为终点 | v002 改为"三人返回卢利特村 → 整合骑士来到村中宣告 → 告别 → 带走" |
| K2 | v001 把"静默线 / 14.5 页 / 两息风声 / 见报名册桌"作为关键节点的推动力 | v002 降为 C 类可选支线，不进关键节点表 |
| K3 | v001 把"见习记录员"列为"核心 7 人之一"，等于新增第 4 名同行者 | v002 玩家 = 桐人；见习记录员是桐人的村民岗位，不增加角色 |
| K4 | v001 把"原作没明说"的剧情（被俘在山侧、整合骑士数息出现）当作"正典留白 + 项目原创推进" | v002 严格区分 A / B / C 三类；B 类必须忠实还原 |
| K5 | v001 把"桐人"显示名问题挂起为"待用户裁决" | v002 闭合：玩家显示名 = 桐人 |
| K6 | v001 把"整合骑士"列入 Pre-Capture 频繁出现角色 | v002 限定整合骑士仅 N08 / N09 / N10 在村中出现 |
| K7 | v001 的"记录员"作为叙事第三人称观察者，导致 v001 N01–N10 的部分选择以"看见/记下/不说"为主语 | v002 全部改回"桐人"为主语；保留桐人"既视感"限制 |
| K8 | v001 §3.2 桐人"既视感"未在主线节点中体现 | v002 桐人"既视感"在 N05 / N06 高压瞬间以"我好像……见过这种——" + 立刻撤回呈现 |
| K9 | v001 §6 整合骑士 N10 之前已"在山侧出现" | v002 整合骑士 N10 之前**不**出现；N05 / N06 期间**不**有整合骑士在场 |
| K10 | v001 §1 把"Alice 父亲"与"加斯夫特"混为同一概念 | v002 明确：Alice 父亲（A 类，官方身份"the chief of Rulid Village"）+ 加斯夫特（C 类，村务长代行人） |

### 7.2 已识别的外部风险

| 序 | 风险 | 影响 | 处置 |
|---|---|---|---|
| R1 | "End of World" 是否为独立官方正传电影 | 若有官方页面/书页明确指向另一作品，本项目对"混称"的解释需要更新 | 等待用户返还明确素材后再定（见 §6 / §8） |
| R2 | 整合骑士在 N08 的具体台词是否触发"复刻官方台词" | 玩家面向文本可能因台词过近而被识别为搬运 | 整合骑士 N08 台词必须原创；本项目已锁定"3 句对话上限 + 不透露 Synthesis 编号 + 不复刻官方台词" |
| R3 | AI agent 在 hybrid / agent 模式下越权改写 `effects.ending_id` | 终点被改写 | `NAR-ADAPT-001` v002 §4 + `AI_NPC_BOUNDARY.md` 锁定 |
| R4 | NPC 主动入口在不同玩家路径下数量爆炸 | 分支膨胀 | `NAR-ADAPT-001` v002 §6.4 限制每节点 ≤ 1 个 NPC 主动入口 |
| R5 | `data/story/events_chapter_01.json` 老事件（`ch1_d*_`）与本文件 `ch1pc_*` 共存导致内容校验冲突 | QA 工具可能误报 | 旧 `ch1_d*_` 事件保留为"系统验证 + 候选内容库"；本文件 `ch1pc_*` 事件由后续 PR 增量补入；不在本文件范围直接修改 |
| R6 | 整合骑士 N10 之前玩家是否需要"既视感"提示（桐人"我好像……见过这种——"） | 影响 N05 / N06 的氛围 | N05 / N06 高压瞬间按 v002 §1.7 桐人说话方式执行，**不**外显 |

### 7.3 概念性风险（**软风险**）

| 序 | 风险 | 处置 |
|---|---|---|
| C1 | 玩家无法在 N06 阻止 Alice 越界 → 部分玩家可能感到"无意义" | N10 提供 3 种"最后表达"选择；让玩家保留"我的反应"而非"我的结果" |
| C2 | 玩家无法在 N07 阻止三人返回 / N08 阻止骑士宣告 | 同上 |
| C3 | N08 整合骑士出现可能"过于突然" | `WORLD-MACRO-001` v002 §2.2 + `NAR-PRECAP-001` v002 N08 注明"在 N07 返回后约 12 小时"；UI 上以"压感"代替角色对话预警 |
| C4 | "既视感"机制需要玩家盲测才能知道是否可读 | 3 名陌生玩家盲测时确认 |

## 8. **必须等待用户素材确认**的内容（独立列出，v002 更新）

> 下列 5 项在用户返还明确素材前，**不得**在玩家面向文本中写死。

| 序 | 待裁决项 | 状态 | 等待用户素材类型 |
|---|---|---|---|
| **W1** | 玩家面向显示名：桐人 / 见习记录员 / 其他 | ✅ **v002 闭合** | 已确认 = 桐人；`uwCanonText.js` 需同步将"凛斗"映射从"见习记录员"改为"桐人"或保留"见习记录员"作为职业岗位渲染 |
| **W2** | "End of World" 是否为独立官方正传电影 | ⚠️ **未确认** | 官方页面 / 影像 / 书页链接；若为另一作品，提供带来源的标题与时间 |
| **W3** | 整合骑士在 N08 宣告的具体台词模板 | 🆕 **新增** | 接受"3 句对话上限 + 不透露 Synthesis 编号 + 不复刻官方台词" / 提供新的台词模板 / 改为完全匿名 |
| **W4** | 整合骑士的"3 名 Pre-Capture 投影"是否被接受 | 🆕 **新增** | 接受 Deusolbert + 2 次级骑士 / 改为只 1 名主骑士 / 改为完全匿名 |
| **W5** | Alice 父亲在 N08 / N09 的具体出场形式 | 🆕 **新增** | 接受 C 类的"父亲近期叮嘱 Alice"对话 / 改为沉默出场 / 让加斯夫特完全代行 |
| **W6** | 北方洞窟的"前人划痕"细节是否在 N10 之后出现 | 🆕 **新增** | 接受 v002 降级为 N10 之后 / 改为完全无痕迹 / 改为不同形态 |

> 上述 5 项在 `materials/README.md` 与 `docs/art/ASSET_REVIEW.md` 的评审流程中处理；在用户返还素材前，本项目主线收束不强行写死。

> **W1 在 v002 闭合**：玩家显示名 = 桐人。`uwCanonText.js` 仍可保留"见习记录员"作为职业岗位渲染（不删除），但玩家面向文本优先用"桐人"。`characters/kirito/README.md` 与 `characters/kirito/persona.md` 仍存在"凛斗"旧译名（属 v001 之后仍需清理的遗留项 D，与 v001 一致）。

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

- [ ] 3 名陌生玩家在 15–25 分钟内能完成 4 幕 10 节点。
- [ ] 玩家能复述三人为什么前往尽头山脉。
- [ ] 玩家能解释禁忌目录意味着什么。
- [ ] 玩家能解释为什么"接触受伤者 → Alice 越界 → 返回 → 骑士来村中宣告 → 告别 → 带走"是 B 类原作剧情、**不能**被任何选项改变。
- [ ] 玩家能说出至少一次"自己改变了准备 / 对话 / 关系 / 承诺 / 最后表达"的体验。
- [ ] 玩家在 N10 后不感到"被骗"或"突然"，而感到"它确实要发生，只是我多说了什么 / 多做了什么"。

> 上述 6 项是 `docs/PLAN.md` 的发布阻塞与验收 完成定义的精简版；详细测试方法见 `docs/DELIVERY.md` 与 `docs/PLAN.md`。

## 11. 完成定义

- ✅ 覆盖时间线 / 年龄阶段 / 角色语气 / 世界规则 / 事件闸门 / 固定抓捕终点 / 素材来源检查。
- ✅ 每个 key node 的前置条件与后续影响列出。
- ✅ 抓捕终点验收标准（§6）齐备。
- ✅ 矛盾（§7.1）/ 风险（§7.2 / §7.3）/ 待裁决事项（§8）分别列出。
- ✅ 5 项"必须等待用户素材确认"内容（W1 闭合 + W2 未确认 + W3–W6 新增）独立列出。
- ✅ 不直接修改 `data/story/`、`backend/`、`frontend/`。
- ✅ v001 全部 10 项内部矛盾（K1–K10）已修复。
