# NAR-PRECAP-001 — Pre-Capture 主线四幕事件方案（v002）

- request_id: NAR-PRECAP-001
- creator/source: Mavis 叙事智能体（基于用户 2026-08-06 反馈修订 v001；保留 v001 不删）
- created_at: 2026-08-06
- replaces: NAR-PRECAP-001_pre_capture_story_v001
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/
- edits: v002 主要修正：
  1. 主线节点表完全按用户 2026-08-06 给出的 10 步顺序：日常 → 天职 → 谈及禁忌目录 → 前往 → 接触受伤者 → 爱丽丝越界 → 返回 → 骑士宣告 → 告别 → 带走
  2. 玩家 = 桐人（核心三人 = 桐人 / 尤吉欧 / 爱丽丝），不再把"见习记录员"列为第 4 名
  3. 抓捕地点 = 卢利特村内（N08 / N09 / N10），不再写成"在山侧立即被抓"
  4. "静默线 / 14.5 页 / 两息风声 / 见报名册桌"等 v001 原创降为可选支线（C 类），不进关键节点表
  5. 接触暗黑界一侧 + 受伤者 + 爱丽丝越界救人 = B 类（原作·动画明确但当前官方网页摘要未覆盖），v002 必须忠实还原
  6. 跨节点回响 5 条（≥3）
- intended_use: 编剧 / 数据驱动事件作者参考；后续 `data/story/events_chapter_01.json` 的 authored 事件需按本文件的 `precapture_act` / `precapture_key_node` / `precapture_endpoint` 标记与回响 flag 写入
- notes: 上一轮被退回的修订已从工作树删除，可通过 Git 历史追溯。事件 ID 前缀 `ch1pc_` 沿用 v001 命名建议。

---

## 0. 范围与终点

- 玩家：**桐人**（`kirito` 内部 id；村民岗位 = 见习记录员，是职业身份，不是第 4 名角色）。
- 核心三人：桐人、尤吉欧、爱丽丝。
- 起点：玩家在卢利特村以桐人身份与 Eugeo、Alice 共同生活。
- 终点：**爱丽丝被整合骑士（Deusolbert Synthesis Seven + 随行骑士）从卢利特村带走**。
  - 终点 marker：`precapture_endpoint: alice_captured`（合法候选之一，亦可写 `precapture_alice_captured`）。
  - 终点所在节点必须为最后一个被标记的 key node。
  - 终点节点的至少一个 choice 必须写 `effects.ending_id = alice_captured`（与 marker 一致）。
- 本文件**不写**整合骑士在中央大教堂的训练、不写 Eugeo 与 Kirito 的剑术学院、不写 War of Underworld；它们属后续阶段。

## 1. 四幕结构总览（10 节点）

| 幕 | 名 | 节点 | 对应用户 10 步 |
|---|---|---|---|
| Act 0 | 可信日常 | N01 / N02 | 步骤 1（日常）+ 步骤 2（天职） |
| Act 1 | 规则与决定 | N03 / N04 | 步骤 3（谈及禁忌目录与尽头山脉）+ 步骤 4（前往） |
| Act 2 | 山侧遭遇 | N05 / N06 | 步骤 5（接触受伤者）+ 步骤 6（爱丽丝越界） |
| Act 3 | 返回与带走 | N07 / N08 / N09 / N10 | 步骤 7（返回）+ 步骤 8（骑士宣告）+ 步骤 9（告别）+ 步骤 10（带走） |

总节点数 = **10**，符合 8–12 节点要求；终点 N10。

## 2. 跨节点回响总览（5 条，≥3）

