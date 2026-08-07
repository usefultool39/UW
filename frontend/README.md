# 前端

Vue 3 + Vite 提供界面，Phaser 提供地图、移动与空间互动。前端只发送玩家意图并展示结果，权威世界状态由 FastAPI 维护。

- 产品与边界：`../docs/PROJECT.md`
- 客户端契约：`../docs/architecture/CLIENT_CONTRACT.md`
- 运行：`../docs/operations/RUNBOOK.md`

## 启动

```bash
cd frontend
npm install
npm run dev
```

默认地址：`http://127.0.0.1:3000`

开发环境下 `/api` 代理到 `http://127.0.0.1:8765`，因此后端需要同时运行。

## 测试与构建

```bash
npm run test:unit
npm run build
npm run test:e2e
```

## 主要入口

| 文件 | 作用 |
|---|---|
| `src/App.vue` | 应用入口与全局 API 状态 |
| `src/components/FieldSlice.vue` | 地图体验、HUD、菜单和面板调度 |
| `src/field/createWorldFieldScene.js` | Phaser 地图、移动、NPC、事件和 POI |
| `src/field/gameContentConfig.js` | 显示名、runtime 素材路径和场景配置 |
| `src/composables/useGameApi.js` | API 封装 |
| `src/components/DialoguePanel.vue` | NPC 对话 |
| `src/components/StoryEventPanel.vue` | 剧情选择 |
| `src/components/StoryResultPanel.vue` | 结果反馈 |

## Runtime 素材

正式接入的稳定素材位于：

```text
frontend/public/assets/runtime/
```

候选素材不得直接复制到 runtime。审查规则见 `../docs/art/ASSET_REVIEW.md` 和 `../materials/README.md`。
