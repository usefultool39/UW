# 0.5 Pre-Capture 素材返工交接

- **状态**：Current / 素材返工唯一交接入口
- **交接日期**：2026-08-07
- **项目路径**：`C:\Users\liang\Desktop\UW`
- **目标版本**：`0.5.0-pre-capture`
- **下一交付版本**：`v004`，不得覆盖失败的 v002/v003
- **正式终点**：爱丽丝被整合骑士带走

本文只负责视觉/音频返工。整个项目的版本、Git、架构和下一智能体入口见 [PROJECT_HANDOFF_20260807.md](PROJECT_HANDOFF_20260807.md)；真实完成度见 [CURRENT_STATUS.md](../planning/CURRENT_STATUS.md) 和 [MATERIALS_AUDIT_20260807.md](MATERIALS_AUDIT_20260807.md)。

## 1. 当前素材到底到了什么程度

- 故事为 `story=ready`：四幕、N01-N10、10 个关键节点、46 个跨节点回响和唯一 `alice_captured` 终点已通过自动校验。
- 素材仍为 `materials=pending`：16 项第一阶段 runtime 请求维持 4 项 `received`、8 项 `changes_requested`、4 项 `deferred`。
- v003 五个包已经输出到 inbox，但全部仍是 `changes_requested`，没有任何 v003 文件进入正式 MANIFEST 或 runtime。
- 后续收件区已出现 `VIS-MAP-001 v004`、`VIS-ENV-001 v004` 和 `VIS-CHR-001/002/003 v005`；它们仍是 inbox 收件证据。地图/环境尚未满足 active metadata schema，角色 v005 每方向只有 4 个有效帧，音频仍只有 v003 文件；逐包事实以 [ASSET_HANDOFF_SNAPSHOT_20260807.md](ASSET_HANDOFF_SNAPSHOT_20260807.md) 为准。
- v003 稳定快照：`check_materials.py` 为 7 errors；v003 runtime review 为 76 issues。之后 active contract 已非破坏性切到 v004，当前 v004 gate 为 52 issues（等待交付），不能把 v003 或中间态误判为通过。
- v003 人工抽查失败：地图像调试网格且缺可信村庄语义，三人 Sprite 是极简程序化人偶，六场景是几何占位；音频仅有自报测量，metadata/命名未通过 gate，且尚未完成人耳循环验收。
- 现有 runtime 的关键图、肖像、12 枚图标、村庄 BGM 和细雨 ambience 只算原型/内测候选，不代表完整美术完成。
- 真人盲测仍为 `0/3`。

## 2. v003 为什么不能接入

| 包 | request_id | v003 结论 | v004 重点 | 优先级 |
|---|---|---|---|---|
| 可玩地图 | `VIS-MAP-001` | 调试网格感强；黑块/几何覆盖；terrain+water 合并；metadata schema 不符；atlas 名无 request_id | 重做正式视觉，独立 9 层与 3 类数据，严格按 active contract | P1 blocker |
| 三名角色 | `VIS-CHR-001/002/003` | 极简几何人偶；动作差异弱；JSON 不能被 gate 解析 | 真正可读的四向 idle/walk/interact RGBA sheet 和逐动画 metadata | P1 blocker |
| 六个场景 | `VIS-ENV-001` | 1920x1080 但只是平面几何占位；scenes schema 不符 | 六张正式活动/转场背景，地点可辨，安全裁切，正确 source map | P1 |
| 两组 BGM | `AUD-BGM-002/003` | 时长/测量接近目标，但命名、sidecar 目录、metadata/measurement schema 不符；未做人耳 QA | 非破坏性 v004 导出与 exact metadata；听感/循环/ducking QA | P1 blocker |
| 森林环境声 | `AUD-AMB-002` | 等长自报通过，但同样未被 gate 读取；未做人耳 A/B 验收 | v004 exact contract、同 loop points、非数字静音、人耳 A/B QA | P1 blocker |

逐包评审：

- [VIS-MAP-001 v003 评审](../../materials/inbox/visual/world/REVIEW_VIS-MAP-001_v003_20260807.md)
- [VIS-CHR-001/002/003 v003 评审](../../materials/inbox/visual/characters/REVIEW_VIS-CHR-001-003_v003_20260807.md)
- [VIS-ENV-001 v003 评审](../../materials/inbox/visual/environments/REVIEW_VIS-ENV-001_v003_20260807.md)
- [AUD-BGM-002/003 v003 评审](../../materials/inbox/audio/bgm/REVIEW_AUD-BGM-002-003_v003_20260807.md)
- [AUD-AMB-002 v003 评审](../../materials/inbox/audio/ambience/REVIEW_AUD-AMB-002_v003_20260807.md)

`VIS-VFX-001`、`VIS-KA-002`、`AUD-SFX-001`、`AUD-SFX-002`、`VIS-CHR-005`、`VIS-ANIM-001`、`VIS-TILE-001` 仍为 deferred，本轮不要擅自生成。

## 3. 谁负责什么

### 素材智能体

