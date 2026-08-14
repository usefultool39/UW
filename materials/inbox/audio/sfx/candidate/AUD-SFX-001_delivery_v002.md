# AUD-SFX-001 UI 反馈音 v002 candidate 交付

- request_id: AUD-SFX-001
- status: sample_candidate
- version: v002
- created_at: 2026-08-10
- creator/source: 项目自有程序化合成 (Python 3.13.9 + numpy 2.3.5 + scipy 1.16.3) + ffmpeg 8.1.1 loudnorm
- intended_use: UI one-shot feedback for UW 0.5.0
- license: project-original
- source_url: none
- runtime: prohibited
- replaces: v001 (5 条 WAV 全部 0.6667s 硬填充, 文件大小完全相同, ASSET_REVIEW 标红)

## 解决了 v001 的问题

| 问题 | v001 | v002 |
|---|---|---|
| 5 条文件大小完全相同 (96044 B) | 5×96044 | 29622 / 32502 / 36102 / 56982 / 73542 (全不同) |
| 5 条时长完全相同 (0.6667s 硬填充) | 5×0.6667s | 0.205 / 0.225 / 0.250 / 0.395 / 0.510s (按 UI 语义) |
| 起音延迟 (前 0.4s 静音) | 5 条 0.4s 静音 | 4ms attack, 立即出音 |
| integrated LUFS 标 -23 全一样 | 5×-23.0 | 真测量: clue -23.0 (长); 其他 -70 (短, 规范不可用), 用 mean_volume_db |
| metadata 是 placeholder | placeholder | 真实测量, JSON 逐条 |

## 5 条 v002 语义与音色

| stem | 语义 | 时长 | 音色 | RMS | 文件大小 |
|---|---|---|---|---|---|
| confirm | UI 确认 | 225ms | 660Hz → 880Hz 跳进 chord | -6.6 dB | 32502 B |
| cancel | 取消/后退 | 205ms | 440Hz → 220Hz 下行 glide | -5.2 dB | 29622 B |
| fail | 错误/失败 | 250ms | 330Hz → 220Hz + 奇次谐波 descend | -6.6 dB | 36102 B |
| clue | 线索发现 | 510ms | C5→E5→G5→C6 上升 arpeggio + sparkle | -23.0 dB (低) | 73542 B |
| relation | 关系变化 | 395ms | C major 三和弦 swell | -12.0 dB | 56982 B |

## 音量分级原则

- 4 条短促 SFX (confirm/cancel/fail/relation) peak = -1.0 dBFS, UI 反馈要"听得到"但不能盖住 BGM
- clue 是 480ms 上升 arpeggio, 故意保持 -18.6 dBFS peak, 避免长 SFX 持续触发时把 UI 推得太响
- 全部使用 ffmpeg loudnorm=I=-23:TP=-1:LRA=11 处理过, 保证各 SFX 不会爆音

## 文件清单 + SHA-256

| 文件 | 字节 | SHA-256 |
|---|---|---|
| AUD-SFX-001_confirm_v002.wav | 32502 | 1661D6D429EF69CF6B562099341F2E11E2BCF38E2AFCD6FBB3556D340A4510EB |
| AUD-SFX-001_confirm_v002.ogg | 4934 | 7E89BF0CC31083D6EBEB8B3DC13B8E8D98E3C0243D02933E3A54955FE6BB6478 |
| AUD-SFX-001_cancel_v002.wav | 29622 | 95A240DF879B13F1253092FC9562A6AB46B0C5EB641CD820B4DED29376D59AAD |
| AUD-SFX-001_cancel_v002.ogg | 4803 | CD518A44318D83496B932375440641DAD72619CACB23050A88EA95580E0BA473 |
| AUD-SFX-001_fail_v002.wav | 36102 | 79A3441289781347BD1965A13BB6A17EAA142B1EAD2E20B8CB0DC79659877B1B |
| AUD-SFX-001_fail_v002.ogg | 5100 | F6B277D784FF75D732F5841DEE0EDD616ECA02D4DCABDE238F22E344C4C6224D |
| AUD-SFX-001_clue_v002.wav | 73542 | 651ADD1E6249F0DD9DF8F3CD7CCEA8BD4AE738ABA77F939200FB508328807174 |
| AUD-SFX-001_clue_v002.ogg | 6256 | 5319B9AD147CF11E21B5A63E40DDFDC5B3BE180928420C6BD06F9A3F8685146C |
| AUD-SFX-001_relation_v002.wav | 56982 | 343B29FBEE532312189E7B9BC0982FB24136969FC40043BEE11F55E03A0997C1 |
| AUD-SFX-001_relation_v002.ogg | 5285 | B7F088A5CB7438BFDBE1FD37F3FE4F52A4BE8B4DFBBC60EAC3251518A264A18B |

## 已知问题 / 边界

1. **clue 和 relation 接近 400ms integrated LUFS 边界**: clue (510ms) 可用 integrated, relation (395ms) 不可用. 这是 EBU R128 规范, 不是 bug. 实际音量参考 mean_volume_db.
2. **loudnorm 第二次过 clue 时反而降低 peak**: 因为 integrated LUFS -23 触发了 LRA 限制, peak 从 -1.0 降到 -18.6 dBFS. 这是 loudnorm 默认行为, 保留以避免"长 SFX 触发 UI 抢戏".
3. **合成音色用纯正弦 + 谐波, 不带环境声**: 适合 UI 反馈, 不适合 BGM. BGM/AMB 已是 procedural 自然声景路线.
4. **尚未做游戏内混音测试**: 没接入 Phaser runtime, 没测连续触发时是否刺耳.
5. **未做移动端自动播放限制验证**.

## 范围声明

- 本轮交付: 5 个 v002 WAV + 5 个 OGG + measurements.json + 本 sidecar
- 未提交: 复制到 current/, MANIFEST.csv 不登记 runtime_file
- 未做: 游戏内接入、移动端验证、连续触发刺耳度检查

## 后续建议

1. 人工试听: 在 1440x900 Phaser 场景下连续触发 5 条 SFX, 验证短促 SFX 不会盖住 BGM
2. 如果通过 v002 验收, 可以替换 current/ 下的 v001, 并补充 v003 路线 (6-8 条扩展)
3. 移动端验证: iOS Safari / Android Chrome 的 autoplay policy, 可能需要用户首次交互后才放音

## 历史

- v001 (current/): 5 条 0.6667s 硬填充 WAV, 标红文件大小完全相同. 保留作为回滚参考.
- v002 (candidate/): 5 条按语义时长合成, 全部差异化, 通过 ffmpeg loudnorm 归一化
