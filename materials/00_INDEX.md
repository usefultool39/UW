# 《边境回声》素材工作区总目录

- **本机实际交付路径**：`C:\Users\liang\Desktop\UW\materials`
- **当前目标版本**：`0.5.0-pre-capture`
- **状态**：Current / 素材需求与来源的单一入口
- **当前返工交接**：[MATERIALS_REWORK_HANDOFF_20260807.md](../docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md)
- **原则**：原始素材只进入 `inbox`；项目负责人完成 request、sidecar、来源/权利、技术、风格、游戏内和 manifest/hash 验收后，才可复制/转换到 `frontend/public/assets/runtime`。素材智能体不得直接修改正式 runtime。

## 当前长期方向

第一长期阶段只做到“爱丽丝被带走”：从卢利特村可信日常、巨神树天职、禁忌目录和尽头山脉铺垫，连续推进到爱丽丝越界并被整合骑士带走。事实终点固定，玩家可以改变线索掌握、关系、承诺、准备方式和最后表达。

当前停止继续无上限扩写 Day 118+。先用现有系统和场景做紧凑、完整、可回放的 Pre-Capture 四幕主线；用户返还的新素材一律先登记请求 ID、来源和版本，再进入评审与运行时。

## 2026-08-06 产品方向收束（历史输入阶段）

- 产品、交互、美术、战斗资产和技术边界的唯一基线：`docs/product/PRODUCT_DIRECTION.md`。
- 另一个智能体只处理视觉/音频素材请求（`VIS-*` / `AUD-*`）；剧情、正典、世界观、人物和游戏接入由开发侧负责。
- 当时 `NAR-CANON-001`、`NAR-PRECAP-001`、`WORLD-*`、`CHAR-DEPTH-001`、`NAR-ADAPT-001`、`QA-CANON-001` 的 v001/v002 均按待审核候选处理，不允许直接进入 `approved`、runtime 或 `data/story`。
- 当前七项叙事输入已通过 readiness 并由 authored 主线吸收；原始 v001/v002 继续保留作为来源审计，不能因 `story=ready` 反向宣称原始材料本身已进入 runtime。

## 你现在最需要做什么

当前不是首轮样张阶段。方向板、关键图、肖像样张、核心图标、村庄 BGM 和细雨 ambience 已有候选或原型接入；正式 Pre-Capture 素材仍未完成。

本轮只做 [素材返工交接](../docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md) 中的五个 v004 包。v003 已收到但全部返工，不能进入 runtime：

1. `VIS-MAP-001`：真实可玩地图层、tile/prop、碰撞、可走区、遮挡和交互数据。
2. `VIS-CHR-001` 至 `003`：桐人、爱丽丝、尤吉欧真实透明四向 Sprite 动画包。
3. `VIS-ENV-001`：六张 1920x1080 活动/转场背景，不冒充地图。
4. `AUD-BGM-002`、`003`：满足时长、响度、峰值和 loop metadata 的两组 v004 BGM。
5. `AUD-AMB-002`：等长 normal/silent 森林 ambience v004 对。

失败的 v002/v003 保留在 inbox。返工统一用 v004，不启动 deferred 项，不把登记或生成写成验收完成。

## 文件地图

| 文件 | 用途 |
|---|---|
| `01_REQUEST_CATALOG.md` | 全量素材需求台账；含优先级、数量、构图、路径和验收标准 |
| `02_VISUAL_STYLE_BIBLE.md` | 原创视觉语言、色彩、角色、地图、UI、禁区 |
| `03_TECHNICAL_SPECS.md` | 图片/音频/文本规格、命名、sidecar、运行时预算 |
| `04_AI_PROMPT_KITS.md` | 可直接复制到生成工具的详细提示词与负面提示词 |
| `05_WORKFLOW_AND_REVIEW.md` | 收件、评审、返工、批准、接入、回滚、维护流程 |
| `06_RIGHTS_AND_PROVENANCE.md` | 来源、授权、AI 生成记录、禁止项和归属要求 |
| `07_CURRENT_ASSET_AUDIT.md` | 现有素材、占位项、真实缺口与推荐替换顺序 |
| `08_NARRATIVE_REQUIREMENTS.md` | 爱丽丝被带走前的正典兼容叙事需求与交付定义 |
| `09_PRECAPTURE_STORY_TARGET.md` | 长期故事结构、人物深度和世界观目标 |
| `10_CANON_CONTINUITY_CHECKLIST.md` | 每次新增内容的正典连续性与可玩性检查 |
| `11_PRECAPTURE_EXECUTION_BRIEF.md` | 当前差距、紧凑四幕实施顺序、素材返还入口和完成定义 |
| `../docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md` | 当前五个 v004 返工包、职责、状态机制、验收链和唯一整包提示词 |
| `REQUESTS.csv` | 机器可读请求状态；更新 `status` 即可跟踪 |
| `MANIFEST_TEMPLATE.csv` | 每个实际文件的来源、许可证、哈希与接入记录模板 |
| `inbox/README.md` | 你放文件时必须遵守的最简规则 |
| `review/` | 待评审候选；由开发侧移动，不要自行视为批准 |
| `approved/` | 已批准源素材；不等同于运行时压缩文件 |
| `archive/` | 被替换但需要保留来源记录的旧版本 |

## 状态词

`REQUESTS.csv` 记录整项请求：

- `requested`：已提出，尚未收到。
- `received`：文件和最低元数据已收到，不代表合格。
- `reviewing`：正在做技术、风格、权利或游戏内测试。
- `changes_requested`：需要返工，原因必须写入评审记录。
- `approved`：该请求的指定源版本已批准。
- `integrated`：批准版本已进入 runtime 并完成游戏内验收。
- `deferred` / `rejected`：当前延期或明确拒绝。

`MANIFEST.csv` 记录每个具体文件版本：`received`、`review-only`、`approved-for-direction`、`approved-candidate`、`changes_requested`、`integrated`、`deferred`、`rejected`。`approved-for-direction` 只能约束风格；`approved-candidate` 也不能替代游戏内验收。

## 最重要的维护规则

1. 每个素材都必须带请求 ID，例如 `VIS-KA-001`。
2. 每个二进制文件旁边放一个同名 `.md` sidecar，记录来源/提示词/模型/许可证/修改。
3. 不要覆盖旧文件；按 `v001`、`v002`、`v003`、`v004` 递增版本。
4. 不要把官方截图、影视截图、游戏拆包素材、来源不清素材放入 `approved`。
5. 所有图像尽量无文字；游戏中文案由前端渲染，避免分辨率和本地化问题。
6. `inbox` 是收件区，不是运行时目录；运行时接入由代码和 manifest 控制。
| `tools/check_precapture_readiness.py` | 只读检查 7 项叙事输入、16 项第一阶段 runtime 素材、四幕 authored 标记、8–12 个节点、固定抓捕终点和跨节点回响 |
| `tools/check_runtime_asset_specs.py` | 只读检查地图层/网格、Sprite alpha/帧 manifest、场景尺寸、音频 WAV/OGG/loop/响度/峰值 |
