# 边境回声 · Underworld 分支篇

一款以 **NPC 记忆、关系后果与逐渐不安的乡村日常** 为核心的单人叙事 RPG 原型。项目参考《刀剑神域 Alicization》的 Underworld 氛围和公开设定，以原创“见习记录员”身份和分支时间线进行非商业二次创作。

当前优先目标是打磨一段成熟、容易上手、可反复验证的卢利特村 Day 1–3 纵切片，同时把 authored 月度内容延伸到 Day 103，验证路线、资源和关系后果能否持续驱动玩家。默认 NPC 完全离线运行；未来准备好模型 API 后，可按角色切换 Hybrid / Agent，而不改写世界规则和存档核心。

## 项目导航

| 你要知道 | 权威文档 |
|---|---|
| 已经做了什么、测试基线、已知风险 | [当前状态](docs/planning/CURRENT_STATUS.md) |
| 最终要做成什么 | [产品简述](docs/product/PRODUCT_BRIEF.md) / [路线图](docs/product/ROADMAP.md) |
| 下一阶段只做什么 | [下一阶段](docs/planning/NEXT_PHASE.md) |
| 当前候选版说明 | [0.4.0-preview.1](docs/delivery/RELEASE_0.4.0-preview.1.md) |
| 需要我准备什么素材 | [素材总目录](materials/00_INDEX.md) / [详细需求](materials/01_REQUEST_CATALOG.md) |
| 如何规范开发 | [开发流程](docs/delivery/DEVELOPMENT_PROCESS.md) / [贡献指南](CONTRIBUTING.md) |
| 全部文档 | [文档中心](docs/README.md) |

## 当前能力

- Vue 3 + Phaser 地图主客户端，FastAPI 权威世界状态。
- 地图移动、地点调查、对话、故事事件、三日主线与后续月份骨架。
- 阅读、训练、用餐、边境探查/巡查等短玩法。
- 时间、HP、MP、体力、flag、关系、记忆、承诺和紧张关系后果。
- `scripted` / `hybrid` / `agent` NPC 模式与失败回退。
- 存档导入导出、内容校验、pytest、Playwright E2E。
- macOS 一键启动；Windows 和手动启动入口保留；新增 `试玩盲测.command`，固定 scripted + production build 并重置试玩存档。

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
cd frontend && PYTHON_BIN=../backend/.venv/bin/python npm run test:e2e
```

## 重要边界

- 后端决定位置、时间、资源、剧情闸、关系和永久记忆。
- 大模型只提供候选表达/意图，不能绕过规则。
- `runs/`、`data/memory/`、`frontend/dist/` 是运行产物，不是内容源。
- 公开发布前需要重新评估同人名称、素材和版权边界。
