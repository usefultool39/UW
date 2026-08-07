# WORLD-MACRO-001 — Underworld 宏观世界设定（v002，Pre-Capture 范围）

- request_id: WORLD-MACRO-001
- creator/source: Mavis 叙事智能体（基于用户 2026-08-06 反馈修订 v001；保留 v001 不删）
- created_at: 2026-08-06
- replaces: WORLD-MACRO-001_world_bible_v001
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/ ; https://www.aniplex.co.jp/lineup/sao-alicization/story/
- edits: v002 主要修正：
  1. 整合骑士在 Pre-Capture 阶段**只在 N08 / N09 / N10 出现在村中**（不在 N05 / N06 出现在山侧、不在山侧执行"立即逮捕"）
  2. 三栏分类与 `NAR-CANON-001` v002 §0 对齐：A 官方明确 / B 原作·动画明确但当前官方网页摘要未覆盖 / C 项目原创补充
  3. 不再把"爱丽丝在山侧被带走"作为 v001 终点；改为"在卢利特村被带走"
  4. 不再把"中央层级"在 Pre-Capture 阶段作为可玩角色；整合骑士仅在 N08 之后作为可玩投影
- intended_use: 编剧 / 资料 / Agent system prompt 共用的宏观世界约束；`NAR-PRECAP-001`、`CHAR-DEPTH-001`、`WORLD-MICRO-001` 全部以本文件的"分类分栏"为前提
- notes: v001 保留在 `materials/inbox/writing/world_bible/WORLD-MACRO-001_world_bible_v001.md`，MANIFEST 状态 = `changes_requested`。本文件只写到 Alice 被带走为止；中央大教堂内部政治、整合骑士训练、暗黑界大战、War of Underworld 战后状态不在本文件范围。

---

## 0. 范围声明

- **空间范围**：人界（Human Empire）为主，包含卢利特村、北境、Centoria（中央都市）、中央大教堂（Central Cathedral）；暗黑界（Dark Territory）只作"尽头山脉之外"的远方存在被敬畏提及。
- **时间范围**：Alice 越界前 → Alice 被整合骑士从卢利特村带走。**不写** Alice 进入中央大教堂之后；**不写** Eugeo 与 Kirito 进入剑术学院；**不写** War of Underworld 战后。
- **目标读者**：编剧、AI agent、QA 校验器。
- **术语裁决**：玩家可见文本以 `frontend/src/utils/uwCanonText.js` 为唯一裁决；本文件用规范译名。
- **三栏分类**：A = 官方明确；B = 原作·动画明确但当前官方网页摘要未覆盖；C = 项目原创补充。

## 1. 顶层结构：人界 vs 暗黑界

| 区域 | 分类 | 描述 | 来源 |
|---|---|---|---|
| 人界（Human Empire） | A | 官方角色页 Administrator 描述："a singular entity who rules the people of the Human Empire" | https://sao-alicization.com/1st/character/ |
| 暗黑界（Dark Territory） | A | 官方角色页 Deusolbert 描述："the Dark Territory beyond the End Mountains" | https://sao-alicization.com/1st/character/ |
| 尽头山脉（End Mountains） | A | 官方 Ep.1："the fabled cave in the End Mountains" | https://sao-alicization.com/1st/story/01.html |
| 中央大教堂（Central Cathedral） | A | 官方角色页 Cardinal 描述："the great library within the Central Cathedral" | https://sao-alicization.com/1st/character/ |
| Centoria（中央都市） | A | 官方 Ep.3："the central city, Cenotria" / 角色页"Cenotria" | https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/ |
| 北方洞窟（North Cave） | A | 官方 Ep.3："the Blue Rose Sword that he found in the North Cave a long time ago" | https://sao-alicization.com/1st/story/03.html |

> 项目约束（A）：玩家在 Pre-Capture 阶段**不**进入 Centoria、Central Cathedral、Dark Territory 内部；仅以敬畏口吻出现。

## 2. 权力结构

### 2.1 中央层级 `[A]`