- 只制作/重导 `VIS-*`、`AUD-*`、包内 metadata、sidecar、测量和 MANIFEST fragment。
- 不修改剧情、代码、`REQUESTS.csv`、正式 `MANIFEST.csv` 或 `frontend/public/assets/runtime`。
- 不删除或覆盖 v002/v003，不把“文件已输出”写成“已批准/已接入”。

### 项目负责人

- 核对 request、版本、目录、来源/权利和逐文件 hash。
- 执行技术、风格/正典、桌面/触控游戏内 QA。
- 只有通过完整链路后才更新正式台账和 runtime。

### 用户

- 把第 7 节提示词发给视觉/音频素材智能体。
- 最终组织 3 名陌生玩家从新游戏完成 N01-N10；不以开发者或智能体代打替代。

## 4. 三层状态机制

| 层级 | 权威位置 | 回答的问题 | 禁止混淆 |
|---|---|---|---|
| 请求层 | `materials/REQUESTS.csv` | 请求是待交、收到、返工、批准还是延期 | `received` 不等于合格 |
| 文件层 | `materials/MANIFEST.csv` | 具体版本的来源、权利、hash、审核人与状态 | fragment 不等于正式登记；`approved-candidate` 不等于游戏内验收 |
| runtime 层 | runtime + 正式 manifest + 游戏内证据 | 文件是否真实显示/播放并通过桌面/触控 QA | 有路径或 build 通过不等于美术完成 |

请求状态流：

```text
changes_requested -> received -> reviewing -> approved -> integrated
                           |          |
                           +-> changes_requested
                           +-> rejected / deferred
```

## 5. v004 交付合同

> **当前收件修订（2026-08-07）**：active contract 仍然是 `materials/runtime_asset_requirements.json` 中的 v004。收件区后来出现的 `VIS-MAP-001 v004`、`VIS-ENV-001 v004` 和三人 `v005 Sprite` 仍是 `received`/待审文件，不是 approved；v005 Sprite 不能替代 active contract 所要求的 `*_frames_v004.json`。音频当前仍没有 v004 文件。逐包结论见 [ASSET_HANDOFF_SNAPSHOT_20260807.md](ASSET_HANDOFF_SNAPSHOT_20260807.md)。

1. 新文件按 active contract 交付 `v004`，不得覆盖、改名或删除 v002/v003；若生成工具内部版本已经推进到 v005，仍必须按项目负责人要求提供与 contract 对齐的正式替代包，并明确 `supersedes`，不得以版本号变化绕过门禁。
2. 只放入 request 对应目录；工作脚本、测试音频和临时图不得留在正式 inbox 扫描范围。
3. 每个 request 提供同目录主 sidecar，列出包内每个文件；不得把 review memo 当 sidecar。
4. sidecar 包含 request_id、creator/source、created_at、真实 tool/model/version、完整 prompt/negative prompt、seed/settings、edits、license、source_url/无 URL 原因、intended_use、rights statement。
5. 每包提供 18 列 `*_manifest_fragment_v004.csv`，一文件一行且 SHA-256 匹配；status 只写 received，runtime/审核/接入字段留空。已收到的 v005 fragment 只能作为收件证据，项目负责人不会直接合并到正式 manifest。
6. JSON 与文件名严格按 `materials/runtime_asset_requirements.json` 和逐包 v003 评审；不要自创近似 schema。
7. 视觉不得使用纯几何占位、烘焙文字/UI/水印/棋盘格、官方截图、动画临摹、拆包素材或来源不清参考。
8. 交付回复只陈述文件与实测，不得宣称 approved、integrated、ready 或完成第一阶段。

## 6. 项目负责人验收链

1. 收件：request_id、v004、目录、清单与命名完整。
2. 来源/权利：sidecar、工具、提示词、许可和 URL/说明完整。
3. 登记：fragment 18 列、逐文件 hash 与实物一致；项目负责人再合并正式 MANIFEST。
4. 技术：运行 materials、runtime specs 和 readiness。
5. 内容：地图语义、Sprite 动作、场景完成度、音频循环/原创性人工审查。
6. 候选接入：只复制最小通过切片到 runtime，补审核人与时间。
7. 游戏内：键鼠/触控、碰撞/遮挡、锚点、UI、loop/ducking、桌面/390x844 截图。
8. 升级状态：更新 request、manifest、素材审计、CURRENT_STATUS、NEXT_PHASE；只有此时才能写 integrated。

命令：

```powershell
backend\.venv\python.exe materials\tools\check_materials.py
backend\.venv\python.exe materials\tools\check_runtime_asset_specs.py --require-complete
backend\.venv\python.exe materials\tools\check_precapture_readiness.py
backend\.venv\python.exe -m pytest -q
npm.cmd --prefix frontend run test:unit
npm.cmd --prefix frontend run build
```

## 7. 可直接复制给素材智能体的 v004 提示词

