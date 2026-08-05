# Inbox 使用说明

实际放置路径：`/Users/lzm/Desktop/UW/materials/inbox/`。

## 每次交付至少包含

1. 素材文件：如 `VIS-KA-001_rulid_drizzle_v001_desktop.png`。
2. 同名 sidecar：`VIS-KA-001_rulid_drizzle_v001_desktop.md`。
3. 若使用外部参考，放入 `research/moodboards/` 并在 sidecar 写来源链接和许可状态。
4. 若为 AI 生成，sidecar 写：工具/模型、完整提示词、负面提示词、seed（若有）、生成日期、后期修改。

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
