# NAR-PRECAP-001 — Pre-Capture 主线四幕事件方案

- request_id: NAR-PRECAP-001
- creator/source: Mavis 叙事智能体（基于 `NAR-CANON-001`、`NAR-VOICE-001`、`WORLD-MACRO-001`、`WORLD-MICRO-001`、`CHAR-DEPTH-001` 草稿与 `materials/09_PRECAPTURE_STORY_TARGET.md`）
- created_at: 2026-08-06
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/
- edits: none
- intended_use: 编剧/数据驱动事件作者参考；后续 `data/story/events_chapter_01.json` 的 authored 事件需按本文件的 `precapture_act` / `precapture_key_node` / `precapture_endpoint` 标记与回响 flag 写入
- notes: 本文件不写爱丽丝被带走之后的剧情；所有标记节点数 = 10（在 8–12 范围内）。事件 ID 前缀 `ch1pc_`（Pre-Capture）以区别已有 `ch1_d*_` 骨架；该前缀属于作者建议，最终由 `materials/inbox/writing` 系列在评审后定。

---

## 0. 范围与终点

- 起点：玩家在卢利特村以"见习记录员"身份报到，已与 Eugeo、Alice、Selka、加利塔、加斯夫特建立日常接触。
- 终点：**爱丽丝越过尽头山脉的规则边界，被整合骑士（Deusolbert Synthesis Seven 等）带走**。
  - 终点 marker：`precapture_endpoint: alice_captured`（合法候选之一，亦可写 `precapture_alice_captured`）。
  - 终点所在节点必须为最后一个被标记的 key node。
  - 终点节点的至少一个 choice 必须写 `effects.ending_id = alice_captured`（与 marker 一致）。
- 本文件**不写**整合骑士在中央大教堂的训练、不写 Eugeo 与 Kirito 的剑术学院、不写 War of Underworld；它们属后续阶段。

## 1. 四幕结构总览

| 幕 | 名 | 节点数 | 主题 | 目标 |
|---|---|---|---|---|
| Act 0 | 可信日常 | 3 | 让玩家爱上卢利特村与三人关系 | 理解 Eugeo 的天职、Alice 的判断、记录员的位置 |
| Act 1 | 规则裂缝 | 3 | 让玩家看见禁忌目录压不住的事实 | 决定掌握哪条线索、向谁说、对谁保留 |
| Act 2 | 共同决定 | 2 | 让玩家体会越界不是"探险" | 决定谁提出去、谁准备、谁留守、玩家是否在出发前说全 |
| Act 3 | 越界与带走 | 2 | 玩家在抓捕瞬间拥有最后表达权 | 决定最后一句话、最后一个动作、最后一份记录 |

总节点数 = **10**，符合 8–12 节点要求。

## 2. 跨节点回响总览（≥3，实际 5）

| Echo # | 写入端（节点.选项） | 写入 flag | 读取端（节点.trigger） | 触发效果 |
|---|---|---|---|---|
| E1 | N01.choice.follow_eugeo / follow_alice / follow_selka / follow_elder | `d1_follow_target ∈ {eugeo,alice,selka,elder}` | N05 (静默线第一证据) | 玩家所跟随者会先察觉 / 提前给出技术性提示 |
| E2 | N04.choice.recorded_14_5 / kept_14_5 | `book14_5_recorded ∈ {1,0}` | N07 (炉边晚餐分歧) | Alice 对玩家信任度基线变化 |
| E3 | N06.choice.report_to_garret / report_to_elder / keep_silent | `d2_reported_to ∈ {garret,elder,none}` | N10 (越界 + 抓捕) | 整合骑士到来时，玩家手上的"已上报证据"数量与对话内容不同 |
| E4 | N05.choice.marker_pressed / marker_kept | `silent_line_marker ∈ {pressed,kept}` | N09 (抵达尽头山脉) | Alice 是否把神圣术标记压在线外作为越界前最后一道提醒 |
| E5 | N03.choice.sided_eugeo / sided_alice / kept_neutral | `dinner_sided ∈ {eugeo,alice,neutral}` | N07 (炉边晚餐分歧) | N07 的开场语气与开篇台词基线 |

