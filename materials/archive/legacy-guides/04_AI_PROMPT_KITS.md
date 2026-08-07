# AI 生成提示词套件

这些提示词用于快速得到“方向样张”，不是直接批准。生成后仍需按 sidecar、权利和技术规范走评审。若工具对中文理解不稳定，可使用英文版。**不要额外加入现成游戏、动画、艺术家姓名。**

## 通用负面约束（视觉）

```text
no text, no logo, no watermark, no trademark, no copyrighted character likeness,
no recognizable franchise costume, no UI screenshot, no modern vehicles, no firearms,
no cyberpunk neon, no gothic horror cathedral, no apocalyptic ruins, no photobashed game screenshot,
no illegible pathways, no extreme fog, no oversaturated candy colors, no excessive bloom,
no malformed hands, no duplicate limbs, no inconsistent perspective, no dirty transparency edges
```

中文补充：

```text
不要生成任何文字、按钮、地名、徽标、水印；不要复刻现成 IP 角色脸、服装、武器和徽章；
不要赛博霓虹、末日废墟、哥特恐怖、过曝光晕、浓雾遮路；不要让地图道路不可辨识。
```

---

## REF-STYLE-001 视觉方向板

### 方向 A：湿润田园 + 冷色异常

```text
Create an original visual direction board for a narrative action RPG set in a livable frontier village during light rain.
The player is a young apprentice recorder investigating an impossible northern record in a church library.
Show: an isometric hand-painted village thumbnail, warm wood and wet grass materials, a quiet church library,
a forest boundary where wind and birds suddenly stop, three original character silhouettes (recorder, cautious golden-haired female companion,
reliable blue-accented male companion), a dark translucent HUD sample, readable resource icons, sacred geometric light glyphs.
Mood: warm daily life invaded by a precise cold anomaly; hopeful but uneasy; clear navigation and strong gameplay readability.
Include a coherent color palette with muted natural greens, parchment cream, restrained gold, cyan clue light, amber tension, violet unknown.
Professional game art bible presentation, clean grid, no text labels inside the image, no existing franchise designs.
```

### 方向 B：记录员工作台 + 发光术式

```text
Original game visual development board combining a frontier village with a field recorder's notebook language.
Use parchment fibers, ink marks, brass measuring tools, thin luminous geometric spell lines, dark blue translucent panels,
and clean modern information hierarchy. The environment remains painterly and readable rather than becoming a literal card table.
Show small samples for village rain, library candlelight, silent forest anomaly, relationship feedback, resource decision chips,
and three original character silhouettes. Restrained, tactile, mysterious, practical, not steampunk, no text, no logos.
```

### 方向 C：低分彩绘角色 + 高清环境

```text
Original hybrid art direction board for a readable top-down narrative RPG:
soft low-resolution painted character sprites with strong silhouettes, detailed high-resolution village environments,
crisp UI icons, subtle sacred-art particles, warm rural materials contrasted with a cold silent boundary.
Show scale tests at 48 pixel character height, portrait samples, map readability, and HUD hierarchy.
Not cute chibi, not pixel-art parody, no existing franchise references, no text.
```

---

## VIS-KA-001 Day 1 开场关键图

### Desktop 2560×1440

```text
Original cinematic key art, 16:9, high-angle three-quarter view of a small frontier village in gentle morning rain.
A stone church with an attached library sits off-center as the visual focal point, with a restrained warm golden window
and a faint unnatural cool stillness beyond it toward the northern forest. Readable village roads connect a square, river,
wheat fields, wooden homes, a distant giant tree route, and a northern gate. The village feels inhabited, safe, and worth protecting,
while one subtle absence in the birds and rain suggests a hidden rule has been interrupted.
Hand-painted environment, natural wet materials, clear navigable paths, restrained fantasy, hopeful tension.
Reserve the left 45 percent as a dark low-detail safe area for title and objective UI.
No characters in foreground, no text, no logo, no watermark, no franchise architecture or symbols.
```

### Mobile 1440×1920

```text
Original vertical cinematic key art, 3:4, a frontier village under gentle rain viewed from a high three-quarter angle.
The upper half reveals the church library and the route toward the northern forest; the lower 45 percent transitions into dark wet riverbank,
soft vegetation, and low-detail rain for mobile title and objective UI. A restrained golden library light contrasts with a barely visible cold silent zone.
Readable roads, warm livable village, subtle mystery, hand-painted fantasy realism, no text, no logo, no copyrighted designs.
```

### 返工指令示例

- “把教会从画面正中移到右上三分线，给左侧标题更多低细节空间。”
- “降低全图雾量，只在北方树线制造运动停止感。”
- “村庄要更可居住：加入菜地、木檐排水和远处劳动痕迹，但不要增加人物大特写。”
- “减少紫色，异常用雨线中断和鸟群缺席表现。”

---

## VIS-POR-001 三核心肖像

### 共通前缀

```text
Original character portrait for a restrained frontier fantasy narrative RPG, half body, three-quarter view,
transparent background, consistent soft key light from upper left, readable at 128 pixels, practical rural clothing,
subtle sacred-art motifs, clean silhouette, painterly linework, mature but not photoreal, no existing franchise likeness.
```

### 玩家：见习记录员

```text
A young adult apprentice field recorder, quiet and observant, dark practical coat with muted cyan accents,
small notebook and compact marking tool, travel-worn but not heroic armor, slim mobile silhouette.
Expression variant A: neutral focused attention. Variant B: alert after noticing an impossible detail, controlled breathing, tense shoulders.
The design should communicate that observation and judgment are the character's strength.
```

### 爱丽丝

