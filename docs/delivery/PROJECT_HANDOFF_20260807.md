# UW 项目交接总览

- **状态**：Current / 项目级唯一交接入口
- **交接日期**：2026-08-07
- **项目路径**：`C:\Users\liang\Desktop\UW`
- **发布版本**：`0.4.0-preview.1`
- **当前未发布目标**：`0.5.0-pre-capture`
- **Git 基线**：`main` / `5ca1cb6efab3394c46a204ad5cec6ab7adef84e1`，与 `origin/main` 一致

本文供下一位项目负责人或智能体接手整个 UW 项目。素材生成/返工另以 [MATERIALS_REWORK_HANDOFF_20260807.md](MATERIALS_REWORK_HANDOFF_20260807.md) 为生成入口；最新逐包收件事实以 [ASSET_HANDOFF_SNAPSHOT_20260807.md](ASSET_HANDOFF_SNAPSHOT_20260807.md) 为准。当前事实、实际队列和产品边界分别以 [CURRENT_STATUS.md](../planning/CURRENT_STATUS.md)、[NEXT_PHASE.md](../planning/NEXT_PHASE.md) 和 [PRODUCT_DIRECTION.md](../product/PRODUCT_DIRECTION.md) 为准。

> **最新收件修订（2026-08-07）**：收件区已出现 `VIS-MAP-001 v004`、`VIS-ENV-001 v004`、`VIS-CHR-001/002/003 v005` 等新文件，但这些文件仍未通过 active v004 contract、来源/hash、人工内容审查和游戏内验收。角色 v005 明确只有每方向 idle 2、walk 1、interact 1 个有效帧；环境 v004 的 JSON 使用 `file` 而非 contract 要求的 `source`；地图 v004 仍缺 9 层 source 与 collision/walkable/interaction 数据；音频仍只有 v003 文件。不要把“新版本已收到”写成“返工完成”。完整事实见 [ASSET_HANDOFF_SNAPSHOT_20260807.md](ASSET_HANDOFF_SNAPSHOT_20260807.md)。

## 1. 一句话状态

正式 Pre-Capture 故事已经接入并达到 `story=ready`；第一阶段仍未完成，因为正式可玩地图、真实 Sprite 动画、VFX、抓捕表现、完整音频/SFX、运行时素材验收和 3 名陌生玩家完整主线盲测尚未完成。当前 readiness 必须写作 `materials=pending, story=ready`。

## 2. 产品目标与不可越界边界

UW 的长期目标是面向大众、容易上手、内容完整且可扩展的 2D 单人叙事 RPG。第一阶段只覆盖以下正典顺序：

```text
卢利特村三人日常 -> 巨神树天职 -> 禁忌目录与尽头山脉
-> 三人进入洞窟 -> 爱丽丝为施救越界 -> 返回卢利特村
-> 整合骑士宣告罪名 -> 告别 -> 爱丽丝被带走
```

- 唯一正式终点是 `alice_captured`；不能增加“救下爱丽丝”或其他事实结局。
- 玩家可改变关系、记忆、承诺、线索、准备和最后表达，不能改变正典关键事实。
- 不制作抓捕后剧情，不继续扩写 Day 118+；旧 Day 1-117 只保留兼容和系统压力测试价值。
- 原创内容只补充日常、活动、调查和人物表达。
- 不迁移 Cocos、不改 3D、不引入联网多人；战斗先做独立原型，验证后再接主线。

## 3. 版本与 Git 事实

- `VERSION`、frontend package 和已发布说明仍是 `0.4.0-preview.1`。
- 当前工作树承载尚未发布的 `0.5.0-pre-capture`，不能把它写成已经发布，也不能给它创建 tag。
- 交接审计历史起点为 38 个 tracked modified、152 个 untracked 文件、共 190 个 porcelain entries；当前复核为 44 个 tracked modified、180 个 untracked 文件、共 224 个 porcelain entries。数字会随素材智能体继续写入而变化；全部现有改动均保留，未清理或提交。
- 不得 `reset`、`checkout`、删除、覆盖、自动格式化整个仓库或清理 untracked 文件。
- 不得自动 commit、tag 或 push。提交前必须由用户明确确认要纳入的工作树范围。
- 过时方案应保留或移入 `docs/archive/`；不得用历史文档覆盖当前产品方向。