- 最高司祭（Administrator / Pontifex）：Axiom Church 最高司祭，"rules the people of the Human Empire"。**玩家在 Pre-Capture 阶段不会遇到，也不允许在玩家可见文本里出现其具体姓名 / 长相 / 政治动作**。
- 元老院（Council of Elders）：本项目 `uwCanonText` 与 `voice bible` 已锁定的术语。元老院对村民是"禁忌目录背后那个看不见的权威"，在 Pre-Capture 阶段不出现具体人名、席位、内部流程。
- 整合骑士（Integrity Knight）：由最高司祭主持的 Synthesis Ritual 产生（A：参考官方 Eugeo 角色页 "Eugeo's appearance after undergoing Administrator's Synthesis Ritual"）。

### 2.2 整合骑士在 Pre-Capture 阶段的可见度 `[B + C]`

- **可见时间窗**：仅 `N08`（来到村中宣告）、`N09`（在告别现场）、`N10`（在北门外带走）。**不**在 N05 / N06 出现（爱丽丝越界瞬间**不**有整合骑士在场）。
- **可见地点**：仅卢利特村内（中央广场、北门外）。**不**在尽头山脉或森林中段出现。
- **可见人数**：Deusolbert Synthesis Seven + 2 名次级骑士（C：项目原创占位 id `knight_secondary_a` / `knight_secondary_b`）。
- **不展示**：整合骑士的完整名字（B 级保护：只说"整合骑士" + "来自中央大教堂"）、Synthesis 编号在 N10 之前**不**出现在玩家面向文本中（B 级保护）。

> v001 错误修正：v001 曾将"整合骑士"作为"中央层级可玩投影"在多个场景出现，v002 限定为**仅 N08/N09/N10 在村中**。

### 2.3 村务层级 `[A + C]`

- 村务长代行：加斯夫特（`rulid_elder`），代行 Alice 父亲（"the chief of Rulid Village"，A）的村务；本项目 `meta.json` 已存在 `rulid_elder` id。
- Alice 父亲：项目原创占位 `rulid_chief`，**在 N08 / N09 出现**（A：Alice 是 "the daughter of the chief of Rulid Village"），不作为可玩 NPC。
- 北门巡守：加利塔（`garret`），C 类项目原创。
- 见习疗愈者：赛尔卡（`selka`），A：Alice 的妹妹（官方角色页）。
- 见习记录员：**桐人在卢利特村的村民岗位**（C：项目原创；不是新角色）。

> **关键修正**：v001 曾把"见习记录员"列为"中央层级独立角色"，v002 明确为"桐人的村民岗位"，不增加第 4 名角色。

## 3. 法律：禁忌目录（Taboo Index）

| 维度 | 分类 | 描述 | 来源 |
|---|---|---|---|
| 定义 | A | 官方 Ep.1："the Taboo Index, the laws of their world" | https://sao-alicization.com/1st/story/01.html |
| 玩家可见条目 | C | 仅"北门不越过"等可观察条目 | 项目原创（与 `voice bible` §0.2 一致） |
| 执行主体 | A + B | Axiom Church / 整合骑士（远端执行）；具体在 Pre-Capture 阶段表现为整合骑士来到村中宣告与带走 | A：官方角色页 Deusolbert 描述；B：原作·动画明确"来到村中宣告"过程 |
| 村民对它的理解 | A + C | 敬畏 + 不完全理解（A：官方 Ep.1 "Eugeo's fear that they might be violating the Taboo Index"）；具体敬畏表达 C 类项目原创 | https://sao-alicization.com/1st/story/01.html |
| 与可玩性的关系 | C | 玩家在 N03 决定"讨论深度"；在 N06 看见 Alice 越界；在 N08 听到整合骑士宣告 | 项目原创约束 |

> **不可写**（B 类原作保护）：禁忌目录的具体条文原文；禁忌目录的惩罚机制细节；禁忌目录与整合骑士之间的具体通信流程。

## 4. 信仰：神圣术（Sacred Arts）

| 维度 | 分类 | 描述 | 来源 |
|---|---|---|---|
| 性质 | A | 官方角色页：Alice "is skilled in the Sacred Arts" | https://sao-alicization.com/1st/character/ |
| 在卢利特村的可观察表现 | C | 治疗、读/写记录、做标记、存物、简短的记号 | 项目原创 |
| 与禁忌目录的关系 | C | 神圣术不直接违犯禁忌，但部分应用在某些场景下会触发"压感" | 项目原创 |
| 玩家能否学 | C | 玩家作为桐人**不会**学到战斗级术式；可学"读记录"与"做标记"两档基础 | 项目原创约束 |

