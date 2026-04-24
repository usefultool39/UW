# Cocos 客户端占位

当前可运行客户端是 `frontend/` 的 Vue + Phaser 浏览器切片。`cocos-client/` 只保留为未来正式 2.5D 客户端占位，不存放 Cocos Creator 自动生成的大量工程文件。

未来如果要接 Cocos，优先复用同一套后端 API：

- `GET /api/state`
- `GET /api/world/map`
- `GET /api/world/regions`
- `GET /api/story/available_events`
- `POST /api/story/choose`
- `POST /api/player/action`
- `POST /api/dialogue`
- `GET /api/npc/{npc_id}/profile`
- `GET /api/save/export`
- `POST /api/save/import`

正式开工前先读 [../docs/PROJECT.md](../docs/PROJECT.md)，确认 Cocos 只替换表现层，不改变“后端规则定事实”的边界。
