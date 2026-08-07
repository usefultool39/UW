# WORLD-MACRO-001 — Underworld 宏观世界设定（Pre-Capture 范围）

- request_id: WORLD-MACRO-001
- creator/source: Mavis 叙事智能体（基于 `NAR-CANON-001`、官方角色/故事页与 `docs/research/UNDERWORLD_REFERENCE_BASELINE.md`）
- created_at: 2026-08-06
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/ ; https://www.aniplex.co.jp/lineup/sao-alicization/story/
- edits: none
- intended_use: 编剧 / 资料 / Agent system prompt 共用的宏观世界约束；`NAR-PRECAP-001`、`CHAR-DEPTH-001`、`WORLD-MICRO-001` 全部以本文件的"正典固定/留白/原创"分栏为前提
- notes: 本文件只写到 Alice 被带走为止；中央大教堂内部政治、整合骑士训练、暗黑界大战、War of Underworld 战后状态不在本文件范围。每条宏观设定都标 `[官方固定]` / `[正典留白]` / `[项目原创]`。

---

## 0. 范围声明

- **空间范围**：人界（Human Empire）为主，包含卢利特村、北境、Centoria（中央都市）、中央大教堂（Central Cathedral）；暗黑界（Dark Territory）只作"尽头山脉之外"的远方存在被敬畏提及。
- **时间范围**：Alice 越界前 → Alice 被整合骑士带走。**不写** Alice 进入中央大教堂之后；**不写** Eugeo 与 Kirito 进入剑术学院；**不写** War of Underworld 战后。
- **目标读者**：编剧、AI agent、QA 校验器。
- **术语裁决**：玩家可见文本以 `frontend/src/utils/uwCanonText.js` 为唯一裁决；本文件用 `uwCanonText` 规范译名。

## 1. 顶层结构：人界 vs 暗黑界

| 区域 | 官方固定 | 项目约束 |
|---|---|---|
| 人界（Human Empire） | 官方角色页 Administrator 描述："a singular entity who rules the people of the Human Empire" | 玩家在 Pre-Capture 阶段只见到边缘地带（卢利特村、北境、Centoria 作为远景）。 |
| 暗黑界（Dark Territory） | 官方角色页 Deusolbert 描述："the Dark Territory beyond the End Mountains" | 仅以"尽头山脉另一侧"作敬畏口吻；不描写具体生物、不出现具体地名。 |
| 尽头山脉（End Mountains） | 官方 Ep.1："the fabled cave in the End Mountains" | Pre-Capture 终点边界；不可越界后仍"游戏正常进行"。 |
| 中央大教堂（Central Cathedral） | 官方角色页 Cardinal 描述："the great library within the Central Cathedral" | **仅在远处 / 传闻层级出现**；玩家不能进入。 |
| Centoria（中央都市） | 官方 Ep.3："the central city, Cenotria" | 在卢利特村可被村民偶尔提到；不直接出现。 |

> 来源：https://sao-alicization.com/1st/character/

## 2. 权力结构

### 2.1 中央层级 `[官方固定]`

- 最高司祭（Administrator / Pontifex）：Axiom Church 最高司祭，"rules the people of the Human Empire"。**玩家在 Pre-Capture 阶段不会遇到，也不允许在玩家可见文本里出现其具体姓名 / 长相 / 政治动作**。
- 元老院（参议院 / Council of Elders）：本项目 `uwCanonText` 与 `voice bible` 已锁定的术语。元老院对村民是"禁忌目录背后那个看不见的权威"，在 Pre-Capture 阶段不出现具体人名、席位、内部流程。
- 整合骑士（Integrity Knight）：由"最高司祭"主持的"Synthesis Ritual"产生（参考官方 Eugeo 角色页 "Eugeo's appearance after undergoing Administrator's Synthesis Ritual"）。**Pre-Capture 阶段仅 Deusolbert Synthesis Seven（或 1–2 名次级骑士）以"远方来人"身份出现**；不暴露其编号 / 神器 / 完整名字。

### 2.2 村务层级 `[项目原创 + 正典留白]`

- 村务长：Alice 父亲（官方仅说"the daughter of the chief of Rulid Village"）；本项目 `meta.json` 中尚未独立建立 `rulid_chief` id，由 `rulid_elder`（加斯夫特）代行村务。
- 北门巡守：加利塔（`garret`）。
- 见习疗愈者：赛尔卡（`selka`），在教会书库帮手。
- 见习记录员：玩家；定位为"先听后记"的村内观察岗位，**不进入任何村务决策**。

