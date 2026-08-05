# 0.4.0-preview.1 候选版本说明

- 日期：2026-08-04
- 状态：Candidate workspace / 未 commit、未 tag、未 push
- Git 基线：`main` / `49ae78d` + 本轮未提交成熟化改动
- 版本事实源：`VERSION` = `0.4.0-preview.1`

## 本版目标

把《边境回声》Day 1–3 纵切片从“功能齐全但需要自行理解”收束为“开场目标单一、行动代价清楚、短玩法入口唯一、关系选择有三日回响、固定 NPC 与未来 agent 共用活动结构”的外部试玩候选。

## 玩家可见收束

1. Day 1 开场只保留“定位第一条线索”一个主 CTA，进入地图后主目标只在右侧任务卡提供一个可点击入口。
2. 三步提示和短循环 HUD 解释“线索 → 选择 → 关系回响”，不再由多个大型引导层同时遮挡地图。
3. 行动前显示耗时、资源成本、收益类别、锁定原因与恢复建议。
4. 书库读书只有一个正式短玩法入口；NPC 主动邀请与 POI 基础活动同 ID 时只显示带人物语境的入口。
5. Day 1 “共同记录 / 隐瞒符号”在 Day 2 产生互斥可操作回响，并在 Day 3 判定中继续显示因果。
6. 读书、用餐、巡查的面板、结果字段和完成提示统一由 activity registry 驱动。

## 系统边界

- FastAPI 继续拥有位置、时间、资源、flag、关系、剧情闸、奖励、记忆的最终裁决。
- scripted 是完整离线基线；hybrid / agent 只提供意图与表达，失败时回退，不绕过后端事务。
- 被拒绝行动不会部分写入状态。
- 存档 schema、HTTP API、内容 ID 和 NPC runtime envelope 本版未做破坏性变更。

## 验证证据

- Backend pytest：205 passed；1 个 Starlette/httpx 第三方弃用警告。
- Frontend unit：12 passed。
- Frontend production build：passed。
- Playwright E2E：11 passed，覆盖 Day 1–3、北境巡查、Day 24/28/31/39/46；最终使用隔离端口 `8875/3077` 复验，避免误连本机旧服务。
- `git diff --check`：passed。
- 验证克隆与实际桌面项目同步文件逐字节一致。

## 已知限制

- 仍缺真实首次玩家盲测，不把自动化 E2E 当作可理解性证据。
- 现有地图、角色和音频多为占位/程序化素材，视觉与听觉风格尚未正式锁定。
- Phaser minified chunk 约 1.48 MB，暂不阻塞本候选版。
- 工作区仍未 commit/tag；正式发布前还需干净环境启动、存档导入导出复验和人工试玩签字。

## 下一步

下一候选版转入“素材风格锁定 + 真实首次玩家盲测”，执行计划见 `docs/planning/NEXT_PHASE.md`，素材入口见 `materials/00_INDEX.md`。
