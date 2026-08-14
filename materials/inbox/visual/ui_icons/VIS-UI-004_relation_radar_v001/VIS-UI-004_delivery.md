# VIS-UI-004 关系雷达图 UI 素材 v001 交付 (0.6.0 P0)

- request_id: VIS-UI-004
- status: sample_candidate
- version: v001
- priority: P0 (0.6.0 玩法优化)
- created_at: 2026-08-10
- creator/source: Pillow 程序化绘制 (5 边形 + 5 轴 + 中文角色标签)
- intended_use: 关系系统可视化 (玩家 + 4 NPC 关系度)
- license: project-original
- runtime: prohibited

## 解决了 REQUESTS 的问题

- REQUESTS 标 requested 是因为没素材. 本轮交付 1 套 5 角色轴 + 1 模板 + 5 角色示例数据
- 用 Pillow 程序化画, 5 边形 + 5 轴 + 5 角色 dot + 标签 (含中文)
- 数据多边形自动按识别色 fill

## 5 角色识别色 (按项目识别色规范)

| axis | cn | color | hex | 备注 |
|---|---|---|---|---|
| 0 | 桐人 Kirito | cyan-400 | #7DD3FC | 玩家 + 主角 |
| 1 | 尤吉欧 Eugeo | green-400 | #86EFAC | 兄弟角色 |
| 2 | 爱丽丝 Alice | gold-400 | #F6D36E | 羁绊核心 |
| 3 | 赛尔卡 Selka | paper-300 | #D9E3E8 | 朋友 NPC |
| 4 | 加斯夫特 Garret | amber-700 | #B45309 | 长老 NPC |

## 6 张 PNG (1024x1024)

| 文件 | 内容 |
|---|---|
| radar_template_empty.png | 5 边形 + 5 轴 + 5 角色 dot, 无数据 |
| radar_kirito_example.png | 以桐人视角, 0.7/0.85/0.9/0.3/0.2 (均匀高 + Selka/Garret 低) |
| radar_eugeo_example.png | 以尤吉欧视角, 0.85/0.5/0.9/0.4/0.3 (与桐人/爱丽丝近) |
| radar_alice_example.png | 以爱丽丝视角, 0.9/0.85/0.4/0.5/0.4 (与桐人/尤吉欧近) |
| radar_selka_example.png | 以赛尔卡视角, 0.3/0.4/0.5/0.7/0.6 (与 Garret/Elders 高) |
| radar_garret_example.png | 以加斯夫特视角, 0.2/0.3/0.4/0.6/0.85 (自中心低, Garret 高) |

## 文件结构

```
VIS-UI-004_relation_radar_v001/
├── _manifest.json (6 PNG 登记)
├── src/ (6 张 1024x1024 源, 用于 Phaser 高清渲染)
└── png/512/  (6 PNG @ 512x512, 用于游戏内显示)
```

总计: 1 manifest + 6 src + 6 png = 13 文件

## 视觉验证

- 5 边形 + 5 轴 + 4 圈 25%/50%/75%/100% 刻度
- 5 角色 dot 用识别色 + 白色 outline
- 中文标签 (桐人/尤吉欧/爱丽丝/赛尔卡/加斯夫特) 用微软雅黑
- 数据多边形按 active character 颜色半透明 fill

## 已知问题

1. **未做运行时数据接入**: 当前是 5 张静态示例图, 实际游戏需要根据存档数据动态绘制
2. **未做移动端布局**: 1024x1024 在 390x844 移动端可能过大, 建议 mobile 用 512x512 + scrollable 标签
3. **未做颜色盲友好模式**: 5 色中 cyan/green 可能对色盲用户难分, 建议加 pattern (实线/虚线) 区分
4. **未做历史变化轨迹**: 关系度变化历史 (上一周 vs 这一周) 还没设计
5. **雷达图不能表达方向 (好感/信任)**: 0-1 一维数据, 实际游戏可能要拆 trust/affection/fear 三维

## 范围声明

- 本轮交付: 1 模板 + 5 角色示例 = 6 张 PNG, 含中文标签
- 未提交: 复制到 runtime/, MANIFEST.csv 不登记
- 未做: 动态数据接入, 移动端布局, 颜色盲模式, 历史轨迹, 三维雷达

## 后续建议

1. **动态数据接入** (VIS-UI-004-B): 把 draw_radar_template() 函数移植到 Phaser runtime, 用存档 JSON 数据动态画
2. **三维雷达**: 拆 trust/affection/fear 三层, 玩家看 3 个值而不是 1 个
3. **历史对比**: 双层多边形 (上周 vs 本周), 灰底 + 亮色填充
