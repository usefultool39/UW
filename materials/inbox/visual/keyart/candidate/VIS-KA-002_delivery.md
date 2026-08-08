# VIS-KA-002 抓捕终点关键图上色候选

- request_id: VIS-KA-002
- status: sample_candidate
- created_at: 2026-08-08
- creator/source: Mavis image synthesis (colorize from BW reference) + local Pillow resize
- intended_use: N10 抓捕终点事件面板(桌面 + 移动);不直接接入 runtime
- license: project-original
- runtime: prohibited

## 文件

- `VIS-KA-002_capture_desktop_color.png` — 2560x1440 RGB,16:9。
- `VIS-KA-002_capture_mobile_color.png` — 1440x1920 RGB,3:4。
- `VIS-KA-002_preview_combined.png` — 1440x810 desktop + 360x480 mobile 并排元信息图。

## 与 current 黑白版的差异

- current `VIS-KA-002_capture_desktop_bw.png` 和 `VIS-KA-002_capture_mobile_bw.png` 是通过的黑白构图。
- candidate 在保持原图人物关系、姿势、构图、事件顺序的基础上加颜色。
- **人物关系完全保留**:父亲+爱丽丝+桐人+尤吉欧四人组 + 整合骑士+2 随从三人组,叙事顺序"宣罪→告别→带走"。

## 颜色方向(已落实)

- **村庄环境**:雨后晨光、暖灰、湿石板、柔和木色;教会书库为灰白石墙,茅草屋顶暖黄。
- **爱丽丝**:暖金长发(明确非银白非灰白),金背心 + 白衬衫 + 蓝带,识别色金白蓝。✓
- **桐人**:深墨黑发,冷蓝灰上衣。✓
- **尤吉欧**:浅金色短发,明显天蓝色 tunic(和爱丽丝金白蓝区分)。✓
- **整合骑士**:冷银盔甲 + 深蓝披风,披风下摆有破损,持展开的卷轴。✓
- **2 随从**:冷钢灰盔甲,完整头盔。✓
- **父亲**:朴素棕色亚麻工作服,白须。✓
- 画面无浓重血腥、无过度黑暗、无纯黑背景。

## 桌面版细节

- 2560x1440 16:9。
- 整合骑士在右半主导(展开卷轴宣罪),父亲+爱丽丝+桐人+尤吉欧在左半。
- **lower-left 对白安全区**:左下角地面是空地,无人物遮挡,可放对白文字。
- 右侧随从 2 人完整可见,没有被裁切。

## 移动版细节

- 1440x1920 3:4。
- 上下双构图:上半父亲拥抱爱丽丝 + 桐人尤吉欧 + 骑士 2 随从;下半留白(芦苇+石头),为 lower-third 按钮和对白安全区。
- 人物下半身有控制性裁切(桐人尤吉欧露出上半身,父亲和爱丽丝大半可见),关键动作(父亲握手于爱丽丝肩、爱丽丝抬头看骑士)可读。

## 验收对照(按 T03 验收标准)

- [x] 黑白版人物关系完整保留。
- [x] 三段事件顺序(宣罪→告别→带走)无需长文字说明也能理解。
- [x] 爱丽丝、桐人、尤吉欧的识别色正确。
- [x] 桌面和移动端安全区可用。
- [x] 没有水印、文字、Logo、现代物件或科幻化误读。
- [x] 颜色与已通过的村庄关键图、人物肖像处于同一光照方向和色温(雨后晨光、暖灰湿石板、柔和木色)。

## 已知问题

- **雨丝效果**:画面有细密雨丝,营造"雨后晨光"氛围,可能偏重(取决于人工验收偏好)。
- **整合骑士发色偏浅金**:原黑白图骑士发色是浅色,候选保持一致。如需"铁灰/银发"可再调。
- **mobile 上下构图**:mobile 黑白原图本身是双构图(上半主体+下半留白),候选严格保留此构图。

## SHA256

- VIS-KA-002_capture_desktop_color.png: `1cad5d2e3b55458f15af6c02ad380bc8d346297dfd8802c648750842bff97ded`
- VIS-KA-002_capture_mobile_color.png: `b408313063ad21114f60b6945027ec5bf59c5f97ed0d3a5aa3f01d5e09bcf31c`
- VIS-KA-002_preview_combined.png: `c0db75a6f6dd67dfed84a49d50dcc08b1bede4d47c0a2ee7abddcaf2d5e0c3b8`
