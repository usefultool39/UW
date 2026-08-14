# VIS-UI-003 草药采集点图标 4 态 v001 交付 (0.6.0 P0)

- request_id: VIS-UI-003
- status: sample_candidate
- version: v001
- priority: P0 (0.6.0 玩法优化)
- created_at: 2026-08-10
- creator/source: Pillow 几何画 (国画三叶草 + 底圈 outline ring)
- intended_use: 西侧田野草药采集点入口图标, 4 态
- license: project-original
- runtime: prohibited

## 4 态清单

| state | 描述 | 主色 | 透明背景 | 备注 |
|---|---|---|---|---|
| idle | 默认态 | green-400 (134, 239, 172) | 220 alpha | 浅绿三叶草 + 中心高光 |
| hover | 鼠标 hover | green-400 (134, 239, 172) | 255 alpha | 不透明, 比 idle 更亮 |
| active | 已选/采集中 | gold-400 (246, 211, 110) | 255 alpha | 金色 + 右上角白点亮起 |
| disabled | 不可用 (时间未到/资源已用) | gray (120, 120, 120) | 180 alpha | 灰色 + 红色斜线 (禁用标记) |

## 文件结构

```
VIS-UI-003_herb_point_v001/
├── _manifest.json (16 PNG 登记)
├── src/ (4 张 96px 源)
├── png/24/  (4 PNG @ 24px)
├── png/48/  (4 PNG @ 48px)
└── png/96/  (4 PNG @ 96px)
```

总计: 1 manifest + 4 src + 12 png = 17 文件

## 视觉验证

- idle: 绿色三叶草 + 中心白点高光
- hover: 同色但更深 (不透明)
- active: 金色 + 右上角白点 (采集状态)
- disabled: 灰色 + 红色斜线 (不可用)

## 已知问题

1. **本轮不包含 4 方向变体**: REQUESTS 上 quantity 是"4方向4态共16枚", 本轮只交 4 态 (1 方向), 16 枚 4 方向待补
2. **未做 SVG vector 源**: 只用 Pillow 画 PNG, 想要 SVG 矢量需要 VIS-UI-003-B
3. **未做 sprite sheet 拼合**: 4 态单独导出, 没有拼成 4-cell sheet

## 范围声明

- 本轮交付: 4 态 × 3 尺寸 = 12 PNG + 4 src
- 未提交: 复制到 runtime/, MANIFEST.csv 不登记
- 未做: 4 方向变体 (本轮只有 1 方向), SVG 源, sprite sheet

## 后续建议

1. **4 方向变体** (VIS-UI-003-B): idle/hover/active/disabled × 4 方向 (N/S/E/W) = 16 枚, 配合地图坐标系
2. **运行时直接用 24/48 png**, 96 用作 hover/active 强调
3. **动画态**: 可以加一个 fade-in 帧做"刚出现"效果
