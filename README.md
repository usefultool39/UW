# UW · 卢利特村序章

一个以桐人、尤吉欧和爱丽丝为核心的 2D 叙事 RPG 原型。当前只收束 **爱丽丝被带走之前** 的连续体验：村庄日常、巨神树天职、尽头山脉越界、返村告别与抓捕终点。

## 当前结论

- **可运行**：FastAPI 后端、Vue + Phaser 客户端、离线 scripted NPC、存档和十个主线节点已具备。
- **未发布**：地图、角色动画、抓捕关键图、音效包和真人盲测尚未达到发布门槛。
- **唯一方向**：不再扩写旧的“见习记录员”长线，也不再新增按日期编号的计划文档。
- **版权边界**：这是含既有作品名称与设定的内部原型；公开发行前必须完成授权评估，或改写为原创世界与角色。

## 开始

macOS：

```bash
./启动游戏.command
```

Windows：

```powershell
.\启动全部项目.bat
```

质量检查：

```bash
./scripts/quality.sh
```

发布门禁（包含素材、真人盲测和 E2E）：

```bash
./scripts/release.sh
```

## 文档入口

- [项目总览：目标、范围、架构、设计与计划](docs/PROJECT.md)
- [当前状态](docs/planning/CURRENT_STATUS.md)
- [下一阶段](docs/planning/NEXT_PHASE.md)
- [素材审查与缺口清单](docs/art/ASSET_REVIEW.md)
- [素材收件说明](materials/README.md)
- [系统架构](docs/architecture/SYSTEM_OVERVIEW.md)

历史方案、旧交接和带日期的阶段记录已经移到 `docs/archive/` 与 `materials/archive/`，只用于追溯，不再作为任务入口。
