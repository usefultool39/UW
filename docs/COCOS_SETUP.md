# Cocos 本机环境与验证记录

更新日期：2026-05-14

## 当前产品决策

2026-05-15 调整：Cocos Creator 由于账号登录、首次启动弹窗和编辑器预览流程带来额外摩擦，暂时不再作为当前主开发路径。`cocos-client/` 保留为未来备用工程和契约样板；当前 Demo 继续以 `frontend/` 的 Vue + Phaser 客户端为主线推进。

## 当前结论

已经解决“本机没有 Cocos 入口”的问题：已通过 `winget` 安装 Cocos Dashboard 2.2.1.2616，并通过 Dashboard 官方协议安装 Cocos Creator 3.8.7。

```text
C:\Program Files (x86)\CocosDashboard\CocosDashboard.exe
C:\ProgramData\cocos\editors\Creator\3.8.7\CocosCreator.exe
```

当前已能用 Creator 3.8.7 打开 `cocos-client/`，窗口标题显示为 `Untitled - border-echo-cocos-client - Cocos Creator 3.8.7`。如果出现“温馨提示”或登录提示，属于 Cocos 首次启动提示，不影响本地工程。

## 已补齐的工程骨架

- `cocos-client` 已加入官方 `@cocos/creator-types@3.8.7`。
- `cocos-client` 已加入 `typescript@5.6.3`。
- 新增 `npm run typecheck`，会对 `assets/scripts/**/*.ts` 做 Cocos 类型检查。
- 新增 `npm run doctor`，会检测 Dashboard、Creator 编辑器、`project.json` 和 Cocos 类型包。
- 新增 `npm run verify`，串联 `validate`、`typecheck`、offline smoke、cross-client smoke。
- 新增真实 `assets/scenes/Boot.scene`：挂载 `Boot.ts`，运行后自动加载 `Field`。
- 新增真实 `assets/scenes/Field.scene`：建立 `Canvas/Camera/FieldRoot`，并挂载 `FieldController.ts`。
- `FieldController` 支持运行时自举，未手动拖拽绑定时会自动创建地图渲染节点和基础 Overlay。
- `MapRenderer` 支持 `uiToTile`，地图偏移后点击坐标仍能换算到正确 tile。
- `FieldController` 会运行时生成 Refresh、Story、Read、Train、Lunch、Dinner、NPC Profile、Greet、Rest、Reset 按钮。
- 按钮有命中区域判断，点击按钮不会同时触发地图移动。
- `validate-client.mjs` 已扩展为检查场景文件、scene meta、Boot/Field 脚本组件类型。
- Cocos Creator 运行中已经自动导入 `Boot.scene` 与 `Field.scene`，`library/.assets-info.json` 和 `.assets-data.json` 均能看到对应 UUID。

## 命令

```bat
cd /d F:\usefultool39\02-UW小镇\cocos-client
npm install
npm run doctor
npm run verify
```

后端已启动时，可运行：

```bat
npm run smoke:live
```

重新打开 Cocos 项目：

```bat
"C:\ProgramData\cocos\editors\Creator\3.8.7\CocosCreator.exe" --project "F:\usefultool39\02-UW小镇\cocos-client"
```

## 本轮验证结果

- `winget install --id Cocos.CocosDashboard --exact --accept-package-agreements --accept-source-agreements --silent`：通过。
- `cocos-dashboard://download/2d_3.8.7`：通过，Dashboard 下载并解压 Cocos Creator 3.8.7。
- `npm run doctor`：通过，找到 Dashboard 和 `C:\ProgramData\cocos\editors\Creator\3.8.7\CocosCreator.exe`。
- `npm run validate`：通过，场景、meta、关键 API、Day 1 入口方法和运行时按钮生成均通过检查。
- `npm run typecheck`：通过。
- `npm run verify`：通过。
- `npm run smoke:live`：通过。
- Cocos 编辑器资产导入：通过，`Boot.scene` / `Field.scene` 已进入 `library` 缓存。

## 后续动作（仅在恢复 Cocos 路线时执行）

1. 在编辑器预览窗口内完成真实点击验收：移动、读书、训练、午餐/晚餐、NPC Profile、休息跨天。
2. 如果运行时按钮体验正常，再把自动生成按钮替换为手工布局的正式 Cocos UI。
3. 之后再把自动生成的临时 Label/Graphics 替换成正式 tileset 表现。

当前默认后续动作：回到 Vue + Phaser 前端，继续优化地图、性能、UI、交互反馈和美术资源接入。
