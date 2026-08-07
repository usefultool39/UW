# UW 素材工作区

素材协作只使用四个位置：

- `inbox/`：刚收到、尚未审查。
- `review/`：来源和技术信息完整，等待人工看图/试听与游戏内验证。
- `approved/`：通过审查，但不一定已经接入。
- `archive/`：旧版本、中间文件、被拒绝或暂缓素材。

## 工作原则

1. 文件存在不等于完成；只有台账、来源、技术和游戏内证据都齐全才可接 runtime。
2. 新沟通使用可读名称，不在标题里叠加升级代号和长版本链。
3. 请求 ID 只保留在 `REQUESTS.csv`、`MANIFEST.csv` 和 sidecar 中，用于机器追溯。
4. 不覆盖旧 runtime 文件；先在 review 中验证，再以稳定短名接入。
5. 原始生成图、测试音频和工作脚本不留在 active inbox；Git 历史足以追溯。

当前可用性、返工意见和下一批详细需求见 [`docs/art/ASSET_REVIEW.md`](../docs/art/ASSET_REVIEW.md)。

## 门禁

```bash
./backend/.venv/bin/python materials/tools/check_materials.py
./backend/.venv/bin/python materials/tools/check_runtime_asset_specs.py --require-complete
./backend/.venv/bin/python materials/tools/check_precapture_readiness.py
```

前两个命令检查仓库和技术合同；最后一个是发布准备报告，允许在开发阶段显示 pending，但发布前必须通过。
