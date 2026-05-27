# 边境回声

单人 AI RPG 纵切 Demo。当前目标不是 MMO，也不是完整开放世界，而是先把“露茵村第一章”做成稳定、可试玩、可扩展的 20-30 分钟体验。

玩家以见习记录员身份在封闭村庄里行动、对话、训练、阅读、休息和做选择。世界事实由后端规则决定；AI 负责 NPC 的表达、情绪、记忆摘要和非关键反应；章节事件由配置和剧情导演控制。

内部 id 仍保留 `alice/eugeo/kirito` 以兼容代码和存档；玩家可见文本已迁移到原创称呼：艾琳、尤里、凛斗、露茵村、古誓树、北境律令、静默线。

## 当前版本

- **v1.0 纵切基础**：地图主界面、玩家移动、艾琳 / 尤里地图实体、章节事件、NPC 对话、关系档案、第一章三日流程和三个结局。
- **v1.1 体验与存档**：章节选择结果面板、关系/记忆反馈、导出/导入存档、日结算和 Day 2 预告。
- **v1.2 Day 1 自然玩法循环**：地点自然触发、线索日志、训练小游戏、读书关键词拼接、午餐/晚餐关系选择。

## 必读文档

1. [docs/README.md](docs/README.md)：文档入口和阅读顺序。
2. [docs/PROJECT.md](docs/PROJECT.md)：产品定位、原创化清单、架构、入口。
3. [docs/FUTURE_DETAILED_PLAN.md](docs/FUTURE_DETAILED_PLAN.md)：未来详细计划。
4. [docs/EXECUTION_BOARD.md](docs/EXECUTION_BOARD.md)：下一步执行看板。
5. [docs/CLIENT_CONTRACT.md](docs/CLIENT_CONTRACT.md)：Vue/Phaser 与 Cocos Creator 共用客户端契约。
6. [docs/DAY1_VERTICAL_SLICE.md](docs/DAY1_VERTICAL_SLICE.md)：Day 1 完整体验脚本。
7. [docs/PLAYTEST.md](docs/PLAYTEST.md)：第一章三日 Demo 试玩和验收流程。
8. [docs/GAME_QUALITY_ROADMAP.md](docs/GAME_QUALITY_ROADMAP.md)：长期任务板。

## 快速启动

方式 A：Windows 一键启动：

```bat
启动全部项目.bat
```

方式 B：两个终端：

```bat
:: 终端 1：后端
cd /d <项目根目录>\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765

:: 终端 2：前端
cd /d <项目根目录>\frontend
npm install
npm run dev
```

访问：

- 前端：http://127.0.0.1:3000
- 后端健康检查：http://127.0.0.1:8765/api/health

## 常用验证

```bat
cd /d <项目根目录>\backend
python -m pytest -q

cd /d <项目根目录>\frontend
npm.cmd run build
npm.cmd run test:e2e
```

## 目录结构

```text
边境回声/
  backend/              FastAPI 后端、世界规则、剧情导演、记忆、测试
  frontend/             Vue 3 + Phaser 地图主界面
  cocos-client/         Cocos Creator 并行客户端骨架，未来正式表现层
  characters/           NPC persona、背景、阶段 overlay、角色元数据
  data/
    story/              第一章事件与主线节点
    world/              地图、区域、NPC 日程、场景活动
      maps/             未来多地图文件
    memory/             本地运行记忆，不是剧情配置源
  docs/                 当前权威文档
  runs/                 本地 JSONL 运行日志和视觉截图，可清理
```

不要把 `runs/`、`data/memory/`、`frontend/dist/` 当成剧情配置源；它们是运行产物或本地状态。
