# UW 素材交接快照

- **快照日期**：2026-08-07
- **项目路径**：`C:\Users\liang\Desktop\UW`
- **目标版本**：`0.5.0-pre-capture`
- **素材总状态**：`materials=pending`
- **故事总状态**：`story=ready`
- **唯一正式终点**：`alice_captured`
- **当前结论**：素材收件区已有明显更新，但没有任何本轮返工包完成完整验收或进入正式 runtime。

## 1. 结论先行

当前可以交接的是一个“故事已锁定、工程骨架已验证、素材仍在返工”的工作树，不是第一阶段正式完成版。

- Authored 主线：四幕、N01-N10、31 个合并事件、10 个关键节点、46 个跨节点回响，唯一终点为 `alice_captured`。
- 工程门最近基线：backend `330 passed`，frontend unit `16 passed`，production build 通过，Playwright `22 passed`，`git diff --check` 通过。
- 素材门：`check_materials.py` 仍有 `7 errors`；active v004 runtime contract 仍有 `52 issues`。
- 真人盲测：`QA-PLAY-001` 为 `pending-human-run`，完整 N01-N10 到终点的证据为 `0/3`。
- 未批准文件一律留在 `materials/inbox`，不得因为尺寸、文件存在或视觉质量变好而进入 `frontend/public/assets/runtime`。

## 2. 当前请求台账

第一阶段 16 项 runtime 请求的状态为：4 项 `received`、8 项 `changes_requested`、4 项 `deferred`。另外 7 项叙事输入为 `received`，`QA-PLAY-001` 尚未完成真人运行。

| request_id | 最新收件包 | 台账状态 | 当前判断 | 下一动作 | 优先级 |
|---|---|---|---|---|---|
| `VIS-MAP-001` | v004 master + map JSON + manifest fragment | `changes_requested` | 视觉语义比 v003 好，但仍是一张合并 master；JSON 没有 active contract 要求的 9 层 source、runtime_size、collision/walkable/interaction | 重新交付可玩的分层地图与独立数据；不得接入 master 代替地图 | P1 blocker |
| `VIS-CHR-001` | v005 Sprite sheet + frames JSON | `changes_requested` | 每方向只有 idle 2、walk 1、interact 1 个有效帧，walk 其余 5 帧和 interact 其余 3 帧为空；不是完整动作包 | 按 active v004 contract 交四向 idle 2 / walk 6 / interact 4 的真实不同帧 | P1 blocker |
| `VIS-CHR-002` | v005 Sprite sheet + frames JSON | `changes_requested` | 同上；不可用静态或重复帧冒充动作 | 重新交付完整四向动作包 | P1 blocker |
| `VIS-CHR-003` | v005 Sprite sheet + frames JSON | `changes_requested` | 同上；三人必须有清晰轮廓、动作差异和共同锚点 | 重新交付完整四向动作包 | P1 blocker |
| `VIS-ENV-001` | v004 六张 1920x1080 背景 + scenes JSON | `changes_requested` | 六张图已有地点语义，JSON 仍使用 `file`，active contract 要求 `scenes.<scene_id>.source`；尚无人机内验收 | 修正 metadata/source 映射后做桌面与 390x844 游戏内验收 | P1 |
| `AUD-BGM-002` | v003 WAV/OGG + v003 metadata/measurement | `changes_requested` | 时长和自报测量接近目标，但 active contract 只接收 v004；尚无可读的 v004 metadata、measurement 和人耳 loop/ducking QA | 非破坏性导出 v004，补齐 schema、sidecar、hash 和人耳 QA | P1 blocker |
| `AUD-BGM-003` | v003 WAV/OGG + v003 metadata/measurement | `changes_requested` | 同上 | 非破坏性导出 v004，补齐 schema 与 QA | P1 blocker |
| `AUD-AMB-002` | v003 normal/silent WAV/OGG + v003 metadata/measurement | `changes_requested` | normal/silent 等长自报接近目标，但 active contract 只接收 v004；尚无 v004 metadata、measurement 和人耳 A/B QA | 非破坏性导出 v004，确认 2-4 秒交叉淡化和非数字静音听感 | P1 blocker |

## 3. 已收到但不是正式完成的素材

以下状态只说明文件进入收件区或已有历史候选，不说明通过验收：

- `VIS-POR-001`：三名核心角色肖像候选；不能替代地图 Sprite、四向移动或互动动作。
- `VIS-UI-001`：12 枚 UI 图标候选；不是完整 32 枚 UI 包，仍需 24px 可读性和数据注册验收。
- `AUD-BGM-001`、`AUD-AMB-001`：村庄/细雨内测候选；仍需 runtime loop、ducking、桌面/触控验收。
- `VIS-ENV-001 v004`：可作为活动/转场背景候选，不能冒充可玩地图。
- `VIS-MAP-001 v004`：可作为视觉方向候选，不能冒充分层地图。
- `VIS-CHR-001/002/003 v005`：外观比 v003 更好，但动作合同未满足，不能作为正式 Sprite。

失败的 v002/v003、中间测试文件、review memo、delivery sidecar 和 manifest fragment 都必须保留为审计证据，不得覆盖、删除或改写为 approved。

## 4. 素材状态机制

### 请求层：整项工作是什么状态

权威文件：`materials/REQUESTS.csv`

```text
requested -> received -> reviewing -> approved -> integrated
                         |              |
                         +-> changes_requested
                         +-> rejected / deferred
```

