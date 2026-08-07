# UW-UPGRADE-1.0 全素材主目录

- 状态：Current / 素材整理唯一入口
- 日期：2026-08-07
- 项目根：`C:\Users\liang\Desktop\UW`
- 生产批次：`UW-UPGRADE-1.0`
- 请求事实：`materials/REQUESTS.csv`
- 文件事实：`materials/MANIFEST.csv`
- 机器合同：`materials/runtime_asset_requirements.json`
- 生产 Prompt：`materials/UW_UPGRADE_1_0_ASSET_AGENT_PROMPT.md`

本目录整理现有素材、候选素材、待返工项、尚未生成项和未来包。它不把“文件存在”“规格通过”或“看起来更好”误写成 approved/integrated。

## 1. 总量快照

| 区域 | 文件数 | 体积 |
|---|---:|---:|
| `materials/inbox/visual` | 346 | 184.55 MiB |
| `materials/inbox/audio` | 103 | 811.13 MiB |
| `materials/inbox/writing` | 29 | 0.25 MiB |
| `materials/inbox/research` | 17 | 0.09 MiB |
| `frontend/public/assets/runtime` | 21 | 9.86 MiB |

收件区文件约 996 MiB。绝大部分仍是候选、历史版本或生成工作产物；正式 runtime 的数量不能代表全素材完成。

## 2. 状态规则

```text
requested/deferred
-> received
-> reviewing
-> approved
-> integrated

reviewing -> changes_requested -> received
reviewing -> rejected
```

- `received`：文件和最低信息已收到，不代表可用。
- `changes_requested`：存在明确返工问题。
- `approved`：具体文件版本通过来源、权利、技术和内容审查。
- `integrated`：approved 文件真实进入 runtime 并通过游戏内验收。
- `deferred`：需求已登记但尚未启动。

## 3. 当前可运行素材

当前 runtime 主要包含：

- `VIS-KA-001` 开场关键图候选；
- `VIS-POR-001` 三名核心人物六张 v002 肖像；
- `VIS-UI-001` 12 枚核心图标候选；
- `AUD-BGM-001` 村庄清晨 BGM；
- `AUD-AMB-001` 村庄细雨 ambience。

这些只支持当前原型表现，不能替代正式地图、Sprite、背景、VFX、完整 SFX 或抓捕终点表现。

## 4. 最新核心候选包

| 资产组 | 最新候选 | 自动规格 | 正式状态 | 人工审查要点 |
|---|---|---|---|---|
| MAP | `VIS-MAP-001_map_v005.json` 及 v005/v006 图层/atlas | ready | `changes_requested` | terrain 仍烘焙道路、建筑、树木和可见网格；分层语义需重做 |
| CHAR-KIRITO | `VIS-CHR-001_frames_v008.json` + sheet | ready | `changes_requested` | 帧数满足，但人物过度简化、动作差异和成品感不足 |
| CHAR-ALICE | `VIS-CHR-002_frames_v008.json` + sheet | ready | `changes_requested` | 同上；需要独立轮廓、递物/关心动作和服装层次 |
| CHAR-EUGEO | `VIS-CHR-003_frames_v008.json` + sheet | ready | `changes_requested` | 同上；训练/协作动作必须清晰 |
| SCENES | `VIS-ENV-001_scenes_v005.json` + 六张背景 | ready | `changes_requested` | 画面已明显改善；仍需安全裁切、风格一致和游戏内验收 |
| BGM-BOUNDARY | AUD-BGM-002 v004 WAV/OGG | ready | `changes_requested` | 补正式登记、版权/来源和人耳 loop/ducking 审核 |
| BGM-RELATIONSHIP | AUD-BGM-003 v004 WAV/OGG | ready | `changes_requested` | 同上 |
| AMB-FOREST | AUD-AMB-002 v004 normal/silent | ready | `changes_requested` | 补正式登记与 normal/silent 人耳 A/B 审核 |

