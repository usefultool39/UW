# REF-MOOD-001 暂停状态说明

- request_id: REF-MOOD-001
- status: **PAUSED**（暂停于 2026-08-04 23:27，用户要求明日续跑）
- created_at: 2026-08-04
- resume_doc: `../../RESUME_NEXT.md`（断点交接文档，必读）

## 为什么暂停

执行该任务的采集在 Wikimedia Commons 上卡住。人工诊断：

| 目标源 | 结果 |
|---|---|
| Wikimedia Commons API | ❌ TLS 握手超时（curl 返回 000） |
| Library of Congress | ❌ 403 |
| **Met Open Access API** | ✅ 200，可正常访问 |

## 已确定方案（续跑时执行）

改用 **Met Open Access API**（全部 CC0 / public domain）作为参考源：
- search：`https://collectionapi.metmuseum.org/public/collection/v1/search?q={kw}&hasImages=true`
- object：`https://collectionapi.metmuseum.org/public/collection/v1/objects/{id}`
- 字段已验证：title / objectDate / artistDisplayName / medium / primaryImage / objectURL / rightsAndReproduction

详见 `materials/RESUME_NEXT.md` 第 2 节（14 类关键词映射 + 交付文件规范）。

## 产物目录

`inbox/research/moodboards/`（当前为空，续跑时在此产出 3 个文件）
