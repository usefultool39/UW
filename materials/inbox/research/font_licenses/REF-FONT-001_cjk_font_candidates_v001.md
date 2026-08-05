# REF-FONT-001_cjk_font_candidates_v001

- request_id: REF-FONT-001
- creator/source: 项目调研（CodeBuddy Code 辅助核实）
- created_at: 2026-08-04
- tool_model: CodeBuddy Code / hy3
- prompt: none（非 AI 生成素材，为人工调研文档）
- negative_prompt: none
- seed/settings: none
- license: 本文件自身为项目自有文档（owned）；文中所列各字体许可证以逐条标注为准
- source_url: 见正文每套组合的「官方来源」栏，全部为 2026-08-04 实际访问并返回 HTTP 200 的链接
- edits: none
- intended_use: reference（字体选型与法务评估依据，不作为字体文件本身的授权凭证）
- notes: |
  所有许可证结论均来自实际抓取的 LICENSE 原文或官方法律声明页面，未采信二手转述。
  无法从权威一手来源核实的条目一律标注 `unknown / 未核实`，不得进入 approved。
  文件体积分两类：标注「实测」的来自 GitHub Release API 或 jsDelivr 包索引返回的真实字节数；
  标注「估算」的为按压缩比推算，未实测，使用前需自行验证。

---

## 0. 核实方法与证据链

本轮核实于 **2026-08-04** 完成，方法如下（不依赖记忆断言）：

| 手段 | 用途 | 说明 |
|---|---|---|
| `GitHub Releases API` | 版本号、发布日期、资产真实体积 | `api.github.com/repos/{owner}/{repo}/releases/latest` |
| `raw.githubusercontent.com` 抓 LICENSE 原文 | 许可证名称、保留字体名（RFN）、附加条款 | 读取全文而非依赖 GitHub 侧边栏的自动识别 |
| `jsDelivr Data API` | woff2 分片真实字节数、字重枚举 | `data.jsdelivr.com/v1/packages/npm/...` |
| `curl` HTTP 状态码探测 | 确认每个引用 URL 实际可打开 | 全部返回 200 才写入本文档 |
| 官方法律声明页直读 | 厂商免费商用协议条款 | 阿里巴巴普惠体走语雀官方法律声明页 |

**重要提示**：GitHub 仓库页侧边栏对 `adobe-fonts/source-han-sans` 与 `source-han-serif` 显示 `NOASSERTION`（无法自动识别），
但直接读取 `LICENSE.txt` 全文可确认为 **SIL OFL 1.1**。本文档以原文为准。

---

## 1. 五套候选组合总览

| 套 | 标题 | 正文 | 数字 | 许可证综合结论 | Web 嵌入 | 建议 |
|---|---|---|---|---|---|---|
| **A** | Source Han Serif SC | Noto Sans CJK SC | Inter | 全 OFL 1.1，零商用风险 | 允许 | **主推（UI 主力）** |
| **B** | Smiley Sans 得意黑 | Noto Sans CJK SC | Inter | 全 OFL 1.1，零商用风险 | 允许 | 备选（标题更有个性） |
| **C** | Source Han Serif SC | LXGW WenKai 霞鹜文楷 | IBM Plex Mono | 全 OFL 1.1（文楷含附加许可） | 允许，有明确条件 | **主推（叙事/书库文本）** |
| **D** | Alibaba PuHuiTi 3.0 | Alibaba PuHuiTi 3.0 | Inter | 厂商免费商用，但**未授予再分发/转换权** | **不可**（见 §2.4） | 仅限桌面设计稿 |
| **E** | 站酷系列 | — | — | **unknown / 未核实** | unknown | **不批准** |

---

## 2. 逐套详情

### 2.1 组合 A —— 全 OFL 安全基线（主推 · UI 主力）

| 角色 | 字体全名 | 版本 | 发布日期 |
|---|---|---|---|
| 标题 | Source Han Serif SC（思源宋体 简体中文） | **2.003R** | 2024-07-30 |
| 正文 | Noto Sans CJK SC（思源黑体 Google 版） | **Sans2.004** | 2022-01-27 |
| 数字 | Inter | **v4.1** | 2024-11-16 |

**许可证（逐条核实）**