`received` 只代表收到文件和最低元数据；`changes_requested` 代表存在明确评审意见；`approved` 只能由项目负责人在技术、来源/权利和内容审查后写入；`integrated` 还必须有 runtime 与游戏内验收证据。

### 文件层：具体文件能不能追溯

权威文件：`materials/MANIFEST.csv`，素材智能体只交 `*_manifest_fragment_vXXX.csv`。

每个二进制文件必须能追溯到 request_id、版本、来源/创作者、工具/模型、许可、source URL 或无 URL 原因、SHA-256、审核人、审核时间、runtime 路径和接入时间。fragment 不是正式 manifest，`approved-for-direction`/`approved-candidate` 也不等于游戏内验收。

### Runtime 层：玩家实际看到/听到的是什么

只有完整通过以下链路才可以复制到 `frontend/public/assets/runtime`：

```text
request
  -> inbox delivery
  -> sidecar + rights
  -> manifest/hash
  -> technical checker
  -> visual/canon/audio review
  -> minimal runtime integration
  -> desktop + touch in-game QA
  -> request/manifest status upgrade
```

素材智能体不得修改正式 runtime、正式 `MANIFEST.csv`、`REQUESTS.csv`、剧情或代码。项目负责人不得把“已登记”“文件存在”“build 通过”写成“美术完成”。

## 5. 当前门禁命令

在项目根目录执行：

```powershell
.\backend\.venv\python.exe materials\tools\check_materials.py
.\backend\.venv\python.exe materials\tools\check_runtime_asset_specs.py --require-complete
.\backend\.venv\python.exe materials\tools\check_precapture_readiness.py
.\backend\.venv\python.exe scripts\check_playtest_round.py --json
```

预期的当前结果是：materials 失败并报告 7 个未登记中间文件，runtime specs 失败并报告 52 个 v004 合同缺口，Pre-Capture 为 `materials=pending, story=ready`，真人盲测为 `0/3`。这些失败是阻塞证据，不能通过改文案隐藏。

## 6. 下一位智能体接手顺序

1. 先读 `PROJECT_HANDOFF_20260807.md`、本文件、`CURRENT_STATUS.md`、`NEXT_PHASE.md`、`MATERIALS_REWORK_HANDOFF_20260807.md` 和 `MATERIALS_AUDIT_20260807.md`。
2. 检查 git status；保留所有现有未提交修改，不 reset、checkout、删除、覆盖、自动 commit/tag/push。
3. 对本快照表中的 8 个返工 request 做版本化收件和审查；先处理 P1 blocker。
4. 只把通过完整链路的最小地图/角色/音频垂直切片接入 runtime，并留下桌面和 390x844 证据。
5. 再处理 VFX、SFX、抓捕关键图和整合骑士到场素材；deferred 不得擅自激活。
6. 素材门通过后，组织 3 名陌生玩家从新游戏完成 N01-N10，并验证 `alice_captured` 后日期、剧情和 authored 状态不可继续推进。
7. 每一轮更新 `CURRENT_STATUS.md`、`NEXT_PHASE.md`、本文件或 `MATERIALS_AUDIT_20260807.md`，并记录实际测试输出。

## 7. 本次收束验证

2026-08-07 交接收束完成后重新执行：

- Backend：`330 passed`，保留 1 个既有 Starlette/httpx 弃用警告。
- Frontend unit：`16 passed`。
- Production build：通过；保留 Phaser chunk 约 `1.48 MB` 的既有体积警告。
- `git diff --check`：通过；只有既有 LF/CRLF 提示。
- Pre-Capture targeted E2E：隔离端口 `8034/4194`，`2 passed`；覆盖桌面新游戏 N01-N10 连续路径和 390x844 触控首个 authored 互动。
- Full Playwright：本轮隔离端口 `8033/4193` 在旧 `field-smoke` 的 Day 54-61 兼容场景超时。证据显示页面进入“地图加载失败 / 未知地点 / 无 nearby-enter”状态，重试随后出现前端连接拒绝；没有形成新的全量通过结果。此前 fresh-port `22/22` 仍是最近一次成功基线，但不得写成本轮复验通过。
- 素材门：`7 errors` / active v004 contract `52 issues`；这是预期阻塞，不是通过。
- Pre-Capture readiness：`materials=pending, story=ready`。
- 真人盲测：`0/3`。

全量 E2E 兼容 smoke 需要下一轮单独修复或稳定其 web-server 生命周期；它不改变本轮 Pre-Capture targeted E2E 已通过的事实，也不能被 targeted 结果替代为“全量 E2E 通过”。

## 8. 交接时必须如实报告

- 已完成：故事、后端权威闸门、自动化测试基线、素材请求/审查机制。
- 未完成：正式地图、完整 Sprite 动画、正式音频返工、VFX/SFX/抓捕表现、游戏内素材验收、3 名陌生玩家盲测。
- 新素材问题：本快照第 2 节的 v004/v005 具体问题。
- 需要其他智能体生成：只发 `MATERIALS_REWORK_HANDOFF_20260807.md` 第 7 节提示词，并要求遵循本快照的版本与状态边界。
- 测试结果：以本快照第 5 节和 `CURRENT_STATUS.md` 顶部 checkpoint 为准。
- 下一步实际行动：对最新收件包重跑门禁，失败就按 request_id 建立返工记录；不要直接接入。
