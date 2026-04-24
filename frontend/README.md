# 前端说明

Vue 3 + Vite + Phaser 地图主界面。前端只发送玩家意图和展示结果，权威世界状态由后端维护。

完整架构见 [../docs/PROJECT.md](../docs/PROJECT.md)。

## 运行

```bat
cd /d C:\Users\liang\Downloads\30小镇\30小镇\frontend
npm install
npm run dev
```

默认地址：

```text
http://127.0.0.1:3000
```

开发环境下 `/api` 通过 Vite 代理到 `http://127.0.0.1:8765`。后端需另起一个终端运行。

## 构建与 E2E

```bat
npm.cmd run build
npm.cmd run test:e2e
```

在 Codex 沙箱中，esbuild 或 Playwright 子进程可能报 `spawn EPERM`。这通常是沙箱限制，不是前端代码错误；正常 Windows 环境或获准提权后可运行。

## 主要入口

| 文件 | 作用 |
|------|------|
| `src/App.vue` | 应用入口，地图/调试台切换 |
| `src/components/FieldSlice.vue` | 地图主体验容器、HUD、热键、存档、面板调度 |
| `src/field/createWorldFieldScene.js` | Phaser 地图渲染、移动、NPC、事件、POI |
| `src/field/gameContentConfig.js` | 显示名、素材路径、场景名、目标提示 |
| `src/composables/useGameApi.js` | API 封装 |
| `src/components/DialoguePanel.vue` | NPC 对话 |
| `src/components/StoryEventPanel.vue` | 章节事件选择 |
| `src/components/StoryResultPanel.vue` | 选择结果反馈 |
| `src/components/NpcProfilePanel.vue` | NPC 关系档案 |

## 素材

稳定游戏素材目录：

```text
frontend/public/assets/game/
```

替换规则见 [public/assets/game/README.md](public/assets/game/README.md)。