> 上述 5 条回响在 `NAR-ADAPT-001` 的"分支收束"中会被压缩为 ≤3 条关键回响 + ≤2 条次要回响；本文件保留全部 5 条供作者选择。

## 3. 节点清单

> 每个节点统一字段（按用户任务规范）：
> 1) 目标 2) 地点 3) 参与角色 4) 冲突 5) 玩家选择 6) 选择后果 7) 关系变化 8) 记忆 9) 承诺 10) 紧张度 11) 后续回响
> 标记字段：
> - `precapture_act`: `act_0` / `act_1` / `act_2` / `act_3`
> - `precapture_key_node`: `true`
> - 终点节点 `N10` 额外：`precapture_endpoint: alice_captured`

---

### N01 — 见习记录员报到（Act 0 · key node · Day 1 上午）

- 事件 id（建议）：`ch1pc_n01_rookie_first_look`
- **目标**：让玩家理解自己是"先听后记"的村内岗位，决定今日跟随谁获得第一手观察。
- **地点**：卢利特村中央广场 → 玩家头像落点为"见报名册桌"。
- **参与角色**：玩家 + Eugeo（巨神树）+ Alice（送餐途中）+ Selka（书库帮手）+ 加斯夫特（村务长，加利塔在北门备班）。
- **冲突**：玩家只有半天时间，跟随不同的人会拿到不同第一证据。
- **玩家选择**：
  - `follow_eugeo` "跟 Eugeo 上巨神树" — 看到伐木场天气、斧痕、风声断点的物理证据
  - `follow_alice` "跟 Alice 走送餐路线" — 听到她与赛尔卡在书库门口的对话和她对禁忌目录的敬畏
  - `follow_selka` "跟 Selka 在书库" — 看到书库如何保管旧记录、谁可以看什么
  - `follow_elder` "去见加斯夫特" — 听到村务长对"安静的风"的解释与他的汇报流程
- **选择后果**：写 `d1_follow_target` flag；玩家今天的"首条观察"类型不同。
- **关系变化**：
  - `follow_eugeo` → `eugeo.trust +2`, `eugeo.tension +1`
  - `follow_alice` → `alice.trust +2`, `alice.tension +0`
  - `follow_selka` → `selka.trust +2`, `alice.tension +1`（被观察会让 Alice 紧张）
  - `follow_elder` → `garret.trust +1`, `eugeo.tension +2`（Eugeo 担心村务长封锁信息）
- **记忆**：每个被跟随者写一条 weight=2 的 memory（"玩家第一天选择跟我走"）。
- **承诺**：无。
- **紧张度**：2/10。
- **后续回响**：被 `N05` 读取。

---

### N02 — 巨神树伐木场日常（Act 0 · key node · Day 1 上午末/中午）

- 事件 id：`ch1pc_n02_gigas_daily`
- **目标**：让玩家认识 Eugeo 的天职与节奏，建立"每天砍多少"的尺度感。
- **地点**：巨神树伐木场（`gigas_clearing`）。
- **参与角色**：Eugeo、玩家、加利塔（路过的北门巡守）。
- **冲突**：Eugeo 当天的伐木计数比昨天少 3 下；他归因于"风向不对"，但其实是"心里有别的事"。
- **玩家选择**：
  - `steady_train` "按 Eugeo 节奏挥斧" — 学习他的握斧方式与退让
  - `ask_about_axe` "问 Eugeo 这把斧头的来路" — 听到他提一句"北方洞窟里应该还有更顺手的工具"，留作伏笔
- **选择后果**：
  - `steady_train` 写 `trained_with_eugeo_day1=1`
  - `ask_about_axe` 写 `eugeo_mentioned_north_tool=1`（Eugeo 提及北境工具；不暴露 Blue Rose Sword）
- **关系变化**：`steady_train` → `eugeo.affinity +3, eugeo.trust +2`；`ask_about_axe` → `eugeo.trust +3, eugeo.tension +2`。
- **记忆**：Eugeo 写一条"玩家第一天问过我斧头"（weight=3）。
- **承诺**：无。
- **紧张度**：1/10。
- **后续回响**：被 `N04` 间接读取（`ask_about_axe` 路径会触发书库 "第 14.5 页" 内容优先显示"工具 / 北方"的描述）。