| Echo # | 写入端 | flag | 读取端 | 触发效果 |
|---|---|---|---|---|
| E1 | N01.choice.互动方式 | `d1_bond ∈ {warm, neutral, distant}` | N05 | 玩家三人日常关系紧张度决定 N05 接触受伤者时桐人是否先发问 |
| E2 | N02.choice.天职节奏 | `d2_calling_pace ∈ {steady, push, slow}` | N08 | 玩家 / Eugeo 的伐木节奏影响 N08 整合骑士宣告时 Eugeo 的反应台词 |
| E3 | N03.choice.讨论深度 | `d3_talk_about_index ∈ {casual, deep, avoid}` | N06 | 是否在 N03 真正讨论禁忌目录影响 N06 爱丽丝越界时的判断基线 |
| E4 | N04.choice.准备方式 | `d4_pack ∈ {full, light, none}` | N07 | 准备充分度决定 N07 返回时体力与时间基线 |
| E5 | N05.choice.接触方式 | `d5_approach ∈ {cautious, helping, observing}` | N06 | 接触受伤者的方式决定 N06 爱丽丝是否在桐人 / Eugeo 注视下越界 |

> v002 不再使用 v001 的"静默线 / 14.5 页"作为关键回响；E1–E5 全部基于用户锁定的 10 步。

## 3. 节点清单

> 每个节点统一字段：
> 1) 目标 2) 地点 3) 参与角色 4) 冲突 5) 玩家选择 6) 选择后果 7) 关系变化 8) 记忆 9) 承诺 10) 紧张度 11) 后续回响
> 标记字段：
> - `precapture_act`: `act_0` / `act_1` / `act_2` / `act_3`
> - `precapture_key_node`: `true`
> - 终点节点 N10 额外：`precapture_endpoint: alice_captured`
> 分类字段（参考 `NAR-CANON-001` v002 §0）：
> - **A** = 官方明确
> - **B** = 原作·动画明确但当前官方网页摘要未覆盖
> - **C** = 项目原创补充（不得替代 A/B）

---

### N01 — 卢利特村三人日常（Act 0 · key node · Day 1 上午）[A + C]

- 事件 id：`ch1pc_n01_rulid_daily`
- 分类：A（三人日常、卢利特村、Alice 送食物、Calling + Eugeo 提及 End Mountains 与 Taboo Index，来自官方 Ep.1）+ C（日常细节：天气、当天午餐、桐人先听后问等）
- **目标**：让玩家理解桐人与 Eugeo、Alice 的童年关系，以及他们在卢利特村中的位置。
- **地点**：卢利特村中央广场 / 巨神树伐木场 / 炉边（按选择切换）
- **参与角色**：桐人（玩家）、尤吉欧、爱丽丝；村民 / Selka（背景）
- **冲突**：Eugeo 关心当天的伐木进度，Alice 关心 Eugeo 的心情，桐人夹在两人之间。
- **玩家选择**：
  - `warm_bond` "先听 Eugeo 说伐木进度" — 强化与 Eugeo 的伙伴关系
  - `neutral_bond` "听完两人再说" — 保持中立观察
  - `distant_bond` "先去书库看看旧记录" — 倾向 Alice 的求知路径
- **选择后果**：写 `d1_bond` flag。
- **关系变化**：
  - `warm_bond` → `eugeo.trust +3, alice.trust +1`
  - `neutral_bond` → `eugeo.trust +1, alice.trust +1`
  - `distant_bond` → `eugeo.tension +1, alice.trust +2`
- **记忆**：Eugeo / Alice 各 weight=2。
- **承诺**：无。
- **紧张度**：1/10。
- **后续回响**：被 N05 读取。

---

### N02 — 尤吉欧的巨神树天职（Act 0 · key node · Day 1 上午末/中午）[A + C]

- 事件 id：`ch1pc_n02_gigas_calling`
- 分类：A（Gigas Cedar / Calling / Kirito 与 Eugeo 一起挥斧，官方 Ep.1 描述）+ C（具体下数、斧痕、天气、当天风）
- **目标**：让玩家通过与 Eugeo 一起挥斧，理解 Calling 的日常压力。
- **地点**：巨神树伐木场（`gigas_clearing`）
- **参与角色**：桐人、尤吉欧、Alice（送餐路过）
- **冲突**：Eugeo 觉得今天进度比昨天慢，担心"这样下去巨神树永远不会倒"。
- **玩家选择**：
  - `steady_pace` "按 Eugeo 的节奏挥" — 稳定 + 信任
  - `push_pace` "今天多挥几下" — 进度 + 体力消耗
  - `slow_pace` "问 Eugeo 最近在想什么" — 关心 + 关系
