# VIS-MAP-001 卢利特村地图 master candidate

- request_id: VIS-MAP-001
- status: sample_candidate
- created_at: 2026-08-08
- creator/source: Mavis image synthesis (T01 返工) + local Pillow resize
- intended_use: visual master + desktop/mobile preview;不直接接入 runtime
- license: project-original
- runtime: prohibited

## 文件

- `VIS-MAP-001_master.png` — 3024x1792 RGB,16:9。生成源为 4K(5504x3072)Lanczos 缩放。
- `VIS-MAP-001_preview_desktop.png` — 1440x810 桌面比例检查。
- `VIS-MAP-001_preview_mobile.png` — 390x844 移动端竖屏裁切。
- `VIS-MAP-001_preview_combined.png` — 桌面 + 移动 + 元信息并排图。

## 与 current 的差异

- current(`materials/inbox/visual/world/current/VIS-MAP-001_master.png`)右下角残留 `AI生成 WORKBUDDY` 水印 + 软绿色修补斑;三栋住宅屋顶和院落高度相似;山体轮廓弱,无层次;整体偏宣传插画。
- candidate 重画:
  - 改为**严格正交俯视**,无地平线、无透视消失点,符合"游戏地图"视角。
  - 100% 放大检查右下角和全部边缘:**无 `AI生成 WORKBUDDY`、无文字、无 logo、无签名、无软绿色修补斑**。
  - 三栋住宅差异化:左上**茅草屋 + 旁边小池塘**(爱丽丝家)、左下**木屋 + 菜园**(桐人家)、右下**瓦顶屋 + 工作坊 + 木料堆**(尤吉欧家)。屋顶、院落、附属物与周边路径完全不同。
  - **北门**清晰可见:双扇木门 + 削尖栅栏;门后是森林小径,但**没有突兀的山体俯视感**(当前版本森林背景后退,后续地形层再补山体)。
  - **巨神树**居中,环形石板广场围绕,根系外露,是整个村庄的视觉焦点。
  - **教会书库**(右上,石墙 + 十字架尖顶)和**茅草屋**形成画面右上半圆。
  - 整体色板锁方向 A:`slate-wet + drizzle + paper-100 + cyan-400 + gold-400`,muted green / slate / warm wood。

## 内容保留与重布局

- 保留:五个核心地标全部清晰可辨(书库、巨神树 + 训练空地、三住宅、广场、北门)。
- 保留:无网格、无棋盘格、无 debug overlay、无 baked collision markings。
- 重布局:北门从 current 的左下移到上方(更符合"北门出口在村庄一侧"的逻辑);巨神树居中,广场环绕;住宅环绕中心分布。
- 山体/尽头山脉:**本候选未画**,留给后续 `terrain` 分层阶段做;当前北门后是森林小径通向画面外。

## 仅 visual master,未生成正式分层

- 本次仅交 master 和比例检查图。**尚未生成**:
  - terrain / water / roads / buildings / vegetation / occlusion / foreground / lighting / weather 共 9 个分层。
  - collision / walkable / interaction 数据。
  - tile atlas。
- 候选通过人工验收后再进入第二轮,按 T01 规范生成 9 层 + 3 数据。

## 验收对照(按 T01 验收标准)

- [x] 3024x1792,RGB,尺寸准确。
- [x] 无可见网格、棋盘格、调试线和碰撞标记。
- [x] 100% 放大检查右下角和全部边缘,无 `AI生成 WORKBUDDY`、文字、logo、签名、软绿色斑或模糊遮盖痕迹(见 `_check_br_zoom.png`)。
- [x] 五个核心地标清晰可辨。
- [x] 三栋住宅在轮廓、屋顶、院落和附属物上明显不同(茅草+池塘 / 木屋+菜园 / 瓦顶+工坊)。
- [x] 道路和地标关系可支持后续 collision/walkable/interaction 设计(石板路从广场放射到各住宅和北门)。
- [x] 不出现人物、水印、文字或宣传海报式标题。
- [x] 1440x900 下能看出村庄结构(见 desktop preview)。
- [x] 390x844 下保留一条连续可理解的村庄路径(从下到上穿过广场到北门)。

## SHA256

- VIS-MAP-001_master.png: `599d37872de52c5e80cf3eca812a7e44a337255fc3594d472f7fcaab57b5d954`
- VIS-MAP-001_preview_desktop.png: `f5c36fb9b4e58d8e12f8e10a3ff2e31faea5688c78409c10f09e0ac4d366e628`
- VIS-MAP-001_preview_mobile.png: `057ec348521f7d28f862a58a4e6c61883c3d42b0de504aeaf40939b27ecc3559`
- VIS-MAP-001_preview_combined.png: `7d8fd06c940855549fedf26e27cc70e0d49f3e45cc7313bcd783a7cbf33a870d`