### 2.3 整合骑士在 Pre-Capture 阶段的可见度 `[项目原创]`

- 卢利特村**没有整合骑士常驻**；村民对其认知停留在"远方来的、没人见过真面目的权威"。
- 整合骑士的到来**只触发一次**（在 `N10`），且不被预警。
- 整合骑士在玩家面前**不会**透露其"Synthesis 编号"、神器、过往履历；只执行"Axiom Church 带走该名越界者"的标准动作。

## 3. 法律：禁忌目录（Taboo Index）

| 维度 | 描述 | 来源 |
|---|---|---|
| 定义 | 官方 Ep.1："the Taboo Index, the laws of their world" | https://sao-alicization.com/1st/story/01.html |
| 玩家可见条目 | 仅"北门不越过"等可观察条目 | 项目原创（与 `voice bible` §0.2 一致） |
| 执行主体 | Axiom Church / 整合骑士（远端执行） | https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/ |
| 村民对它的理解 | 敬畏 + 不完全理解 | 官方 Ep.1 "Eugeo's fear that they might be violating the Taboo Index" |
| 与可玩性的关系 | "它通常能让人活着回来"，但**不能解释北境全部异常** | 项目原创约束（来自 `NAR-PRECAP-001` `N05` 与 `N09`） |

> **不可写**：禁忌目录的具体条文原文（避免与官方文本逐字重复）；禁忌目录的惩罚机制细节；禁忌目录与整合骑士之间的具体通信流程。

## 4. 信仰：神圣术（Sacred Arts）

| 维度 | 描述 | 来源 |
|---|---|---|
| 性质 | "Sacred Arts" 是 Underworld 中可习得的术式体系；Alice 擅长 | https://sao-alicization.com/1st/character/ |
| 在卢利特村的可观察表现 | 治疗、读/写记录、做标记、存物、简短的记号 | 项目原创 + `uwCanonText` 锁定 |
| 与禁忌目录的关系 | 神圣术不直接违犯禁忌，但部分应用（如"做标记"）**在某些场景下会触发"压感"** | 项目原创（`NAR-PRECAP-001` `N05` 与 `N09`） |
| 玩家能否学 | 玩家作为"见习记录员"**不会**学到战斗级术式；可学到"读记录"与"做标记"两档基础 | 项目原创约束 |

## 5. 军事：整合骑士体系

| 维度 | 描述 | 来源 |
|---|---|---|
| 角色 | 整合骑士是 Axiom Church 的执法力量 | https://sao-alicization.com/1st/character/ |
| 数量与编号 | Eugeo "Synthesis Thirty-Two"、Alice "Synthesis Thirty"、Deusolbert "Synthesis Seven"、Fanatio "Synthesis Two"、Bercouli "Synthesis One" | https://sao-alicization.com/1st/character/ |
| Pre-Capture 阶段可见度 | 仅 Deusolbert（或一名同级骑士）在 `N10` 出现；不展示 Synthesis 编号 | 项目原创约束（剧透护栏） |
| 武器 | Eugeo 后期有"Blue Rose Sword"、Fanatio 有"Heaven-Piercing Blade"、Bercouli 有"Time-Splitting Sword"——**Pre-Capture 阶段全部不可见** | https://sao-alicization.com/1st/character/ （剧透护栏） |
| 与村民关系 | 村民从没人见过整合骑士在村里；只通过教会回廊的"远行回访"听到一些 | 项目原创 |

## 6. 资源

| 资源 | 来源 | Pre-Capture 阶段的可玩表现 |
|---|---|---|
| 食物 | 项目原创 | 干粮 / 汤 / 馅饼（爱丽丝送餐） |
| 木材 | 巨神树（基加斯西达） | 伐木手天职的产出 |
| 神圣力 | 神圣术使用者（Alice、Selka、书库） | 神圣术可观察表现（标记、读/写） |
| 天命 | 官方体系（HP/MP） | 玩家与 NPC 的体力 / 状态；不可直接显示为"HP" |

> **不可写**：任何具体的"金币" / "通货"系统；任何"等级 / 经验值"暴露。

## 7. 信息传播