上述包在正式 `MANIFEST.csv` 中仍无对应批准/接入行，不得直接复制到 runtime。

## 5. 全请求目录

### 5.1 视觉

| request_id | 内容 | 当前状态 | 位置 | UW-UPGRADE-1.0 动作 |
|---|---|---|---|---|
| REF-STYLE-001 | 视觉方向板 | received | `visual/styleboards` | 提取色板/线稿/比例，不直接接 runtime |
| VIS-KA-001 | 开场关键图 | received | `visual/keyart` | 复核桌面/移动安全区，保留为候选 |
| VIS-KA-002 | 抓捕终点关键图 | deferred | `visual/keyart` | 终点阶段生成 desktop/mobile |
| VIS-POR-001 | 三核心肖像样张 | received | `visual/portraits` | 作为风格参考，统一后再决定保留 |
| VIS-POR-002 | 六角色 x 五表情 | deferred | `visual/portraits` | 核心角色风格冻结后生成 |
| VIS-UI-001 | 12 枚核心图标 | received | `visual/ui_icons` | 做 24px 可读性复核 |
| VIS-UI-002 | 完整 32 枚 UI 图标 | deferred | `visual/ui_icons` | 生成 SVG + 24/48/96 PNG 和状态集 |
| VIS-MAP-001 | 卢利特村可玩地图 | changes_requested | `visual/world` | 先重做干净分层，不沿用烘焙 terrain |
| VIS-TILE-001 | tile/prop/遮挡生产包 | deferred | `visual/world` | 与新地图同步生成 atlas 和规则 |
| VIS-CHR-001 | 桐人地图 Sprite | changes_requested | `visual/characters` | 重做可读动作与原创轮廓 |
| VIS-CHR-002 | 爱丽丝地图 Sprite | changes_requested | `visual/characters` | 同上 |
| VIS-CHR-003 | 尤吉欧地图 Sprite | changes_requested | `visual/characters` | 同上 |
| VIS-CHR-004 | 赛尔卡/加利塔/加斯夫特 Sprite | deferred | `visual/characters` | 核心三人通过后生成 |
| VIS-CHR-005 | 整合骑士叙事姿态 | deferred | `visual/characters` | 只做到场/宣告/押送，不做战斗包 |
| VIS-ANIM-001 | 阅读/书写/递物/调查/告别动作 | deferred | `visual/characters` | 与角色 anchor/触发 ID 对齐 |
| VIS-ENV-001 | 六张活动/转场背景 | changes_requested | `visual/environments` | 保留 v005 候选，先做游戏内裁切审查 |
| VIS-VFX-001 | 六类反馈 VFX | deferred | `visual/vfx` | golden slice 先做 clue-pulse |
| VIS-MARKETING-001 | 商店/封面/横幅 | deferred | `visual/keyart` | 盲测通过前不启动 |

### 5.2 音频

| request_id | 内容 | 当前状态 | 位置 | UW-UPGRADE-1.0 动作 |
|---|---|---|---|---|
| AUD-BGM-001 | 村庄清晨循环 | received | `audio/bgm` | 保留候选并做最终 loop/ducking 审查 |
| AUD-BGM-002 | 边界调查两版 | changes_requested | `audio/bgm` | 复核 v004、登记、人耳审核 |
| AUD-BGM-003 | 关系日常两版 | changes_requested | `audio/bgm` | 作为 golden slice 音乐候选 |
| AUD-AMB-001 | 村庄细雨 | received | `audio/ambience` | 复核长时间重复和移动端播放 |
| AUD-AMB-002 | 森林 normal/silent | changes_requested | `audio/ambience` | 人耳 A/B 与 2-4 秒交叉淡化审核 |
| AUD-SFX-001 | UI/线索/奖励反馈 | deferred | `audio/sfx` | 18-24 个短 SFX，先做 golden slice 触发 |
| AUD-SFX-002 | 脚步/活动/边界 | deferred | `audio/sfx` | 16-24 个世界 SFX，多材质变体 |
| AUD-VOICE-001 | 临时语音/呼吸声 | deferred | `audio/sfx` | 当前不启动 |