```text
你是 UW 项目的视觉与音频素材返工智能体。项目路径是 C:\Users\liang\Desktop\UW，目标版本是 0.5.0-pre-capture，故事只到爱丽丝被整合骑士带走。你只负责生成/重导素材及交付元数据，不得修改剧情、代码、REQUESTS.csv、正式 MANIFEST.csv 或 frontend/public/assets/runtime，不得宣称 approved、integrated、materials=ready 或第一阶段完成。

先完整阅读：
- docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md
- materials/runtime_asset_requirements.json
- materials/inbox/visual/world/REVIEW_VIS-MAP-001_v003_20260807.md
- materials/inbox/visual/characters/REVIEW_VIS-CHR-001-003_v003_20260807.md
- materials/inbox/visual/environments/REVIEW_VIS-ENV-001_v003_20260807.md
- materials/inbox/audio/bgm/REVIEW_AUD-BGM-002-003_v003_20260807.md
- materials/inbox/audio/ambience/REVIEW_AUD-AMB-002_v003_20260807.md

v002/v003 均为失败审计证据，禁止覆盖、删除或改名。本轮只交 v004，且只处理以下五包：

1. VIS-MAP-001：重做原创、清晰、明快、具有可信村落语义的卢利特村 3/4 俯视可玩地图。v003 的黑色网格块、平直矩形道路、圆形光斑和几何建筑不可沿用为正式美术。严格 108x64 tiles、28px/tile、3024x1792。独立交 terrain、water、roads、buildings、vegetation、occlusion、foreground、lighting、weather；另交 request-prefixed tile/prop atlas、collision、walkable、interaction 数据。metadata 为 VIS-MAP-001_map_v004.json，顶层包含 runtime_size:[3024,1792]、layers.<name>.source、data.collision/walkable/interaction，路径从项目根可解析。无角色、文字、UI、水印、棋盘格或版权构图。

2. VIS-CHR-001/002/003：重做桐人、爱丽丝、尤吉欧儿童阶段的原创 RGBA Sprite。禁止继续使用 v003 的极简几何人偶和轻微位移重复帧。统一 64x96 或 96x128 cell；down/left/right/up 每方向 idle 2、walk 6、interact 4 个真正不同且动作可读的帧；统一 bottom-center 脚底锚点与 collision footprint，44-52px 显示高度可区分三人。分别交 *_frames_v004.json，顶层 frame_width/frame_height，animations.down_idle 至 animations.up_interact；每帧提供 source 和 [x,y,width,height] rect。真实 8-bit RGBA，既有透明像素也有可见角色像素，无背景、文字、烘焙阴影或官方动画临摹。

3. VIS-ENV-001：重做六张正式 1920x1080 活动/转场背景：church_library、gigas_clearing、home_hearth、north_gate、forest_path、end_mountains_cave。v003 的纯色块/三角形/矩形占位不可沿用。每张需有独立地点身份、材质、光照、景深和叙事焦点，与地图/Sprite 风格一致；无角色、文字、水印，保留中下部互动区和桌面/移动裁切安全区。VIS-ENV-001_scenes_v004.json 使用 scenes.<scene_id>.source。

4. AUD-BGM-002/003：可在确认听感合格后使用 v003 音源作候选源，但非破坏性导出 v004。BGM-002 两版 75-110 秒、-20 至 -17 LUFS、peak <= -1 dBFS；BGM-003 两版 60-100 秒、同响度/峰值范围。每版交 48kHz/24-bit stereo `<stem>_48k24b.wav` 和有效 OGG，loop start/end samples。metadata 写入 materials/inbox/audio/audio.meta_v004.fragment.json，按 stem 建对象并含 duration/sample_rate_hz/bit_depth/channels/loop_safe/loop_start_sample/loop_end_sample。measurements_v004.json 必须是逐文件数组，每项含 file、integrated_loudness_lufs、peak_dbfs。request sidecar/manifest fragment 放在 materials/inbox/audio/bgm/。完成人耳两轮循环、重复前景和版权旋律自检。

5. AUD-AMB-002：normal/silent 两版必须 60-90 秒、完全等长且 loop samples 相同，-26 至 -22 LUFS、peak <= -2 dBFS，支持 2-4 秒交叉淡化。silent 不是数字静音，要保留低空气压力和远处细枝并形成不自然频段空缺。文件、metadata/measurement schema 同第 4 项；request sidecar/manifest fragment 放在 materials/inbox/audio/ambience/。

每个 request 在对应目录交一个 v004 主 sidecar，记录真实 creator/source、created_at、tool/model/version、完整 prompt/negative prompt、seed/settings、edits、license、source_url/无 URL 原因、intended_use、rights statement 和全文件清单。每包交 18 列 *_manifest_fragment_v004.csv：asset_id,request_id,status,source_file,runtime_file,sha256,creator,tool_model,created_at,license,source_url,attribution_required,attribution_text,approved_by,approved_at,integrated_at,replaces_asset_id,notes。status 只写 received；runtime_file、approved_by、approved_at、integrated_at 留空。

工作脚本、测试 ogg、临时 atlas 不要放在正式 inbox 扫描范围；所有正式文件名必须含 request_id。完成后先自行运行 check_materials.py 和 check_runtime_asset_specs.py --require-complete，只汇报实际输出、实测值、命令结果和未满足项。不要修改正式台账，不要把“已生成/技术检查通过”写成“已验收”。
```
