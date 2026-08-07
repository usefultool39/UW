# 素材收件、评审、接入与维护流程

## 1. 为什么要有这套流程

当前游戏已经可运行；素材接入最大的风险不是“没有漂亮图”，而是：风格漂移、文件覆盖、授权不清、移动端不可用、压缩后变糊、生成提示词丢失、未来无法重做。因此所有素材从原始来源到游戏运行时都必须可追溯。

## 2. 生命周期与三层状态

素材状态不能只看一个词：

1. `REQUESTS.csv` 管整项需求是否已请求、收到、返工、批准或接入。
2. `MANIFEST.csv` 管每个具体文件版本的来源、权利、hash、审核人与接入记录。
3. `frontend/public/assets/runtime` 和游戏内证据证明某个已审核文件是否真实显示或播放。

```text
request: requested -> received -> reviewing -> approved -> integrated
                         |             |
                         +-> changes_requested -> received
                         +-> rejected / deferred

file:    received/review-only -> approved-candidate -> integrated
                              +-> changes_requested/rejected/deferred
```

`approved-for-direction` 只表示风格方向可参考。`approved-candidate` 表示具体源文件可进入受控候选接入，但不等于最终游戏内美术完成。

### Step A：提出需求

- 在 `REQUESTS.csv` 创建 request ID、优先级、交付目录和验收标准。
- 需求未写清前不批量生成。
- 同一问题尽量先做 2–3 个方向样张，不直接做全量。

### Step B：收件

素材智能体把文件放入 `materials/inbox/<category>/`，并附同名 `.md` sidecar，或同目录 request-scoped 主 sidecar。返工必须递增版本，禁止覆盖旧版。

收件最低检查：

- 文件名有 request ID 和版本号。
- 文件可以正常打开。
- sidecar 存在，来源/提示词/许可证不为空，并明确列出包内文件。
- manifest fragment 为每个文件提供 source path 和 SHA-256，runtime/审核字段留空。
- 不把多个完全不同方向混在一个无说明 ZIP 里。

通过后，由项目负责人将 `REQUESTS.csv.status` 改为 `received`；素材智能体不得直接修改正式台账。

### Step C：四项评审

1. **玩法评审**：是否让目标/数值/关系更清楚，而不是只装饰？
2. **风格评审**：是否符合 `02_VISUAL_STYLE_BIBLE.md`，是否与现有批准素材同世界？
3. **技术评审**：尺寸、透明、循环、响度、命名、预算、移动端是否合格？
4. **权利评审**：来源、许可、AI 平台条款、参考风险是否可追溯？

任何一项不通过，状态改 `changes_requested`，把问题写成可执行修改：例如“左侧安全区从 30% 增到 45%”，不要只写“感觉不对”。

### Step D：批准候选

- 批准的是**具体文件版本**，不是整个 request 永久批准。
- 在正式 `MANIFEST.csv` 记录来源、SHA-256、许可证、审核人、审核时间和用途。
- 源文件通过后可复制到 `materials/approved/<category>/`；原始 inbox 版本仍保留审计记录。
- `approved-candidate` 只允许进入受控候选接入；技术通过不等于风格完成或游戏内验收。
- 原始生成结果、分层源、无损音频保留，不要只留压缩 runtime 文件。

### Step E：运行时转换与接入

由开发侧执行：

1. 从 approved 源导出 runtime 版本。
2. 放入 `frontend/public/assets/runtime/`；禁止使用其他未登记 runtime 目录绕过门禁。
3. 通过 `gameContentConfig.js` / `sceneRegistry.js` / tileset manifest 等数据入口引用；不要在多个组件散落硬编码路径。
4. 补齐 `runtime_file`、`approved_by`、`approved_at`、`integrated_at` 和匹配 hash；更新 attribution、CHANGELOG（玩家可见时）、CURRENT_STATUS 和测试。
5. 跑 backend tests、frontend unit/build、定向 E2E、完整 E2E。
6. 比较桌面/移动截图、移动/碰撞/遮挡/动画/音频实际行为和性能体积。

`check_materials.py` 会拒绝未登记 runtime 文件、非允许状态的 runtime 路径、缺审核人与时间、hash 不匹配和 runtime 孤儿文件。正式状态升级必须由项目负责人完成。

### Step F：替换与回滚

- 新版本接入前不删除旧 approved 源。
- 运行时替换要能通过 git 回滚；用户存档不得依赖图片文件名之外的不可迁移状态。
- 被替换源移动到 `archive/`，保留 manifest 和批准记录。

## 3. 评审评分表

每项 0–2 分，满分 16；任何“权利”或“技术完整性”为 0 直接不批准。

| 维度 | 0 | 1 | 2 |
|---|---|---|---|
| 目标清晰 | 妨碍识别 | 中性 | 明显帮助玩家 |
| 原创与一致 | 有复制/漂移 | 部分一致 | 稳定原创语言 |
| 实际尺寸可读 | 不可读 | 勉强 | 清楚 |
| 桌面构图 | 遮 UI/目标 | 可裁 | 安全区合理 |
| 移动构图 | 不可用 | 机械裁切 | 独立适配 |
| 技术完整 | 缺源/规格 | 可补 | 完整 |
| 权利可追溯 | 不明 | 有待确认 | 明确可用 |
| 性能预算 | 超预算 | 可压缩 | 合理 |

建议：14–16 批准；10–13 返工；<10 拒绝或换方向。

## 4. AI 生成迭代规则

- 一轮只改变 1–3 个关键变量（构图、色温、服装语言），避免每版全部随机。
- 记录 seed 和设置；保留最初高分方向，即使后续返工失败也能回退。
- 角色批量生成前，先锁定统一光向、镜头、肩线、线条精度。
- 地图大图生成前，先用低分辨率构图草案确认道路和 UI 安全区。
- 不用“更像某作品”作为返工指令；改写成具体视觉属性。

## 5. 搜索素材流程

1. 优先公共领域、CC0、明确商用许可、本人拍摄/录制。
2. 保存原始页面 URL、作者、许可截图或许可文本副本。
3. 下载后不要改名到看不出来源；运行时别名写在 manifest。
4. 只作为参考的图明确标 `reference_only`，不得剪贴进成品。
5. 字体、音效库、音乐库必须确认“游戏分发/嵌入”是否允许，不只确认“可商用”。

## 6. 真实试玩素材流程

- 测试者使用新 run；每人独立。
- 不在过程中指导；如必须提示，记录精确时间和原话。
- 保存录屏、观察笔记、访谈答案；文件名不使用真实姓名。
- 从三人共同卡点中提问题，不因一人偏好立刻大改。
- 录屏只进 `materials/inbox/research/playtest/`，若包含隐私不提交公开仓库。

## 7. 每次接入的 Definition of Done

- [ ] request 状态和 manifest 已更新。
- [ ] sidecar、来源、许可证完整。
- [ ] 源文件与 runtime 文件分离。
- [ ] 桌面/移动实际画面审查通过。
- [ ] 体积和加载没有明显回归。
- [ ] 程序化/旧素材 fallback 仍可用（若要求）。
- [ ] 玩家可见变化已写 CHANGELOG。
- [ ] backend/unit/build/E2E 通过。
- [ ] 被替换素材可回滚，未破坏存档/API/NPC runtime。
