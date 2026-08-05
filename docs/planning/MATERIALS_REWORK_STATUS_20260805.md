# UW 素材返工交付状态（Follow-up to 2026-08-05 审查）

- 状态日期：2026-08-05 08:50（Asia/Shanghai）
- 对应审查：`/Users/lzm/Documents/Codex/2026-08-05/new-chat-2/outputs/UW_新增素材审查与宏观审查_2026-08-05.md`
- 工作区：`/Users/lzm/Desktop/UW`

## 已交付的返工

| request_id | 返工内容 | 路径 | 状态 |
|---|---|---|---|
| VIS-KA-001 | 重抽 6 张关键图（village/library/boundary × desktop/mobile），master 尺寸达标，无水印 | `inbox/visual/keyart/VIS-KA-001_{village,library,boundary}_{desktop,mobile}_v002.png` | approved-candidate |
| VIS-POR-001 | 重抽 6 张肖像（player/alice/eugeo × neutral/concerned），去 IP 化，无水印，1024² 透明 PNG；附 256 缩略图 | `inbox/visual/portraits/VIS-POR-001_{player,alice,eugeo}_{neutral,concerned}_v002{,_256}.png` | approved-candidate |
| AUD-AMB-001 | （审查文档漏检，v002 已存在）loudnorm 重校准至 -24.6 LUFS / TP -13.1 dBTP | `inbox/audio/ambience/v002/AUD-AMB-001_drizzle_village_{a,b}_v002.{wav,ogg,md}` | approved-candidate |

## 顺手做的项目级更新

| 项 | 改动 |
|---|---|
| `materials/tools/check_materials.py` | `_v001` master 校验改为 `_v\d+`，支持 v002+ 多版本 master sidecar |
| `materials/MANIFEST.csv` | 用 `MANIFEST_TEMPLATE.csv` 的 18 字段完整 schema 重建（asset_id / request_id / status / source_file / runtime_file / sha256 / creator / tool_model / created_at / license / source_url / attribution_required / attribution_text / approved_by / approved_at / integrated_at / replaces_asset_id / notes）；107 → 142 行 |
| MANIFEST 状态分类 | approved-candidate: 96 / approved-for-direction: 6 / changes_requested: 36 / received: 3 / review-only: 1 |
| `materials/inbox/visual/portraits/VIS-POR-001_*.md` | v002 sidecar 明确 v001→v002 变更（去 IP 化、补 concerned/tense 表情、移除水印） |

## 验证

- `python3 tools/check_materials.py materials` → **passed: 29 requests**
- v002 ambience 响度实测：I = -24.6 LUFS，TP = -13.1 dBTP（A）/ -12.4 dBTP（B），均落在目标区间 -26 ~ -22 LUFS 内
- v002 关键图尺寸：2560×1440（desktop）/ 1440×1920（mobile），master 达标
- v002 肖像：1024×1024 RGBA 透明，256 派生，文件命名 player / 数据保管员 Alice / 劳作者 Eugeo

## 仍未完成（不属于本次返工范围）

- REF-MOOD-001 暂停，参考包未交付
- QA-PLAY-001 缺 3 名真实首次玩家数据
- REF-FONT-001 字体许可证据 / 子集化方案
- Audio runtime integration（接入运行时、保留 WebAudio fallback 等）属项目运行时任务，materials 已就绪
- E2E 重跑需在 127.0.0.1:8765 可用环境下
- 桌面工作区仍有未提交候选改动，未打 tag

## 提交建议

按当前 MANIFEST 状态，下一步提交策略：

1. **可入 `approved/`**：
   - VIS-UI-001 全部（12 枚 + sheet + 3 档 PNG）
   - AUD-BGM-001 A + B（首屏/书库）
   - AUD-AMB-001 v002（注意：v002 仍在 `inbox/audio/ambience/v002/`，需整合进 `approved/`）
   - VIS-KA-001 v002（首屏主推荐 village，备选 library，异常态 boundary）
   - VIS-POR-001 v002（player / alice / eugeo × 2 表情）

2. **保留 `changes_requested` 不入**：
   - v001 关键图（direction_a/b/c × desktop/mobile）
   - v001 肖像（kirito / alice_warm / alice_neutral / eugeo × 2）
   - v001 ambience（v001 → v002 已替换）

3. **暂缓**：
   - writing 类：先在 agent/script 引用再转 approved
   - font：等许可证 + 哈希
   - research：mood/playtest 等数据回收
