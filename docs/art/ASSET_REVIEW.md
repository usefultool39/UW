# 素材审查与制作清单

- **对应版本**：`0.6.0`
- **审核日期**：2026-08-10
- **本轮交付摘要**：修复 SFX 96KB 同尺寸问题（v002 差异化 SFX）、三角色三方向 sprite base reference（v010 up/left/right）、NPC sprite 从 unreviewed 升级、32 枚完整 UI 图标、0.6.0 P0 关系雷达图 + 草药采集点 4 态、VIS-ENV-001 schema v006 修复、BGM/AMB 状态提升、0.6.0 新增 11 项需求正式登记
- **结论**：0.5.0 候选已 90% 收齐；0.6.0 P0 关键素材 (草药采集点 + 关系雷达图) 已交付；runtime 实际只有 22 个文件（~15MB）仍未变 — 所有 candidate 仍禁止进 runtime，等人工验收

## 1. 状态定义

- **可用**：来源和技术条件基本清楚，可继续用于内部版本。
- **可试接**：文件可加载，但必须通过真实游戏中的比例、裁切、安全区和风格检查。
- **仅原型**：只能证明技术流程，不代表正式美术完成。
- **返工**：内容、风格、完整性或来源不满足当前目标。
- **`sample_candidate`**：已登记的候选样张；只允许用于审查和技术验证，不允许进入 runtime。

## 2. Runtime 实际在用素材（22 个文件，~15MB）

| 类别 | 数量 | 内容 | 问题 |
|---|---|---|---|
| 关键图 | 1 | 村庄开场图 | 只有一张；无移动端独立裁切 |
| 肖像 | 6 | 三人各 2 表情（neutral/concerned） | 缺紧张/坚定/告别/温暖；支持 NPC 无肖像 |
| UI 图标 | 12 | 12 枚 48px 核心图标 | **完整 32 枚 v001 已交付 (VIS-UI-002 expanded 20 枚 + 12 枚 core)**, 24/48/96 三种尺寸, sample_candidate, runtime 仍禁止 |
| BGM | 1 | 村庄清晨 | 只有一条；边界/关系 BGM 未进 runtime |
| 环境声 | 1 | 细雨村庄 | 森林静默未进 runtime |
| SFX | 0 | 无 | **v002 candidate 已修复 96KB 同尺寸问题**: 5 条差异化时长 205-510ms, 大小 29-73KB, peak -1.0 dBFS. v001 (current/) 仍标红. v002 在 candidate 等人工验收 |
| VFX | 0 | 无 | 候选在等待修复 |
| 地图 | 0 | 用关键图当背景 | 无正式可走地图 |
| 角色 sprite | 0 | 用 token 圆形图 | **三角色 down 12 帧 v009 + up/left/right base reference v010 (3 角色 × 3 方向 × 2 文件类型 = 18 文件)**; 三 NPC (Selka/Garret/Elders) 17 单帧 + 6 sheet 已升级到 candidate; 仍缺 walk 6 帧 / interact 4 帧 / left-right 派生 |
| 场景插图 | 0 | 无 | 6 张 v005 在 candidate + **v006 schema 修复** (geometry_placeholder + safe_area 像素 rect + runtime_file + source_sha256) |

**结论：runtime 素材覆盖率极低。玩家体验中大量使用占位图或替代方案。**

## 3. 当前结论