| 渠道 | 描述 |
|---|---|
| 教会书库 | 旧记录 / 神圣术教材 / 禁忌目录节选；由 Selka 与书库其他帮手保管。 |
| 村务会议 | 村务长（Alice 父亲 / 加斯夫特代行）召集；公布禁忌目录变更与"安全提醒"。 |
| 北门值班记录 | 加利塔每日填写；与教会书库可互查。 |
| 村道传闻 | 村民口耳相传；与 N05/N06 的"是否上报"流程形成对照。 |
| 三人内部记录 | Eugeo 与玩家的记录本 + Alice 的判断 + 见习记录员的抄件；是 `N04`/`N05`/`N10` 的关键证据。 |

> **项目原创约束**：上述五种渠道必须能被玩家在 `N04`/`N05`/`N06` 三个 Act 1 节点里**至少各接触到一次**，且玩家可对每条渠道**选择信任度**。

## 8. 哪些是正典固定 / 留白 / 原创

| 类别 | 内容 |
|---|---|
| 官方固定 | 卢利特村、巨神树、尽头山脉、禁忌目录、Centoria、中央大教堂、人界 / 暗黑界二元、Axiom Church、整合骑士（编号、Synthesis 仪式）、Alice / Eugeo / Selka / Kirito 身份、Alice 后期为"Alice Synthesis Thirty"、Eugeo 后期为"Eugeo Synthesis Thirty-Two"、Deusolbert 在 End Mountains 带走 Alice、Cardinal 是大教堂图书馆内的自治程序、Administrator 是最高司祭与人界统治者 |
| 正典留白 | 禁忌目录具体条文、卢利特村日常细节、Alice 何时越界、Eugeo 何时从北洞窟找到 Blue Rose Sword、北门静默线、整合骑士在卢利特村的可见度、Selka 在 Alice 被带走后的具体生活变化 |
| 项目原创 | 见习记录员身份、见报名册桌、巨神树伐木场"两息风声"信号、加利塔 / 加斯夫特 / `rulid_chief` 三层村务结构、玩家 UI 上的"线索 / 记录 / 紧张 / 承诺 / 记忆"五维、`N01–N10` 全部四幕事件 |

## 9. 宏观关系速查图（项目内 ASCII 速查）

```
                  ┌───────────────────────────────┐
                  │   最高司祭 (Administrator)     │   ← Pre-Capture 阶段不可见
                  │   Axiom Church 最高司祭        │
                  └──────────────┬────────────────┘
                                 │
                  ┌──────────────▼────────────────┐
                  │   元老院 / 整合骑士团         │   ← 整合骑士只在 N10 出现一次
                  │   (Integrity Knights 1..N)    │
                  └──────────────┬────────────────┘
                                 │ 远端执行禁忌目录
                                 │
              ┌──────────────────▼──────────────────────┐
              │      禁忌目录 (Taboo Index)              │   ← 玩家可见条目极少
              └──────────────────┬──────────────────────┘
                                 │
              ┌──────────────────▼──────────────────────┐
              │      卢利特村 (Rulid Village)            │
              │  ┌──────────────────────────────────┐  │
              │  │ 村务长 (Alice 父亲 / 加斯夫特代行) │  │
              │  │ 北门巡守 (加利塔)                 │  │
              │  │ 神圣术见习 (爱丽丝 / 赛尔卡)       │  │
              │  │ 巨神树伐木手 (尤吉欧)             │  │
              │  │ 见习记录员 (玩家)                  │  │
              │  └──────────────────────────────────┘  │
              │     巨神树伐木场 ←──→ 北门 ←──→ 教会    │
              │                          ↓             │
              │                    尽头山脉 (End Mtns)  │
              │                          ↓ 越界        │
              │                    暗黑界 (远端不可见)  │
              └─────────────────────────────────────────┘
```

> 图中所有"远端"层级在 Pre-Capture 阶段**只可被敬畏提及，不可被进入 / 详细描写**。

## 10. 完成定义

- ✅ 覆盖人界 / 暗黑界 / 中央大教堂 / 整合骑士 / 禁忌目录五大宏观主题。
- ✅ 权力结构 / 法律 / 信仰 / 军事 / 资源 / 信息传播六维均给出项目约束。
- ✅ 每条宏观设定都标 `[官方固定]` / `[正典留白]` / `[项目原创]`。
- ✅ 不写 Alice 被带走之后的宏观状态。
- ✅ 不复制动画截图、官方台词、镜头或拆包素材。