- **Source Han Serif**：SIL Open Font License 1.1。LICENSE 原文首句实测为
  `Copyright 2017-2022 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'. Source is a trademark of Adobe in the United States and/or other countries.`
  → **保留字体名为 `Source`，且 `Source` 同时是 Adobe 注册商标。**
- **Noto Sans CJK**：SIL Open Font License 1.1。实测 `Sans/LICENSE` 全文**未声明任何保留字体名**——
  文件直接以 `This Font Software is licensed under the SIL Open Font License, Version 1.1.` 开头，
  文中出现的 "Reserved Font Name" 仅为 OFL 模板里的术语定义段落（第 28–33 行），不构成实际 RFN 声明。
  → **这是 Noto 版相对 Adobe 版的实际优势：改名、魔改、再分发均无 RFN 约束。**
- **Inter**：SIL Open Font License 1.1。实测首句为
  `Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter)`，**同样未声明保留字体名**。

**官方来源（2026-08-04 实测 HTTP 200）**

- https://github.com/adobe-fonts/source-han-serif/releases/tag/2.003R
- https://raw.githubusercontent.com/adobe-fonts/source-han-serif/release/LICENSE.txt
- https://github.com/notofonts/noto-cjk/releases/tag/Sans2.004
- https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE
- https://github.com/rsms/inter/releases/tag/v4.1
- https://raw.githubusercontent.com/rsms/inter/master/LICENSE.txt
- OFL 1.1 全文：https://openfontlicense.org/

**Web 端 webfont 嵌入与再分发**

允许，但必须同时满足 OFL 1.1 的以下具体条件（原文要点）：

1. **§2**：可自由复制、修改、再分发，可打包销售**含**字体的作品，但**字体本身不得单独出售**。
2. **§1**：再分发（含转成 woff2 后放 CDN）必须**随附完整 OFL 授权文本与版权声明**。
   实践做法：在 `frontend/public/assets/fonts/` 下放置 `OFL.txt`，并在游戏「关于/致谢」页列出字体与许可证。
3. **§3 保留字体名（RFN）**：对 Source Han Serif，**任何修改版（含子集化后的衍生文件）不得继续使用 `Source` 字样命名**。
   → 子集文件必须重命名，例如 `BorderEcho-Serif-Subset.woff2`，**不要**叫 `SourceHanSerif-subset.woff2`。
   Noto Sans CJK 与 Inter 无此约束，可保留原名。
4. **§5**：字体以 "AS IS" 提供，无担保。

> 注意：OFL 的 RFN 条款只约束**修改版**。若原封不动分发未修改的字体文件，可保留原名。
> 但 webfont 子集化在 OFL 语境下属于「Modified Version」，因此 Source Han Serif 的子集必须改名。

**覆盖与字重**

| 项 | Source Han Serif SC | Noto Sans CJK SC | Inter |
|---|---|---|---|
| 简体 | 是（SC 为简中优化字形） | 是 | — |
| 繁体 | 需换用 TC/HC 子家族；SC 包内不含台港字形变体 | 同左 | — |
| 日文假名 | 含（泛 CJK 字形集，假名可显示；但 SC 版汉字取简中字形） | 同左 | — |
| 西文/数字 | 含 | 含 | 完整拉丁 + 大量数字特性 |
| 字重 | 7（ExtraLight–Heavy，Adobe 官方静态字重集） | **9**（100/200/300/400/500/600/700/800/900，实测自 fontsource 分片枚举） | **9**（100–900，实测） |

**文件体积**

| 文件 | 体积 | 来源 |
|---|---|---|
| `09_SourceHanSerifSC.zip`（SC 全字重打包） | **132.21 MB** | 实测 · GitHub Release API |
| `08_NotoSansCJKsc.zip`（SC 全字重打包） | **90.14 MB** | 实测 · GitHub Release API |
| `Inter-4.1.zip`（完整家族） | **32.15 MB** | 实测 · GitHub Release API |
| `noto-sans-sc-chinese-simplified-400-normal.woff2`（单字重·简中全量分片） | **1,114.8 KB** | 实测 · jsDelivr |
| `noto-serif-sc-chinese-simplified-400-normal.woff2`（单字重·简中全量分片） | **1,472.9 KB** | 实测 · jsDelivr |
| `inter-latin-400-normal.woff2`（单字重·拉丁） | **23.1 KB** | 实测 · jsDelivr |
| 单字重 OTF（未子集，CJK） | 约 **8–16 MB** | 估算（由全字重 zip 除以字重数反推，未逐文件实测） |

