# VIS-UI-001_core_icons_v001

- request_id: VIS-UI-001
- creator/source: CodeBuddy Code / hy3（程序化绘制）
- created_at: 2026-08-04
- tool_model: 程序化 SVG（Python + Pillow + rsvg-convert），非生成式 AI
- prompt: none
- negative_prompt: none
- seed/settings: none
- license: owned
- source_url: none
- edits: none
- intended_use: ui
- notes: |
  12 枚图标全部手工定义在 24×24 栅格上，统一 stroke-width="1.5"、stroke-linecap="round"、stroke-linejoin="round"；
  SVG 使用 currentColor，颜色由父元素控制；栅格化时按 02_VISUAL_STYLE_BIBLE.md 语义色 token 渲染。
  已验证 24/48/96 px 三尺寸无糊线，黑白打印可区分。

---

## 图标清单

| id | 中文 | 语义色 token | HEX | 轮廓描述 | 语义 |
|---|---|---|---|---|---|
| clue | 线索 | cyan-400 | #7DD3FC | 圆形镜片 + 右下斜柄 | 调查线索 / 可追查信息 |
| record | 记录 | paper-300 | #D9E3E8 | 竖长方形，右上折角 | 书库记录 / 日志条目 |
| time | 时间 | paper-300 | #D9E3E8 | 上下横杠 + 中间收腰沙漏 | 时段推进 / 行动耗时 |
| stamina | 体力 | gold-400 | #F6D36E | 尖顶水滴火焰 | 行动力余量 |
| relationship | 关系 | green-400 | #86EFAC | 左上右下两圆 + 斜连线 | 人物关系度 / 信任 |
| tension | 紧张 | amber-500 | #F59E0B | 左右立柱 + 中间下坠的绷弦 | 紧张度 / 风险累积 |
| memory | 记忆 | paper-300 | #D9E3E8 | 单条向内收束螺旋 | 已获记忆 / 可回溯片段 |
| anomaly | 异常 | violet-500 | #8B5CF6 | 正菱形 + 内部折线裂缝 | 北境异常 / 静默线征兆 |
| locked | 锁定 | rose-500 | #F43F5E | 矩形锁体 + U 形锁梁 | 条件未满足 / 不可交互 |
| recover | 恢复 | green-400 | #86EFAC | 右上缺口的圆环 + 箭头 | 体力 / 状态回复 |
| location | 地点 | cyan-400 | #7DD3FC | 倒水滴地图针 | 可前往地点 / 当前位置 |
| schedule | 日程 | paper-300 | #D9E3E8 | 横矩形 + 顶部双挂耳 + 实心标记格 | 每日安排 / 活动排程 |

## 文件结构

```
inbox/visual/ui_icons/VIS-UI-001_core_icons_v001/
├── svg/<name>.svg           # currentColor 单色 SVG
├── png/24/<name>.png
├── png/48/<name>.png
├── png/96/<name>.png
├── icons.meta.json
├── VIS-UI-001_core_icons_v001_sheet.png
└── VIS-UI-001_core_icons_v001.md
```

## 可复现方式

```bash
cd /Users/lzm/Desktop/UW/materials
/opt/miniconda3/bin/python3 tools/gen_ui_icons.py
/opt/miniconda3/bin/python3 tools/gen_ui_icon_sheet.py
```

依赖：Python 3.x、Pillow、rsvg-convert、Hiragino Sans GB / Menlo 字体。
