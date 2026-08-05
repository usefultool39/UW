# Day 1 陌生玩家盲测执行单

- **版本**：`0.5.0-playable-day1` 候选工作区
- **用途**：验证真实玩家是否能在不解释玩法的情况下理解 Day 1 目标、行动代价/收益和剧情跨日。
- **当前状态**：执行条件已准备；尚未产生 3 名真实玩家数据，不把 E2E 当作真人证据。
- **主模板**：`materials/inbox/research/playtest/QA-PLAY-001_playtest_kit_v001.md`

## 主持前置检查

```bash
cd /Users/lzm/Desktop/UW
python3 materials/tools/check_materials.py
cd frontend
npm run build
PYTHON_BIN=../backend/.venv/bin/python npm run test:e2e
```

启动试玩版本：

```bash
cd /Users/lzm/Desktop/UW
./start-macos.command
```

若端口冲突，使用仓库现有 Playwright 配置的隔离端口变量，不修改玩家看到的内容。

## 每名玩家的固定流程

1. 使用全新浏览器上下文和“新游戏”存档。
2. 逐字念 QA-PLAY-001 开场脚本，不解释目标、地图、行动或日期规则。
3. 屏幕录制；主持人只记时间、误点、停留和原话。
4. 玩家卡住时先观察 60 秒；确实需要提示时，记录提示时间和原话。
5. 至少观察到以下节点之一：
   - 第一次有效互动；
   - 书库线索选择；
   - 训练或其他日常活动；
   - 回家休息时的剧情闸提示；
   - 完成线索后自动进入 Day 2。
6. 结束后逐字询问 QA-PLAY-001 的五个固定问题。

## 必须回填的证据

每名玩家一份，不伪造、不用开发者代打：

```text
materials/inbox/research/playtest/QA-PLAY-001_player01.md
materials/inbox/research/playtest/QA-PLAY-001_player02.md
materials/inbox/research/playtest/QA-PLAY-001_player03.md
```

可选录屏放在本机受控目录，记录文件只写匿名文件名；不要提交私人录屏或个人信息到 Git。

## 判定门槛

- **上手**：3 人中至少 2 人在 60 秒内完成第一次有效互动；
- **目标**：3 人中至少 2 人能说出“今天要查书库边界记录”或等价表达；
- **代价**：3 人中至少 2 人能说出一种行动时间/体力代价；
- **收益**：3 人中至少 2 人能说出一种线索、关系或记忆收益；
- **剧情闸**：没有玩家能在未完成书库线索时直接跨到 Day 2；
- **继续意愿**：至少 2 人表示愿意继续查看 Day 2 或森林异常。

不达标时只修复最高频的一个阻塞点，重新跑自动化质量门，再进行下一轮盲测。