---

### 2.2 组合 B —— 标题更有个性（全 OFL）

| 角色 | 字体全名 | 版本 | 发布日期 |
|---|---|---|---|
| 标题 | Smiley Sans 得意黑 | **v2.0.1** | 2024-02-07 |
| 正文 | Noto Sans CJK SC | Sans2.004 | 2022-01-27 |
| 数字 | Inter | v4.1 | 2024-11-16 |

**许可证** —— SIL Open Font License 1.1。实测 LICENSE 原文首句：

```
Copyright (c) 2022--2024, atelierAnchor <https://atelier-anchor.com>,
with Reserved Font Name <Smiley> and <得意黑>.
```

→ **保留字体名为 `Smiley` 与 `得意黑` 两个**。GitHub API 的 SPDX 字段亦返回 `OFL-1.1`，两处互相印证。
子集化后**不得**在字体族名中保留 `Smiley` 或 `得意黑`。

**官方来源（实测 200）**

- https://github.com/atelier-anchor/smiley-sans
- https://github.com/atelier-anchor/smiley-sans/releases/tag/v2.0.1
- https://raw.githubusercontent.com/atelier-anchor/smiley-sans/main/LICENSE

**Web 嵌入**：允许，条件同 §2.1（附 OFL 文本 + 子集改名 + 不得单独售卖字体）。

**覆盖与字重**

- 简体：是。繁体：部分覆盖，**未逐字核实**，用于标题短句可接受，长段繁体请先实测缺字。
- 日文假名：**未核实**（本轮未取得官方字符集清单，不作断言）。
- 字重：得意黑为**单字重**设计（含倾斜变体），不提供多字重家族。
  标题层级需靠字号/字距/颜色拉开，不能靠字重。**这是选型时的实际限制。**

**文件体积**

- `smiley-sans-v2.0.1.zip`（完整发布包，含多格式）：**5.51 MB** —— 实测 · GitHub Release API。
  相比思源系列小两个数量级，因为字符集规模小得多。
- 单字重 woff2 未子集：**估算约 1.5–2.5 MB**（未实测，建议下载后实测）。

---

### 2.3 组合 C —— 记录员 / 手抄本气质（主推 · 叙事文本）

| 角色 | 字体全名 | 版本 | 发布日期 |
|---|---|---|---|
| 标题 | Source Han Serif SC | 2.003R | 2024-07-30 |
| 正文 | LXGW WenKai 霞鹜文楷 | **v1.522** | **2026-03-17** |
| 数字 | IBM Plex Mono | `@ibm/plex-sans@1.1.0` 发布线 | 2024-11-13 |

**许可证 —— 霞鹜文楷（本套最关键、也最值得单独读的一条）**

SIL Open Font License 1.1，**并带有一条对本项目非常有利的附加许可**。实测 `OFL.txt` 原文：

```
Copyright 2021-2026 LXGW (https://github.com/lxgw/LxgwWenKai), with Reserved Font Name
'霞鹜', '霞鶩', '落霞孤鹜', '落霞孤鶩' and 'LXGW'. [ADDITIONAL PERMISSION] The Reserved Font
Names '霞鹜', '霞鶩', '落霞孤鹜', '落霞孤鶩' and 'LXGW' may continue to be used in Modified
Versions recompiled from the Original Version, without modifications to the font source
code; or in Modified Versions subsetted or converted to other formats (e.g., WOFF/WOFF2)
solely for web font delivery, provided such Modified Versions are not made available as
installable desktop fonts (e.g., on mainstream platforms like Google Fonts, or third-party
non-commercial platforms recognized by the author @lxgw; other web font platforms please
contact the author @lxgw for confirmation).
```

**逐句解读（对本项目的实际影响）**

