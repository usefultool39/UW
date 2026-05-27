# 文档入口

本目录只保留当前权威文档。历史探索、重复路线图和中间版本已删除，避免后续开发者在过时方向里绕路。

## 必读顺序

1. [PROJECT.md](PROJECT.md)  
   当前产品方向、架构边界、文件入口、API、数据流、扩展规则和近期路线。

2. [FUTURE_DETAILED_PLAN.md](FUTURE_DETAILED_PLAN.md)  
   从稳定纵切片、第一月内容、NPC 智能体、村庄社会、美术音频到发布维护的完整未来计划。

3. [EXECUTION_BOARD.md](EXECUTION_BOARD.md)  
   可直接开工的任务看板：质量门、Day 1-3 回归、第一月 Day 4-10、重要 NPC、Agent Loop、调试器、美术音频。

4. [PLAYTEST.md](PLAYTEST.md)  
   第一章三日 Demo 的试玩步骤和验收点。

5. [GAME_QUALITY_ROADMAP.md](GAME_QUALITY_ROADMAP.md)  
   游戏观感、移动手感、可玩性、AI NPC 和内容制作的长期任务板。后续每完成一项就在里面打勾，并追加执行记录。

6. 根目录 [README.md](../README.md)  
   快速启动、目录结构和常用验证命令。

## 专题文档

- [CLIENT_CONTRACT.md](CLIENT_CONTRACT.md)：Vue/Phaser 与 Cocos Creator 并行客户端必须共享的 API、DTO、玩家行动和地图表现契约。
- [DAY1_VERTICAL_SLICE.md](DAY1_VERTICAL_SLICE.md)：Day 1 不超过 20 个关键节点的完整体验脚本。
- [SCENE_SYSTEM.md](SCENE_SYSTEM.md)：场景切换、多地图、未来副本/战斗实例的扩展方式。
- [ART_DIRECTION_PLAN.md](ART_DIRECTION_PLAN.md)：美术方向、地图层级、资产清单和细粒度比例规范。
- [AFTERNOON_MAP_POLISH_PLAN.md](AFTERNOON_MAP_POLISH_PLAN.md)：地图和操作润色计划。
- [NEXT_HANDOFF_PLAN.md](NEXT_HANDOFF_PLAN.md)：上一阶段 Day 1 自然玩法循环交接记录，当前很多任务已完成，可作为历史上下文。
- [CLIENT_STRATEGY_DECISION.md](CLIENT_STRATEGY_DECISION.md)：客户端路线决策，当前主线仍是 Vue + Phaser，Cocos 冻结备用。
- [COCOS_SETUP.md](COCOS_SETUP.md)：Cocos 本机环境与验证记录。

## 外部计划目录

用户侧计划目录：

```text
C:\Users\liang\Desktop\计划to do list\边境回声项目未来详细计划
```

其中 `未来优化计划.md` 是给人看的总计划，`下一步执行清单.md` 是短期执行入口，`文档索引.md` 记录实际项目路径和阅读顺序。

## 局部文档

- [backend/README.md](../backend/README.md)：后端开发、API、测试。
- [frontend/README.md](../frontend/README.md)：前端开发、构建、E2E。
- [characters/README_PERSONA.md](../characters/README_PERSONA.md)：角色 persona 与阶段 overlay。
- [frontend/public/assets/game/README.md](../frontend/public/assets/game/README.md)：地图素材替换。

## 当前判断

项目主线是：

> 单人玩家 + AI NPC + 稳定世界规则 + 章节剧情 + 记忆关系 + 新手村纵切片。

不是：

- 多人在线 MMO。
- 大规模开放世界。
- 纯 AI 聊天室。
- 只看 tick 日志的模拟器。
- 直接发布官方 IP 同人复刻。

如果旧对话、旧代码注释或残留资源与这里冲突，以 [PROJECT.md](PROJECT.md) 为准。