安全检查命令：

```powershell
git -c safe.directory='C:/Users/liang/Desktop/UW' -C 'C:\Users\liang\Desktop\UW' status --short --branch
git -c safe.directory='C:/Users/liang/Desktop/UW' -C 'C:\Users\liang\Desktop\UW' diff --check
```

## 4. 已完成与未完成

| 领域 | 当前状态 | 证据或缺口 |
|---|---|---|
| 四幕主线 | 已完成自动合同与连续路径 | N01-N10、31 个合并事件、10 个关键节点 |
| 正典终点 | 已完成 | 唯一 `alice_captured`，抓捕后剧情/日期/活动/对话/authored 写入被拒绝 |
| 选择回响 | 已完成自动合同 | 46 个跨节点回响，超过至少 3 次要求 |
| 后端权威与离线模式 | 已完成基础 | FastAPI Session 权威；`scripted` 无外部 API 可玩 |
| 地图/活动基础 | 已有原型能力 | 现有 Phaser 地图、POI 和短活动可复用 |
| 正式地图与 Sprite | 未完成 | v002 地图和三人 Sprite 均 `changes_requested`；v003 未通过完整合同 |
| UI/VFX/抓捕表现 | 未完成 | 已有原型 UI；正式 VFX、抓捕关键图和整合骑士到场素材仍缺 |
| 音频 | 部分候选 | 村庄 BGM/细雨 ambience 为内测候选；BGM-002/003、AMB-002 返工，SFX 未完成 |
| 素材 readiness | 未完成 | `materials=pending`；候选文件不得冒充正式资产 |
| 自动质量门 | 工程门通过、素材门预期失败 | 以第 8 节交接末尾实测为准 |
| 真人盲测 | 未完成 | `QA-PLAY-001` 为 `0/3`；必须从新游戏完成 N01-N10 |

## 5. 架构与关键入口

技术栈固定为 Vue 3 + Phaser 3 + FastAPI，采用模块化单体和数据驱动内容：

| 责任 | 关键入口 |
|---|---|
| FastAPI HTTP API | `backend/app/main.py` |
| 权威事务、原子提交、存档/记忆 | `backend/app/session.py` |
| 故事目录、节点和终点闸门 | `backend/app/story_director.py` |
| Pre-Capture authored 数据 | `data/story/events_precapture_chapter_01.json` |
| Vue 主场景容器 | `frontend/src/components/FieldSlice.vue` |
| Phaser 世界场景 | `frontend/src/field/createWorldFieldScene.js` |
| 活动 UI 注册 | `frontend/src/field/activityRegistry.js` |
| runtime 素材路径 | `frontend/src/field/runtimeAssetPaths.js` |
| Pre-Capture 后端回归 | `backend/tests/test_precapture_runtime.py` |
| Pre-Capture E2E | `frontend/e2e/precapture.spec.js` |
| readiness 报告 | `materials/tools/check_precapture_readiness.py` |

不可破坏的不变量：

- 后端是位置、时间、资源、剧情闸、关系、记忆和存档的唯一权威。
- 行动必须先完整校验再原子提交；拒绝时不能部分写入。
- `scripted` 是完整离线产品基线。
- `hybrid/agent` 只能提出候选表达或白名单意图；不能直接修改事实、奖励或终点。
- 前端负责输入与表现，不直接写永久世界事实。
- 新内容优先通过稳定 ID、JSON/CSV 和注册表扩展，不持续扩大巨型条件分支。

## 6. 素材现状与三层状态机制