- **选择后果**：写 `d2_calling_pace` flag。
- **关系变化**：
  - `steady_pace` → `eugeo.trust +2, eugeo.affinity +2`
  - `push_pace` → `eugeo.affinity +1, eugeo.tension +1`（Eugeo 担心桐人受伤）
  - `slow_pace` → `eugeo.trust +3, eugeo.tension -1`
- **记忆**：Eugeo weight=3。
- **承诺**：无。
- **紧张度**：1/10。
- **后续回响**：被 N08 读取。

---

### N03 — 三人谈及禁忌目录与尽头山脉（Act 1 · key node · Day 1 傍晚）[A + C]

- 事件 id：`ch1pc_n03_talk_index_end_mountains`
- 分类：A（三人谈及 Taboo Index 与 End Mountains，官方 Ep.1 描述）+ C（炉边晚餐 / 村中 / 书库前的具体讨论深度）
- **目标**：让玩家经历三人"决定要不要去"的关键讨论。
- **地点**：Eugeo 与桐人家中炉边（`home_hearth`）
- **参与角色**：桐人、尤吉欧、爱丽丝；Selka（送药草路过）
- **冲突**：Eugeo 担心"去 End Mountains 是否违犯 Taboo Index"；Alice 想去确认洞窟的传说；桐人被两人同时看着。
- **玩家选择**：
  - `casual_talk` "随便聊聊就好，不下决定" — 维持日常
  - `deep_talk` "认真讨论禁忌目录到底写了什么" — 加深
  - `avoid_talk` "换个话题，明天再说" — 回避
- **选择后果**：写 `d3_talk_about_index` flag。
- **关系变化**：
  - `casual_talk` → 双方都 +1
  - `deep_talk` → `alice.trust +3, eugeo.tension +1`（Eugeo 被触及恐惧）
  - `avoid_talk` → `alice.tension +2, eugeo.trust +1`
- **记忆**：Eugeo / Alice 各 weight=3。
- **承诺**：无。
- **紧张度**：3/10。
- **后续回响**：被 N06 读取。

---

### N04 — 前往尽头山脉洞窟（Act 1 · key node · Day 2 上午）[A + C]

- 事件 id：`ch1pc_n04_travel_to_end_mountains`
- 分类：A（三人决定出发，官方 Ep.1 描述）+ C（路线、准备、天气、装备）
- **目标**：让玩家做一次"出发前最后准备"的选择。
- **地点**：Eugeo 与桐人家中 → 北门 → 尽头山脉外侧
- **参与角色**：桐人、尤吉欧、爱丽丝；北门值班（Selka 的兄弟 / 加利塔 视场景存在）
- **冲突**：出发前玩家必须做两个准备选择；时间只够两个。
- **玩家选择**（2 选 2）：
  - `pack_food` "带干粮与水" — 体力 +1
  - `pack_tool` "带麻绳与备用工具" — 撤退成功率 +1
  - `pack_record` "带记录本" — 后续 N10 告别场景可用
  - `bring_alice_extra` "给 Alice 多带一份保暖" — 关系 +1
- **选择后果**：写 2 个 `d4_pack_*` flag。
- **关系变化**：视选择而定。
- **记忆**：Eugeo / Alice 各 weight=2。
- **承诺**：无。
- **紧张度**：4/10。
- **后续回响**：被 N07 读取。

---

### N05 — 接触暗黑界一侧及受伤者（Act 2 · key node · Day 2 下午）[B + C]

