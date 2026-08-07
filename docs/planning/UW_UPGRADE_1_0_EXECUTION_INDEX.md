# UW-UPGRADE-1.0 统一执行索引

- 状态：Current / 升级执行总入口
- 日期：2026-08-07
- 项目：`C:\Users\liang\Desktop\UW`
- 产品阶段：`0.5.0-pre-capture`（未发布）
- 资产生产批次：`UW-UPGRADE-1.0`
- 固定终点：`alice_captured`

本文件负责把界面、人物、剧情、操作、玩法优化、地图、贴图、VFX、音频和素材生产入口收束到一个可执行结构。它不复制各专业文档的全部正文；发生冲突时，按下列优先级裁决。

## 1. 权威顺序

1. 产品与正典边界：`docs/product/PRODUCT_DIRECTION.md`
2. 当前事实：`docs/planning/CURRENT_STATUS.md`
3. 当前任务队列：`docs/planning/NEXT_PHASE.md`
4. 本轮升级设计：`docs/planning/VISUAL_INTERACTION_UPGRADE_PLAN_20260807.md`
5. 素材现状与位置：`materials/UW_UPGRADE_1_0_ASSET_CATALOG.md`
6. 素材生产指令：`materials/UW_UPGRADE_1_0_ASSET_AGENT_PROMPT.md`
7. 机器可读规格：`materials/runtime_asset_requirements.json`
8. 请求与文件事实：`materials/REQUESTS.csv`、`materials/MANIFEST.csv`

`docs/archive/`、旧 v002-v008 方案和历史交接只用于追溯，不再直接产生新任务。

## 2. 一句话目标

把当前“故事合同已完成、画面仍像开发版”的 Vue 3 + Phaser 3 + FastAPI 游戏，升级为一条在桌面和移动端都清晰、好看、可操作、选择有反馈的 2D 叙事 RPG 垂直切片；玩家从卢利特村三人日常连续玩到爱丽丝被整合骑士带走，不能改变固定事实，但能改变关系、准备、记忆、承诺和最后表达。

## 3. 当前完成度

| 领域 | 当前状态 | 本轮目标 |
|---|---|---|
| 剧情 | `story=ready`；N01-N10、四幕、46 个跨节点回响、唯一终点已接入 | 不扩写抓捕后剧情，只改善表现与反馈 |
| 工程 | 后端权威、离线 scripted、存档、地图和活动骨架可用 | 保持边界，不大改核心架构 |
| 素材技术规格 | 最新地图 v005、角色 v008、环境 v005、音频 v004 自动规格为 `issues=0` | 仅作为候选输入，继续人工内容审查 |
| 素材台账 | `materials=pending`；核心返工请求未批准、未进入正式 MANIFEST | 清理门禁、审查、批准最小切片 |
| Runtime | 仍以旧肖像、关键图、少量图标和音频为主 | 接入统一 golden slice，再逐组扩展 |
| 真人验证 | `QA-PLAY-001 = 0/3` | 三名陌生玩家完成 N01-N10 |

## 4. 设计方案总图

### 4.1 界面

- 桌面采用“世界画面 + 轻量 HUD + 按需展开面板”，地图和角色始终是主画面。
- 一个屏幕只保留一个强主行动；目标、代价、收益和不可用原因使用稳定位置。
- 行动结果固定顺序：人物反应 -> 资源变化 -> 关系/记忆/承诺 -> 下一步。
- 关键状态不只依赖颜色；同时使用图标轮廓、短文本或纹理。
- 390x844 下关键触控目标不小于 44x44 CSS px，弹窗、底栏和地图目标不得重叠。
- 32 枚 UI 图标、面板 token、按钮状态和反馈触发统一由素材目录管理。

详细设计见升级方案第 5、9、13 节。

### 4.2 人物

- 核心三人：桐人（玩家）、尤吉欧、爱丽丝；不得把“见习记录员”误作第四名角色。
- 支持人物：赛尔卡、加利塔、加斯夫特；终点人物为整合骑士及随行者。
- 三名核心角色需要四方向 idle/walk/interact，统一脚底锚点、碰撞框和显示比例。
- 人物不能只靠换色区分；发型、服装外轮廓、姿态和随身物都要形成辨识度。
- 肖像表情至少覆盖 neutral、concerned、warm、focused、farewell。
- 视觉必须原创，不复制官方动画帧、现成游戏立绘、服装细节或标志性构图。

人物行为与声音以 `CHAR-DEPTH-001_character_depth_v002.md` 和 `NAR-VOICE-001_core_voice_bible_v001.md` 为准。

### 4.3 剧情

唯一顺序：

