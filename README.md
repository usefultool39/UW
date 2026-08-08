# UW · 卢利特村序章

**当前统一版本：0.5.0**

UW 是一个以桐人为玩家角色、围绕桐人、尤吉欧与爱丽丝童年经历展开的单人 2D 叙事 RPG 原型。当前只完成并打磨“爱丽丝被带走之前”的纵向切片，不继续扩写旧的见习记录员、月度路线或超长 Day 计划。

## 当前状态

- **可以开发和试玩**：FastAPI 后端、Vue + Phaser 客户端、离线 scripted NPC、存档、十个主线节点和自动化测试已经建立；0.6.0 P0/P1 已加入关系雷达、每日采药/石碑收集、公告柱任务、8 格物品栏、物品使用、钓鱼接线、家中烹饪、书库三步推理、北门巡查装备和记忆图鉴。
- **尚未达到公开发布标准**：`materials/inbox/**/current/` 中的地图、角色、抓捕终点、VFX 和 SFX 都只是 `sample_candidate`；正式地图、统一角色动画、抓捕终点上色、音频试听、三名陌生玩家盲测和 IP 权利评估尚未完成。
- **唯一事实源**：产品与设计看 `docs/PROJECT.md`；状态和计划看 `docs/PLAN.md`；素材看 `docs/art/ASSET_REVIEW.md`。

## 启动

macOS：

```bash
./启动游戏.command
```

Windows：

```powershell
.\启动全部项目.bat
```

开发质量检查：

```bash
./scripts/quality.sh
```

准备发布时才运行：

```bash
./scripts/release.sh
```

## 文档入口

1. [项目总纲](docs/PROJECT.md)：背景、范围、剧情、系统、UI、美术和技术边界。
2. [统一计划](docs/PLAN.md)：真实完成度、当前工作、优先级、验收和冻结项。
3. [素材审查](docs/art/ASSET_REVIEW.md)：可用素材、返工项和下一批素材规格。
4. [交付规则](docs/DELIVERY.md)：开发、测试、盲测、发布和版本规则。
5. [生图智能体 Prompt](docs/art/GENERATION_AGENT_PROMPT.md)：新的生图智能体必须遵守的完整生成、验收和交付规范。
6. [当前素材任务单](docs/art/ASSET_TASKS.md)：按 T01-T04 顺序执行的下一批任务。
7. [架构总览](docs/architecture/SYSTEM_OVERVIEW.md)：系统所有权和模块关系。
8. [运行手册](docs/operations/RUNBOOK.md)：环境、启动和常见验证命令。

旧方案、旧版本说明和过期阶段文档已从工作树删除；需要追溯时使用 Git 历史，不再让历史文件与当前方案并列。
