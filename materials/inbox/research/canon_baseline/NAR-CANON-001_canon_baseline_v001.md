# NAR-CANON-001 — Pre-Capture 正典事实与时间线基线

- request_id: NAR-CANON-001
- creator/source: Mavis / 由 Mavis 叙事智能体在用户原任务与既有 `materials/08_NARRATIVE_REQUIREMENTS.md`、`materials/11_PRECAPTURE_EXECUTION_BRIEF.md`、`docs/research/UNDERWORLD_REFERENCE_BASELINE.md` 的官方核实基础上整理
- created_at: 2026-08-06
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original（项目原创整理与转译；官方文本仅引用最少必要的英文原句，不复制台词与截图）
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/ ; https://sao-alicization.com/1st/story/intro.html ; https://www.aniplex.co.jp/lineup/sao-alicization/story/
- edits: 基于 2026-08-06 官方页面抓取核对；将所有"End of World"表述重新明确为"Underworld + The End Mountains"的混称，并标注未确认
- intended_use: 写作者与内容校验器共用的正典事实基线；任何新增事件、NPC 意图、Agent 输出在引用本文件的命名/年龄/时间阶段前必须先核对
- notes: 本文件不复制动画镜头、官方截图或拆包素材；项目内显示名以 `frontend/src/utils/uwCanonText.js` 为唯一裁决，本文件与之一致。"桐人 / 见习记录员"显示名问题保持开放，最终裁决由用户返还素材后写入 `characters/meta.json` 与 `uwCanonText.js`。

---

## 0. 使用说明

每条事实分三级：

- **官方固定**（Official fixed）：官方动画故事页、官方角色页或项目内部已收敛的命名直接证明。
- **正典留白**（Canon gap）：原作里存在但未给出细节，需要本项目在不破坏原作的前提下补全生活与心理层次。
- **项目原创**（Project original）：原作无对应内容，由本项目为可玩性补全；进入 `inbox/writing` 系列时必须明确写出"原创"边界。

所有"英文原句"仅在官方页面已抓取验证后引用最小必要片段，不复制台词、镜头或截图。

## 1. 官方时间线（按官方第一季顺序）

| 集数 | 英文标题 | 中文项目用名 | 官方核心事实 | 本项目阶段 |
|---|---|---|---|---|
| Ep. 1 | Underworld | 第 1 集：Underworld | Kirito 与童年伙伴 Eugeo 来自 Rulid 村，受命砍倒巨神树 Gigas Cedar。童年伙伴 Alice 送食物上门。三人决定前往 End Mountains 的传说洞穴。Kirito 与 Alice 都安抚 Eugeo 对 Taboo Index 的担忧。 | Act 0 → Act 1 起手（日常 + 异常萌芽） |
| Ep. 2 | The Demon Tree | 第 2 集：The Demon Tree | Kirito 在 Underworld 醒来，无法登出，遇到 Eugeo。Eugeo 提起童年伙伴 Alice。 | Act 1 中段（异常被命名、被追认） |
| Ep. 3 | The End Mountains | 第 3 集：The End Mountains | 时间已跳到 Alice 被 Axiom Church 带走之后。Kirito 决意前往 Centoria（人界中央大教堂所在的中央都市），Eugeo 给他看从 North Cave 找到的 Blue Rose Sword。Alice 的妹妹 Selka 担心 Eugeo 自 Alice 被带走后不再笑。 | Act 3 之后的状态证据（**不在本阶段可玩范围**，但可作为抓捕后果的参照） |

> 关键判断：官方 Ep.1 文本明确写到"the three friends decide to venture to the fabled cave in the End Mountains"，但**未写到 Alice 在 Ep.1 越界**。因此本项目的"爱丽丝越界"属于官方 1–2 集之间的"未展开"段落，由本项目在不破坏官方接续的前提下原创推进，Ep.3 之前完成抓捕，Ep.3 作为终点后状态证据保留。

## 2. 官方固定事实（已抓取核对）

### 2.1 地点

| 官方名 | 项目用名 | 官方原文要点 | 来源 URL |
|---|---|---|---|
| Rulid Village | 卢利特村 | "Kirito and his childhood friend Eugeo were raised in Rulid village" | https://sao-alicization.com/1st/story/01.html |
| Gigas Cedar | 巨神树 / 基加斯西达 | "a colossal black tree called the Gigas Cedar. This is their Calling." | https://sao-alicization.com/1st/story/01.html |
| End Mountains | 尽头山脉 | "the fabled cave in the End Mountains" | https://sao-alicization.com/1st/story/01.html |
| Centoria / Cenotria | 中央大教堂 / 中央都市 | "the central city, Cenotria"（character 页）/ "journey to Centoria, the center of the Realm of Humanity"（Ep.3） | https://sao-alicization.com/1st/character/ ; https://sao-alicization.com/1st/story/03.html |
| North Cave | 北方洞窟 | "the Blue Rose Sword that he found in the North Cave a long time ago" | https://sao-alicization.com/1st/story/03.html |
| Central Cathedral | 中央大教堂 | "the great library within the Central Cathedral"（Cardinal 描述） | https://sao-alicization.com/1st/character/ |
| Dark Territory | 暗黑界 | "the Dark Territory beyond the End Mountains"（Deusolbert 描述） | https://sao-alicization.com/1st/character/ |

