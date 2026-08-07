# UW · 卢利特村序章

**当前统一版本：0.5.0**

UW 是一个以桐人为玩家角色、围绕桐人、尤吉欧与爱丽丝童年经历展开的单人 2D 叙事 RPG 原型。当前只完成并打磨“爱丽丝被带走之前”的纵向切片，不继续扩写旧的见习记录员、月度路线或超长 Day 计划。

## 当前状态

- **可以开发和试玩**：FastAPI 后端、Vue + Phaser 客户端、离线 scripted NPC、存档、十个主线节点和自动化测试已经建立。
- **尚未达到公开发布标准**：正式地图、统一角色动画、抓捕终点美术、完整音效元数据、三名陌生玩家盲测和 IP 权利评估尚未完成。
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
5. [架构总览](docs/architecture/SYSTEM_OVERVIEW.md)：系统所有权和模块关系。
6. [运行手册](docs/operations/RUNBOOK.md)：环境、启动和常见验证命令。

旧方案、旧版本说明和过期阶段文档已从工作树删除；需要追溯时使用 Git 历史，不再让历史文件与当前方案并列。
