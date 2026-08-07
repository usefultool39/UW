# Inbox 使用说明

`materials/inbox/` 只接收尚未审核的新素材。素材智能体只能写分配给自己的 inbox 子目录，不得修改 `REQUESTS.csv`、正式 `MANIFEST.csv` 或 `frontend/public/assets/runtime/`。

开始前阅读：

1. `materials/README.md`
2. `docs/art/ASSET_REVIEW.md`
3. 对应的 `REQUESTS.csv` 行

## 每次交付至少包含

1. 素材文件。
2. 同名 sidecar，或同目录内一个列出包内全部文件的主 sidecar。
3. 外部参考的来源链接和许可状态。
4. AI 生成素材的工具/模型、提示词、负面提示词、seed/设置、日期和后期修改。
5. 一文件一行的 manifest fragment，包含 source path 与 SHA-256。
6. 清楚的 intended use、技术规格和已知限制。

## Sidecar 最小模板

```md
# 人类可读素材名称

- request_id: VIS-...
- creator/source: 用户生成 / 摄影师 / 素材站
- created_at: YYYY-MM-DD
- tool_model: none 或实际模型
- prompt: |
  完整提示词
- negative_prompt: |
  完整负面提示词
- seed/settings: none 或实际设置
- license: owned / CC0 / CC-BY-4.0 / provider-commercial-output / unknown
- source_url: none 或实际地址
- edits: 裁切、去字、调色、降噪等
- intended_use: opening / portrait / ui / audio / reference
- notes: 已知限制
```

`license: unknown` 的素材只能用于方向讨论，不得进入 `approved` 或 runtime。

## 命名

日常沟通和文档使用“村庄地图、桐人动作、抓捕关键图”等可读名称。请求 ID 与修订序号只用于台账和 sidecar；不创建 `final_final`、日期副本或并行“最终版”。被退回的历史修订由 Git 追溯，不继续堆在 active inbox。
