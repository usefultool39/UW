# VIS-UI-002 完整 32 枚图标集 v001 交付

- request_id: VIS-UI-002
- status: sample_candidate
- version: v001
- created_at: 2026-08-10
- creator/source: SVG vector (12 枚 core 沿用 VIS-UI-001) + Pillow 几何画 (20 枚 expanded 新增)
- intended_use: 32 枚完整 UI 图标集, 24/48/96px 三种尺寸
- license: project-original
- runtime: prohibited

## 解决了 deferred 状态的问题

- REQUESTS 标 deferred 是因为"样张批准后". 本轮把 12 枚 core (VIS-UI-001) 批准态保持, 新增 20 枚 expanded, 总数到 32 枚
- 提供 SVG vector 源 + PNG 三种尺寸
- 提供统一 meta.json 含识别色 (cyan-400/green-400/amber-500/gold-400/rose-500/violet-500/paper-300/amber-700)

## 32 枚清单 (12 core + 20 expanded)

### 12 枚 core (来自 VIS-UI-001 v001, 完整保留)
- anomaly (异常, violet-500), clue (线索, cyan-400), location (地点, cyan-400), locked (锁定, rose-500)
- memory (记忆, paper-300), record (记录, paper-300), recover (恢复, green-400), relationship (关系, green-400)
- schedule (日程, paper-300), stamina (体力, gold-400), tension (紧张, amber-500), time (时间, paper-300)

### 20 枚 expanded (本轮新增, 分类如下)
- **物品/资源 (5)**: herb (草药, green-400), wood (木材, amber-700), fish (鱼, cyan-400), meal (餐食, gold-400), water (水, cyan-400)
- **活动/小游戏 (4)**: cook (烹饪, amber-500), fish_action (钓鱼, cyan-400), gather (采集, green-400), forage (觅食, amber-700)
- **关系/角色 (4)**: bond (羁绊, rose-500), farewell (告别, paper-300), capture (抓捕, violet-500), prayer (祈祷, gold-400)
- **收集/成就 (3)**: stele (石碑, paper-300), notice (公告, amber-500), codex (图鉴, violet-500)
- **状态/系统 (4)**: save (存档, green-400), quest (任务, amber-500), map_icon (地图, cyan-400), altar (祭坛, violet-500)

## 文件结构

```
VIS-UI-002_expanded_icons_v001/
├── icons.meta.json (32 枚含 cn/color/hex/sem/sil)
├── svg/ (32 SVG, vector 源)
├── png/24/  (32 PNG @ 24px)
├── png/48/  (32 PNG @ 48px)
└── png/96/  (32 PNG @ 96px)
```

总计: 1 meta + 32 svg + 96 png = 129 文件

## 与 VIS-UI-001 的关系

- 12 枚 core 完全沿用 VIS-UI-001 的 SVG 源 (验证: `get-childitem` 显示 12 svg)
- 20 枚 expanded 新增, SVG 风格与 core 统一 (24x24 viewBox, stroke 1.5, currentColor, round cap/join)
- 20 枚 expanded 的 PNG 是用 Pillow 几何画的, 不是从 SVG 转的 (因为本机无 cairo/SVG 转 PNG 工具)
- 视觉效果: SVG 简洁线稿, PNG 是几何实心形, 风格有差异但都识别得出

## 已知问题

1. **PNG 渲染方式差异**: core 12 枚用 SVG 渲染器 (Inkscape/cairosvg 之类), expanded 20 枚用 Pillow 几何画. 视觉风格不同: 12 枚偏线稿, 20 枚偏实心.
2. **未做 24/48/96 全尺寸 sprite sheet 拼合**: 本轮只单独导出 PNG, 未做 sheet 排版
3. **未做游戏内 in-context 截图**: 需要工程接入后看实际使用效果
4. **未做 12 枚 + 20 枚 风格统一**: 可在 v002 路线里把 core 12 枚也用 Pillow 重画, 保持视觉一致

## 范围声明

- 本轮交付: 32 SVG + 96 PNG + 1 meta
- 未提交: 复制到 runtime/, MANIFEST.csv 不登记 runtime_file
- 未做: 12/20 风格统一, sprite sheet 拼合, 移动端自动播放测试

## 后续建议

1. **风格统一** (VIS-UI-002-B): 用 Pillow 重新画 12 枚 core 匹配 20 枚 expanded 的实心风格
2. **批量 sprite sheet 拼合**: 用 Pillow 把 32 枚 96px 拼成 4 张 8x4 网格 sheet (用于引擎快速加载)
3. **运行入库**: 把 12 枚 core 直接合并到 runtime/icons/, 走 MANIFEST.csv 流程