### 2.2 制度

| 官方名 | 项目用名 | 官方原文要点 | 来源 |
|---|---|---|---|
| Taboo Index | 禁忌目录 | "the Taboo Index, the laws of their world" | https://sao-alicization.com/1st/story/01.html |
| Calling | 天职 | "This is their Calling" | https://sao-alicization.com/1st/story/01.html |
| Sacred Arts | 神圣术 | Alice "is skilled in the Sacred Arts" | https://sao-alicization.com/1st/character/ |
| Axiom Church | Axiom Church（项目音译保留） | Alice "taken away by the Axiom Church"（Ep.3） | https://sao-alicization.com/1st/story/03.html |
| Integrity Knight | 整合骑士 | "the seventh Integrity Knight of the Axiom Church"（Deusolbert）；"the head of the Integrity Knights"（Bercouli） | https://sao-alicization.com/1st/character/ |
| Human Empire | 人界 | Administrator "rules the people of the Human Empire" | https://sao-alicization.com/1st/character/ |
| Pontifex / Administrator | Axiom Church 最高司祭 | "the pontifex, the highest officer of the Axiom Church" | https://sao-alicization.com/1st/character/ |

> 命名裁决：本项目 `uwCanonText.js` 已将禁忌目录 / 天职 / 神圣术 / 卢利特村 / 巨神树 / 整合骑士统一为规范译名；Axiom Church 作为整合骑士所属的权威名称，在玩家可见文本中**不直接显示为外文**，而是按"禁忌目录背后的远方权威"作敬畏口吻处理（见 `materials/inbox/writing/character_voice/NAR-VOICE-001_core_voice_bible_v001.md` 第 0.4 节"剧透护栏"）。

### 2.3 人物

| 官方名 | 项目用名 | 项目内部 id | 官方身份 | 来源 |
|---|---|---|---|---|
| Kirito (Kazuto Kirigaya) | 见习记录员（**显示名待用户裁决**，内部仍为 `kirito`） | kirito | Underworld 童年村民，后成剑术学院与整合骑士体系 | https://sao-alicization.com/1st/character/ |
| Eugeo | 尤吉欧 | eugeo | 童年村民，与 Kirito 同为伐木手；后成整合骑士 Eugeo Synthesis Thirty-Two | https://sao-alicization.com/1st/character/ ; https://sao-alicization.com/1st/story/01.html |
| Alice | 爱丽丝 | alice | Rulid 村村长之女，精通神圣术；后成整合骑士 Alice Synthesis Thirty | https://sao-alicization.com/1st/character/ ; https://sao-alicization.com/1st/story/01.html |
| Selka | 赛尔卡 | selka | Alice 的妹妹，教会书库见习疗愈者 | https://sao-alicization.com/1st/character/ ; https://sao-alicization.com/1st/story/03.html |
| Deusolbert Synthesis Seven | Deusolbert（整合骑士七号） | （新增 placeholder id `knight_deusolbert`） | 整合骑士第 7 位，将 Alice 从尽头山脉外侧带回中央大教堂 | https://sao-alicization.com/1st/character/ |
| Fanatio Synthesis Two | Fanatio（整合骑士二号） | （新增 placeholder id `knight_fanatio`） | 整合骑士副队长，使用多段光剑 | https://sao-alicization.com/1st/character/ |
| Bercouli Synthesis One | Bercouli（整合骑士一号） | （新增 placeholder id `knight_bercouli`） | 整合骑士之首，被 Alice 称为"Uncle" | https://sao-alicization.com/1st/character/ |
| Administrator | 最高司祭 | （占位 `administrator`，**仅在剧透护栏外作背景存在**） | Axiom Church 最高司祭，人界统治者 | https://sao-alicization.com/1st/character/ |

> 村民/支持角色命名裁决：本项目 `characters/meta.json` 已存在 `garret`（加利塔，北门巡守）和 `rulid_elder`（加斯夫特，村务长）作为村民代表与村务长；这两人在官方原作文本中**没有对应实名**（官方仅说"the chief of Rulid Village"指 Alice 父亲），属于本项目"正典留白 + 项目原创"层。Alice 的父亲在 `meta.json` 中尚未独立建立 id，可由后续事件需要时新增 `rulid_chief`。

## 3. 正典留白（本项目可补全的区域）

