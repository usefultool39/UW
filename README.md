# 边境回声 · Alicization Pre-Capture 篇

一款面向大众、以 **生活互动、关系后果与逐渐失衡的正典叙事** 为核心的 2D 单人 RPG。项目以《刀剑神域 Alicization》Underworld 前期事件为正典参考，采用数据驱动的 Vue 3 + Phaser 3 + FastAPI 架构。

当前产品与长期开发唯一基线见 [产品方向与长期开发基线](docs/product/PRODUCT_DIRECTION.md)。原有“原创见习记录员分支”描述属于历史定位；当前正式主线围绕桐人、尤吉欧和爱丽丝展开。

当前优先目标是完成 `0.5.0-pre-capture`：用四幕、8–12 个关键节点把卢利特村日常、尽头山脉越界、返村告别和爱丽丝被带走连续做成可玩的正典纵切片。旧 Day 1–117 内容只保留为系统验证和兼容记录，不继续扩写 Day 118+。默认 NPC 完全离线运行；未来模型 API 只提供候选表达，不改写世界规则和存档核心。

## 项目导航

| 你要知道 | 权威文档 |
|---|---|
| 下一位负责人如何完整接手 | [项目交接总览](docs/delivery/PROJECT_HANDOFF_20260807.md) |
| 已经做了什么、测试基线、已知风险 | [当前状态](docs/planning/CURRENT_STATUS.md) |
| 最终要做成什么 | [产品方向](docs/product/PRODUCT_DIRECTION.md) / [产品简述](docs/product/PRODUCT_BRIEF.md) |
| 下一阶段只做什么 | [下一阶段](docs/planning/NEXT_PHASE.md) |
| 当前候选版说明 | [0.4.0-preview.1](docs/delivery/RELEASE_0.4.0-preview.1.md) |
| 需要我准备什么素材 | [素材总目录](materials/00_INDEX.md) / [详细需求](materials/01_REQUEST_CATALOG.md) |
| 如何规范开发 | [开发流程](docs/delivery/DEVELOPMENT_PROCESS.md) / [贡献指南](CONTRIBUTING.md) |
| 全部文档 | [文档中心](docs/README.md) |

## 当前能力

- Vue 3 + Phaser 地图主客户端，FastAPI 权威世界状态。
- 地图移动、地点调查、对话、故事事件与旧三日/月度兼容骨架；正式 Pre-Capture 四幕 N01-N10 已接入并达到 `story=ready`，素材和真人盲测仍未完成。
- 阅读、训练、用餐、边境探查/巡查等短玩法。
- 时间、HP、MP、体力、flag、关系、记忆、承诺和紧张关系后果。
- `scripted` / `hybrid` / `agent` NPC 模式与失败回退。
- 存档导入导出、内容校验、pytest、Playwright E2E。
- Windows/macOS 一键启动；`试玩盲测.command` 固定 scripted + production build 并重置试玩存档。

## Windows 快速启动

双击 **`启动全部项目.bat`**，或在 PowerShell 中运行：

```powershell
.\启动全部项目.bat
# 等价入口
.\start.bat
```

游戏：http://127.0.0.1:3000；健康检查：http://127.0.0.1:8765/api/health。

## macOS 快速启动

Finder 双击根目录 **`启动游戏.command`**，或：

```bash
./启动游戏.command
```

首次运行会创建 `backend/.venv` 并安装依赖。游戏：http://127.0.0.1:3000；健康检查：http://127.0.0.1:8765/api/health。

完整运行说明见 [本地运行手册](docs/operations/RUNBOOK.md)。

## 验证

```bash
./scripts/quality.sh
cd frontend && npm run test:e2e
```

Windows 下 Playwright、质量门和试玩预检会自动发现 `backend/.venv/python.exe`；如需指定解释器，可设置 `PYTHON_BIN`。

## 重要边界

- 后端决定位置、时间、资源、剧情闸、关系和永久记忆。
- 大模型只提供候选表达/意图，不能绕过规则。
- `runs/`、`data/memory/`、`frontend/dist/` 是运行产物，不是内容源。
- 公开发布前需要重新评估同人名称、素材和版权边界。
