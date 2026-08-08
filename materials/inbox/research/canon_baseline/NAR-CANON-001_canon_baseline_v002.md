# NAR-CANON-001 — Pre-Capture 正典事实与时间线基线（v002）

- request_id: NAR-CANON-001
- creator/source: Mavis 叙事智能体（基于用户 2026-08-06 反馈修订 v001；保留 v001 不删）
- created_at: 2026-08-06
- replaces: NAR-CANON-001_canon_baseline_v001
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: project-original
- source_url: https://sao-alicization.com/1st/story/01.html ; https://sao-alicization.com/1st/story/02.html ; https://sao-alicization.com/1st/story/03.html ; https://sao-alicization.com/1st/character/ ; https://www.aniplex.co.jp/lineup/sao-alicization/story/
- edits: v002 主要修正：
  1. 玩家 = 桐人（不再以"见习记录员"为第 4 名核心同行者；v001 §0 的"显示名待用户裁决"问题已闭合）
  2. 事实分栏从"官方固定 / 正典留白 / 项目原创"改为更严格的"官方明确 / 原作·动画明确但当前官方网页摘要未覆盖 / 项目原创补充"三类，禁止把"官方页没写"误判为"正典留白"
  3. 把"爱丽丝在 End Mountains 受伤者前越界 → 立即被整合骑士在山侧带走"修正为原作顺序：爱丽丝越界 → 三人返回卢利特村 → 整合骑士来到村中宣告罪名 → 爱丽丝与家人/桐人/尤吉欧告别 → 爱丽丝被带走
  4. 把"静默线 / 第 14.5 页 / 两息风声 / 见报名册桌"等 v001 原创核心从事实表中移除，改为可标注在 `WORLD-MICRO-001` / `NAR-PRECAP-001` 的"项目原创补充（可选支线）"
  5. "End of World" 维持"未确认"判定
- intended_use: 写作者与内容校验器共用的正典事实基线；任何新增事件、NPC 意图、Agent 输出在引用本文件的命名/年龄/时间阶段前必须先核对
- notes: 上一轮被退回的修订已从工作树删除，可通过 Git 历史追溯。本文件不复制动画截图、官方台词、镜头或拆包素材；项目内显示名以 `frontend/src/utils/uwCanonText.js` 为最终裁决。

---

## 0. v002 重要修正（来自用户 2026-08-06 反馈）

1. **核心三人 = 桐人 / 尤吉欧 / 爱丽丝**。玩家即桐人（`kirito`），不是第四名角色。`characters/kirito/README.md` 中"见习记录员"原为桐人在卢利特村的村民岗位（已通过 `OpeningCinematic.vue` 渲染），属"职业身份"，不增加角色数量。
2. **事实分栏三档**：
   - **A. 官方明确**（Official, on-page）：sao-alicization.com 官方页面已直接陈述。
   - **B. 原作·动画明确但当前官方网页摘要未覆盖**（Novel/anime confirmed, official page silent）：广为人知于原作 / 动画，但 sao-alicization.com 的 `1st/story/` 摘要未列出。本类不等于"留白"，更不等于"可以改写"。
   - **C. 项目原创补充**（Project original）：原作与官方页均无对应，本项目为可玩性补全；可作可选支线，**不得**覆盖或替代 A/B 类。
3. **抓捕地点 = 卢利特村内**，不在尽头山脉。整合骑士在村中宣告罪名 → 爱丽丝告别 → 带走。
4. **v001 原创核心（静默线 / 14.5 页 / 两息风声 / 见报名册桌）不再是事实表的固定项**。它们最多作为 C 类"项目原创补充"出现在 `WORLD-MICRO-001` 的可选支线列表里，不进 `NAR-PRECAP-001` 的关键节点表。

## 1. 官方明确（A 类）— 2026-08-06 抓取核对

### 1.1 第 1 季官方故事页 / 角色页（URL = 唯一来源）

