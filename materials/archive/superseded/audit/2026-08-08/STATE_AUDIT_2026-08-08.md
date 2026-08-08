# UW 素材状态盘点（2026-08-08）

- 对应版本：0.5.0
- 负责人：UW 素材智能体
- 输入材料：materials/inbox/*、materials/MANIFEST.csv、materials/REQUESTS.csv
- 作用：把当前素材真实状态、上一轮返工的实际差距、本次交付的样张策略写清楚，给下游审核人一次过目。
- 不在本文中：runtime 接入、approved 标记、玩家 UI 文案。

## 1. 真实状态

| Request | 已交付版本 | 视觉/听觉判断 | 结论 |
|---|---|---|---|
| VIS-POR-001 肖像 | v002（player/alice/eugeo × neutral/concerned） | 1024×1024 RGBA 透明，识别色稳定，IP 化完成，签字笔+记录册+剑鞘等原创功能件 | **可用**，runtime 256 已就位 |
| VIS-KA-001 关键图 | v002（village/boundary/library × desktop/mobile） | 2560×1440 / 1440×1920，村庄主图与开场图风格一致，色调雨后清晨，无水印 | **可用** |
| VIS-ENV-001 场景 | v005（6 场） | 1920×1080 RGB，文字安全区/中心焦点保留，与 v002 风格一致 | **可用** |
| VIS-MAP-001 地图 | master_v004 + layers_v005 + tile_atlas_v006 | **master_v004 底图带可见方格网格**（每 28px 一格），违反 P0 规则"无可见网格"；v005/v006 分层虽完整，但都派生自违规底图 | **返工**。优先重画无网格底图 |
| VIS-CHR-001/002/003 角色 sprite | v008 程序化 | head-body 比例偏 chibi，walk 6 帧几乎无跨步差异，interact 4 帧差异弱，delivery md 自称"圆润有机剪影+真实行走相位+4 帧可读交互动作"与实物不符 | **返工**。v009 重画 |
| VIS-UI-001 核心图标 | v001 12 枚 | SVG currentColor，24/48/96 PNG，线宽/留白统一 | **可用** |
| VIS-UI-002 完整 32 枚 | 未启动 | 缺缺口清单 | **待缺口** |
| VIS-VFX-001 VFX | 未启动 | 序章需要至少神圣术/静默线/关系暖光/奖励闪光 | **待做** |
| AUD-BGM-001 村庄清晨 | v001 | 时长/LUFS/peak 达标，已进 runtime | **可用** |
| AUD-AMB-001 细雨 | v002 | LUFS/peak 达标，已进 runtime | **可用** |
| AUD-BGM-002 边界调查 | v004 a/b | 时长/LUFS/peak 达标，sidecar/manifest 在 `audio/bgm/`，**缺人耳 QA** | **可入 review**，需人耳 |
| AUD-BGM-003 关系日常 | v004 a/b | 同上 | **可入 review**，需人耳 |
| AUD-AMB-002 森林静默 | v004 normal/silent | 76s 等长，normal/silent 切换保留低频空气 | **可入 review**，需人耳 A/B |
| AUD-SFX-001 反馈 | 未启动 | 缺最小集：确认/取消/失败/线索/关系变化 | **待做** |
| AUD-SFX-002 脚步/翻书/门 | 未启动 | 需多 surface 变体 | **待做** |
| VIS-KA-002 抓捕终点 | 未启动 | 序章核心 P0 阻塞 | **待做** |
| VIS-ANIM-001 互动动作包 | 未启动 | 依赖 v009 sprite 风格 | **待做** |
| VIS-CHR-004 支持 NPC | 未启动 | 依赖 v009 sprite 风格 | **待做** |
| VIS-CHR-005 整合骑士 | 未启动 | 依赖 VIS-KA-002 抓取构图 | **待做** |
| VIS-TILE-001 完整贴图 | 未启动 | 依赖无网格底图 | **待做** |

## 2. 上一轮 v008 失败的根本原因

- v008 用 Python + Pillow 程序化绘制（圆头 + 矩形身体 + 直线四肢），把"动画 12 帧"理解为 12 张相似姿态的描边涂色。
- 真正需要的：3.5 头身儿童比例、可见的腿部跨步、interact 4 帧有明确可读的姿势差异。
- 解决路径：v009 用 AI 单帧生成分辨率更高的原画，再 PIL 程序化拼成 768×384 sheet。这样既保留 AI 对"姿势"和"剪影"的真实理解，又保留程序化的帧对齐与锚点精度。

## 3. 上一轮 v004 master 失败的根本原因

- v004 master 用 prompt 生成的图自带 28px 网格（因 prompt 中写了"108×64 grid, 28px/tile"被模型读成"请画格"）。
- 解决路径：master 图的 prompt 改成"no grid, no checkerboard, no debug overlay, orthographic / top-down 3/4"；同时不再把 grid 写进 prompt，grid 概念只用于 v005/v006 内部拼接。

## 4. 本次（2026-08-08）交付范围

不做全量重做、不批量铺全图、不接 runtime、不标 approved。本次只交**样张**：

1. **v009 sprite 样张**（VIS-CHR-001 kirito 1 方向 down 12 帧样张 sheet）。
   - 通过后再做 alice、eugeo 1 方向样张；三个全通过后再做剩余 3 方向。
2. **VIS-KA-002 v001 黑白构图**（桌面 2560×1440 + 移动 1440×1920）。
   - 通过后再进入上色 v002。
3. **VIS-VFX-001 v001 样张**（神圣术 1 张 + 静默线 1 张 frame table）。
4. **AUD-SFX-001 v001 最小反馈音**（5 条 TTS 替代后处理为短音）。

每一项交付都附 delivery md、manifest fragment、sidecar JSON、SHA-256、来源与权利。

## 5. 不在本次范围

- 整合骑士 VIS-CHR-005：等 VIS-KA-002 黑白构图定稿。
- 支持 NPC VIS-CHR-004：等 v009 sprite 风格定稿。
- VIS-ANIM-001 互动动作包：等 v009 全方向完成。
- VIS-TILE-001 完整贴图表：等 VIS-MAP-001 无网格底图完成。
- VIS-UI-002 32 枚扩展图标：等 12 枚核心接入并总结缺口。
- AUD-SFX-002 脚步/翻书/门：等本次反馈音完成并校准音量。

## 6. 验收口径

- 每张样张交付时附 1440×900 + 390×844 屏幕坐标示意图。
- 同一角色的肖像、sprite、关键图必须保持发型、服装、识别色、身高比例一致。
- 6 张场景图、2 张关键图必须在同一晨光色温下保持。
- 任何带水印/文字/棋盘格/几何占位/烘焙阴影的样张不交付。