1. RFN 有 5 个：`霞鹜` `霞鶩` `落霞孤鹜` `落霞孤鶩` `LXGW`。
2. **附加许可明确放行了我们最需要的两件事**：为 web font 投放而做的**子集化**与**格式转换（WOFF/WOFF2）**，
   在这两种情况下**可以继续沿用保留字体名**——不必像思源那样被迫改名。
3. **附带的限制条件**：这类修改版**不得以「可安装的桌面字体」形式提供**。
   → 我们把子集 woff2 放进游戏站点由浏览器加载，属于 web font delivery，符合许可；
   → 但**不得**在游戏内提供「下载字体文件」按钮，也不得把子集包再传到字体分发站。
4. 该字体**衍生自 FONTWORKS 的 Klee One**——`OFL.txt` 中另有一段
   `Copyright 2020 The Klee Project Authors (https://github.com/fontworks-fonts/Klee)`。
   两层版权都在同一份 OFL 下，链条完整，无额外风险。

**IBM Plex Mono 许可证**：SIL OFL 1.1，实测首句
`Copyright © 2017 IBM Corp. with Reserved Font Name "Plex"` → **RFN 为 `Plex`，子集必须改名。**

**官方来源（实测 200）**

- https://github.com/lxgw/LxgwWenKai
- https://github.com/lxgw/LxgwWenKai/releases/tag/v1.522
- https://raw.githubusercontent.com/lxgw/LxgwWenKai/main/OFL.txt
- https://github.com/IBM/plex
- https://raw.githubusercontent.com/IBM/plex/master/LICENSE.txt
- https://www.ibm.com/plex/

**Web 嵌入**：允许。霞鹜文楷条件见上；思源宋体与 Plex Mono 需子集改名 + 随附 OFL。

**覆盖与字重**

- 霞鹜文楷：简体覆盖良好；另有独立的 TC（繁体）与 Mono 子家族需分别下载。
  日文假名因源自 Klee One 而具备基础覆盖，但**未逐字核实**，不作保证。
- 霞鹜文楷字重：**3 个**（Light / Regular / Medium）——由 Release 资产文件名实测确认，
  另有 3 个对应的 Mono 变体。**无 Bold**，强调层级需改用思源黑体或加粗描边。
- IBM Plex Mono 字重：**7 个**（100/200/300/400/500/600/700，实测自 fontsource 分片枚举）。

**文件体积（大量实测数据）**

| 文件 | 体积 | 来源 |
|---|---|---|
| `LXGWWenKai-Regular.ttf` | **24.39 MB** | 实测 · GitHub Release API |
| `LXGWWenKai-Light.ttf` | **26.96 MB** | 实测 · GitHub Release API |
| `LXGWWenKai-Medium.ttf` | **24.20 MB** | 实测 · GitHub Release API |
| `lxgw-wenkai-v1.522.zip`（完整包） | **76.92 MB** | 实测 · GitHub Release API |
| `ibm-plex-mono-latin-400-normal.woff2` | **14.5 KB** | 实测 · jsDelivr |
| 霞鹜文楷单字重 woff2（未子集） | 约 **7–9 MB** | 估算（楷体笔形复杂，压缩率低于黑体，务必子集化） |

> 霞鹜文楷单文件 24 MB 是本轮所有候选里对运行时预算威胁最大的一项。
> `03_TECHNICAL_SPECS.md` §8 规定首屏新增资源总量 < 4 MB，**未子集化的文楷单字重就会直接击穿该预算**。
> 结论：文楷**只能**以子集形式使用，且建议延迟加载（非首屏）。

---

### 2.4 组合 D —— 阿里巴巴普惠体（免费商用，但 Web 端有实质障碍）

| 角色 | 字体全名 | 版本 |
|---|---|---|
| 标题 / 正文 | Alibaba PuHuiTi 3.0（阿里巴巴普惠体 3.0） | 3.0（GB18030-2022 版） |
| 数字 | Inter | v4.1 |

**许可证名称**：厂商自订**免费商用普通许可**（非 OFL、非 Apache）。
一手来源为语雀官方法律声明页，**已实测打开（HTTP 200）并读取全文**：
https://www.yuque.com/yiguang-wkqc2/puhuiti/nus9wiinq4aeiegy

**协议限制（原文摘录，非转述）**