```text
A young adult female companion whose first instinct is to verify records and control risk.
Original wheat-gold hair design, practical pale protective clothing with restrained teal-blue details,
a marked record page or distance-measuring tool, stable triangular silhouette, capable and guarded.
Expression variant A: calm analytical scrutiny. Variant B: trust has been challenged; hurt is visible but contained behind a firm risk assessment.
Do not use ornate knight armor or recognizable existing costume designs.
```

### 尤吉欧

```text
A young adult male companion, gentle but decisive, original cool-blue and natural linen workwear,
training and village-labor practicality, soft vertical silhouette, reliable posture.
Expression variant A: warm steady support. Variant B: facing a silent boundary, visibly tense but choosing to stay and act.
No recognizable signature weapon or existing franchise clothing.
```

### 肖像负面提示

```text
no school uniform, no ornate anime armor, no crown, no giant sword, no recognizable franchise face,
no glossy plastic skin, no extreme beauty retouching, no chibi proportions, no cropped head, no inconsistent light,
no extra fingers, no fused accessories, no busy background
```

---

## VIS-UI-001 核心图标

```text
Design a coherent set of 12 original game UI icons: clue, record, time, stamina, relationship, tension,
memory, anomaly, locked, recovery, location, schedule.
Style: clean 1.75px-equivalent linework with small solid accents, inspired by practical field recording tools and thin sacred geometric light,
rounded corners without childish softness, readable at 24px, dark HUD compatible, no text.
Default cool gray-blue, focus gold, relationship cyan, tension amber-rose, anomaly restrained violet.
Each icon must remain distinguishable in monochrome and must not rely on color alone.
Deliver as a consistent grid on transparent background, no logo, no existing game icon copies.
```

返工重点：统一笔画；减少细小内部线；24px 测试；锁定/恢复不能只是同一图标换颜色。

---

## VIS-MAP-001 地图重绘

```text
Original 16:9 master map for a top-down narrative RPG, high-angle three-quarter hand-painted view of a small frontier village.
Clear walkable roads, river and bridge, central square, church library, hearth home, route to a giant tree worksite,
northern gate, fields, woods, and a subtle teleport structure. The map must function as navigation, not only illustration.
Keep character-scale ground areas visually quiet, maintain continuous roads at 50 percent scale, separate buildings by silhouette and roof color,
and reserve central gameplay space despite UI panels on left and right. Wet morning weather, natural materials, restrained fantasy.
No characters, no labels, no quest markers, no UI, no text, no copyrighted location layout.
```

---

## AUD-BGM-001 音乐生成描述

### 中文

```text
为一款叙事动作 RPG 生成 90 秒左右可无缝循环的“边境村庄清晨”配乐。
气质：细雨、木屋、一天记录工作的开始、温暖但克制；底层藏一处很轻的不稳定音程，暗示北境记录有问题。
配器：轻柔木质拨弦、稀疏木管、非常少的玻璃/钟音，避免史诗鼓、合唱、人声和强旋律占用注意力。
节奏稳定，不要每 8 小节大起伏；前 5–8 秒自然进入；循环点无点击、无尾响断裂。
适合长时间阅读 UI 和做资源决策，综合响度约 -18 LUFS，48kHz/24-bit WAV。
```

### English

```text
Create a seamless 90-second loop for a narrative action RPG's rainy frontier village morning.
Warm, restrained, orderly, like beginning a day of field recording; hide one subtle unstable interval suggesting that a northern record is wrong.
Instrumentation: soft wooden plucks, sparse woodwinds, very occasional glass or bell texture.
No vocals, choir, epic drums, trailer rises, or dominant melody. Stable density for reading UI and making resource decisions.
Natural entry within 5–8 seconds, seamless tail-to-head loop, approximately -18 LUFS, 48kHz/24-bit master.
```

---

## AUD-AMB-001 环境声生成/搜索说明

```text
Seamless stereo ambience, 120 seconds, a small rural frontier village in gentle morning drizzle.
Layers: rain on wooden eaves and wet grass, distant river, sparse birds, occasional far wooden door or work sound,
very subtle breeze, no intelligible speech, no modern traffic, no aircraft, no loud thunder.
The soundscape should feel alive enough that a later 'silent boundary' version can remove birds and wind for contrast.
No prominent event repeating more often than every 20 seconds. 48kHz/24-bit WAV, clean loop, ambience around -24 LUFS.
```

---

## NAR-VOICE-001 人物声音圣经生成提示

```text
请为《边境回声》的固定 NPC 与未来 AI 智能体共用系统写一份可执行人物声音圣经。
不要写泛泛人物小传。对每个角色必须输出：价值排序、最害怕的具体后果、面对未知时的默认动作、
Day 1/2/3 的语气变化、常用句长、常用动词、避免词、绝不会承诺的事、紧张时的身体/语言表现、
同一事实的 5 种角色化说法、玩家诱导其越权时的拒绝范例、scripted fallback 句。
世界事实和奖励仍由后端决定，NPC 不得自创资源、flag、地点或已经发生的事件。
角色重点：见习记录员重观察与选择；爱丽丝重记录完整与风险控制；尤吉欧温和但有行动/撤退判断。
```

---

## QA-PLAY-001 盲测主持词

开始前只说：

> “请从新游戏开始，像你自己下载到这个游戏一样玩。过程中我不会教你；你可以把想法说出来。卡住也没关系。”

结束后依次问：

1. 你认为今天最主要的目标是什么？
2. 你看到过哪一种行动代价？它会影响你怎么选？
3. 你获得过哪一种奖励或反馈？
4. 爱丽丝和尤吉欧分别更在意什么？
5. 你最想继续追查的悬念是什么？
6. 哪个按钮/卡片/文字你以为能做一件事，实际却不是？
7. 如果只能改一个地方，你会改什么？

记录员不要评价答案；只追问“你在哪看到的？”和“当时你以为会发生什么？”。
