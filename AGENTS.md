# UW 协作规则

进入仓库后按顺序阅读：

1. `docs/PROJECT.md`
2. `docs/PLAN.md`
3. `docs/art/ASSET_REVIEW.md`
4. `docs/DELIVERY.md`

## 当前唯一目标

完成版本 `0.5.0` 的卢利特村序章纵切片：玩家身份为桐人，主线从三人村庄日常推进到爱丽丝在村中被带走。旧“见习记录员”、月度路线、长期 Day 编号和历史升级代号均已停止，不得以新文档或新 UI 形式恢复。

## 不可破坏的边界

- FastAPI 是位置、时间、资源、flag、关系、剧情闸和永久记忆的权威。
- scripted NPC 是无模型 API 时的完整产品基线；hybrid/agent 必须可回退。
- 被拒绝的行动不得部分写入状态。
- 未审核素材不得进入 runtime。
- `runs/`、`data/memory/`、`frontend/dist/`、密钥和本地环境不得提交。
- 架构所有权变化先写 ADR；产品范围变化先修改 `docs/PROJECT.md`。

## 文档纪律

- 不新增日期型 status、handoff、upgrade、phase 或版本副本。
- 当前完成度和下一步只写入 `docs/PLAN.md`。
- 玩家可见名称、文档标题和沟通使用自然语言，不暴露内部 ID。
- 素材请求 ID 只保留在 `REQUESTS.csv`、`MANIFEST.csv` 和素材 sidecar 中。
- 旧事实使用 Git 历史追溯，不在仓库内继续复制归档文档。

## 完成前

```bash
./scripts/quality.sh
./scripts/release.sh   # 仅在准备发布时运行
```

用户可见改动更新 `CHANGELOG.md`；测试和交付证据更新 `docs/PLAN.md`；素材结论更新 `docs/art/ASSET_REVIEW.md`。