- 事件 id：`ch1pc_n05_encounter_dark_territory_injured`
- 分类：**B**（原作·动画明确：三人前往 End Mountains 洞窟附近，遇到来自暗黑界的受伤者 / 倒下的存在，**当前官方网页摘要未覆盖**）+ C（具体地形、伤者形态、桐人面对时的"既视感"强度）
- **目标**：让玩家做出面对受伤者的具体选择。
- **地点**：尽头山脉洞穴外侧（`end_mountains_entrance`）
- **参与角色**：桐人、尤吉欧、爱丽丝；受伤者（B 类：原作设定存在，C 类：具体形态 / 伤势由本项目在不剧透前提下原创）
- **冲突**：三人到达洞穴附近，发现边界另一侧有受伤者（暗黑界一侧）；Eugeo 想直接折返，Alice 想施援手，桐人夹在中间。
- **玩家选择**：
  - `cautious_approach` "三人先在边界外观察，不贸然越过" — 谨慎
  - `helping_approach` "三人共同尝试救助" — 共同行动，但触及边界
  - `observing_approach` "让 Alice 主导，桐人和 Eugeo 退后半步" — 把决定权交给 Alice
- **选择后果**：写 `d5_approach` flag。
- **关系变化**：
  - `cautious_approach` → `eugeo.trust +2, alice.tension +1`
  - `helping_approach` → `alice.trust +2, eugeo.tension +1`
  - `observing_approach` → `alice.trust +1, eugeo.trust +1`
- **记忆**：Eugeo / Alice 各 weight=3。
- **承诺**：无。
- **紧张度**：7/10。
- **后续回响**：被 N06 读取。

---

### N06 — 爱丽丝为救人触碰/越过边界（Act 2 · key node · Day 2 下午）[B]

- 事件 id：`ch1pc_n06_alice_crosses_boundary`
- 分类：**B**（原作·动画明确：爱丽丝因施援受伤者而触碰 / 越过禁忌目录规定的"北门不越过"边界，**当前官方网页摘要未覆盖**）
- **目标**：在玩家**不能阻止** Alice 越界的前提下，让玩家记录这一瞬的判断与情绪。
- **地点**：尽头山脉边界（`silence_line_boundary`）
- **参与角色**：桐人、尤吉欧、爱丽丝
- **冲突**：Alice 决定越过边界。Eugeo 在边界这一侧伸手想拉住她。
- **玩家选择**（**不**影响 Alice 是否越界；只影响桐人这一瞬的"在场方式"）：
  - `grasp_alice_arm` "伸手拉 Alice 的手臂" — 失败，但桐人在场
  - `shout_stop` "喊了一声'停下'" — 失败，但 Alice 听见
  - `keep_silent` "沉默，把这一刻记下" — 玩家作为观察者不打断
- **选择后果**：写 `d6_alice_crossed_instant ∈ {grasp, shout, silent}` flag。
- **关系变化**：
  - `grasp_alice_arm` → `alice.trust +3, eugeo.trust +2, alice.tension +2`（Alice 感到被拉住但仍选择越过）
  - `shout_stop` → `alice.trust +2, alice.tension +3`（Alice 听见但仍越界）
  - `keep_silent` → `eugeo.trust +1, alice.trust +1`（Eugeo 觉得桐人冷静；Alice 觉得桐人理解）
- **记忆**：Alice / Eugeo 各 weight=4；Alice 永久记忆"桐人在场"。
- **承诺**：无。
- **紧张度**：9/10。
- **后续回响**：被 N07 读取（决定返回时的氛围）。

> ⚠️ **不可改写约束**：本节点的三个 choice **都不能**阻止 Alice 越界；这是 B 类原作剧情，本项目**不得**让玩家以任何选项永久阻止爱丽丝越界。

---

### N07 — 三人返回卢利特村（Act 3 · key node · Day 2 傍晚）[B + C]

- 事件 id：`ch1pc_n07_return_to_rulid`
- 分类：**B**（原作·动画明确：三人返回卢利特村，**当前官方网页摘要未覆盖**）+ C（路线、体力、具体时段）
- **目标**：让玩家经历"带着爱丽丝刚刚越界的紧张"返回村子的过程。
- **地点**：尽头山脉外侧 → 森林 → 卢利特村北门
- **参与角色**：桐人、尤吉欧、爱丽丝；北门值班（背景）
- **冲突**：三人带着"爱丽丝刚刚越界"的事实回村；途中他们讨论"要不要对村务长说实话"。
- **玩家选择**：
  - `tell_truth_now` "在北门值班棚就跟值班人说实话" — 立即上报
  - `wait_for_alice` "让 Alice 自己决定何时说" — 推迟
  - `keep_secret` "三人先不说，等整合骑士自己来" — 隐瞒（**不**改变 N08 触发，但影响 N09 告别台词）
