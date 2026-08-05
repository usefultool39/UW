#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIS-UI-001  12 枚核心 UI 图标生成器

设计约束（来自 01_REQUEST_CATALOG.md / 02_VISUAL_STYLE_BIBLE.md）：
  - 24x24 设计栅格，所有图形吸附到 0.2px
  - 统一笔画宽度 1.5（24px 基准），round cap / round join
  - 单线为主 + 少量面填充
  - stroke 一律 currentColor，颜色由外层 CSS/父元素控制
  - 轮廓（silhouette）两两互异，黑白打印可区分
  - 无文字、无商标化图形

输出：
  svg/<name>.svg            单色可着色 SVG
  png/{24,48,96}/<name>.png 透明背景 PNG（按语义色渲染）
  ..._sheet.png             2048x1024 总览
"""

import json
import math
import os
import subprocess
from pathlib import Path

ROOT = Path("/Users/lzm/Desktop/UW/materials")
OUT = ROOT / "inbox" / "visual" / "ui_icons" / "VIS-UI-001_core_icons_v001"
RSVG = "/opt/miniconda3/bin/rsvg-convert"

SW = 1.5  # 统一笔画宽度

# ---------------------------------------------------------------- 调色板
# 取自 02_VISUAL_STYLE_BIBLE.md 的语义色 token
PALETTE = {
    "ink-950":   "#071018",
    "ink-800":   "#102331",
    "paper-100": "#FFF7DF",
    "paper-300": "#D9E3E8",
    "gold-400":  "#F6D36E",
    "cyan-400":  "#7DD3FC",
    "green-400": "#86EFAC",
    "amber-500": "#F59E0B",
    "rose-500":  "#F43F5E",
    "violet-500": "#8B5CF6",
}


# ---------------------------------------------------------------- 几何助手
def spiral_path(cx, cy, r_start, r_end, turns, n=140):
    """阿基米德螺线折线 —— 用于 memory 图标。
    逐点计算而非拼接圆弧，保证曲率连续、无接缝硬点。"""
    pts = []
    total = turns * 2 * math.pi
    for i in range(n + 1):
        t = total * i / n
        r = r_start + (r_end - r_start) * (t / total)
        a = t - math.pi / 2  # 从正上方起笔
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = "M{:.2f} {:.2f}".format(*pts[0])
    for p in pts[1:]:
        d += " L{:.2f} {:.2f}".format(*p)
    return d


def arc_path(cx, cy, r, a0_deg, a1_deg):
    """SVG 圆弧（顺时针方向，角度以正右为 0、顺时针为正）。"""
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    sweep = 1
    large = 1 if (a1_deg - a0_deg) % 360 > 180 else 0
    return (f"M{x0:.2f} {y0:.2f} A{r} {r} 0 {large} {sweep} {x1:.2f} {y1:.2f}",
            (x0, y0), (x1, y1))


def arrow_head(px, py, ang_deg, size=3.0, spread=38):
    """在 (px,py) 处、朝向 ang_deg 的开口箭头（两笔 V 形）。"""
    a = math.radians(ang_deg)
    a1 = a + math.radians(180 - spread)
    a2 = a - math.radians(180 - spread)
    return (f"M{px + size * math.cos(a1):.2f} {py + size * math.sin(a1):.2f} "
            f"L{px:.2f} {py:.2f} "
            f"L{px + size * math.cos(a2):.2f} {py + size * math.sin(a2):.2f}")


# ---------------------------------------------------------------- 图标定义
def build_icons():
    I = {}

    # 1. clue 线索 —— 放大镜 + 镜内线索之"线"。轮廓：圆 + 斜柄
    I["clue"] = dict(
        color="cyan-400", cn="线索", sem="调查线索 / 可追查信息",
        sil="圆形镜片 + 右下斜柄",
        body="""
  <circle cx="10" cy="10" r="5.6"/>
  <path d="M14.1 13.9 L20.4 20.2"/>
  <path d="M7.3 10.7 c1.1 -2.1 2.1 -2.1 2.9 0 c0.8 2.1 1.8 2.1 2.9 0"/>""")

    # 2. record 记录 —— 折角纸页 + 横线。轮廓：竖长方 + 右上缺角
    I["record"] = dict(
        color="paper-300", cn="记录", sem="书库记录 / 日志条目",
        sil="竖长方形，右上折角",
        body="""
  <path d="M6 3.6 A1.6 1.6 0 0 1 7.6 2 H14 l4 4 v12.4 A1.6 1.6 0 0 1 16.4 20 H7.6
           A1.6 1.6 0 0 1 6 18.4 Z"/>
  <path d="M14 2 v4 h4"/>
  <path d="M8.8 10.4 h6.4"/>
  <path d="M8.8 13.4 h6.4"/>
  <path d="M8.8 16.4 h3.6"/>""")

    # 3. time 时间 —— 沙漏（刻意避开圆形钟面，与 clue/recover 拉开轮廓）
    I["time"] = dict(
        color="paper-300", cn="时间", sem="时段推进 / 行动耗时",
        sil="上下横杠 + 中间收腰沙漏",
        body="""
  <path d="M6.6 2.8 h10.8"/>
  <path d="M6.6 21.2 h10.8"/>
  <path d="M8.4 2.8 v3.1 c0 2.9 3.6 4.2 3.6 6.1 c0 -1.9 3.6 -3.2 3.6 -6.1 V2.8"/>
  <path d="M8.4 21.2 v-3.1 c0 -2.9 3.6 -4.2 3.6 -6.1 c0 1.9 3.6 3.2 3.6 6.1 v3.1"/>
  <path d="M9.9 19.6 c0.7 -1.6 3.5 -1.6 4.2 0 Z" fill="currentColor" stroke="none"/>""")

    # 4. stamina 体力 —— 火焰 + 内核。轮廓：水滴状火苗
    I["stamina"] = dict(
        color="gold-400", cn="体力", sem="行动力余量",
        sil="尖顶水滴火焰",
        body="""
  <path d="M12 2.4 C12 2.4 6.4 7.6 6.4 13.2 a5.6 5.6 0 0 0 11.2 0
           C17.6 9.4 14.6 6.4 12 2.4 Z"/>
  <path d="M12 19.6 a3.1 3.1 0 0 1 -3.1 -3.1 c0 -1.9 1.6 -3.2 3.1 -5.4
           c1.5 2.2 3.1 3.5 3.1 5.4 A3.1 3.1 0 0 1 12 19.6 Z"
        fill="currentColor" stroke="none" opacity="0.55"/>""")

    # 5. relationship 关系 —— 双节点连线。轮廓：两圆 + 斜连接
    I["relationship"] = dict(
        color="green-400", cn="关系", sem="人物关系度 / 信任",
        sil="左上右下两圆 + 斜连线",
        body="""
  <circle cx="8" cy="8.6" r="3.4"/>
  <circle cx="16" cy="15.4" r="3.4"/>
  <path d="M10.6 10.8 L13.4 13.2"/>""")

    # 6. tension 紧张 —— 两端立柱 + 被拉紧的弦。轮廓：H 形 + 下坠 V
    I["tension"] = dict(
        color="amber-500", cn="紧张", sem="紧张度 / 风险累积",
        sil="左右立柱 + 中间下坠的绷弦",
        body="""
  <path d="M3.6 5.4 v13.2"/>
  <path d="M20.4 5.4 v13.2"/>
  <path d="M3.6 9 L12 15.2 L20.4 9"/>
  <circle cx="12" cy="15.2" r="1.5" fill="currentColor" stroke="none"/>""")

    # 7. memory 记忆 —— 向内收束的螺线。轮廓：螺旋
    I["memory"] = dict(
        color="paper-300", cn="记忆", sem="已获记忆 / 可回溯片段",
        sil="单条向内收束螺旋",
        body="\n  <path d=\"" + spiral_path(12, 12, 1.2, 9.0, 1.75) + "\"/>" +
             "\n  <circle cx=\"12\" cy=\"12\" r=\"1.05\" fill=\"currentColor\" stroke=\"none\"/>")

    # 8. anomaly 异常 —— 菱形 + 内部裂缝。轮廓：正菱形
    I["anomaly"] = dict(
        color="violet-500", cn="异常", sem="北境异常 / 静默线征兆",
        sil="正菱形 + 内部折线裂缝",
        body="""
  <path d="M12 2.6 L21.4 12 L12 21.4 L2.6 12 Z"/>
  <path d="M12.4 6.6 L10.2 11.3 L13.8 12.7 L11.6 17.4"/>""")

    # 9. locked 锁定 —— 挂锁。轮廓：方体 + 上方 U 形锁梁
    I["locked"] = dict(
        color="rose-500", cn="锁定", sem="条件未满足 / 不可交互",
        sil="矩形锁体 + U 形锁梁",
        body="""
  <path d="M5.4 10.4 h13.2 a1.6 1.6 0 0 1 1.6 1.6 v7 a1.6 1.6 0 0 1 -1.6 1.6 H5.4
           A1.6 1.6 0 0 1 3.8 19 v-7 a1.6 1.6 0 0 1 1.6 -1.6 Z"/>
  <path d="M7.7 10.4 V7.3 a4.3 4.3 0 0 1 8.6 0 v3.1"/>
  <circle cx="12" cy="14.6" r="1.35" fill="currentColor" stroke="none"/>
  <path d="M12 15.9 v2.1"/>""")

    # 10. recover 恢复 —— 缺口圆 + 箭头。轮廓：开口环
    d, p0, p1 = arc_path(12, 12, 7.6, -55, 215)
    I["recover"] = dict(
        color="green-400", cn="恢复", sem="体力/状态回复",
        sil="右上缺口的圆环 + 箭头",
        body=f"""
  <path d="{d}"/>
  <path d="{arrow_head(p0[0], p0[1], -55 + 90, size=3.1)}"/>""")

    # 11. location 地点 —— 地图针。轮廓：倒水滴
    I["location"] = dict(
        color="cyan-400", cn="地点", sem="可前往地点 / 当前位置",
        sil="倒水滴地图针",
        body="""
  <path d="M12 21.4 s-6.9 -7.4 -6.9 -11.9 a6.9 6.9 0 1 1 13.8 0
           C18.9 14 12 21.4 12 21.4 Z"/>
  <circle cx="12" cy="9.5" r="2.6"/>""")

    # 12. schedule 日程 —— 日历 + 标记格。轮廓：横矩形 + 上方两耳
    I["schedule"] = dict(
        color="paper-300", cn="日程", sem="每日安排 / 活动排程",
        sil="横矩形 + 顶部双挂耳 + 实心标记格",
        body="""
  <path d="M4.6 5.4 h14.8 a1.6 1.6 0 0 1 1.6 1.6 v11.4 a1.6 1.6 0 0 1 -1.6 1.6 H4.6
           A1.6 1.6 0 0 1 3 18.4 V7 a1.6 1.6 0 0 1 1.6 -1.6 Z"/>
  <path d="M3 9.8 h18"/>
  <path d="M7.9 3 v4.2"/>
  <path d="M16.1 3 v4.2"/>
  <rect x="6.4" y="12.4" width="3.6" height="3.4" rx="0.8"
        fill="currentColor" stroke="none"/>
  <path d="M13 14.1 h4.6"/>""")

    return I


SVG_TMPL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
     fill="none" stroke="currentColor" stroke-width="{sw}"
     stroke-linecap="round" stroke-linejoin="round"
     role="img" aria-label="{cn}">
  <title>{name} / {cn}</title>{body}
</svg>
"""