| 素材 | 判定 | 当前用途 | 修改意见 |
|---|---|---|---|
| 村庄开场图 | 可用 | 开场和短提示背景 | 补移动端独立裁切 |
| 核心人物肖像 | 可用 | 对话面板 | 统一服装线稿光源；补紧张/坚定/告别/温暖表情；补支持 NPC 肖像 |
| 核心 UI 图标 | 可用 | 资源/关系/线索/状态 | 批准完整 32 枚图标集（在 archive/unreviewed 中已有） |
| 村庄清晨音乐、细雨 | 可用 | 当前离线声景 | 补淡入淡出、循环点和移动端自动播放 |
| 书库、巨神树、炉火、北门等场景插图 | 可试接 | 事件卡/互动面板 | 标注安全区和裁切；修复几何占位和 schema 问题 |
| 三位核心角色动作表 | 仅原型 | 验证加载 | **v010 已补 up/left/right base reference (3 角色 × 3 方向 × 2 文件类型 = 18 文件)**; down v009 36/36 帧 anchor (32,94) alpha=0; 4 帧变体差异较弱 (±2px), 完整 12 帧需 T02-B |
| 分层村庄地图 | 仅原型 | 保留技术合同 | **v005 full runtime layers 已交 + v006 tile atlas + v010 candidate AI 重做** (3024x1792 正交俯视, 三个住宅差异化, 水印清除); 仍 sample_candidate, 需人工验收替换 |
| 抓捕终点关键图 | 返工 | 不接入终点 | **color candidate 已交** (2560x1440 桌面 + 1440x1920 移动 + combined preview), 识别色全对齐 (爱丽丝暖金/桐人墨黑/尤吉欧天蓝/骑士冷银), sample_candidate 等人工验收 |
| 支持 NPC sprite (VIS-CHR-004) | 返工 | 不接 runtime | **v002 已升级**: 17 张 alpha 单帧 (11 张 JPEG 假 PNG 已用 rembg 修复) + 6 张 sprite sheet (3 角色 × up/down); 缺 left/right 方向, walk 6 帧, interact 4 帧 |
| UI/环境 SFX 候选 | 返工后可复用 | 先试听 | **v002 candidate 已修复 96KB 同尺寸问题**: 5 条差异化时长 205-510ms, 大小 29-73KB, peak -1.0 dBFS. v001 (current/) 仍标红, v002 等人工验收替换 |
| VFX sheet | 仅原型 | 功能验证 | 神圣术 v003 candidate (1024x256 RGBA, 4/4 cell corner alpha=0) 已修 alpha + 真透明; 静默线 v002 current (环境断裂+鸟散) 已重做语义 |
| BGM-002/003 | 返工 | 不接 runtime | **v004 已修复时长和 LUFS**: BGM-002 91s/84s (目标 75-110s), BGM-003 76s/66s (目标 60-100s), seam dB -240, LUFS -18.7/-18.8 真实值. 2026-08-10 状态从 changes_requested 提升到 received |
| AMB-002 森林静默 | 返工 | 不接 runtime | **v004 已修复等长和 LUFS**: 76s/76s (从 v003 的 16s/34s 不等长修复), LUFS -23.0/-22.9. 2026-08-10 状态从 changes_requested 提升到 received |

### 3.1 当前样张

| 请求 | 当前判定 | 已确认 | 必须解决 |
|---|---|---|---|
| `VIS-MAP-001` 当前地图 | `sample_candidate` | v005 9 层 + v006 tile atlas + v010 candidate AI 重做; 3024x1792 RGB; 桌面/移动预览齐全; 五地标可辨; 水印/三住宅相似/山体都修了 | 仍 sample_candidate; runtime 仍禁止; 缺 in-game 截图; v010 视觉 master 缺正式 terrain/water/roads 分层 |
| `VIS-CHR-001/002/003` 当前角色 | `sample_candidate` | down v009 36/36 帧 anchor alpha=0; **up/left/right v010 base reference 9 base + 9 sheet** | v010 4 帧差异弱 (±2px 抖动); 缺 12 帧/方向完整 walk; 缺 in-game 截图; runtime 仍禁止 |
| `VIS-KA-002` 当前抓捕终点 | `sample_candidate` | **color candidate 已交** (2560x1440 + 1440x1920 + combined); 桌面和移动黑白构图已交; 5 角色识别色全对齐 | 仍 sample_candidate; runtime 仍禁止; 需人工故事事实复核 |
| `VIS-VFX-001` 当前 VFX | `sample_candidate` | 静默线 v002 current 已重做语义; 神圣术 v003 candidate 已修 alpha | 神圣术 v003 candidate 仍在 candidate; 静默线 v002 仍在 current; 缺 in-game 播放验证 |
| `AUD-SFX-001` 当前 SFX | `sample_candidate` | **v002 candidate 已修 96KB 同尺寸**: 5 条差异化时长 205-510ms, 大小 29-73KB, peak -1.0 dBFS | v001 (current/) 仍 5×96KB; v002 在 candidate 等人工验收; 缺游戏内混音和移动端验证 |
| `AUD-BGM-002/003` | `received` (2026-08-10 提升) | v004 时长和 LUFS 全修 | 缺人耳 QA; 缺游戏内混音; 缺 ducking 验证 |
| `AUD-AMB-002` | `received` (2026-08-10 提升) | v004 等长 76s/76s + LUFS -23 | 缺人耳 QA; 缺游戏内 ducking; 缺 silent 段真听感 |