## 5. 军事：整合骑士体系

| 维度 | 分类 | 描述 | 来源 |
|---|---|---|---|
| 角色 | A | 整合骑士是 Axiom Church 的执法力量 | https://sao-alicization.com/1st/character/ |
| 数量与编号 | A | Deusolbert Synthesis Seven、Alice Synthesis Thirty、Eugeo Synthesis Thirty-Two、Fanatio Synthesis Two、Bercouli Synthesis One 等 | https://sao-alicization.com/1st/character/ |
| Pre-Capture 阶段可见度 | B + C | 仅 N08 / N09 / N10 在村中；B：原作明确整合骑士来到村中；C：具体投影方式（3 名骑士 + 公告 + 带走）由本项目在不剧透前提下原创 | https://sao-alicization.com/1st/character/ |
| 武器 | A | 整合骑士有多种神器（Blue Rose Sword、Heaven-Piercing Blade、Time-Splitting Sword） | https://sao-alicization.com/1st/character/ |
| Pre-Capture 阶段武器可见度 | C | **N08 / N09 / N10 不展示任何整合骑士的神器**（属后续阶段剧透保护） | 项目原创约束 |
| 与村民关系 | B + C | 村民从没人见过整合骑士在村里；B：原作明确；C：具体"敬畏但不太懂"由本项目原创 | 项目原创 |

> **B 类原作保护**：N10 之前玩家面向文本**不**出现 Synthesis 编号、不出现神器名字、不出现整合骑士在中央大教堂的训练生活。

## 6. 资源

| 资源 | 分类 | 描述 |
|---|---|---|
| 食物 | C | 干粮 / 汤 / 馅饼（爱丽丝送餐） |
| 木材 | A | 巨神树（基加斯西达） |
| 神圣力 | C | 神圣术使用者（Alice、Selka、书库） |
| 天命 | A | 官方体系（HP/MP）；Pre-Capture 阶段不显示具体数值 |

> **不可写**：任何具体的"金币 / 通货"系统；任何"等级 / 经验值"暴露。

## 7. 信息传播

| 渠道 | 分类 | 描述 |
|---|---|---|
| 教会书库 | A + C | 旧记录 / 神圣术教材 / 禁忌目录节选；由 Selka 与书库其他帮手保管。 |
| 村务会议 | A + C | 村务长（Alice 父亲 / 加斯夫特代行）召集；公布禁忌目录变更与"安全提醒"。 |
| 北门值班记录 | A + C | 加利塔每日填写；与教会书库可互查。 |
| 村道传闻 | C | 村民口耳相传；N03 之前可能影响三人的讨论氛围。 |
| 三人内部记录 | C | 桐人 / Eugeo 的记录本 + Alice 的判断；N10 的最后一份记录属此渠道。 |

> **C 类项目原创约束**：上述五种渠道在 N01–N10 关键节点中**不**作为单独关键节点出现；可作为可选支线。

## 8. 哪些是 A / B / C

### 8.1 A（官方明确）
卢利特村、巨神树、尽头山脉、禁忌目录、Centoria、中央大教堂、人界 / 暗黑界二元、Axiom Church、整合骑士（编号、Synthesis 仪式）、Alice / Eugeo / Selka / Kirito 身份、Alice 后期为 "Alice Synthesis Thirty"、Eugeo 后期为 "Eugeo Synthesis Thirty-Two"、Deusolbert 在 End Mountains 带走 Alice 之事后的"took her to the Central Cathedral"、Cardinal 是大教堂图书馆内的自治程序、Administrator 是最高司祭与人界统治者。

### 8.2 B（原作·动画明确但当前官方网页摘要未覆盖）
- 三人前往 End Mountains 洞窟附近，遇到来自暗黑界的受伤者 / 倒下的存在
- 爱丽丝因施援受伤者而触碰 / 越过禁忌目录规定的"北门不越过"边界
- 三人在爱丽丝越界后返回卢利特村
- 整合骑士 Deusolbert Synthesis Seven + 随行骑士来到卢利特村宣告爱丽丝违反禁忌目录
- 爱丽丝与家人、桐人、尤吉欧告别
- 整合骑士将爱丽丝带往中央大教堂
- 桐人在童年阶段具有"既视感"，表现为偶尔对动作 / 习惯的熟悉感，**未**给出具体来源