### 5.3 剧情、设定和研究

| request_id | 内容 | 当前状态 | 用途 |
|---|---|---|---|
| NAR-CANON-001 | 正典事实基线 | received | 判定 A/B/C 内容边界 |
| NAR-PRECAP-001 | 四幕十节点故事 | received | N01-N10 素材镜头与情绪依据 |
| WORLD-MACRO-001 | 世界宏观设定 | received | 世界规则与地点层级 |
| WORLD-MICRO-001 | 地点圣经 | received | 地图/背景/道具内容依据 |
| CHAR-DEPTH-001 | 人物深度设定 | received | 人物轮廓、姿态、表情和关系依据 |
| NAR-VOICE-001 | 人物声音圣经 | received | 对白/SFX/可选语音依据 |
| NAR-ADAPT-001 | 改编连续性规则 | received | 禁止素材提前剧透 |
| QA-CANON-001 | 正典检查表 | received | 内容审查 |
| NAR-LORE-001 | 书库记录碎片 | received | 书页/记录道具内容 |
| NAR-BARK-001 | 村庄环境短句 | received | 环境交互和 NPC 短反馈 |
| REF-FONT-001 | 中文字体候选 | received | UI 字体权利与可读性 |
| REF-MOOD-001 | 可追溯参考包 | requested | 只做参考，不剪贴进成品 |
| QA-PLAY-001 | 三名陌生玩家盲测 | requested | 最终体验证据 |
| AI-CORPUS-001 | NPC 对话测试集 | deferred | 当前素材生产不启动 |

## 6. UW-UPGRADE-1.0 命名

为兼容请求登记检查，新文件必须同时包含 request_id 和统一批次：

```text
<REQUEST-ID>_UW-UPGRADE-1.0_<descriptor>.<ext>
```

例：

```text
VIS-MAP-001_UW-UPGRADE-1.0_terrain.png
VIS-CHR-001_UW-UPGRADE-1.0_kirito_sheet.png
VIS-ENV-001_UW-UPGRADE-1.0_church_library.png
AUD-BGM-003_UW-UPGRADE-1.0_relationship_a_48k24b.wav
```

- 不覆盖、删除或改名现有 v002-v008。
- 不再新建 v009/v010。
- 返工仍使用同一批次工作区；被替换候选移入审计归档并记录 hash。
- 正式 runtime 文件由项目负责人审核后导出，不由素材智能体自行写入。

## 7. 目录边界

```text
materials/inbox/                 未批准收件与生产结果
materials/archive/               历史失败版本和中间文件
materials/approved/              已批准无损源（由项目负责人维护）
frontend/public/assets/runtime/  游戏正式运行文件（由项目负责人维护）
```

素材智能体只能写对应 request 的 `materials/inbox` 目录，不得修改后三层中的正式状态。

## 8. 每包最低交付

- 主文件和必要的无损源/分层源；
- 同目录主 sidecar；
- 完整 prompt、negative prompt、模型/工具/版本、seed/settings、编辑步骤；
- 作者/来源、许可、source URL 或无 URL 原因、rights statement；
- 尺寸、色彩模式、alpha/帧/anchor 或音频测量；
- 18 列 manifest fragment，一文件一行，SHA-256 与实物一致；
- contact sheet/预览图和自动检查结果；
- 状态只能写 `received`，审核/runtime 字段留空。

## 9. 当前执行批次

1. `MAP + CHARACTERS + church_library + clue-pulse + BGM-003 A` golden slice。
2. 通过桌面/移动游戏内验收后，扩展其余 SCENES、BGM、AMBIENCE、UI、VFX、SFX。
3. 最后制作 `VIS-KA-002 + VIS-CHR-005 + farewell/capture animation + capture-silence`。
4. 所有包完成后再组织 QA-PLAY-001；营销图和语音仍延期。

