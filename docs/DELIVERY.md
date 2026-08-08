# UW 交付规则

本文件统一开发流程、完成定义、测试策略、盲测、发布和版本规则。

## 1. Git 工作方式

1. 从稳定分支创建一个目标明确的短分支。
2. 一个分支只解决一个可描述的问题。
3. 开工前写清问题、范围、验收和风险；重大架构变化先写 ADR。
4. 优先小步、可回滚提交，不用大规模重写掩盖范围变化。
5. PR 必须说明玩家可见变化、素材变化、测试、风险和回滚方式。
6. 不覆盖他人未提交修改，不提交密钥、运行产物、虚拟环境或构建目录。

提交信息使用：

```text
feat: ...
fix: ...
docs: ...
test: ...
refactor: ...
chore: ...
```

## 2. 完成定义

一项工作只有在以下条件满足时才算完成：

- 行为与 `docs/PROJECT.md` 的当前范围一致。
- 验收标准可以被测试、截图、日志或人工记录验证。
- 后端权威状态与 scripted 离线基线没有被破坏。
- 新旧存档、失败路径和回退路径得到考虑。
- 玩家可见变化已更新 `CHANGELOG.md`。
- 当前状态和证据已更新 `docs/PLAN.md`。
- 素材变化已更新素材台账和 `docs/art/ASSET_REVIEW.md`。
- `git diff --check` 和适用测试通过。

“代码已写”“素材已生成”“本机看起来没问题”都不等于完成。

### 素材样张的额外交付规则

- 新图片或音频先登记为 `sample_candidate`；该状态只表示已收到候选，不代表批准、可发布或可接入 runtime。
- 样张必须同时提供 source 文件、SHA-256、生成/后处理说明、license/rights 声明、sidecar 或 delivery 说明、机器检查结果，以及 1440×900 和 390×844 预览（音频则提供测量和试听记录）。
- `MANIFEST.csv` 中的样张必须留空 `runtime_file`、`approved_at` 和 `integrated_at`，并把已知问题和下一步写入 `notes`。
- 只有人工内容/正典审查、透明度或音频试听、桌面/移动真实界面验证、权利确认全部通过，才可改为 `approved-candidate` 或 `integrated`。
- 任何水印、文字、棋盘格、透明边缘、锚点漂移、错误人物识别色或不符合正典的内容，都必须保持候选或改为 `changes_requested`；不能靠测试通过来绕过。

新的生图智能体必须先读 `docs/art/GENERATION_AGENT_PROMPT.md`，再按 `docs/art/ASSET_TASKS.md` 的 T01-T04 顺序执行。它不负责替工程接入、音频人耳 QA 或真人盲测签字。

### 稳定命名与晋级

- 产品版本只使用 `0.5.0`；素材文件名不附加 `v001`、`v008`、`final2` 等修订链。
- 已验收前的最新基线放在各分类的 `current/`，下一轮输出放在同级 `candidate/`，两边使用相同的稳定文件名。
- candidate 通过人工验收后，先把旧 current 移入 `materials/archive/superseded/`，再把 candidate 晋级为 current，并同步更新 `MANIFEST.csv`。
- `VIS-MAP-001` 等 request ID 是稳定机器键，不是版本号，保留用于请求、台账和 sidecar 关联。
- 历史生成脚本、原图、manifest fragments 和失败样张只留在 archive 或 Git，不放回 active inbox。

## 3. 开发质量门

日常开发运行：

```bash
./scripts/quality.sh
```

它检查：

1. 素材登记完整性。
2. Runtime 素材规格。
3. 后端测试。
4. 前端单元测试。
5. Production build。
6. Git diff 格式健康。

失败时优先修复根因，不通过删除测试、降低检查或把状态转移到前端绕过。

## 4. 发布门禁

只有准备发布候选时运行：

```bash
./scripts/release.sh
```

它在开发质量门之外检查：

- 序章故事与阻塞素材准备状态。
- 真人盲测记录。
- Playwright E2E。

发布候选还必须人工确认：

- 全新 run 可连续完成 N01–N10。
- N10 是当前终点，不能误入未规划章节。
- 桌面和移动端无阻塞性遮挡。
- 所有 runtime 素材来源、权利、hash 和回滚路径完整。
- IP 权利已处理，或已经完成原创化改写。

## 5. 真人盲测

至少三名未参与开发的玩家，使用全新浏览器上下文和全新 run。测试者不得阅读开发文档，也不接受口头操作教学。

必须记录：

- 是否知道自己是桐人。
- 是否理解第一个目标。
- 第一次有效互动耗时。
- 每次停顿、误触、重复点击和求助位置。
- 是否抵达 N10。
- 是否能描述一次选择对后续反馈的影响。
- 是否愿意继续，以及原因。

问题按以下顺序处理：

1. 阻塞通关。
2. 多名玩家重复出现。
3. 目标、反馈或操作理解错误。
4. 单一审美偏好。

盲测完成后更新 `docs/PLAN.md`，不要另建一份带日期的报告；原始记录按工具要求保存在既有 playtest 数据位置。

## 发布门禁的 fail-closed 约束

`release.sh` 必须以 `--require-complete` 运行素材准备和真人盲测检查：只要正式素材仍为 pending，或 QA-PLAY-001 未达到 3/3 `received-human-run`，发布脚本必须非零退出，不能仅打印报告后继续显示 `Release gate passed.`。质量门和 Playwright 通过不能替代素材人工验收、音频试听、真人盲测或权利结论。

## 6. 版本规则

- 当前唯一版本为 `0.5.0`。
- `VERSION`、`frontend/package.json` 和 `backend/pyproject.toml` 必须一致。
- 文档不使用 `preview`、`dev`、阶段号或日期作为并行产品版本。
- 日常提交由 Git commit 追踪，不递增产品版本。
- 只有产品范围或兼容性发生明确变化时，才统一修改三个版本源。
- 只有发布门禁和权利检查通过后，才创建 `v0.5.0` annotated tag。

## 7. 文档维护矩阵

| 发生变化 | 更新位置 |
|---|---|
| 产品目标、剧情范围、系统/UI/美术原则 | `docs/PROJECT.md` |
| 完成度、优先级、执行顺序和验收证据 | `docs/PLAN.md` |
| 素材状态、返工意见和新规格 | `docs/art/ASSET_REVIEW.md` 与素材台账 |
| 开发、测试、盲测、发布或版本流程 | `docs/DELIVERY.md` |
| 架构所有权或不可逆技术决策 | `docs/architecture/adr/` |
| 用户可见变化 | `CHANGELOG.md` |

禁止通过新增 `STATUS_日期.md`、`NEXT_PHASE_2.md`、`FINAL_v3.md` 等文件表达进展。

## 8. 回滚

- 代码通过 Git revert 回滚，不手工覆盖历史文件。
- 素材通过 manifest 的 source/runtime/hash 和对应提交回滚。
- schema 变化提供默认值或迁移，不要求玩家手工修改存档。
- 外部 AI Provider 不可用时自动回退 scripted，不影响主线完成。