| URL | 标题 | 直接证据 |
|---|---|---|
| https://sao-alicization.com/1st/story/01.html | Episode 1: Underworld | "Kirito and his childhood friend Eugeo were raised in Rulid village, and they've been tasked with chopping down a colossal black tree called the Gigas Cedar. This is their Calling. Today, they're at it again, swinging their axe, when their childhood friend Alice arrives with homemade pie for them. As they eat, the three friends decide to venture to the fabled cave in the End Mountains. Both Kirito and Alice alleviate Eugeo's fear that they might be violating the Taboo Index, the laws of their world, and soon enough, it's time for them to set off." |
| https://sao-alicization.com/1st/story/02.html | Episode 2: The Demon Tree | "Kirito wakes up to find himself inside a fantasy game, resembling a mysterious world. His memory is fuzzy, and he attempts to log out, but is unable to return to the real world. … There, he meets a boy named Eugeo. Kirito asks him about the world they're in, but can't find a way to log out. Eugeo then begins to talk about his childhood friend, a girl named Alice." |
| https://sao-alicization.com/1st/story/03.html | Episode 3: The End Mountains | "Kirito makes up his mind to journey to Centoria, the center of the Realm of Humanity in Underworld. … Amidst taking turns with the axe, Eugeo shows Kirito the Blue Rose Sword that he found in the North Cave a long time ago. It occurs to Kirito that with this sword, they may be able to chop down the Gigas Cedar but… Meanwhile, Alice's younger sister Selka is worried about Eugeo, who hasn't smiled since Alice was taken away by the Axiom Church, and opens up to Kirito about her concerns…" |
| https://sao-alicization.com/1st/character/ | CHARACTER | 角色名单包含 Kirito (Kazuto Kirigaya)、Eugeo、Alice (Childhood / Integrity Knight Alice Synthesis Thirty)、Selka、Cardinal、Administrator 等；并写明 Alice "Kirito and Eugeo's childhood friend in the Underworld. The daughter of the chief of Rulid Village, she is skilled in the Sacred Arts"；Deusolbert Synthesis Seven "The seventh Integrity Knight of the Axiom Church. He arrested Alice, who entered the Dark Territory beyond the End Mountains, and took her to the Central Cathedral" |
| https://www.aniplex.co.jp/lineup/sao-alicization/story/ | Aniplex 官方日文故事页 | 与英文版同源；用于交叉核对 |

> **方法学说明**：A 类事实仅以 sao-alicization.com 上**可直接看到**的文本为准；未直接出现在页面上的官方信息（例如动画第 4–18 集的具体台词）不算 A 类。

## 2. 原作·动画明确但当前官方网页摘要未覆盖（B 类）

> B 类来自原作 / 动画在 Alicization War of Underworld 之前的剧情。sao-alicization.com 的故事页只覆盖到 Episode 1–24 概要，并不逐集复述。因此下列条目**不应**被标为"留白"或"项目原创"——它们是原作已知剧情，本项目主线必须忠实还原。

### 2.1 三人前往尽头山脉洞窟与"受伤者"事件（B）

- 桐人、尤吉欧、爱丽丝三人**实际成行**前往 End Mountains 的洞穴。来源：原作《刀剑神域 14 Alicization Beginning》 / Alicization 动画 Season 1（国内通称 Alicization 上半）。
- 洞穴附近存在来自暗黑界的**受伤者 / 倒下的存在**。原作中三人遇到这一存在并尝试处理。
- 爱丽丝因**对受伤者施以援手**而触碰 / 越过禁忌目录规定的"北门不越过"边界。
- 三人在爱丽丝越界后**返回卢利特村**。
- 整合骑士（Deusolbert Synthesis Seven + 数名随行骑士）**来到卢利特村**，宣告爱丽丝违反禁忌目录的罪名。
- 爱丽丝与家人、桐人、尤吉欧**告别**后，被整合骑士带走。
- 此后爱丽丝接受 Synthesis Ritual，成为整合骑士 **Alice Synthesis Thirty**（参考官方角色页"Integrity Knight Alice Synthesis Thirty"段）。