- **选择后果**：写 `d7_return_disclosure ∈ {truth, wait, secret}` flag。
- **关系变化**：
  - `tell_truth_now` → `alice.trust +1, eugeo.tension +2`（Eugeo 担心被村务长处理）
  - `wait_for_alice` → `alice.trust +3, eugeo.trust +1`
  - `keep_secret` → `alice.trust +2, eugeo.trust +1, alice.tension +1`
- **记忆**：Eugeo / Alice 各 weight=3。
- **承诺**：写承诺 `promise_disclosure_to_knights ∈ {full, partial, none}`。
- **紧张度**：7/10。
- **后续回响**：被 N08 / N09 读取。

---

### N08 — 整合骑士来到村中宣告罪名（Act 3 · key node · Day 3 上午）[B]

- 事件 id：`ch1pc_n08_knights_arrive_village`
- 分类：**B**（原作·动画明确：整合骑士 Deusolbert Synthesis Seven + 随行骑士来到卢利特村宣告爱丽丝违犯禁忌目录的罪名，**当前官方网页摘要未覆盖**；A 由官方角色页 Deusolbert 描述"arrested Alice … took her to the Central Cathedral"间接支撑）
- **目标**：让玩家经历"整合骑士进村宣告"这一可观察事件。
- **地点**：卢利特村中央广场
- **参与角色**：整合骑士 Deusolbert Synthesis Seven、随行 2 名次级骑士、桐人、尤吉欧、爱丽丝、村务长（加斯夫特）、Alice 的父亲、村中部分村民
- **冲突**：Deusolbert 在广场宣告爱丽丝违犯禁忌目录的罪名；Eugeo 试图争辩但被骑士的标准回答压制；Alice 接受宣告。
- **玩家选择**：
  - `step_forward` "走上前去站在 Alice 身边" — 在场表态
  - `stand_with_eugeo` "站在 Eugeo 身边一起听" — 与 Eugeo 同位
  - `stay_back_observe` "退后两步继续观察" — 保持距离
- **选择后果**：写 `d8_knight_arrival_posture ∈ {forward, with_eugeo, back}` flag。
- **关系变化**：
  - `step_forward` → `alice.trust +3, eugeo.trust +1, alice.tension +2`
  - `stand_with_eugeo` → `eugeo.trust +3, alice.trust +1`
  - `stay_back_observe` → `eugeo.tension +1, alice.trust +1`
- **记忆**：Eugeo / Alice 各 weight=4；Alice 永久记忆"桐人当时的位置"。
- **承诺**：无（承诺在 N09 写出）。
- **紧张度**：8/10。
- **后续回响**：被 N09 读取。

> ⚠️ **不可改写约束**：本节点的三个 choice **都不能**阻止整合骑士宣告或改变宣告内容；这是 B 类原作剧情。

---

### N09 — 爱丽丝与家人、桐人、尤吉欧告别（Act 3 · key node · Day 3 中午）[B + C]

- 事件 id：`ch1pc_n09_alice_farewell`
- 分类：**B**（原作·动画明确：爱丽丝与家人 / 桐人 / 尤吉欧告别后被带走，**当前官方网页摘要未覆盖**）+ C（告别场景细节、桐人最后一句对话的选项 / 字数限制）
- **目标**：让玩家在告别场景里做出"桐人最后一句话 / 最后一个动作 / 最后一份记录"的选择。
- **地点**：卢利特村中央广场（与 N08 同址）
- **参与角色**：桐人、尤吉欧、爱丽丝、Alice 的父亲、Alice 的妹妹 Selka、村务长（加斯夫特）、整合骑士 Deusolbert
- **冲突**：Alice 在被带走前有一次与桐人、尤吉欧、家人的短暂告别。玩家作为桐人拥有"最后一句话 / 最后一个动作 / 最后一份记录"的选择权。
- **玩家选择**：
  - `speak_one_sentence` "说一句不超过 8 个字的话" — 8 字硬限制
  - `pass_record_book` "把记录本递给 Alice" — 给 Alice 一份"桐人在场"的可见证据
  - `stand_silently_with_eugeo` "沉默，与 Eugeo 并肩站着" — 不打破氛围