> 第 3 条：阿里巴巴授权个人、企业等用户在遵守本声明相关条款的前提下，**可以下载、安装和使用**上述阿里巴巴字体，
> 该授权是免费的普通许可，用户可基于合法目的用于商业用途或非商业用途……

> 第 4 条：除本法律声明中明确授权之外，**阿里巴巴未授予用户关于阿里巴巴字体的其他权利**。未经阿里巴巴书面授权，任何人不得：
> 1）对阿里巴巴字体进行仿制、**转换**、翻译、反编译、反向工程、**拆分**、破解……；
> 2）删除、覆盖或修改阿里巴巴字体法律声明的全部或部分内容；
> 3）将阿里巴巴字体进行单独定价出售、出租、出借、**转让、转授权**、或采取其他未经阿里巴巴明确授权的行为；
> 4）发布任何使外界误认其与阿里巴巴……存在合作、赞助或背书等商业关联的不实信息。

**对本项目的结论（这是必须写清楚的部分）**

| 用途 | 结论 | 依据 |
|---|---|---|
| 桌面设计稿、海报、商店页截图、宣传物料 | **允许商用** | 第 3 条明确授权「使用」，且明示可商用 |
| 转成 WOFF2 作为 webfont | **不可** | 第 4.1 条明文禁止「**转换**」；格式转换需书面授权 |
| 子集化裁剪字符 | **不可** | 第 4.1 条明文禁止「**拆分**」 |
| 把字体文件随游戏包分发给玩家 | **不可** | 第 3 条只授予「下载、安装和使用」，**未授予分发权**；第 4.3 条禁止「转让」 |
| 嵌入到 App / 游戏 / 硬件 | **未获授权，视为不可** | 第 4 条兜底：明确授权之外未授予其他权利 |

> 补充事实：该官方法律声明页的评论区中，有多名用户（含明确自述「我是做游戏的」者）
> 提问能否嵌入游戏、能否内嵌网页端，**截至 2026-08-04 抓取时官方均未答复**。
> 这进一步说明嵌入场景**没有**书面授权，不能自行推定为允许。

**因此本组合的判定**：`license: 厂商免费商用许可（仅限下载/安装/使用）`，
**Web 嵌入与再分发：不可 / 需另行取得书面授权**。仅可用于不进入运行时的桌面设计环节。

**覆盖与字重（来自官方站点描述）**

- 简体中文 3.0：**7 字重**（符合 GB18030-2022 实现级别 1+2）+ 实现级别 3 的 Regular 单字重；2.0 版为 9 字重。
- 7 字重共 **194,460 个全形汉字**；含拉丁、希腊、西里尔字母与标点。
- 繁体另有 TC（Big5，4 字重）与 HK（HKSCS，4 字重）；日文、韩文各 3 字重。
- 官方站点：https://www.alibabafonts.com/ （实测 200）

**文件体积**：**未实测**。官方下载需经网页交互，本轮未取得可校验的字节数 → 标注 `未核实`。

---

### 2.5 组合 E —— 站酷系列：`unknown / 未核实`，不予批准

**结论先行：本轮无法从权威一手来源核实站酷系列字体的完整授权文本，因此按 `03_TECHNICAL_SPECS.md` §7
「商用可用性不明确时写 unknown，不得批准」处理。**

- `license: unknown`
- `source_url: unknown（未取得官方授权原文页面）`
- **未核实**

核实过程中发现的**二手来源互相矛盾**，这正是不能采信的理由：

| 来源 | 说法 | 问题 |
|---|---|---|
| zcool.com.cn 站酷文章页 | 「免费授权全社会使用（包括商用）」 | 属宣传性文章，**非**独立、完整、可引用的授权协议文本 |
| iconfont.cn 字体详情页 | 「免费使用开源」「使用范围：免费授权全社会使用（包括商用）」 | 第三方平台转述，未附协议全文 |
| mfonts.cn | 明确列出「**嵌入式 · 软件嵌入 ✗**」「出版物 ✗」「商标 LOGO ✗」 | 第三方**自行整理**，页面自述「根据经验整理……并不代表法律建议」 |
| zitiquan.com | 称其采用 **SIL Open Font License 1.1** | 与上一条直接冲突；且未给出 OFL 文本位置，**高度可疑** |