> ⚠️ **本项目原则**：B 类事件是 Pre-Capture 主线**必须忠实复现**的事件链，不可压缩为"在山侧立即被抓"。任何"项目原创"对 B 类事件的改动（如"受伤者其实是村民"或"骑士在山侧埋伏"）**不被允许**。

### 2.2 桐人的现实世界记忆缺口（B）

- 桐人具有"说不清来源的既视感"（misty memory / 既视感），在原作中表现为偶尔对动作 / 习惯的熟悉感，**未给出具体来源解释**直至中后期揭示。
- 在童年阶段，桐人这种"既视感"**只表现为停顿 / 提前做某事**，**不出现**"SAO / 现实世界 / 死亡游戏"等具体关键词。
- 玩家可见表达：在高压瞬间出现"我好像……见过这种——" + 立刻撤回。本项目保持该限制。

### 2.3 Blue Rose Sword 与北方洞窟（B，但不在本项目范围）

- Eugeo 长期持有"从 North Cave 找到的 Blue Rose Sword"（官方 Ep.3 明确："Eugeo shows Kirito the Blue Rose Sword that he found in the North Cave a long time ago"）。
- 童年阶段桐人 / 爱丽丝**不知道**此剑，Eugeo 自己也未必每次都带在身上。
- 本项目 Pre-Capture 阶段**不出现** Blue Rose Sword 实体；只在 Eugeo 提及"北方的工具"时**轻提**。

## 3. 项目原创补充（C 类）— 可选支线，**不得**覆盖 A/B

> C 类是本项目为可玩性补全的内容。它们**不得**进入关键节点、不**得**改写 A/B 事件顺序；最多作为可选活动 / 支线 / 个人观察。

| 类别 | 内容 | 用途 |
|---|---|---|
| C1 | 卢利特村"静默线"附近的两息风声断点 | 可选支线（在 N05 / N06 路径作为"个人观察"出现） |
| C2 | 教会书库"第 14.5 页"夹层 | 可选支线（在 N04 路径作为 Alice 早期判断点） |
| C3 | 见习记录员桌 / 报岗流程 | 玩家作为桐人在村里的日常安排（**不增加第 4 角色**） |
| C4 | 加利塔（北门巡守）人格 / 说话方式 | 村民代表 |
| C5 | 加斯夫特（村务长代行）人格 / 说话方式 | 村务代表 |
| C6 | "北方洞窟前人划痕"细节 | 在 N10 告别场景的石板旁；不暗示 Blue Rose Sword |
| C7 | Alice 父亲近期叮嘱 Alice "不要靠近北门" | 家庭私下对话；不改变主线 |
| C8 | Eugeo 在 N02 提到"北方洞窟里应该还有更顺手的工具" | 不指明 Blue Rose Sword |
| C9 | Alice 永久记忆的内容（"玩家最后没有撒谎"） | 在 N10 写入 NPC 记忆字段；不外显 |

> **C 类的硬约束**：若新增 C 类项目，必须在 `NAR-CANON-001` / `NAR-PRECAP-001` / `WORLD-MICRO-001` 同时显式标注 "C 类"；不进入关键节点表，不写入 `precapture_key_node: true` 的事件。

## 4. 主线顺序（用户 2026-08-06 锁定）

```text
1. 卢利特村三人日常
   ↓
2. 尤吉欧的巨神树天职（Gigas Cedar Calling）
   ↓
3. 三人谈及禁忌目录与尽头山脉
   ↓
4. 前往尽头山脉洞窟
   ↓
5. 接触暗黑界一侧及受伤者（B 类：原作·动画明确）
   ↓
6. 爱丽丝为救人触碰/越过边界（B 类：原作·动画明确）
   ↓
7. 三人返回卢利特村（B 类：原作·动画明确）
   ↓
8. 整合骑士来到村中宣告罪名（B 类：原作·动画明确）
   ↓
9. 爱丽丝与家人、桐人、尤吉欧告别（B 类：原作·动画明确）
   ↓
10. 爱丽丝被带走（A/B 类；A 由官方角色页 Deusolbert 描述 "took her to the Central Cathedral" 支撑）
```