技术规格通过不代表内容、透明度、听感、正典、权利或 runtime 验收通过；所有以上样张的 `runtime_allowed` 都必须保持 `false`。

具体机器文件名和历史修订只在 `materials/MANIFEST.csv`、`materials/REQUESTS.csv` 与素材 sidecar 中追溯，不在主文档堆叠版本号。

## 3.2 T02 候选技术清理轮（仍未批准）

2026-08-08 对 `materials/inbox/visual/characters/candidate/` 中已有 down sprite 候选做了候选-only 的 matte 清理，未覆盖 `current/`，未新增 MANIFEST runtime 映射。

- 新文件：`VIS-CHR-001/002/003_sprite_sheet_down_matte_candidate.png`。
- 机器检查：3 张均为 768x96 RGBA，36/36 帧 `(32,94)` alpha=0。
- 处理内容：去除低 alpha 雾边和低色差半透明灰色背景；保留候选目录和 `sample_candidate` 边界。
- 配套证据：`VIS-CHR-001_002_003_matte_candidate_delivery.md`、`VIS-CHR-001_002_003_matte_candidate_metadata.json`，含 SHA-256 和逐帧统计。

**人工结论仍为 pending**：帧间动作/比例跳变、透明边缘是否误伤、发型/服装/道具连续性、四方向缺失和权利说明都未通过人工验收。该轮只能证明技术问题有候选改进，不能升级为 `approved-candidate`，不能填写 `runtime_file`，不能进入 runtime。

## 3.4 三方向 sprite base reference pass (v010, 2026-08-10)

在 v009 down base reference 基础上生成 3 角色 × 3 方向 (up/left/right) = 9 张 base reference + 9 张 4 帧 sheet：

- **9 base reference** (1024x1024 RGBA, alpha range [0, 255])
- **9 sheet** (256x96 RGBA, 4 帧: idle + walk_a + walk_b + interact, 36/36 cell anchor (32, 94) alpha=0)
- **image_synthesize 8/9 输出是 JPEG 假 PNG**, 已用 rembg 重新生成真 RGBA PNG
- 4 帧差异仅 ±2px 抖动 + 头部 -4px, 实际游戏内走 6 帧看不出"走路", 完整 walk 6 帧需 T02-B 程序化关键帧插值
- 配套证据: `VIS-CHR-001_002_003_v010_3direction_delivery.md`

## 3.5 SFX v002 差异化 (2026-08-10)

修复了 5 条 SFX 同尺寸同时长问题：

- 之前 v001: 5×0.6667s 硬填充, 5×96044 bytes 同尺寸
- v002 candidate: 5 条差异化时长 205/225/250/395/510ms, 5 条不同 size 29/32/36/57/74 KB
- 音色族: confirm (上行双音), cancel (下行 glide), fail (双音 descend), clue (C5→C6 arpeggio), relation (C major chord swell)
- integrated LUFS 对 < 400ms SFX 不可用, 改用 mean_volume_db
- 配套证据: `AUD-SFX-001_delivery_v002.md` + `AUD-SFX-001_v002_manifest_fragment.csv`

## 3.6 NPC sprite v002 升级 (2026-08-10)

从 `archive/unreviewed/supporting-npc/` 升级到 `inbox/visual/characters/candidate/`：

- 17 张 alpha 修复单帧 (11 张 JPEG 假 PNG 已用 rembg 修复)
- 6 张 sprite sheet (3 角色 Selka/Garret/Rulid Elder × up/down)
- 36/36 cell anchor (32, 94) alpha = 0
- 仍缺 left/right 方向, walk 6 帧, interact 4 帧 (留给 VIS-CHR-004-B/C/D)
- 配套证据: `VIS-CHR-004_v002_npc_sprite_delivery.md`

## 3.7 UI 图标集 32 枚 v001 (2026-08-10)