**关键冲突点**：一个来源说走 OFL（则嵌入完全自由），另一个来源说禁止软件嵌入。
两者不可能同时成立。在拿到站酷/仓耳官方发布的授权原文之前，**不得**将站酷系列用于游戏运行时。

**若后续要启用，需补的动作**：向站酷或仓耳字库（https://tsanger.cn）索取书面授权文本，
确认是否覆盖「软件/游戏嵌入」与「webfont 转换分发」两项，取得后再更新本文件版本号。

---

## 3. 子集化建议

### 3.1 为什么必须子集化

`03_TECHNICAL_SPECS.md` §8 规定：**首屏新增资源总量尽量 < 4 MB**。
而本轮实测的未子集 CJK 单字重 woff2 分片已达 **1,114.8 KB（Noto Sans SC）**、**1,472.9 KB（Noto Serif SC）**，
霞鹜文楷 TTF 更是 **24.39 MB**。三个角色字体叠加会直接击穿预算。

### 3.2 建议字集分层（按《边境回声》实际文本构成）

| 层级 | 字集内容 | 规模 | 加载策略 | woff2 体积估算 |
|---|---|---|---|---|
| **L0 首屏关键** | UI 固定文案 + 12 枚图标标签 + 数字 + 标点 | 300–500 字 | 内联 / preload | 约 40–80 KB |
| **L1 核心玩法** | 通用规范汉字表一级字（常用字） | 约 3,500 字 | 首屏后立即加载 | 约 380–550 KB |
| **L2 叙事扩展** | 一级+二级字，覆盖 lore/记录碎片/人名地名 | 约 6,500 字 | 进入书库场景时延迟加载 | 约 700 KB–1.1 MB |
| **L3 兜底** | 完整简中分片 | 20,000+ 字 | 仅在检测到缺字时按需拉取 | 1.1–1.5 MB（实测值见 §2.1） |

> 上表 L0–L2 的体积为**估算**（按实测的 L3 全量分片体积与字数比例推算），
> 非实测数字。落地前请用 `fonttools subset` 实际生成并测量。

### 3.3 具体做法

1. **抽取真实字集**：从 `writing/` 下的 lore、barks、UI 文案里跑脚本收集实际用到的字符，
   而不是拍脑袋用「常用 3500 字」——游戏专名（卢利特、静默线等）常落在常用字表之外。
2. **工具**：`fonttools subset` + `--flavor=woff2`，配合 `--layout-features` 保留必要的 OpenType 特性。
3. **unicode-range 分片**：用 CSS `unicode-range` 把 CJK 切成多个分片，浏览器只下载命中的片，
   这也是 fontsource 那 45 / 816 个 woff2 分片的做法。
4. **命名合规**（对应各字体的 RFN 约束）：

   | 字体 | 子集后是否需改名 | 建议文件名 |
   |---|---|---|
   | Source Han Serif SC | **必须改**（RFN `Source`） | `BorderEcho-Serif-L1.woff2` |
   | Smiley Sans | **必须改**（RFN `Smiley`/`得意黑`） | `BorderEcho-Display-L0.woff2` |
   | IBM Plex Mono | **必须改**（RFN `Plex`） | `BorderEcho-Mono-L0.woff2` |
   | Noto Sans CJK SC | 不需要（无 RFN 声明） | 可保留原名 |
   | Inter | 不需要（无 RFN 声明） | 可保留原名 |
   | LXGW WenKai | **不需要改**（附加许可明确放行 webfont 子集沿用原名） | 可保留原名 |

5. **随附授权**：在 `frontend/public/assets/fonts/OFL.txt` 放完整 OFL 文本，
   并在游戏「关于」页列出每款字体的名称、版本、版权行与许可证。这是 OFL §1 的硬性要求。

---

## 4. 推荐组合与理由

### 4.1 最终推荐：A + C 双轨（UI 用 A，叙事用 C 的文楷）

**推荐配置**

