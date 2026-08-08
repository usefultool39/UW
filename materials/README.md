# UW 素材工作区

素材协作使用四个状态位置：

- `inbox/`：刚收到、尚未审查。
- `review/`：来源和技术信息完整，等待人工看图/试听与游戏内验证。
- `approved/`：通过审查，但不一定已经接入。
- `archive/`：旧版本、中间文件、被拒绝或暂缓素材。

当前生成但尚未通过的素材统一使用 `sample_candidate`，放在各分类的 `current/` 目录并使用稳定文件名。它们已进入总台账，但没有 runtime 映射，不能被质量检查通过误读为正式完成。

每个分类内部只保留两个工作入口：

- `current/`：当前唯一基线，供项目测试和下一轮参考。
- `candidate/`：下一轮候选；通过后晋级为 current，旧 current 同时归档。

文件名表达用途，不表达修订历史。例如使用 `VIS-MAP-001_master.png`，不使用 `_v008_final2.png`。request ID 是稳定机器键，可以保留。

## 工作原则

1. 文件存在不等于完成；只有台账、来源、技术和游戏内证据都齐全才可接 runtime。
2. `sample_candidate` 不属于正式批准状态；素材智能体只能交付候选，批准和接入由人工/工程验收完成。
3. 新沟通使用可读名称，不在标题里叠加升级代号和长版本链。
4. 请求 ID 只保留在 `REQUESTS.csv`、`MANIFEST.csv` 和 sidecar 中，用于机器追溯。
5. 不覆盖旧 runtime 文件；先在 review 中验证，再以稳定短名接入。
6. 原始生成图、测试音频和工作脚本不留在 active inbox；Git 历史足以追溯。

当前可用性、返工意见和下一批详细需求见 [`docs/art/ASSET_REVIEW.md`](../docs/art/ASSET_REVIEW.md)。
生图智能体的稳定规范见 [`docs/art/GENERATION_AGENT_PROMPT.md`](../docs/art/GENERATION_AGENT_PROMPT.md)，当前任务见 [`docs/art/ASSET_TASKS.md`](../docs/art/ASSET_TASKS.md)。

## 门禁

```bash
./backend/.venv/bin/python materials/tools/check_materials.py
./backend/.venv/bin/python materials/tools/check_runtime_asset_specs.py --require-complete
./backend/.venv/bin/python materials/tools/check_precapture_readiness.py
```

前两个命令检查仓库和技术合同；最后一个是发布准备报告，允许在开发阶段显示 pending，但发布前必须通过。