### 8.3 C（项目原创补充）
- 桐人作为"见习记录员"村民岗位（不增加新角色）
- 卢利特村北门"静默线"附近的两息风声断点
- 教会书库"第 14.5 页"夹层
- 加利塔（北门巡守）人格
- 加斯夫特（村务长代行）人格
- 北方洞窟的"前人划痕"细节（N10 之后才可能被提到，不在 Pre-Capture 范围）
- Alice 父亲近期叮嘱 Alice "不要靠近北门"
- Eugeo 在 N02 提到"北方洞窟里应该还有更顺手的工具"
- 整合骑士在 N08 / N09 / N10 的具体台词模板与"3 句对话上限"投影方式

> **C 类的硬约束**：若新增 C 类项目，必须在 `NAR-CANON-001` / `NAR-PRECAP-001` / `WORLD-MICRO-001` 同时显式标注 "C 类"；不进入关键节点表，不写入 `precapture_key_node: true` 的事件。

## 9. 宏观关系速查图（项目内 ASCII 速查）

```
                  ┌───────────────────────────────┐
                  │   最高司祭 (Administrator)     │   ← Pre-Capture 阶段不可见（A）
                  │   Axiom Church 最高司祭        │
                  └──────────────┬────────────────┘
                                 │
                  ┌──────────────▼────────────────┐
                  │   元老院 / 整合骑士团         │   ← 仅 N08/N09/N10 在村中
                  │   (Integrity Knights 1..N)    │   ← B + C：N08 来到村中宣告
                  └──────────────┬────────────────┘
                                 │ 远端执行禁忌目录
                                 │
              ┌──────────────────▼──────────────────────┐
              │      禁忌目录 (Taboo Index)              │   ← A：玩家可见条目极少
              └──────────────────┬──────────────────────┘
                                 │
              ┌──────────────────▼──────────────────────┐
              │      卢利特村 (Rulid Village)            │   ← A：玩家在此出生成长
              │  ┌──────────────────────────────────┐  │
              │  │ 村务长 (Alice 父亲 / 加斯夫特代行) │  │   ← A + C
              │  │ 北门巡守 (加利塔)                 │  │   ← C
              │  │ 神圣术见习 (爱丽丝 / 赛尔卡)       │  │   ← A
              │  │ 巨神树伐木手 (桐人 / 尤吉欧)       │  │   ← A：玩家 = 桐人
              │  │ 见习记录员 (桐人的村民岗位)        │  │   ← C：不增加新角色
              │  └──────────────────────────────────┘  │
              │     巨神树伐木场 ←──→ 北门 ←──→ 教会    │
              │                          ↓             │
              │                    尽头山脉 (End Mtns)  │   ← A
              │                          ↓ 越界 (B)    │
              │                    暗黑界 (远端不可见)  │   ← A
              │                                         │
              │  ←←← 三人返回卢利特村 (B) ←←←←←←←←←←←←←│
              │                                         │
              │  N08 整合骑士来到村中宣告 (B)            │
              │  N09 爱丽丝与家人/桐人/尤吉欧告别 (B)   │
              │  N10 爱丽丝被带走 (A + B, ENDPOINT)     │
              └─────────────────────────────────────────┘
```

> 图中所有"远端"层级在 Pre-Capture 阶段**只可被敬畏提及，不可被进入 / 详细描写**。

## 10. 完成定义

- ✅ 覆盖人界 / 暗黑界 / 中央大教堂 / 整合骑士 / 禁忌目录五大宏观主题。
- ✅ 权力结构 / 法律 / 信仰 / 军事 / 资源 / 信息传播六维均给出 A/B/C 项目约束。
- ✅ 每条宏观设定都标 A / B / C 三类。
- ✅ 不写 Alice 被带走之后的宏观状态。
- ✅ 整合骑士仅 N08 / N09 / N10 在村中可见，**不**在山侧出现。
- ✅ 不复制动画截图、官方台词、镜头或拆包素材。
