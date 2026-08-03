# ADR-0004：Vue + Phaser 作为主客户端

- **状态**：Accepted
- **日期**：2026-08-03（补录现状）

## 背景
同时维护 Vue/Phaser 和 Cocos 会稀释玩法、测试与内容投入。

## 决策
当前主客户端是 Vue 3 + Phaser。Cocos 冻结为备用验证，不扩展独有玩法；共享能力以 HTTP/DTO 为边界。

## 后果
当前试玩/E2E/UI 以 Web 为准；只有原生发布、性能或制作管线收益明确时才用新 ADR 重评。