当前 16 项第一阶段 runtime 请求为 4 项 `received`、8 项 `changes_requested`、4 项 `deferred`。v003 五包已收到但返工：稳定 `check_materials.py` 快照为 7 个未登记中间文件错误，v003 runtime review 为 76 项问题；active contract 已切到 v004。v002/v003 必须保留审计，不得覆盖或进入 runtime。

五个当前返工包：`VIS-MAP-001`、`VIS-CHR-001/002/003`、`VIS-ENV-001`、`AUD-BGM-002/003`、`AUD-AMB-002`。完整规格和可复制素材提示词见 [素材返工交接](MATERIALS_REWORK_HANDOFF_20260807.md)。

三层状态不能混写：

1. `materials/REQUESTS.csv`：整项请求的 requested/received/reviewing/changes_requested/approved/integrated/deferred。
2. `materials/MANIFEST.csv`：具体文件版本的来源、权利、SHA-256、审核和接入记录。
3. `frontend/public/assets/runtime` + 游戏内证据：已批准文件是否真实显示/播放并通过桌面与触控 QA。

正式接入链必须完整经过：

```text
request -> inbox delivery -> sidecar/rights -> manifest/hash
-> technical check -> art/canon review -> minimal runtime integration
-> desktop/touch in-game QA -> status upgrade
```

“已登记”不等于“已生成”；“已收到”不等于“合格”；“技术检查通过”不等于“美术完成”；有 runtime 路径或 build 通过也不等于游戏内验收通过。

## 7. 真人盲测机制

- `QA-PLAY-001` 当前为 `pending-human-run`，`0/3`。
- 旧 Day 1 套件只能提供上手证据，不能独立满足第一阶段完成条件。
- 每位陌生玩家必须从新游戏连续完成 N01-N10，到达 `alice_captured`，并证明抓捕后无法继续推进 authored 状态。
- 记录首次有效互动、目标/代价/收益理解、跨节点回响识别、终点理解、提示次数、卡点、完成时长和继续意愿。
- 自动 E2E、开发者自测、智能体代玩均不能替代真人记录。
- 权威跟踪页：`docs/delivery/PLAYTEST_ROUND_01_TRACKER_20260806.md`。

## 8. 质量门与当前实测

工程门：

```powershell
backend\.venv\python.exe -m pytest -q
npm.cmd --prefix frontend run test:unit
npm.cmd --prefix frontend run build
$env:CI='1'
$env:E2E_BACKEND_PORT='8033'
$env:E2E_FRONTEND_PORT='4193'
npm.cmd --prefix frontend run test:e2e -- --reporter=line
git -c safe.directory='C:/Users/liang/Desktop/UW' diff --check
```

材料与真人证据门：

```powershell
backend\.venv\python.exe materials\tools\check_materials.py
backend\.venv\python.exe materials\tools\check_runtime_asset_specs.py --require-complete
backend\.venv\python.exe materials\tools\check_precapture_readiness.py
backend\.venv\python.exe scripts\check_playtest_round.py --json
```

交接收束重新实测为 backend `330 passed`、frontend unit `16 passed`、build passed、Pre-Capture targeted Playwright `2 passed`、`git diff --check` passed。此前 fresh-port 全量 Playwright `22/22` 是最近一次成功基线；本次全量复跑在旧 Day 54-61 `field-smoke` 的地图加载/前端连接问题上超时，不能写成本轮全量通过。素材门仍为 pending：v003 产生 7 个中间文件登记错误、76 个历史技术/结构/视觉返工问题，active v004 contract 当前 52 个待交付问题；readiness 为 `materials=pending, story=ready`；真人盲测为 `0/3`。这些失败是当前产品阻塞证据，不得隐藏。

## 9. 第一阶段完成条件

只有以下条件同时成立才能宣称完成：

