# ADR-0003：NPC 使用 scripted / hybrid / agent 运行时

- **状态**：Accepted
- **日期**：2026-08-03

## 背景
当前没有稳定模型 API，但长期希望 NPC 自主；现在强依赖模型会使游戏不可稳定试玩。

## 决策
默认 scripted，按 NPC 配 hybrid/agent。模式返回同一结构；超时/无效时回退 scripted。模型只产生候选，规则决定执行和记忆。

## 后果
离线版本是持续维护基线；供应商细节隔离在 runtime/adapter；Agent 必须有兼容和回退测试。
