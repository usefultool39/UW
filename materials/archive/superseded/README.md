# Superseded materials

这里保存从 active inbox 移出的历史样张、生成中间件、重复 sidecar 和 manifest fragments。

- `MANIFEST-history.csv` 是整理前 168 行完整台账，可用于恢复历史 source、hash 和审核信息。
- `world/`、`characters/`、`keyart/`、`vfx/`、`audio/` 保存旧生成工作和被替代样张。
- `registry-fragments/` 保存已经合并过的异构 manifest fragments。

当前项目不得从本目录读取 runtime 或生成任务输入；需要追溯时优先查 Git，其次查本目录。