- readiness 为 `materials=ready, story=ready`；
- 新游戏连续运行四幕 N01-N10 到唯一抓捕终点；
- 至少三次选择产生跨节点可见回响；
- 抓捕后剧情、日期和 authored 状态不可继续推进；
- 核心地图、角色动作、UI、VFX、音频完成来源、技术、游戏内和移动端验收；
- 后端、前端、build、E2E、素材与 hash 检查全部通过；
- 3 名陌生玩家完成真人盲测并留下完整证据。

当前不满足素材和真人盲测条件，因此第一阶段未完成。

## 10. 下一位负责人实际开工顺序

1. 先读本文、产品方向、当前状态、下一阶段和素材返工交接；检查 Git，不清理工作树。
2. 将素材返工交接第 7 节提示词交给视觉/音频智能体，只接收五个 v004 包；v002/v003 仅作审计证据。
3. 对返还包依次做收件、权利、hash、技术和人工内容审查；失败即写 request_id、问题、修改要求、验收标准和优先级。
4. 只把最小通过的地图/角色/音频垂直切片接入 runtime，并完成桌面与 390x844 触控 QA 证据。
5. 再激活 VFX、SFX、抓捕关键图和整合骑士到场素材；不要提前批量生成 deferred 项。
6. 素材门通过后组织 3 名陌生玩家完整 N01-N10 盲测，修复最高频阻塞。
7. 每轮重跑全部质量门并更新 `CURRENT_STATUS.md`、`NEXT_PHASE.md`、素材审计和 `CHANGELOG.md`。

## 11. 给下一智能体的启动提示词

```text
你是 UW 项目的长期负责人。项目路径是 C:\Users\liang\Desktop\UW。先完整阅读 AGENTS.md、docs/delivery/PROJECT_HANDOFF_20260807.md、docs/product/PRODUCT_DIRECTION.md、docs/planning/CURRENT_STATUS.md、docs/planning/NEXT_PHASE.md、docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md 和 docs/delivery/MATERIALS_AUDIT_20260807.md，然后检查 git status、git diff 和现有测试；不得 reset、checkout、删除、覆盖、自动 commit/tag/push 或清理 untracked 文件。

长期目标是把 UW 做成面向大众的 2D 单人叙事 RPG。第一阶段只制作 Alicization 前期从卢利特村日常到爱丽丝被整合骑士带走，唯一终点为 alice_captured；不得制作抓捕后剧情或扩写 Day 118+。保留 Vue 3 + Phaser 3 + FastAPI，FastAPI 后端是位置、时间、资源、剧情闸、关系、记忆和存档的唯一权威；scripted 必须离线完整可玩，AI 只能提供候选表达，战斗先做独立原型。

当前事实：发布版本仍是 0.4.0-preview.1；工作树是尚未发布的 0.5.0-pre-capture。四幕 N01-N10、10 个关键节点、46 个跨节点回响和唯一抓捕终点已经 story=ready；第一阶段未完成。readiness 是 materials=pending, story=ready；五个 v003 素材返工包已收到但未通过，当前只接收 v004，QA-PLAY-001 为 0/3。不要把 received、registered、technical pass 或 build pass 写成美术完成。

每轮必须实际完成一个可验证工作单元，优先处理 NEXT_PHASE.md 当前第一项。素材返还必须留在 request 对应 inbox，经过 sidecar/rights、manifest/hash、技术、风格/正典、游戏内桌面/触控验收后才能接入 runtime。发现素材问题时，写 request_id、问题、修改要求、验收标准和优先级，更新素材审计，并立即给用户一段可复制的生成提示词。

每轮结束运行相应后端、前端、build、E2E、素材、readiness、盲测与 git diff --check，并更新 CURRENT_STATUS.md、NEXT_PHASE.md、素材审计或需求文档。报告必须包含：已完成、未完成、新素材需求/美术问题、需其他智能体生成的内容、测试结果、下一步实际行动。只有 materials=ready、story=ready、完整主线/终端状态、全部运行时素材、全部质量门和 3 名陌生玩家真人盲测同时通过，才能宣称第一阶段完成。
```
