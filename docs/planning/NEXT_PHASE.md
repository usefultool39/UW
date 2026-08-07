# 下一阶段：0.5.0 Pre-Capture 主线收束

> 接手整个项目先读 [PROJECT_HANDOFF_20260807.md](../delivery/PROJECT_HANDOFF_20260807.md)；交给素材智能体只使用 [MATERIALS_REWORK_HANDOFF_20260807.md](../delivery/MATERIALS_REWORK_HANDOFF_20260807.md)。

## 2026-08-07 Runtime checkpoint

- Story is `ready`: the authored N01-N10 route is continuous, four acts and 10 key nodes are validated, and all choices converge on the single `alice_captured` endpoint.
- Materials are `pending`: eight received requests are `changes_requested`, four required runtime requests remain deferred, the v003 delivery snapshot reports 7 unregistered intermediate-file errors and 76 technical/schema/visual issues, and the active v004 runtime contract currently reports 52 missing/invalid delivery items. No incoming replacement binary is approved or integrated.
- Latest inbox delta is recorded in [ASSET_HANDOFF_SNAPSHOT_20260807.md](../delivery/ASSET_HANDOFF_SNAPSHOT_20260807.md): map v004 and environment v004 are received but schema/gameplay review is incomplete; character v005 contains only 4 effective frames per direction and cannot satisfy the required 12; audio remains v003 while the active contract requires v004. Keep all of these inbox-only.
- Immediate external action: send [MATERIALS_REWORK_HANDOFF_20260807.md](../delivery/MATERIALS_REWORK_HANDOFF_20260807.md) to the visual/audio asset agent and receive five v004 correction packages. v002/v003 remain audit evidence and must not be overwritten. The map must become a real grid/layer/collision package; the characters must become true RGBA frame sets; scenes must stop being geometry placeholders; audio must be exported with exact metadata, rights, and manifest data.
- Internal gates completed this round: the runtime checker validates map layer dimensions/grid metadata, Sprite alpha/frame manifests, decoded visible/transparent Sprite pixels, scene dimensions, WAV audio duration/format, OGG page framing, and audio loop/loudness metadata; the active contract version lock now targets v004. `check_materials.py` also rejects unregistered runtime files, non-approved runtime statuses, and runtime paths without reviewer/timestamp evidence.
- Verification used the project-local `backend/.venv/python.exe`: backend `330 passed`, frontend unit `16 passed`, production build passed, and targeted Pre-Capture Playwright passed `2/2` on isolated ports `8034/4194`. The previous fresh-port full-suite `22/22` and Day 54 to Day 61 target `1/1` remain historical successful evidence; a new full-suite attempt timed out in the legacy field smoke after a map-load/unknown-location state. The full-suite compatibility risk remains open, and the system Python result is not an accepted project baseline.
- Next actual internal action: run the new gate against corrected deliveries, then integrate the smallest approved map/character/audio vertical slice and capture runtime evidence.
- Keep every returned binary in request-scoped `materials/inbox` until request, sidecar, source/rights, technical, in-game, and manifest/hash checks all pass. Three-player blind testing remains `0/3`.
- Preserve the targeted Pre-Capture E2E baseline (`2/2` on `8034/4194`), then isolate the legacy Day 54-61 `field-smoke` map-load/server-lifecycle timeout before claiming the full Playwright gate again. The previous `22/22` run is historical successful evidence, not the latest rerun result.

- **状态**：Current / 执行入口
- **阶段代号**：M4 Pre-Capture Canonical Arc
- **目标版本**：`0.5.0-pre-capture`（尚未发布）
- **更新日期**：2026-08-07
- **上位基线**：[PRODUCT_DIRECTION.md](../product/PRODUCT_DIRECTION.md)
- **素材入口**：[11_PRECAPTURE_EXECUTION_BRIEF.md](../../materials/11_PRECAPTURE_EXECUTION_BRIEF.md)

## 当前事实

