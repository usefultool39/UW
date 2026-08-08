# 卢利特村地图当前候选

- request_id: VIS-MAP-001
- status: sample_candidate
- created_at: 2026-08-08
- creator/source: ImageGen + local Pillow postprocess
- intended_use: visual map master for UW 0.5.0
- license: project-original
- source_url: none
- runtime: prohibited

## 当前文件

- `VIS-MAP-001_master.png`：3024x1792 RGB 地图 master。
- `VIS-MAP-001_preview_desktop.png`：1440x900 桌面预览。
- `VIS-MAP-001_preview_mobile.png`：390x844 移动预览。
- `VIS-MAP-001_postprocess_summary.json`：尺寸和 hash 记录。

## 已确认

- 明显网格已经移除。
- 北门、巨神树、教会书库、村广场和三人住处可以辨认。
- 道路、水域、建筑和植被已经形成可继续拆层的视觉关系。

## 未通过

- 右下角仍有 AI 水印和软绿色修补残留。
- 三栋住宅相似，北门后的山体层级较弱。
- 当前只是视觉 master，没有正式 terrain、water、roads、buildings、vegetation、collision、walkable 或 interaction 数据。

在水印、地标区分和正式分层完成前，不得进入 runtime。