| 用途 | 字体 | 字重 | 理由 |
|---|---|---|---|
| 界面标题 / 章节标题 | Source Han Serif SC | SemiBold / Bold | 宋体衬线呼应「旧记录/教会书库」，与 REF-STYLE-001 方向 B「旧记录纸张」直接对齐 |
| 界面正文 / HUD / 按钮 | Noto Sans CJK SC | Regular / Medium | 9 字重层级最完整；无 RFN 约束，工程改名自由；小字号可读性优于楷体 |
| 数值 / 时间 / 体力 / 关系度 | Inter | Regular / SemiBold | 有等宽数字（tabular figures），数值跳动时不抖动——这对 `01_REQUEST_CATALOG.md` 强调的「清晰数值」是刚需 |
| 书库记录碎片 / lore 正文 / 手抄页面 | LXGW WenKai 霞鹜文楷 | Regular | 楷体手写感直接服务 NAR-LORE-001「被涂改记录/旁注」的叙事质感，且许可证明确放行 webfont 子集 |

### 4.2 为什么这样选

1. **法务链条最干净**。四款全部是 SIL OFL 1.1，四份 LICENSE 原文本轮均已逐字读取，
   没有任何一条依赖二手转述。相比之下组合 D 的普惠体虽然「免费商用」，
   但**它授予的是「安装使用权」而不是「分发权」**，而游戏 webfont 恰恰是分发行为——这是根本性的不匹配。

2. **霞鹜文楷的附加许可正好命中我们的场景**。它是本轮唯一**主动、明文**允许
   「为 web font 投放而子集化/转 WOFF2 且沿用原名」的候选。其余 OFL 字体虽也允许，
   但都要处理 RFN 改名。同时它禁止的「以可安装桌面字体形式提供」我们本来也不会做，
   限制条件与我们的用法零冲突。

3. **功能分工清晰，不是为了好看而堆字体**。宋体管权威感、黑体管可读性、
   Inter 管数值稳定、楷体管叙事纸感——四个角色各自解决一个具体问题。

4. **风险可控**。Noto Sans CJK 与 Inter 均无 RFN，是整套方案的「安全底座」；
   即使后续要替换标题或叙事字体，正文与数字层不受影响。

### 4.3 明确不推荐

- **组合 D（普惠体）**：桌面设计稿可用，**运行时禁用**。若一定要用，需先向阿里巴巴取得书面授权。
- **组合 E（站酷）**：`unknown`，按规范不得批准，不得进入 `approved`。

### 4.4 落地前仍需完成的动作

1. 用 `fonttools subset` 实测 L0/L1/L2 三层的真实 woff2 体积，替换本文 §3.2 的估算值。
2. 实测霞鹜文楷与得意黑的**日文假名与繁体覆盖**（本轮标注为未核实，不可凭推测使用）。
3. 在 `frontend/public/assets/fonts/` 建立 `OFL.txt` 与致谢清单。
4. 若启用得意黑做标题，先确认单字重是否足以支撑标题层级需求。

---

## 5. 未能核实的部分（明确声明）

| 项 | 状态 | 原因 |
|---|---|---|
| 站酷系列全部字体的授权原文 | **unknown / 未核实** | 未找到官方发布的完整授权协议文本；二手来源互相矛盾（OFL vs 禁止嵌入） |
| 阿里巴巴普惠体的字体文件字节数 | **未核实** | 官方下载需网页交互，未取得可校验数字 |
| 得意黑的日文假名覆盖 | **未核实** | 未取得官方字符集清单 |
| 霞鹜文楷、得意黑的繁体逐字覆盖 | **未核实** | 仅知有独立 TC 子家族，未做缺字实测 |
| 各 CJK 字体单字重 OTF/woff2 的未子集精确体积 | **部分未核实** | 仅 Noto SC / Serif SC 的简中分片与拉丁分片为实测；其余为估算 |
| 子集化后 L0/L1/L2 各层体积 | **估算，未实测** | 需按项目真实字集生成后测量 |
| `fonts.google.com` 的 Noto 规格页 | **未能访问** | curl 探测返回 000（该站拒绝非浏览器请求）；已改用 GitHub 官方仓库作为来源，不引用该链接 |

> 本文件所有标注为「实测」的数字均可复现：
> Release 体积来自 `api.github.com/repos/{owner}/{repo}/releases/latest` 的 `assets[].size`；
> woff2 体积来自 `data.jsdelivr.com/v1/packages/npm/@fontsource/{pkg}@{version}` 的 `files[].size`。