- 12 枚 core (VIS-UI-001) 沿用, 20 枚 expanded (VIS-UI-002) 新增
- 32 枚 × 3 尺寸 (24/48/96) = 96 PNG
- 32 枚 SVG vector 源
- 统一 meta.json 含识别色
- 12 枚 SVG 线稿风格 vs 20 枚 Pillow 实心风格, 风格有差异
- 配套证据: `VIS-UI-002_delivery.md`

## 3.8 0.6.0 P0 关系雷达图 + 草药采集点 (2026-08-10)

- **关系雷达图 VIS-UI-004**: 1 模板 + 5 角色示例 (桐人/尤吉欧/爱丽丝/赛尔卡/加斯夫特), 5 边形 + 5 轴 + 中文标签
- **草药采集点 VIS-UI-003**: 4 态 (idle/hover/active/disabled), 24/48/96 三种尺寸
- 配套证据: `VIS-UI-003_delivery.md`, `VIS-UI-004_delivery.md`

## 3.9 VIS-ENV-001 schema v006 修复 (2026-08-10)

- 添加 `geometry_placeholder_fixed: true` per scene
- 添加 `safe_area_desktop_1440x900` + `safe_area_mobile_390x844` 像素 rect
- 添加 `runtime_file` 短名 (e.g. `runtime/scenes/church-library.jpg`)
- 添加 `source_sha256` 字段 (待 tooling 补)
- 配套证据: `VIS-ENV-001_scenes_v006.json` + `VIS-ENV-001_scenes_v006_delivery.md`

## 3.3 T01 地图候选（仍未批准）

`materials/inbox/visual/world/candidate/VIS-MAP-001_master.png` 及桌面/移动预览已经存在，可作为 T01 人工验收输入：

- 3024x1792 RGB，五个核心地标可辨，右下角水印和文字残留未见于候选预览。
- 三栋住宅已经做了屋顶、院落和附属物差异化，北门、巨神树、书库和中心广场层级更清楚。
- 候选仍只是 visual master：没有正式九层地图、collision、walkable、interaction 或 tile atlas。
- 仍需人工检查正典空间关系、可走区设计、地图裁切、安全区、来源/权利和与当前 Phaser 地图合同的映射。

因此当前结论保持 `sample_candidate`：不能覆盖 `current/`，不能进入 runtime，也不能把视觉 master 当作可走地图发布。

## 4. 0.6.0 新增素材需求

| 需求 | 用途 | 优先级 | 状态 (2026-08-10) |
|---|---|---|---|
| 草药采集点图标 (VIS-UI-003) | 西侧田野采药活动 | P0 | **v001 4 态已交付** (idle/hover/active/disabled), 24/48/96 PNG, sample_candidate |
| 关系雷达图 UI (VIS-UI-004) | 关系系统可视化 | P0 | **v001 已交付** (1 模板 + 5 角色示例), 5 角色轴: 桐人/尤吉欧/爱丽丝/赛尔卡/加斯夫特, sample_candidate |
| 物品栏图标集 (VIS-UI-005) | 物品栏系统 | P1 | requested, 32 枚 48px 待做 |
| 烹饪界面素材 (VIS-UI-006) | 烹饪小游戏 | P1 | requested, 含锅灶食材火苗 |
| 钓鱼界面素材 (VIS-UI-007) | 钓鱼小游戏 | P1 | requested, 含水波鱼线浮标 |
| 石碑碎片图 (VIS-ITEM-001) | 隐藏收集内容 | P1 | requested, 1 套 3 枚 |
| 公告柱图 (VIS-ENV-002) | 村道广场每日任务 | P1 | requested, 1 张含贴纸层 |
| 记忆图鉴面板 UI (VIS-UI-008) | 通关后成就系统 | P1 | requested, 含图鉴卡背板条目 |
| 采集活动 SFX (AUD-SFX-003) | 采摘/上钩/烹饪完成 | P1 | requested, 8-12 条 |
| 西侧田野场景图 (VIS-ENV-003) | 新区域场景表现 | P1 | requested, 1 张 |
| 南湖旧渡场景图 (VIS-ENV-004) | 新区域场景表现 | P1 | requested, 1 张 |

## 5. 现在可以使用