---

### N03 — 炉边晚餐：三人关系基线（Act 0 · key node · Day 1 傍晚）

- 事件 id：`ch1pc_n03_hearth_dinner_d1`
- **目标**：让玩家在放松场景里看到三人的差异，并把紧张度降到最低。
- **地点**：Eugeo 与玩家的家 → 炉火 + 餐桌（`home_hearth`）。
- **参与角色**：Eugeo、Alice（送餐）、玩家、Selka（在书库侧门探视）。
- **冲突**：Alice 送来的汤比平时咸；Eugeo 用"你担心我们就会多放盐"说出她的情绪。
- **玩家选择**：
  - `sided_eugeo` "回应 Eugeo 的玩笑" — 强化"被照顾者"位置
  - `sided_alice` "替 Alice 解释一句" — 强化"被保护者"位置
  - `kept_neutral` "只把汤端起来喝一口" — 强化"观察者"位置
- **选择后果**：写 `dinner_sided` flag。
- **关系变化**：
  - `sided_eugeo` → `eugeo.trust +3`, `alice.tension +1`
  - `sided_alice` → `alice.trust +2`, `eugeo.tension +1`
  - `kept_neutral` → 双方都 `+1 trust`, 无 tension
- **记忆**：Eugeo 与 Alice 各自 weight=2。
- **承诺**：无。
- **紧张度**：1/10。
- **后续回响**：被 `N07` 读取（决定 N07 的开场态度）。

---

### N04 — 教会书库的第 14.5 页（Act 1 · key node · Day 2 上午）

- 事件 id：`ch1pc_n04_library_page_14_5`
- **目标**：让玩家在制度内部找到"禁忌目录解释不了"的旧记录。
- **地点**：教会书库阅览室（`church_library`）。
- **参与角色**：玩家、Selka（书库帮手）、Alice（送药草路过）。
- **冲突**：书库中夹在第 14 与第 15 页之间的一页纸张，字迹与前后不一致；上面写"北方鸟声会停"。禁忌目录无对应条目。
- **玩家选择**：
  - `recorded_14_5` "照原字抄进自己的记录本" — 留下可复核的副本
  - `kept_14_5` "只在心里记下、不写进记录本" — 把证据保留在观察层
  - `report_to_alice` "把发现直接告诉 Alice" — 跳过个人观察，立刻让 Alice 介入
- **选择后果**：
  - `recorded_14_5` 写 `book14_5_recorded=1`
  - `kept_14_5` 写 `book14_5_recorded=0` + `kept_observation=1`
  - `report_to_alice` 写 `alice_warned_14_5=1`
- **关系变化**：
  - `recorded_14_5` → `selka.trust +2, alice.trust +1`（她尊重可复核的记录）
  - `kept_14_5` → `selka.trust +0, alice.tension +2`（她担心"只有你一个人知道"）
  - `report_to_alice` → `alice.trust +3, alice.tension +3`（她同时获得安全感与负担）
- **记忆**：Alice 写一条 weight=3 memory（"玩家是否在书库前对我说"）。
- **承诺**：无（承诺在 N07 才出现）。
- **紧张度**：4/10。
- **后续回响**：被 `N07` 读取（决定 N07 开场 Alice 对玩家的初始态度）。

---

### N05 — 静默线第一证据（Act 1 · key node · Day 2 下午）

- 事件 id：`ch1pc_n05_silent_line_first_evidence`
- **目标**：让玩家在北境边缘获得"两息风声断点"的物理证据。
- **地点**：巨神树伐木场北侧 12 步（`gigas_clearing` 北缘）。
- **参与角色**：玩家、Eugeo（同行）、视 N01 选择而可能出现的第三方（Alice / Selka / 加利塔 / 加斯夫特）。
- **冲突**：斧痕北侧 12 步处，风声断约两息；鸟声未恢复前出现一次反向风。
- **玩家选择**：
  - `marker_pressed` "用神圣术标记压在线外" — 把可观察界限固化
  - `marker_kept` "只用记录本记下时间" — 保持证据为可复核文字
  - `tell_eugeo_only` "只告诉 Eugeo，不让第三方加入" — 把信任范围收紧