> 留白不破坏原作接续，但本项目原创补全时必须保留官方约束。下面每条都附"项目约束"，作为 `NAR-PRECAP-001`、`CHAR-DEPTH-001`、`WORLD-MICRO-001` 写作时的硬约束。

| 留白 | 项目约束 | 关联素材 |
|---|---|---|
| 卢利特村日常劳动细节 | 必须能解释 Gigas Cedar 与 Eugeo 的天职责任；保留"每天砍几十下"的尺度 | WORLD-MICRO-001 ; CHAR-DEPTH-001 |
| 神圣术在村民与见习层面的可观察表现 | 限于治疗、记号、读/写记录；不要出现战斗级术式 | WORLD-MACRO-001 ; CHAR-DEPTH-001 |
| 禁忌目录具体条文 | 不复制官方条文原文（项目内仅以"北门不越过"等可观察条目呈现） | WORLD-MACRO-001 ; NAR-PRECAP-001 |
| Alice 何时如何越界 | 由本项目原创；必须发生在 Ep.1 与 Ep.3 之间；终点是 Deusolbert 等整合骑士将其带往中央大教堂 | NAR-PRECAP-001 ; CHAR-DEPTH-001 |
| 北方洞窟的物理形态 | 仅作"传说"出现；不出现 Blue Rose Sword 实体（Eugeo 的青蔷薇之剑在本阶段不能作为随身武器） | WORLD-MICRO-001 ; CHAR-DEPTH-001（剧透护栏） |
| 整合骑士在卢利特村的可见性 | 仅以"远方的、村民从没人见过真面目的权威"出现；不可有整合骑士日常驻村的画面 | WORLD-MACRO-001 ; QA-CANON-001 |

## 4. 项目原创（必须明确标注）

- 见习记录员作为"事实层固定、观察层可变"的可玩角色（参考 `materials/09_PRECAPTURE_STORY_TARGET.md` 与 `NAR-VOICE-001`）。
- 卢利特村北门静默线、巨神树伐木场附近的"两息风声"等可观察异常信号（参考 `materials/10_CANON_CONTINUITY_CHECKLIST.md` 与 `NAR-VOICE-001`）。
- 玩家 UI 上的"线索 / 记录 / 紧张 / 承诺 / 记忆"等机制（参考 `docs/architecture/AI_NPC_BOUNDARY.md` 与 `materials/04_AI_PROMPT_KITS.md`）。
- 加利塔（garret，北门巡守）与加斯夫特（rulid_elder，村务长）的姓名与人格细节。

## 5. 关于"End of World"的处置（**重要**）

- 2026-08-06 复核官方动画故事页，**未发现以"End of World"为标题的《刀剑神域》正传电影条目**。本项目官方核实过的 Alicization 第一季英文故事页标题为 `Underworld`、`The Demon Tree`、`The End Mountains` 等。
- "End of World"在本项目历史记录中曾作为 `Underworld` 与 `The End Mountains` 的混称使用（见 `materials/08_NARRATIVE_REQUIREMENTS.md` 第 0 节）。
- 处置原则：在本项目玩家可见文本与本系列素材中**不出现"End of World"**。若用户后续提供明确指向"End of World"为另一部作品的链接/片名/截图，先建立带来源的新参考对象版本，**不覆盖本次官方核实**。
- 待用户确认：用户若能提供"End of World"对应的官方页面/影像/书页链接，本文件将在 v002 增加"End of World"独立条目并保留本节作为混称来源。

## 6. 三集与本项目阶段的对应关系（核心结论）

| 官方事实 | 项目 Pre-Capture 阶段 | 抓取核对状态 |
|---|---|---|
| Ep.1：卢利特村 + 巨神树 + 三人 + 尽头山脉 + 禁忌目录 | Act 0（可信日常）到 Act 1（规则裂缝） | ✅ 已抓取 |
| Ep.1 末尾的"出发去 End Mountains"是决定，不是越界 | Act 2 起点（准备与共同决定） | ✅ 已抓取 |
| Ep.2：Kirito 在 Underworld 醒来 + Eugeo 谈 Alice | 不可直接用为本项目起点（项目从"已经在一起"开始） | ✅ 已抓取 |
| Ep.1→Ep.3 之间的"越界 + 带走"是未展开段 | Act 2 中后段 + Act 3（越界 + 整合骑士带走） | ⚠️ 项目原创推进 |
| Ep.3：Alice 已被 Axiom Church 带走 + Selka 担心 Eugeo | 终点后状态证据（**不在本阶段可玩范围**） | ✅ 已抓取 |

> 因此"Pre-Capture 主线 = Ep.1 后半段 + Ep.1→Ep.3 之间的未展开段"，终点以本项目 Act 3 的 `precapture_endpoint: alice_captured`（或等价的 `precapture_alice_captured`）收束。任何在 Act 3 之后继续写 Selka 与 Eugeo 担忧的剧情，**不属于本阶段交付**。