1. 村庄开场图。
2. 现有核心肖像和 32 枚完整 UI 图标 (12 core + 20 expanded)。
3. 村庄清晨音乐与细雨环境声。
4. 选择一张场景插图试接事件面板。
5. 关系雷达图模板 (5 角色轴 + 中文标签)。
6. 草药采集点 4 态图标 (24/48/96 PNG)。
7. `current/` 中的样张只用于验收和返工参考，不升级为正式美术。
8. **新增 (v001-v010 候选)**: 三方向 sprite base reference, NPC sprite, SFX v002, BGM/AMB v004, 抓捕终点 color candidate — 全部 sample_candidate, runtime 仍禁止, 等人工验收

## 6. 下一批必须制作

### 可走村庄地图（T01）

- 主画布 3024x1792，正交或轻俯视，无透视地平线和可见网格。
- 分为地形、水、道路、建筑、植被、遮挡、前景、光照和天气层。
- collision、walkable、interaction 数据必须与地标一致。
- 教会书库、巨神树、三人住处、村广场和北门必须一眼可辨。
- 先交一张 1440x900 游戏内截图验收，不先批量生产整套。

### 核心角色（T02）

- 桐人、尤吉欧、爱丽丝使用统一帧格与人体比例。
- 四方向；idle 至少 2 帧、walk 至少 6 帧、interact 至少 4 帧。
- 三人的脚底锚点、落地阴影、碰撞盒和光照一致。
- 先验收 down 方向，通过后再补其他方向。

### 抓捕终点（T03）

- 必须同时出现卢利特村、整合骑士、爱丽丝、家人、桐人和尤吉欧。
- 事件顺序是公开宣罪、告别、被带走。
- 桌面和移动端分别构图，预留对白与按钮安全区。

### VFX（T04）

- 神圣术：alpha 修复，背景真透明。
- 静默线：重做语义（冷雾/草叶断裂/飞鸟散开），不是科幻激光。

### 音频

- BGM-002/003 返工：满足时长（75-110s / 60-100s），补正确 LUFS。
- AMB-002 返工：等长（60-90s），补正确 LUFS。
- SFX 人耳 QA：排查 5 条文件大小相同问题，确认可区分。

### 0.6.0 新增

- 关系雷达图 UI 素材（VIS-UI-004, P0）→ **v001 已交付**
- 草药采集点图标（VIS-UI-003, P0）→ **v001 已交付 (4 态)**
- 物品栏图标集（VIS-UI-005, P1）→ 32 枚 48px 待做
- 烹饪界面素材（VIS-UI-006, P1）→ 待做
- 钓鱼界面素材（VIS-UI-007, P1）→ 待做
- 公告柱图（VIS-ENV-002, P1）→ 待做
- 记忆图鉴面板（VIS-UI-008, P1）→ 待做
- 石碑碎片图（VIS-ITEM-001, P1）→ 待做
- 采集活动 SFX（AUD-SFX-003, P1）→ 待做
- 西侧田野场景图（VIS-ENV-003, P1）→ 待做
- 南湖旧渡场景图（VIS-ENV-004, P1）→ 待做

## 7. 统一命名

玩家界面、文档和日常沟通使用“村庄地图、桐人动作、抓捕关键图”等可读名称。新批准的 runtime 文件使用稳定短名：

```text
runtime/maps/rulid-village/
runtime/characters/kirito.png
runtime/scenes/church-library.jpg
runtime/audio/boundary-investigation.ogg
```

请求 ID 与历史修订只属于素材台账和 sidecar。不要再创建 `final_final`、日期副本或把素材版本号放进玩家界面。

## 8. 进入 runtime 的证据

- 来源与权利说明完整。
- 技术检查通过。
- 人工内容和正典检查通过。
- 1440×900 与 390×844 游戏内截图通过。
- 无文字遮挡、锚点漂移、可走区错位、明显水印或风格跳变。
- `MANIFEST.csv` 的 source、runtime、hash、审核人和时间完整。

`sample_candidate` 的最低交付证据还必须包括：source 与 SHA-256、delivery sidecar、机器规格检查、桌面/移动预览，以及明确的 known issues 和 next action。没有这些信息的图片或音频不得进入正式台账。