- **选择后果**：
  - `speak_one_sentence` 写 `final_words` flag（≤8 字）
  - `pass_record_book` 写 `final_log` flag（≤25 字）
  - `stand_silently_with_eugeo` 不写额外 flag（已由 N08 / N07 决定）
- **关系变化**：
  - `speak_one_sentence` → `alice.trust +3, eugeo.trust +2, alice.tension +2`
  - `pass_record_book` → `alice.trust +4, eugeo.trust +2, alice.tension +1`（Alice 知道桐人记下了什么）
  - `stand_silently_with_eugeo` → `eugeo.trust +3, alice.trust +2`
- **记忆**：Alice weight=5（**永久记忆**）；Eugeo weight=4（永久）。
- **承诺**：写承诺 `promise_bring_alice_back=1`（由玩家在选择中确认；不默认写）。
- **紧张度**：10/10。
- **后续回响**：被 N10 读取。

---

### N10 — 爱丽丝被带走（Act 3 · key node · **ENDPOINT** · Day 3 下午）[A + B]

- 事件 id：`ch1pc_n10_alice_captured`
- `precapture_endpoint: alice_captured`
- 分类：**A**（由官方角色页 Deusolbert 描述"took her to the Central Cathedral"间接支撑）+ **B**（被带往中央大教堂的具体过程属原作童年事件尾段，**当前官方网页摘要未覆盖**）
- **目标**：让玩家在固定终点内拥有"最后一句记录"权；终点不可改写。
- **地点**：卢利特村北门外
- **参与角色**：整合骑士 Deusolbert Synthesis Seven + 2 名次级骑士、爱丽丝、桐人、尤吉欧、Alice 父亲、Selka（送行）
- **冲突**：爱丽丝在北门外被整合骑士带上回中央大教堂的路。桐人作为在场者**不**能与骑士发生物理冲突；只能记录。
- **玩家选择**（玩家在爱丽丝被带走瞬间的最后记录权）：
  - `record_one_phrase` "在记录本上写一句不超过 15 字的观察" — `final_log ≤ 15 字`
    - `effects.ending_id = alice_captured`
  - `record_silence` "记录本上只画一道线" — `final_log = "——"`
    - `effects.ending_id = alice_captured`
  - `close_record_book` "合上记录本，不写" — 不写 final_log
    - `effects.ending_id = alice_captured`
- **选择后果**：三个选项**都不阻止** Alice 被带走；差别在于"桐人的最后一份可见记录"。
- **关系变化**：`eugeo.trust +2, eugeo.tension +4`（Eugeo 感到无力）；`alice.trust +5`（无论选哪个，Alice 记下"桐人最后没有撒谎"）。
- **记忆**：Alice weight=5（**永久记忆**）；Eugeo weight=5（**永久记忆**）。
- **承诺**：N09 的 `promise_bring_alice_back` 在本节点兑现检查。
- **紧张度**：10/10。
- **后续回响**：本节点即为终点；不再向后续阶段回响（中央大教堂、剑术学院、整合骑士训练属后续阶段）。

> **重要约束**：`N10` 是唯一一个 `precapture_endpoint: alice_captured` 的事件，且必须是被标记的最后一个 key node；任何在 `N10` 之后新增的 key node 都应取消 `precapture_key_node` 标记或移到 Pre-Capture 之后的新阶段。

## 4. 紧凑化与"长剧情 → 短循环"对应