代码已有 Vue 3 + Phaser 3 + FastAPI 的地图、活动、关系、记忆、日期闸、存档、内容校验和离线回退骨架。材料登记当前并未通过：v003 返工快照为 7 个中间文件登记错误与 76 项技术/结构/视觉问题，active v004 合同等待新交付；候选图/音频不等于完整生产资产。故事 readiness 已为 `ready`：31 个合并事件中有四幕标记、10 个关键节点、唯一抓捕终点和 46 个跨节点回响；21 个旧事件仅作为兼容内容。

Day 1–117 的旧 authored 内容只作为兼容和系统验证记录，不再作为本阶段叙事目标；不继续扩写 Day 118+。爱丽丝被带走之后另立章节。

## 开工顺序

### 1. 文档与输入收束

- [x] 以 `PRODUCT_DIRECTION.md` 为唯一产品基线。
- [x] 将冲突的旧 Brief、Roadmap、MVP、Requirements 和混合 Next Phase 归档。
- [x] 登记四项后续完整性需求：`VIS-KA-002`、`VIS-CHR-005`、`VIS-ANIM-001`、`VIS-TILE-001`；当前均为 `P1/deferred`，不冒充已开工。
- [x] 审核用户/素材智能体返还的正典、人物、地点和连续性资料；七项叙事输入已通过 readiness，来源材料继续保留在 `materials/inbox` 供审计。

### 2. 正典主线

- [x] 建立四幕事件卡：村中日常、尽头山脉越界、返村与告别、整合骑士到场与抓捕。
- [x] 为每幕登记 2–3 个关键节点，写清进入条件、选择、代价、结果、后续回响和正典依据。
- [x] 固定唯一终点 `alice_captured`，抓捕后拒绝剧情推进、日期推进和 authored 写入。
- [x] 统一桐人、尤吉欧、爱丽丝、赛尔卡的玩家可见名称、关系动机和时间锚点；兼容旧 ID 但不再产生旧显示名。
- [x] 用连续性检查阻止抓捕后身份、中央大教堂后期状态和 War of Underworld 内容提前出现。

### 3. 资产与运行时

- [ ] 事件卡冻结后，按素材审计激活 `VIS-MAP-001`、`VIS-CHR-001` 至 `003`、`VIS-ENV-001`、`VIS-VFX-001` 和必要音频；视觉智能体只负责 `VIS-*`/`AUD-*` 交付。
- [ ] 在抓捕节点规格稳定后再激活 `VIS-KA-002`、`VIS-CHR-005`、`VIS-ANIM-001`、`VIS-TILE-001`，避免提前生成后整体返工。
- [ ] 每个场景具备可走层、碰撞/遮挡层、前景层、交互点和 manifest，不以背景图替代地图。
- [ ] 每个核心角色具备 idle、四向 walk、interact、表情/受击所需的最小集；战斗动作留给独立原型。
- [ ] 用代表场景做比例、锚点、文字遮挡、移动端和音画触发验收，再批量扩展。

### 4. 验证与交付

- [ ] 运行 materials、Pre-Capture readiness、后端 pytest、前端单测、build、Playwright 和 `git diff --check`。
- [ ] 组织 3 名没有读过开发文档的玩家从新游戏完成 N01-N10，记录首次互动、目标/代价/收益、选择回响、抓捕原因、终端状态、卡点、完成率和继续意愿；Day 1 记录不能单独满足本项。
- [ ] 只修复最高频阻塞；更新 `CURRENT_STATUS.md`、材料审计和变更记录，不复制第二份 TODO。

## 暂不做

- 不写爱丽丝被带走之后的剧情，不扩写 Day 118+。
- 不做完整战斗、全地图重绘、全角色动作包、全量配音、Cocos 迁移或 3D 重写。
- 不把候选素材直接放入正式 runtime，不让模型修改权威世界事实。
- 不增加独立的“推进日期/跳过当天”玩家按钮；日期只能由剧情闸和日结算推进。

## 完成定义

- readiness 报告为 `materials=ready`、`story=ready`。
- 四幕主线可以从新游戏连续运行到唯一抓捕终点，至少三次选择产生跨节点可见回响。
- 抓捕后本章不可继续推进，存档、回放、刷新和重复请求均保持终端状态。
- 核心素材经过来源、技术、风格、游戏内和移动端验收；不存在 P0 资产缺口。
- 自动质量门全部通过，且 3 名真人盲测记录完整。