def main():
    icons = build_icons()
    assert len(icons) == 12, f"应为 12 枚，实际 {len(icons)}"

    (OUT / "svg").mkdir(parents=True, exist_ok=True)
    for s in (24, 48, 96):
        (OUT / "png" / str(s)).mkdir(parents=True, exist_ok=True)

    # ---- 写 SVG（currentColor 版）
    for name, spec in icons.items():
        svg = SVG_TMPL.format(sw=SW, cn=spec["cn"], name=name, body=spec["body"])
        (OUT / "svg" / f"{name}.svg").write_text(svg, encoding="utf-8")

    # ---- 栅格化：把 currentColor 换成语义色后再渲染
    for name, spec in icons.items():
        hexcol = PALETTE[spec["color"]]
        colored = SVG_TMPL.format(sw=SW, cn=spec["cn"], name=name,
                                  body=spec["body"]).replace("currentColor", hexcol)
        tmp = OUT / f".__{name}.svg"
        tmp.write_text(colored, encoding="utf-8")
        for s in (24, 48, 96):
            subprocess.run([RSVG, "-w", str(s), "-h", str(s),
                            "-o", str(OUT / "png" / str(s) / f"{name}.png"), str(tmp)],
                           check=True)
        tmp.unlink()

    # ---- 导出元数据供 sheet 与 sidecar 使用
    meta = {n: {"cn": s["cn"], "color": s["color"], "hex": PALETTE[s["color"]],
                "sem": s["sem"], "sil": s["sil"]} for n, s in icons.items()}
    (OUT / "icons.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"生成完成：{len(icons)} 枚")
    for n, s in meta.items():
        print(f"  {n:<13} {s['cn']:<3} {s['hex']}  {s['sil']}")


if __name__ == "__main__":
    main()