- **选择后果**：
  - `marker_pressed` 写 `silent_line_marker=pressed` + `alice.trust +2`
  - `marker_kept` 写 `silent_line_marker=kept` + `eugeo.trust +2`
  - `tell_eugeo_only` 写 `silent_line_private=1` + `alice.tension +1`（她要"最后才知道"的位置）
- **关系变化**：见上。
- **记忆**：Eugeo weight=4 memory（"玩家在静默线前做的事"）。
- **承诺**：无。
- **紧张度**：6/10。
- **后续回响**：被 `N09` 读取（决定抵达尽头山脉时 Alice 是否把标记压到外侧）。

---

### N06 — 北门夜巡口供（Act 1 · key node · Day 2 夜）

- 事件 id：`ch1pc_n06_north_gate_dispatch`
- **目标**：让玩家决定是否把静默线证据上报到村务长 / 北门巡守。
- **地点**：北门值班棚（`north_gate`）。
- **参与角色**：玩家、加利塔（北门巡守）、加斯夫特（被通知后赶到）。
- **冲突**：加利塔透露"昨晚我夜巡时也听见过一段断风"；加斯夫特要求走"标准流程"——记录 → 三方签字 → 明日清晨交到教会。
- **玩家选择**：
  - `report_to_garret` "只报给加利塔，让他按北门流程走"
  - `report_to_elder` "直接报给加斯夫特，启动村务流程"
  - `keep_silent` "今晚先不报，保留为三人证据"
- **选择后果**：
  - `report_to_garret` 写 `d2_reported_to=garret` + `garret.trust +3`
  - `report_to_elder` 写 `d2_reported_to=elder` + `garret.trust +1, rulid_elder.trust +2, eugeo.tension +2`（Eugeo 担心加斯夫特封锁证据）
  - `keep_silent` 写 `d2_reported_to=none` + `eugeo.trust +1, alice.tension +2`（Alice 担心瞒报风险）
- **关系变化**：见上。
- **记忆**：加利塔 / 加斯夫特 weight=3。
- **承诺**：写一条可选承诺 `promise_report_next_morning` 仅在 `keep_silent` 路径出现。
- **紧张度**：7/10。
- **后续回响**：被 `N10` 读取（决定整合骑士到来时玩家手上是否已有正式上报记录）。

---

### N07 — 炉边晚餐分歧（Act 2 · key node · Day 3 傍晚）

- 事件 id：`ch1pc_n07_hearth_dinner_split_d3`
- **目标**：把"是否去尽头山脉"作为三人当面对齐事件。
- **地点**：玩家与 Eugeo 家中炉边（`home_hearth`）。
- **参与角色**：Eugeo、Alice、玩家。
- **冲突**：Alice 提出"明天去看静默线另一侧是什么"；Eugeo 反对"至少先告诉加斯夫特"；玩家被两人同时要求表态。
- **玩家选择**：
  - `side_alice_plan` "和 Alice 一起规划明日行动" — 准备食物、记录本、撤退点
  - `side_eugeo_caution` "按 Eugeo 节奏：先报村务长、再决定" — 走流程
  - `propose_compromise` "三人明天清晨当面对齐一次" — 把决定权延后到明早
- **选择后果**：
  - `side_alice_plan` 写 `d3_plan=direct`，解锁 `N08` 准备动作
  - `side_eugeo_caution` 写 `d3_plan=report_first`，`N08` 改为"先上报、再听加斯夫特意见"
  - `propose_compromise` 写 `d3_plan=face_to_face`，`N08` 改为"三人面谈 + 加利塔在北门见证"
- **关系变化**：
  - `side_alice_plan` → `alice.trust +3, eugeo.trust +1, eugeo.tension +2`
  - `side_eugeo_caution` → `eugeo.trust +3, alice.trust +1, alice.tension +2`
  - `propose_compromise` → 双方都 +1，无 tension
