# 边境回声 Cocos Creator 并行客户端

状态：v0 工程骨架和真实 Boot/Field 场景资产已建立，但当前冻结为备用。  
定位：未来可能恢复的正式表现层样板，和 `frontend/` 共用同一 FastAPI 后端；后端仍然是唯一权威世界状态。

2026-05-15 调整：由于 Cocos Creator 登录、首次启动和编辑器预览流程会打断当前开发节奏，本目录不再是当前主开发路径。当前 Demo 默认继续使用 `frontend/` 的 Vue + Phaser 客户端推进。这里保留 API 契约、DTO、地图渲染和场景样板，便于未来重新评估。

## 推荐环境

- Cocos Dashboard 2.2.x
- Cocos Creator 3.8.x
- Node.js + npm
- 后端运行在 `http://127.0.0.1:8765`

本机当前已通过 `winget` 安装 Cocos Dashboard：

```text
C:\Program Files (x86)\CocosDashboard\CocosDashboard.exe
```

本机当前已通过 Dashboard 安装 Cocos Creator 3.8.7：

```text
C:\ProgramData\cocos\editors\Creator\3.8.7\CocosCreator.exe
```

## 目录约定

```text
cocos-client/
  assets/
    scripts/
      api/       后端 API、DTO、契约常量
      field/     地图渲染、本地寻路、Field 控制器
      ui/        Overlay UI 最小绑定
      boot/      Boot 初始化
    scenes/      Boot.scene、Field.scene、场景接线说明和机器可读 manifest
  scripts/       本地 doctor、静态校验、契约 smoke
```

不要提交 Cocos 生成目录：`Library/`、`library/`、`Temp/`、`temp/`、`build/`、`local/`。

## v0 能力边界

- 读取 `/api/state`、`/api/world/map`、`/api/story/available_events`、`/api/world/scene_activities`。
- 用同一份 `world_map.json.rows` 渲染草地、道路、水、森林、障碍。
- 显示玩家、NPC、POI、剧情点。
- 点击 tile 后先本地 BFS 预演，再调用 `/api/player/action` 的 `move_map`，失败则回到后端权威状态。
- 提供 Day 1 最小闭环按钮方法：读书、训练、午餐、晚餐、剧情选择、NPC Profile、NPC 问候、休息跨天、重置。
- `Boot.scene` 已挂载 `Boot.ts` 并自动加载 `Field`。
- `Field.scene` 已挂载 `FieldController.ts`，未手动绑定节点时会自动创建基础地图和 Overlay。
- 自动 Overlay 会生成 Refresh、Story、Read、Train、Lunch、Dinner、NPC Profile、Greet、Rest、Reset 按钮。

## 本地验证

```bat
cd /d F:\usefultool39\02-UW小镇\cocos-client
npm install
npm run doctor
npm run verify
```

如果后端正在运行，可以追加真实 API smoke。注意：它会 reset 当前原型会话。

```bat
npm run smoke:live
```

## 打开方式（仅在恢复 Cocos 路线时使用）

1. 启动后端。
2. 用 Creator 打开 `F:\usefultool39\02-UW小镇\cocos-client`。
3. 打开 `assets/scenes/Boot.scene`，点击预览；Boot 会加载 `Field.scene`。
4. 也可以直接打开 `assets/scenes/Field.scene` 预览地图纵切片。
5. 下一步是在 Creator 预览窗口里做真实点击验收；通过后再把运行时按钮替换成正式手工布局 UI。

当前优先级：暂不继续 Creator 预览验收，优先回到 `frontend/` 做地图、性能、UI 和美术接入。
