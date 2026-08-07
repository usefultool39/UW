# Inbox 使用说明

本机实际放置路径：`C:\Users\liang\Desktop\UW\materials\inbox\`。

当前 v003 返工必须先读：`docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md`。素材智能体只写对应 inbox 目录，不修改 `REQUESTS.csv`、正式 `MANIFEST.csv` 或 `frontend/public/assets/runtime`。

## 每次交付至少包含

1. 素材文件：如 `VIS-KA-001_rulid_drizzle_v001_desktop.png`。
2. 同名 sidecar，或同目录下一个带 request_id 和版本号、完整列出包内文件的主 sidecar。
3. 若使用外部参考，放入 `research/moodboards/` 并在 sidecar 写来源链接和许可状态。
4. 若为 AI 生成，sidecar 写：工具/模型、完整提示词、负面提示词、seed（若有）、生成日期、后期修改。
5. 每个包提供 manifest fragment，一文件一行写 source path 和 SHA-256；正式 runtime、审核人和接入时间字段留空。
6. 返工版本只能递增，不覆盖失败版本；当前五个返工包统一使用 v003。

## Sidecar 最小模板

```md
# VIS-KA-001_rulid_drizzle_v001_desktop

- request_id: VIS-KA-001
- creator/source: 用户生成 / 摄影师 / 素材站名称
- created_at: YYYY-MM-DD
- tool_model: （没有则写 none）
- prompt: |
  完整提示词
- negative_prompt: |
  完整负面提示词
- seed/settings: （没有则写 none）
- license: owned / CC0 / CC-BY-4.0 / provider-commercial-output / unknown
- source_url: （没有则写 none）
- edits: 裁切、去字、调色、降噪等
- intended_use: opening / portrait / ui / audio / reference
- notes: 需要特别说明的内容
```

`license: unknown` 的素材可以用于方向讨论，但不得进入 `approved` 或正式运行时。

`REWORK_*.md` 是项目负责人给出的返工说明，不是交付 sidecar，也不能代替来源、权利、提示词或 hash 记录。
