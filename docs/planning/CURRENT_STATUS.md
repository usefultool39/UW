# 当前状态

- **状态**：Current / 权威事实页
- **快照日期**：2026-08-03
- **Git 基线**：`main` / `fc09f48`，完整历史 54 个提交；成熟化与治理改动尚未提交
- **版本标识**：`0.4.0-dev`

## 已经完成

### 产品与玩法
- Underworld 分支定位、原创见习记录员身份和卢利特村开场。
- 地图移动、POI 交互、故事事件、昼夜、休息和 Day 1–3 主线。
- 阅读、训练、用餐、边境探查/裁决、三回合北境巡查。
- 敌方意图与克制、HP/MP/体力消耗、边境标记、休息恢复。
- 主目标、今日节奏、收益预览、锁定提示、结果、日志和档案。
- 存档导入导出与新游戏重置。

### NPC 与叙事
- 爱丽丝、尤吉欧、赛鲁卡等资料与数据驱动固定对话。
- 关系、重要记忆、承诺、紧张关系和后续回响。
- 记忆按 `run_id` 隔离。
- scripted 默认；hybrid/agent 配置和回退骨架。
- 后端保有世界事实、资源、剧情闸和奖励最终决定权。

### 工程
- FastAPI + Vue 3/Phaser 主客户端，Cocos 备用骨架。
- 数据驱动地图、活动、剧情、日程、角色配置。
- macOS 一键启动，Windows 与手动入口保留。
- 内容校验、健康检查、JSONL、pytest 和 Playwright。
- 本轮建立产品/需求/MVP/架构/ADR/计划/交付/运维体系和 CI。

## 本轮验证基线（2026-08-03）

- 后端：199 passed；1 个 Starlette/httpx 第三方弃用警告。
- 前端单元测试：3 passed。
- 前端 production build：通过。
- Playwright E2E：10 passed。
- `git diff --check`：通过。
- 已知非阻塞项：Phaser minified chunk 约 1.48 MB。

## 已知风险

| 等级 | 项目 | 方向 |
|---|---|---|
| High | `FieldSlice.vue`、Phaser scene 过大 | 先抽注册表/composable，再拆场景 |
| High | `Session.player_action()` 分支长 | 提取纯 activity engine，Session 做事务编排 |
| Medium | 长线内容多于首三日体验验证 | 先稳定 Day 1–3 |
| Medium | Phaser chunk 约 1.48 MB | 记录预算，后续基于性能数据做懒加载 |
| Medium | 缺少真实首次玩家数据 | 记录完成率、卡点、时长和后果发现率 |
| Medium | 尚无正式 tag/release | 首个候选版开始 SemVer + Changelog + tag |
| Low | Cocos/Web 双路线 | 冻结 Cocos，保持契约即可 |

`docs/archive/` 是历史，不是当前计划。当前任务只看 `NEXT_PHASE.md`。
