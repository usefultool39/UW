# UW 协作入口

进入仓库后只需先读四份文件：

1. `docs/PROJECT.md`
2. `docs/planning/CURRENT_STATUS.md`
3. `docs/planning/NEXT_PHASE.md`
4. `docs/art/ASSET_REVIEW.md`

## 当前目标

完成爱丽丝被带走前的可玩纵切片。玩家身份统一为桐人；旧“见习记录员”、长期 Day 编号路线和历史升级代号只保留在 archive，不得重新带回主界面或新计划。

## 不可破坏的边界

- FastAPI 是位置、时间、资源、flag、关系、剧情闸和永久记忆的权威。
- scripted NPC 是无模型 API 时的完整产品基线；hybrid/agent 必须可回退。
- 被拒绝的行动不得部分写入状态。
- `runs/`、`data/memory/`、`frontend/dist/` 是运行产物。
- 不直接向 `main` 堆改动；使用短分支、清晰提交和可回滚 PR。
- 未经来源、技术、内容和游戏内验收的素材不得复制到 runtime。

## 素材规则

日常协作只使用 `materials/inbox`、`materials/review`、`materials/approved`、`materials/archive` 四个位置。新沟通使用可读名称，不再在标题和说明中堆叠升级代号或连续版本号；机器追溯 ID 仅保留在 `REQUESTS.csv`、`MANIFEST.csv` 和 sidecar 中。

## 完成前

```bash
./scripts/quality.sh
./scripts/release.sh   # 只有准备发布时运行
```

用户可见变化更新 `CHANGELOG.md`；真实完成度只更新 `CURRENT_STATUS.md`；下一步只更新 `NEXT_PHASE.md`；架构所有权变化使用 ADR。
