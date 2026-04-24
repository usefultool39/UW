# 30小镇

单人 AI RPG 原型。当前目标不是 MMO，也不是完整开放世界，而是先把“新手村第一章”做成稳定、可试玩、可扩展的纵切片。

玩家在一个小型封闭村庄里行动、对话、训练、阅读、休息和做选择。世界事实由后端规则决定；AI 负责 NPC 的表达、情绪、记忆摘要和非关键反应；章节事件由配置和剧情导演控制。

## 当前版本

- **v1.0 新手村试玩切片**：地图主界面、玩家格子移动、Alice / Eugeo 地图实体、章节事件、NPC 对话、关系档案、第一章三日流程和三个结局。
- **v1.1 体验与存档打磨**：章节选择结果面板、关系/记忆反馈、导出/导入存档、Windows pytest 临时目录权限规避。

正式公开前需要继续原创化角色名、地名和规则名。当前 Alice / Eugeo / Kirito 等名称只作为内部原型占位。

## 必读文档

下一个开发者或智能体优先读这几份即可：

1. [docs/README.md](docs/README.md)：文档入口和阅读顺序。
2. [docs/PROJECT.md](docs/PROJECT.md)：当前架构、数据入口、扩展规则、版本状态。
3. [docs/PLAYTEST.md](docs/PLAYTEST.md)：第一章三日 Demo 试玩和验收流程。
4. [docs/SCENE_SYSTEM.md](docs/SCENE_SYSTEM.md)：场景切换、多地图和未来副本/战斗实例扩展。

局部说明仍保留在：

- [backend/README.md](backend/README.md)：后端 API 与测试入口。
- [frontend/README.md](frontend/README.md)：前端运行、构建与 E2E。
- [characters/README_PERSONA.md](characters/README_PERSONA.md)：persona 与阶段 overlay。
- [frontend/public/assets/game/README.md](frontend/public/assets/game/README.md)：地图素材替换。

## 快速启动

方式 A：Windows 一键启动：

```bat
cd /d C:\Users\liang\Downloads\30小镇\30小镇
start.bat
```

方式 B：两个终端：

```bat
:: 终端 1：后端
cd /d C:\Users\liang\Downloads\30小镇\30小镇\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765

:: 终端 2：前端
cd /d C:\Users\liang\Downloads\30小镇\30小镇\frontend
npm install
npm run dev
```

访问：

- 前端：http://127.0.0.1:3000
- 后端健康检查：http://127.0.0.1:8765/api/health

## 常用验证

```bat
cd /d C:\Users\liang\Downloads\30小镇\30小镇\backend
python -m pytest -q

cd /d C:\Users\liang\Downloads\30小镇\30小镇\frontend
npm.cmd run build
npm.cmd run test:e2e
```

在 Codex 沙箱里，Vite/esbuild/Playwright 可能因为子进程启动被拦而报 `spawn EPERM`。这不是项目代码错误；在正常 Windows 环境或获准提权后可运行。

## 目录结构

```text
30小镇/
  backend/              FastAPI 后端、世界规则、剧情导演、记忆、测试
  frontend/             Vue 3 + Phaser 地图主界面
  characters/           NPC persona、背景、阶段 overlay、角色元数据
  data/
    story/              第一章事件与主线节点
    world/              地图、区域、NPC 日程
      maps/             未来多地图文件
    memory/             本地运行记忆，不是剧情配置源
  docs/                 当前权威文档
  runs/                 本地 JSONL 运行日志，可清理
```

不要把 `runs/`、`data/memory/`、`frontend/dist/` 当成剧情配置源；它们是运行产物或本地状态。