- **记忆**：三人各 weight=4。
- **承诺**：写承诺 `promise_d4_face_check ∈ {alice,eugeo,garret,all}`。
- **紧张度**：6/10。
- **后续回响**：被 `N08` 读取（决定准备阶段的动作集合）。

---

### N08 — 准备与出发（Act 2 · key node · Day 3 夜 → Day 4 晨）

- 事件 id：`ch1pc_n08_prepare_and_set_off`
- **目标**：让玩家在"行动前的最后窗口"完成补给、记录、退路选择。
- **地点**：Eugeo 与玩家家 → 北门 → 森林北缘。
- **参与角色**：Eugeo、Alice、玩家、加利塔（视 N07 选项出现）。
- **冲突**：准备时间只够做两件事；玩家必须选哪两件。
- **玩家选择**（二选二）：
  - `pack_food` "备干粮与水" — 体力 +1，避免越界前体力归零
  - `pack_record` "带完整记录本与抄件" — 增加 N10 的"最后一份记录"可用素材
  - `set_retreat` "和 Eugeo 商定撤退点" — 越界后撤回到某块石头 / 某棵树的概率
  - `tell_garret_truth` "把准备情况如实告诉加利塔" — 增加 N06 路径的可见性
- **选择后果**：
  - 每个选项写一个 flag；最终 2 个 flag 决定 N09 的资源基线
- **关系变化**：见选择路径。
- **记忆**：Eugeo weight=3、Alice weight=3。
- **承诺**：视 `tell_garret_truth` 写入 `promise_honest_to_garret=1`。
- **紧张度**：7/10。
- **后续回响**：被 `N09`、`N10` 同时读取。

---

### N09 — 抵达尽头山脉（Act 3 · key node · Day 4 上午）

- 事件 id：`ch1pc_n09_arrive_end_mountains`
- **目标**：让玩家在越界前最后决定安全距离与口令。
- **地点**：尽头山脉洞穴入口外侧（`end_mountains_entrance`）。
- **参与角色**：Eugeo、Alice、玩家。
- **冲突**：Alice 提议"我先进去十二步看是不是有回应"；Eugeo 提议"我们一起进、听见鸟声就撤"。
- **玩家选择**：
  - `enter_together` "三人一起进、设定鸟声为撤退信号" — 共同承担责任
  - `let_alice_first` "让 Alice 先进十二步" — 风险集中但信任何持
  - `turn_back` "现在撤回" — 改变 N10 触发条件
- **选择后果**：
  - `enter_together` 写 `d4_entrance=together` + `promise_d4_face_check=all` → N10 必触发
  - `let_alice_first` 写 `d4_entrance=alice_first` + `alice.tension +1` → N10 必触发
  - `turn_back` 写 `d4_entrance=retreat` + `alice.trust -2, eugeo.trust +1` → N10 仍触发（**剧情终点不可阻止**）
- **关系变化**：见上。
- **记忆**：三人各 weight=4。
- **承诺**：确认 `promise_d4_face_check`。
- **紧张度**：8/10。
- **后续回响**：被 `N10` 读取。

---

### N10 — 越界 + 整合骑士到来（Act 3 · key node · **ENDPOINT** · Day 4 中午）

- 事件 id：`ch1pc_n10_alice_captured`
- `precapture_endpoint: alice_captured`
- **目标**：让玩家在固定终点内拥有"最后一句话 / 最后一个动作 / 最后一份记录"三种选择权。
- **地点**：尽头山脉洞穴外侧 → 规则边界线（`silence_line_boundary`）。
- **参与角色**：Eugeo、Alice、玩家、整合骑士 Deusolbert Synthesis Seven（项目原创为可玩投影；不暴露其后续编号），随行 2 名次级整合骑士（项目原创）。
- **冲突**：Alice 越过静默线 → 静默线产生"压"感（标记符亮、鸟声停）→ 整合骑士数息后从尽头山脉外侧出现。
- **玩家选择**（玩家在爱丽丝被带走前的最后表达）：
  - `speak_silence` "不开口，把记录本合上交给 Alice" — 表达"事实已留下"
    - `effects.ending_id = alice_captured`
  - `speak_one_sentence` "说一句不超过 8 个字的话" — 输入框限制 8 字（字数硬限制）
    - `effects.ending_id = alice_captured` + `final_words` flag（仅用于日志）
  - `speak_log` "把最后一条观察写进记录本并交出" — 提交一个不超过 25 字的观察句
    - `effects.ending_id = alice_captured` + `final_log` flag