> **A/B/C 标注规则**：
> - 步骤 1–2 涉及 A 类（Ep.1）+ C 类（细节补充）。
> - 步骤 3–4 涉及 A 类（Ep.1 "they decide to venture"）+ C 类（细节补充）。
> - 步骤 5–10 全部为 B 类（原作·动画明确，但官方网页未逐句摘要）。**这些步骤是 Pre-Capture 终点前的关键节点素材，不得替换为 C 类原创。**

## 5. 关于"End of World"的处置

- 2026-08-06 复核官方动画故事页，**未发现以"End of World"为标题的《刀剑神域》正传电影条目**。A 类官方页面标题为 `Underworld`、`The Demon Tree`、`The End Mountains` 等。
- "End of World"在本项目历史记录中曾作为 `Underworld` 与 `The End Mountains` 的混称使用（参考 `docs/PROJECT.md` 的术语与叙事边界）。
- 处置原则：在本项目玩家可见文本与本系列素材中**不出现"End of World"**。若用户后续提供明确指向"End of World"为另一部作品的链接/片名/截图，先建立带来源的新参考对象版本，**不覆盖本次官方核实**。

## 6. 角色显示名最终裁决

- 玩家角色显示名 = **桐人**（用户 2026-08-06 明确）。
- 内部 id = `kirito`。
- `uwCanonText.js` 与 `OpeningCinematic.vue` 中"见习记录员"是桐人在卢利特村的**村民岗位**渲染（职业身份），不是第四名角色。本项目在玩家面向文本中**保留**这个岗位渲染，**不**再以此制造新角色。
- v001 §3.0 的"显示名待用户裁决"问题在 v002 闭合。

## 7. 关键内部矛盾修复（来自用户 2026-08-06 反馈）

| 序 | v001 问题 | v002 修正 |
|---|---|---|
| K1 | v001 把"在 End Mountains 越界后立即被整合骑士在山侧带走"作为终点 | v002 改为"三人返回卢利特村 → 整合骑士来到村中宣告 → 告别 → 带走" |
| K2 | v001 把"静默线 / 14.5 页 / 两息风声 / 见报名册桌"作为关键节点的推动力 | v002 降为 C 类可选支线，不进关键节点表 |
| K3 | v001 把"见习记录员"列为"核心 7 人之一"，等于新增第 4 名同行者 | v002 玩家 = 桐人；见习记录员是桐人的村民岗位，不增加角色 |
| K4 | v001 把"原作没明说"的剧情（被俘在山侧、整合骑士数息出现）当作"正典留白 + 项目原创推进" | v002 严格区分 A / B / C 三类；B 类（受伤者、返回、宣告、告别、带走）必须忠实还原 |
| K5 | v001 把"桐人"显示名问题挂起为"待用户裁决" | v002 闭合：玩家显示名 = 桐人 |
| K6 | v001 的"中央层级"中误把"整合骑士"列入 Pre-Capture 频繁出现角色 | v002 限定整合骑士仅在 N09 / N10 出现在村中，其余时间**不出现** |
| K7 | v001 把"记录员"作为叙事第三人称观察者，导致 v001 N01–N10 的部分选择以"看见/记下/不说"为主语 | v002 全部改回"桐人"为主语；保留桐人"既视感"限制 |

## 8. 旧 v001 备注（保留供对比）

- v001 status = `changes_requested`（MANIFEST）。
- v001 备注："v001 delivered 2026-08-06 by Mavis"。
- v001 核心问题：N01–N10 主线偏离原作童年事件链（被改写为"在山侧越界即被抓"），且"静默线 / 14.5 页 / 两息风声 / 见报名册桌"成为推动主线的核心原创元素，违反了"忠实还原 Alicization 童年回忆"的要求。
- v002 仍可参考 v001 的宏观结构（人界 / 暗黑界 / 整合骑士 / 禁忌目录 / Centoria），但 N01–N10 节点表整体重写。
