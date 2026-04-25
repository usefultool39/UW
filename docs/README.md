# 文档入口

本目录只保留当前权威文档。历史探索、重复路线图和中间版本已删除，避免后续开发者在过时方向里绕路。

## 阅读顺序

1. [PROJECT.md](PROJECT.md)  
   当前产品方向、架构边界、文件入口、API、数据流、扩展规则和近期路线。

2. [PLAYTEST.md](PLAYTEST.md)  
   第一章三日 Demo 的试玩步骤和验收点。

3. [SCENE_SYSTEM.md](SCENE_SYSTEM.md)
   场景切换、多地图、未来副本/战斗实例的扩展方式。

4. 根目录 [README.md](../README.md)
   快速启动、目录结构和常用验证命令。

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