- **选择后果**：三个选项**都不阻止 Alice 被带走**；差别在于最后一份"留在第三方可复核视野"里的内容。
- **关系变化**：`alice.trust +5`（无论选哪个，她都记下"玩家最后没有撒谎"）；`eugeo.trust +2, eugeo.tension +4`（他感到无力）；`garret.tension +3`（若 N06 选择 `keep_silent`）。
- **记忆**：Alice weight=5 memory（**永久记忆**）。
- **承诺**：写承诺 `promise_bring_alice_back=1`。
- **紧张度**：10/10。
- **后续回响**：本节点即为终点；不再向后续阶段回响（中央大教堂、剑术学院、整合骑士训练属后续阶段）。

> **重要约束**：`N10` 是唯一一个 `precapture_endpoint: alice_captured` 的事件，且必须是被标记的最后一个 key node；任何在 `N10` 之后新增的 key node 都应取消 `precapture_key_node` 标记或移到 Pre-Capture 之后的新阶段。

## 4. 紧凑化与"长剧情 → 短循环"对应

- 每个节点的"选择 × 后果"在 `data/story/events_chapter_01.json` 中只保留 2–3 个 choice，每个 choice 一次写完所有关系、记忆、承诺、flag，避免嵌套。
- 每个节点的事件**只读 ≥1 个 `d?_*` flag，写 ≥1 个 `d?_*` flag**；防止节点被删后"什么都不变"。
- 跨节点回响在 `NAR-ADAPT-001` 中会被压成 3 条主回响 + 2 条次要回响；超出部分存档为"内容候选库"，不直接进入 runtime。
- 每日事件数量不超过 4（晨 / 午 / 傍晚 / 夜），每个时段只挂一个 key node + 至多一个 optional 活动（不在本文件范围）。
- AI 生成对白 / 意图必须遵守 `NAR-VOICE-001` 的句长档位与剧透护栏；不修改结局、不提前透露整合骑士真实身份。

## 5. 与既有 `data/story/events_chapter_01.json` 的关系

- 既有 `ch1_d1_reading_clue`、`ch1_d1_training_with_eugeo`、`ch1_d2_forest_anomaly` 等属于"系统验证 + 候选内容库"（参见 `NEXT_PHASE.md` 与 `08_NARRATIVE_REQUIREMENTS.md` §5）。
- 本文件 N01–N10 是 **Pre-Capture 主线收束版**，建议在 `data/story/events_chapter_01.json` 中以 `ch1pc_*` 事件 id 增量补入；旧 `ch1_d*_` 事件在主线收束后归入"候选内容库"，由后续工作决定是否合并 / 改名 / 删除。
- **本文件不直接修改 `data/story/events_chapter_01.json`**；标记字段（`precapture_act` / `precapture_key_node` / `precapture_endpoint`）由后续 PR 在用户返还素材后接入。

## 6. 完成定义（针对本文件）

- ✅ 4 幕（act_0 / act_1 / act_2 / act_3）全部覆盖。
- ✅ 关键节点数 = 10（介于 8–12）。
- ✅ 终点事件唯一（`N10`），且是最后一个被标记的 key node。
- ✅ 终点事件至少一个 choice 写 `ending_id = alice_captured`。
- ✅ 跨节点回响 = 5（≥3）。
- ✅ 不写爱丽丝被带走之后的剧情。
- ✅ 节点至少推进两项（关系、规则理解、行动技巧、世界状态、终点因果）中的至少两项；`N01/N02/N03` 主推关系 + 角色差异；`N04/N05/N06` 主推规则 + 紧张；`N07/N08` 主推承诺 + 准备；`N09/N10` 主推紧张 + 终点因果。
