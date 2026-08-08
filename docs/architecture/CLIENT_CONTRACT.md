# 客户端契约

当前正式客户端是 Vue + Phaser。FastAPI 提供唯一权威状态；客户端只负责输入、表现、本地预测和失败回滚。

## 稳定接口

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/api/health` | 服务与内容健康 |
| `GET` | `/api/state` | 当前权威世界状态 |
| `POST` | `/api/reset` | 创建全新 run |
| `POST` | `/api/player/action` | 移动、活动和系统行动 |
| `GET` | `/api/story/available_events` | 当前可用剧情事件 |
| `POST` | `/api/story/choose` | 提交 authored 剧情选择 |
| `POST` | `/api/dialogue` | NPC 对话；可回退 scripted |
| `GET` | `/api/npc/{npc_id}/profile` | 关系、承诺和记忆投影 |
| `GET` | `/api/save/export` | 导出存档 |
| `POST` | `/api/save/import` | 校验并导入存档 |

允许增加可选字段；删除字段、改变含义或改变所有权必须提供兼容层、测试和 ADR。

## 客户端可以做

- 渲染地图、角色、天气、动画和声音。
- 根据后端状态显示主目标、附近互动、代价预览和结果。
- 在移动动画期间做可撤销的本地预测。
- 缓存非权威的 UI 偏好，如音量和减少动态。
- 在请求失败后恢复到最后一次确认的后端状态。

## 客户端不能做

- 直接修改位置、时间、资源、关系、flag、剧情节点或永久记忆。
- 在本地判断 authored 条件已满足并跳过后端。
- 将模型返回文本视为权威 effects。
- 通过隐藏按钮或浏览器存储修复主线状态。

## 关键对象

### WorldState

必须包含当前 run、玩家、NPC、时间、资源、关系投影、可用剧情/活动和下一目标所需字段。客户端必须容忍新增可选字段。

### PlayerAction

客户端发送受限的 action kind 和必要参数。后端返回：

- `ok` 或明确 rejection；
- 最新权威 state；
- 玩家可见 result；
- 触发的事件、关系或记忆摘要；
- 失败时的原因和恢复建议。

### Story Event

客户端只提交后端返回的事件 ID 与选项 ID。效果、进入条件、回响和下一节点均由后端 authored 数据决定。

### Scene Activity

公开给客户端的预览只包含玩家需要理解的内容，例如资源代价、奖励类型、限制和交互类型。完整 effects 不下放给客户端执行。

烹饪/钓鱼/书库小游戏完成后，客户端可以在 `POST /api/player/action` 的 `mini_game_result` 可选字段中提交性能证据；后端会根据 authored 规则重新核对击打次数、火候、提竿时机或三步推理链，并只执行与性能一致的 authored choice。缺失、越界或不一致的结果必须原子拒绝，不能消耗库存、时间、资源、关系或记忆。

## 移动与场景

- Phaser 可以先播放移动，但后端拒绝时必须回滚。
- 地图 ID、POI、scene zone 和 interaction ID 由后端数据提供。
- 未知 interaction kind 必须安全降级为通用说明，不能猜测结果字段。
- 桌面和触控使用同一权威行动，不建立两套规则。

## 存档兼容

- 新字段提供默认值。
- 导入时校验 schema、非法枚举、范围和终点状态。
- 旧内部显示名可通过显示层转换，但新内容必须使用当前统一称谓。
- 兼容代码不应重新暴露旧产品方向。
