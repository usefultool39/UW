# RESUME_NEXT —— 素材 v001 收尾断点

> 本文件是**暂停/续跑交接文档**。暂停时间：2026-08-04 23:27。明天从这里继续。

## 1. 总体状态：12 项需求，11 项已完成入库

| # | request_id | 状态 | 交付位置 | 备注 |
|---|---|---|---|---|
| 1 | REF-STYLE-001 | ✅ received | `inbox/visual/styleboards/` | 3 套方向板 + sidecar |
| 2 | VIS-KA-001 | ✅ received | `inbox/visual/keyart/` | 6 张开场关键图 + sidecar |
| 3 | VIS-POR-001 | ✅ received | `inbox/visual/portraits/` | 6 张肖像（1024 透明 + 256 缩略图）+ sidecar |
| 4 | VIS-UI-001 | ✅ received | `inbox/visual/ui_icons/` | 12 图标 × 3 尺寸 + sheet + sidecar |
| 5 | AUD-BGM-001 | ✅ received | `inbox/audio/bgm/` | 2 版循环（-18 LUFS，TP≤-1.6dBTP） |
| 6 | AUD-AMB-001 | ✅ received | `inbox/audio/ambience/` | 2 版循环（-18 LUFS） |
| 7 | NAR-VOICE-001 | ✅ received | `inbox/writing/character_voice/` | 38KB 声音圣经 |
| 8 | NAR-LORE-001 | ✅ received | `inbox/writing/lore/` | 24 条碎片 CSV + sidecar |
| 9 | NAR-BARK-001 | ✅ received | `inbox/writing/ambient_barks/` | 120 条短句 CSV + sidecar |
| 10 | REF-FONT-001 | ✅ received | `inbox/research/font_licenses/` | 5 套字体候选（许可证逐条核实） |
| 11 | **REF-MOOD-001** | ⏸ **暂停待续** | `inbox/research/moodboards/` | **见第 2 节** |
| 12 | QA-PLAY-001 | ⏸ requested | `inbox/research/playtest/` | 套件已就绪，**需 3 名真人玩家**回填 |

台账与校验：`REQUESTS.csv` 已更新（received）；`MANIFEST.csv` 已生成（107 行）；`tools/check_materials.py` **已通过（29 请求全绿）**。

---

## 2. ⏸ 待办一：REF-MOOD-001 参考包（唯一技术卡点）

### 2.1 为什么停在这里

后台代理执行此任务约 1.5 小时无产出。人工诊断确认：

- **Wikimedia Commons 在当前网络不可达**：`curl -m 8 https://commons.wikimedia.org/w/api.php` 返回 `000`（TLS 握手超时）。
- **LOC 也不可用**：`https://www.loc.gov/search/?q=thatched+roof&fo=json` 返回 `403`。
- 系统代理：`HTTP_PROXY=http://127.0.0.1:64333`（正常，百度 200）。

### 2.2 已验证可用方案：Met Open Access API（CC0 / 公共领域）

```
curl -s "https://collectionapi.metmuseum.org/public/collection/v1/search?q=thatched%20roof&hasImages=true"
  → {"total":11,"objectIDs":[690257,312581,437261,...]}
curl -s "https://collectionapi.metmuseum.org/public/collection/v1/objects/437261"
  → 字段：title / objectDate / artistDisplayName / medium / primaryImage
         / primaryImageSmall / objectURL / rightsAndReproduction / classification
```

- 许可：Met Open Access 全部为 **CC0（public domain）**，无署名义务（但项目要求仍记录来源）。
- 真实 URL 形态：`https://www.metmuseum.org/art/collection/search/{objectID}`（页面）
  和 `https://images.metmuseum.org/CRDImages/{path}`（原图）。

### 2.3 续跑步骤（明天直接执行）

1. 写采集脚本 `tools/fetch_moodboard_met.py`（标准库 urllib 即可，注意 `User-Agent` 头），
   14 个类别 → Met 搜索关键词映射：
   rain street / alpine village / thatched roof / cobblestone / wheat field /
   river landscape / illuminated manuscript / record book / candlelight interior /
   lapis lazuli / gold ornament / peasant costume / carpenter / forest fog。
2. 每类 search 取前 3-5 个 objectID，逐条拉 objects/{id}，过滤 `primaryImage` 非空。
3. 目标 30-60 条；CSV 列（沿用既有规范）：
   `ref_id,category,title,author,license,source_url,why_relevant`
   - license 统一写 `CC0`；source_url 用 objectURL。
4. 产出三个文件到 `inbox/research/moodboards/`：
   - `REF-MOOD-001_reference_pack_v001.md`
   - `REF-MOOD-001_reference_pack_v001.csv`
   - `REF-MOOD-001_reference_pack_v001.csv.md`（sidecar）
5. 抽样 `curl -m 8 -o /dev/null -w "%{http_code}"` 校验 5 条 URL 均 200，校验结果写入 md。
6. md 中写明：来源单一（Met，因 Wikimedia 不可达）、总条数、类别分布、
   覆盖不足类别、"仅参考不得拼贴复刻"声明、未能核实部分。
7. 完成后更新 `REQUESTS.csv` 中 REF-MOOD-001 状态为 received，重跑 `check_materials.py`。

### 2.4 遗留警告

- 之前启动的 moodboard 后台代理**可能仍在重试** Wikimedia（无 task id 可停止）。
  明日若发现 `inbox/research/moodboards/` 出现该代理的产出，**以本接管方案为准做人工比对**，不要直接采用其 Wikimedia URL（当前网络无法复现验证）。

---

## 3. ⏸ 待办二：QA-PLAY-001 真人试玩（无法代劳）

- 套件已就绪：`inbox/research/playtest/QA-PLAY-001_playtest_kit_v001.md`
  （开场脚本 / 同意书 / 观察记录表模板 / 访谈 5 问 / 录屏检查清单）。
- 需要 3 名未参与开发的人各自从"新游戏"开始实测，回填
  `QA-PLAY-001_player01.md` ~ `player03.md` + 录屏。
- 全部回填后：更新 REQUESTS 状态为 received，归档到 `inbox/research/playtest/`。

---

## 4. 交付物自查清单（明日续跑前可复验）

```bash
cd /Users/lzm/Desktop/UW/materials
/opt/miniconda3/bin/python3 tools/check_materials.py   # 期望：passed 29 requests
```

音频验收（已达标，可复验）：
```bash
cd inbox/audio
for f in bgm/*.wav ambience/*.wav; do ffprobe -v error -show_entries stream=sample_rate,bits_per_sample,channels "$f"; done
# 期望：48000 / 24 / 2（stereo）
```