```text
N01 卢利特村三人日常
-> N02 尤吉欧的巨神树天职
-> N03 谈及禁忌目录与尽头山脉
-> N04 前往尽头山脉洞窟
-> N05 接触暗黑界一侧的受伤者
-> N06 爱丽丝为救人触碰/越过边界
-> N07 三人返回卢利特村
-> N08 整合骑士在村中宣告罪名
-> N09 爱丽丝与家人、桐人、尤吉欧告别
-> N10 爱丽丝被带走（alice_captured）
```

- N06 不能被玩家阻止；选择只改变在场方式和关系反馈。
- 抓捕发生在返回卢利特村之后，不在山侧立即发生。
- N10 后不得继续 authored 剧情、日期、NPC 或世界事实写入。
- 素材可以强化情绪与可读性，不得改变节点事实。

### 4.4 操作与短玩法

- 移动：键鼠点击/WASD 与触控点击均可完成；有到达、阻挡和靠近反馈。
- 统一活动流程：`preview -> observe -> choose -> commit -> result`。
- 线索拼接：观察 3 个图形/文字碎片，选择 2 个关系并提交。
- 路线观察：沿安全路线到达两个异常点，决定公开记录或私下保留。
- 关系交付：选择午餐、记录或训练的交付方式，立即显示人物反应。
- 每个短玩法 30-90 秒、总操作不超过 8 次；失败不部分写状态。
- 所有不可用状态必须告诉玩家原因和恢复动作。

### 4.5 视觉、地图与贴图

- 统一方向：原创 `Rulid Storybook` 3/4 俯视手绘卡通。
- 地图是可玩的分层数据，不是一张插画；道路、入口、碰撞、遮挡和交互点必须一致。
- 目标尺寸 3024x1792，108x64 tiles，28px/tile；九个视觉层加 collision/walkable/interaction。
- 场景背景统一 1920x1080，并提供桌面与窄屏焦点安全区。
- 程序化网格、色块和 token 只保留为加载失败 fallback。
- 建筑、树木、道路、道具使用 atlas 和稳定 ID；不把道路/建筑烘焙回 terrain 层冒充分层。

### 4.6 VFX 与音频

- VFX：clue-pulse、sacred-ink、boundary-ripple、relationship-warmth、reward-spark、capture-silence。
- 音乐：村庄清晨、关系日常、边界调查、抓捕静默；切换使用 1.5-2.5 秒淡化/ducking。
- 环境声：村庄细雨与森林 normal/silent 对照；silent 不是数字静音。
- SFX：UI、线索、关系、记忆、资源、脚步、翻页、递物、神圣术、边界和日结算。
- 所有声音必须有响度/峰值/loop 数据、可关闭设置和无声视觉 fallback。

### 4.7 优化

- 先接一处 golden slice，不批量替换全项目。
- 优先修复目标迷失、遮挡、按钮过小、反馈不明显和低资源恢复不清。
- 素材按组懒加载；在真实设备数据前不引入新框架。
- Phaser chunk 体积作为监控项；不为了拆包改写核心玩法。
- 所有素材保留源文件、runtime 导出、hash 和回滚证据。

## 5. 唯一实施顺序

1. 整理：归档历史中间文件，材料登记门回到 0 errors。
2. 冻结：确定色板、线稿、角色比例、地图 z-order、UI token 和声音层级。
3. Golden slice：地图最小可走区 + 三核心角色 + 书库背景 + clue-pulse + BGM-003 A。
4. 游戏内验收：1440x900、390x844、键鼠、触控、碰撞、遮挡、音频和 fallback。
5. 扩展：其余五张场景、边界 VFX/BGM/ambience、32 图标和 SFX。
6. 终点：抓捕关键图、整合骑士表现、告别动作和 capture-silence。
7. 全门禁：材料、runtime、readiness、pytest、unit、build、Playwright、diff check。
8. 真人盲测：三名陌生玩家完成 N01-N10，只修最高频阻塞。

## 6. 完成定义

只有以下条件同时满足，才可写“UW-UPGRADE-1.0 完成”：

- `materials=ready, story=ready`；
- 新游戏可连续完成 N01-N10 到 `alice_captured`；
- 抓捕后 authored 进度不可继续；
- 地图、角色、背景、UI、VFX、音乐、环境声、SFX 和终点表现通过桌面/触控游戏内验收；
- 正式 MANIFEST、hash、权利、审核人与 runtime 路径完整；
- 后端、前端、build、E2E 和素材门全部通过；
- 三名陌生玩家记录完整。

## 7. 交付入口

- 所有素材状态与位置：`materials/UW_UPGRADE_1_0_ASSET_CATALOG.md`
- 给素材智能体的完整执行指令：`materials/UW_UPGRADE_1_0_ASSET_AGENT_PROMPT.md`
- 现有升级细节与验收：`docs/planning/VISUAL_INTERACTION_UPGRADE_PLAN_20260807.md`