- 每个节点的"选择 × 后果"在 `data/story/events_chapter_01.json` 中只保留 2–3 个 choice，每个 choice 一次写完所有关系、记忆、承诺、flag，避免嵌套。
- 每个节点的事件**至少写 1 个 `d*_*` flag**；防止节点被删后"什么都不变"。
- 跨节点回响 5 条（E1–E5），**不**超过 v001 的 5 条上限。
- 每日事件数量不超过 4（晨 / 午 / 傍晚 / 夜），每个时段只挂一个 key node + 至多一个 optional 活动。
- AI 生成对白 / 意图必须遵守 `NAR-VOICE-001` 的句长档位与剧透护栏；不修改结局、不提前透露整合骑士真实身份（Synthesis 编号在 N10 之后可被玩家回看，但 N10 之前的玩家面向文本不出现 Synthesis 编号）。

## 5. 可选支线（C 类，不进关键节点表）

> 以下为 v001 原创内容，v002 降为可选支线，**不**出现在 N01–N10 的关键节点表中。玩家可以在 Act 0 / Act 1 通过 optional 活动触发，触发结果只影响个人观察与信任度，不影响主线。

| 支线 id（建议） | 描述 | 关联素材 |
|---|---|---|
| `optional_silent_line` | 巨神树伐木场附近的两息风声断点（C1） | WORLD-MICRO-001 v002 §12 |
| `optional_page_14_5` | 教会书库"第 14.5 页"夹层（C2） | WORLD-MICRO-001 v002 §5 |
| `optional_rookie_desk` | 桐人在村里的"见习记录员"日常安排（C3） | WORLD-MICRO-001 v002 §1 |
| `optional_north_cave_scratch` | 北方洞窟的"前人划痕"细节（C6） | 不在 Pre-Capture 范围；N10 之后 |

> **进入 N01–N10 关键节点表的方式**：这些支线的 `precapture_key_node` 必须为 false（`check_precapture_readiness.py` 不会把它们计入 marked_nodes 8–12 范围）。

## 6. 与既有 `data/story/events_chapter_01.json` 的关系

- 既有 `ch1_d*_` 事件保留为"系统验证 + 候选内容库"（参见 `docs/PLAN.md` 与 `docs/PROJECT.md`）。
- 本文件 N01–N10 是 **Pre-Capture 主线收束版**，建议在 `data/story/events_chapter_01.json` 中以 `ch1pc_*` 事件 id 增量补入；旧 `ch1_d*_` 事件在主线收束后归入"候选内容库"，由后续工作决定是否合并 / 改名 / 删除。
- **本文件不直接修改 `data/story/events_chapter_01.json`**；标记字段（`precapture_act` / `precapture_key_node` / `precapture_endpoint`）由后续 PR 在用户返还素材后接入。

## 7. 完成定义（针对本文件）

- ✅ 4 幕（act_0 / act_1 / act_2 / act_3）全部覆盖。
- ✅ 关键节点数 = 10（介于 8–12）。
- ✅ 终点事件唯一（N10），且是最后一个被标记的 key node。
- ✅ 终点事件至少一个 choice 写 `ending_id = alice_captured`。
- ✅ 跨节点回响 = 5（≥3）。
- ✅ 主线节点严格按用户 2026-08-06 锁定的 10 步顺序（日常 → 天职 → 谈及 → 前往 → 接触受伤者 → 越界 → 返回 → 骑士宣告 → 告别 → 带走）。
- ✅ 玩家 = 桐人；核心三人 = 桐人 / 尤吉欧 / 爱丽丝；不增加第 4 名核心同行者。
- ✅ 抓捕发生在卢利特村（N08 / N09 / N10），不在尽头山脉。
- ✅ 接触暗黑界受伤者 + 爱丽丝越界救人 + 返回 + 骑士宣告 + 告别 + 带走 = B 类（原作·动画明确），不替换为 C 类原创。
- ✅ 静默线 / 14.5 页 / 两息风声 / 见报名册桌降为可选支线（C 类），不进关键节点表。
- ✅ 不写爱丽丝被带走之后的剧情。
- ✅ 节点至少推进两项（关系、规则理解、行动技巧、世界状态、终点因果）中的至少两项。
