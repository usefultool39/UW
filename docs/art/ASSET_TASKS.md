# UW 下一批视觉素材任务单

这份文件可以直接交给已经加载 `docs/art/GENERATION_AGENT_PROMPT.md` 的生图智能体。

执行原则：按任务编号顺序执行；每个任务先交样张，等待人工验收后再批量扩展。除非项目负责人明确批准，所有新文件状态都必须保持 `sample_candidate`，不得写入 runtime，不得声称 `approved` 或 `integrated`。

当前优先级：

1. `VIS-MAP-001` 当前地图 master 返工和代表性切片。
2. `VIS-CHR-001/002/003` 三位核心角色 down 基线返工。
3. `VIS-KA-002` 抓捕终点上色版。
4. `VIS-VFX-001` 透明度和静默线语义修复。

不在本轮交给生图智能体的工作：BGM/SFX 人耳 QA、Phaser runtime 接入、manifest 正式登记、真人盲测。这些需要工程或人工验收在素材确认后处理。

---

## T01：卢利特村地图 master 返工

### 任务输入

```text
任务类型：世界地图 / 可走地图 / 地图 master 重绘
项目：UW 0.5.0 卢利特村序章
request_id：VIS-MAP-001
任务名称：卢利特村地图 master 修复样张
用途：可走地图的视觉 master；先做代表性地图样张，不直接接入 runtime
参考文件：
- materials/inbox/visual/world/current/VIS-MAP-001_master.png
- materials/inbox/visual/world/current/VIS-MAP-001_preview_desktop.png
- materials/inbox/visual/world/current/VIS-MAP-001_preview_mobile.png
- materials/inbox/visual/world/current/VIS-MAP-001_delivery.md
```

### 生成目标

以当前地图为直接内容基线，生成一张 3024x1792 的卢利特村地图候选。保留已经可辨认的五个核心地标和无明显网格的优点，必须真正消除右下角 `AI生成 WORKBUDDY` 水印、软绿色修补斑和任何可追溯文字残留；不能用模糊、涂抹、裁切或同色块遮盖伪装移除。

地图应使用正交或轻俯视的游戏地图视角，不要画透视地平线，不要画成宣传插画，不要使用单点透视。玩家看到的是一个可以继续拆分为 tile 和图层的村庄空间。

画面必须能一眼识别：

- 教会书库。
- 巨神树及其训练/活动空地。
- 桐人、尤吉欧、爱丽丝三人的住处或家庭区域。
- 村广场和主要村道。
- 北门及通往森林/尽头山脉的出口。
- 水域、道路、建筑、植被和可辨认的生活设施。

地标不能平均铺满画面。村庄中心、教会书库、巨神树和北门应有明显视觉层级。三栋主要住宅必须有不同的屋顶、院落、附属物和周边路径，不能像复制粘贴；北门后的山体和森林出口必须有清晰但不抢眼的层次。

### 正向提示词要求

```text
original hand-painted game world map of a small rural village in Underworld, orthographic or very light top-down three-quarter view, no horizon, no perspective vanishing point, clear readable village landmarks, church library, giant sacred tree clearing, three children's village homes, central square, northern gate leading to forest and distant mountain path, compact stone and dirt roads, small streams and water edges, wooden village houses, subtle fences, vegetable plots, work yards, restrained vegetation clusters, coherent spatial logic, readable player navigation, rain-washed morning atmosphere, soft overcast warm daylight, muted green blue slate and warm wood palette, clean layer-friendly shapes, clear silhouettes, consistent scale, game map composition, original design, no visible grid, no tile lines, no checkerboard, no debug overlay, no baked collision markings, no text, no labels, no watermark
```

### 负向提示词

```text
visible grid, square grid, tile lines, checkerboard, graph paper, debug overlay, collision overlay, walkable overlay, labels, text, map legend, UI, compass, watermark, logo, signature, perspective horizon, dramatic cinematic perspective, aerial satellite view, duplicated houses, repeated trees, random roads, disconnected buildings, floating objects, geometric placeholder blocks, flat colored rectangles, blurry low detail, excessive fog, dark unreadable shadows, baked character shadows, franchise screenshot, copied anime background
```

### 输出文件

先只交以下文件，不批量生产全部层：

- `materials/inbox/visual/world/candidate/VIS-MAP-001_master.png`，3024x1792，RGB。
- `materials/inbox/visual/world/candidate/VIS-MAP-001_preview_desktop.png`，用于桌面游戏内比例检查。
- `materials/inbox/visual/world/candidate/VIS-MAP-001_preview_mobile.png`，用于移动端裁切检查。
- `materials/inbox/visual/world/candidate/VIS-MAP-001_delivery.md`。

交付说明必须写明：

- candidate 与 current 的逐项差异。
- 网格线、水印、文字、logo、签名和软绿色修补斑已经通过全尺寸视觉检查确认不存在。
- 哪些地标保留，哪些地标重新布局。
- 哪些内容只是视觉 master，尚未生成正式 terrain/water/roads 等层。
- 当前不得进入 runtime。

### 验收标准

- [ ] 3024x1792，RGB，尺寸准确。
- [ ] 无可见网格、棋盘格、调试线和碰撞标记。
- [ ] 100% 放大检查右下角和全部边缘，不存在 `AI生成 WORKBUDDY`、文字、logo、签名、软绿色斑或模糊遮盖痕迹。
- [ ] 五个核心地标清晰可辨：书库、巨神树、住处、广场、北门。
- [ ] 三栋住宅在轮廓、屋顶、院落和附属物上明显不同，北门后的山体/森林出口层次清楚。
- [ ] 道路和地标关系可支持后续 collision/walkable/interaction 设计。
- [ ] 不出现人物、水印、文字或宣传海报式标题。
- [ ] 1440x900 下仍能看出村庄结构。
- [ ] 390x844 下至少有一条连续可理解的村庄路径，不把关键地标全部裁掉。
- [ ] 如果模型无法稳定生成地图结构，停止扩展并标记 `changes_requested`，不要生成大量分层图。

### 通过后的下一步

只有 T01 通过后，才继续生成：

- terrain layer。
- water layer。
- roads layer。
- buildings layer。
- vegetation layer。
- occlusion/foreground/lighting/weather alpha layers。
- collision、walkable、interaction 数据和 tile atlas。

---

## T02：三位核心角色 sprite 基线返工

### 任务输入

```text
任务类型：角色 sprite / 动画帧 / 三人风格基线
项目：UW 0.5.0 卢利特村序章
request_id：VIS-CHR-001、VIS-CHR-002、VIS-CHR-003
任务名称：三位核心角色 down 方向 sprite 修复基线
用途：先验收一个方向和三个核心角色，禁止直接批量生成四方向全套
参考文件：
- materials/inbox/visual/characters/current/VIS-CHR-001_sprite_sheet_down.png
- materials/inbox/visual/characters/current/VIS-CHR-002_sprite_sheet_down.png
- materials/inbox/visual/characters/current/VIS-CHR-003_sprite_sheet_down.png
- materials/inbox/visual/characters/current/VIS-CHR-001_002_003_delivery.md
- materials/inbox/visual/characters/current/VIS-CHR-001_002_003_frame_metadata.json
- frontend/public/assets/runtime/portraits/（当前已批准的三人肖像）
```

### 生成目标

以 current 为身份和色彩参考，重新生成桐人、爱丽丝、尤吉欧三人的 `down` 方向候选。不能把当前帧直接重新拼接或只修改 metadata；每人一个 768x96 的横向 sheet，包含 12 帧：

- idle：2 帧。
- walk：6 帧。
- interact：4 帧。

所有帧 cell 为 64x96，RGBA 透明背景，逻辑脚底锚点为 `(32,94)`。锚点只是 metadata 坐标，不得烘焙成像素；每个 cell 的 `(32,94)` alpha 必须为 0，角色脚底视觉基线稳定在其上方。三人的整体身高、头身比、脚底位置、落地阴影策略、服装层次、线条密度和光照必须统一。

不要先追求细节。第一目标是证明三个人放在同一张地图上时看起来属于同一个游戏，而不是三个不同模型生成的角色。

### 角色识别约束

桐人：

- 深墨黑发。
- 冷蓝识别色。
- 卢利特村男孩的简洁工作服。
- down 方向必须能看出背部服装和头发轮廓。
- interact 动作优先做阅读记录、查看记录册或谨慎伸手。

爱丽丝：

- 暖金色头发，不要银白或灰白。
- 金白蓝识别色。
- 村中劳作/送餐/施救感的服装和道具。
- interact 动作优先做递物、送餐或施救前伸手。

尤吉欧：

- 浅金色头发。
- 明显天蓝色服装识别色，不要和爱丽丝混成同一套颜色。
- 木工/伐木劳动者的服装轮廓。
- interact 动作优先做伐木准备、递工具或查看边界。

### 正向提示词要求

```text
original hand-painted 2D game character sprite, three consistent rural village children and young workers, unified 3.5-head-tall proportion, clean readable silhouette, stable costume design, stable hair silhouette, restrained painterly ink line, soft rain-washed morning light, grounded feet, subtle contact shadow only if it can be separated cleanly, consistent 64x96 sprite cell, front-facing down direction, full body visible, no crop, no perspective distortion, no dramatic pose, transparent background, each animation frame has a clearly different readable pose
```

为每个角色分别追加身份、发色、识别色、服装和动作，不要把三个人写成“同一个模板换颜色”。

### 动作要求

idle 2 帧：

- 只做轻微呼吸、衣摆或重心变化。
- 头部和脚底必须稳定。

walk 6 帧：

- 至少有两帧明确跨步。
- 手臂和腿的相位有变化。
- 不要把六帧做成六张站立图。
- 不要让角色上下漂浮。

interact 4 帧：

- 帧 0：准备动作。
- 帧 1：伸手/举工具/靠近物体。
- 帧 2：动作峰值。
- 帧 3：收回或完成动作。
- 三人的 interact 必须有不同功能轮廓。

### 透明度和后处理硬要求

- 禁止白底、灰底、棋盘格和纯色背景。
- 禁止脚下白色光晕、背景反射和大块半透明矩形。
- 不能直接沿用 current 的半透明边缘、水印残留或锚点 alpha 问题。
- 必须检查每个 cell 四角、角色外接矩形外缘和脚底区域。
- 必须逐帧记录 `(32,94)` alpha；36 帧全部为 0 才能提交。
- Alice 的 `walk_2` 必须与相邻步态保持合理非透明像素量和身体完整度，不得再次出现明显缺失。
- 同一角色必须先锁定统一 base reference、发型、服装、身高和道具，再派生动作；禁止 12 帧各自独立生成导致比例、脸型、衣服或道具跳变。
- 如果只能通过明显锯齿抠图才能去除背景，返回 `changes_requested`，重新生成，不要牺牲角色轮廓。

### 输出文件

使用独立 `candidate/` 目录保存，不覆盖 `current/`：

- `VIS-CHR-001_sprite_sheet_down.png`
- `VIS-CHR-002_sprite_sheet_down.png`
- `VIS-CHR-003_sprite_sheet_down.png`
- 三人的 1440x900 接入示意图。
- 三人的 390x844 接入示意图。
- 每人一份 frame metadata JSON。
- `VIS-CHR-001_002_003_frame_metadata.json`，逐帧包含 anchor alpha、非透明像素量、bbox 和问题列表。
- `VIS-CHR-001_002_003_delivery.md`。

### 验收标准

- [ ] 三人 cell 尺寸、sheet 结构和锚点完全一致。
- [ ] 三人共 36 帧的 `(32,94)` alpha 全部为 0；四角 alpha 全部为 0。
- [ ] 三人身高和脚底基线一致。
- [ ] 三人发型、服装和识别色互相可区分。
- [ ] walk 6 帧有真实跨步，不是伪动画。
- [ ] interact 4 帧动作语义可读。
- [ ] RGBA 真实透明，无灰边、白边、光晕和背景矩形。
- [ ] 同一角色逐帧身高、头身比、发型、服装和道具连续，没有独立生成造成的跳变。
- [ ] Alice `walk_2` 身体完整，非透明像素量与相邻 walk 帧没有异常断崖。
- [ ] 1440x900 和 390x844 中比例不显得过细长或漂浮。
- [ ] 与三张 portrait 的人物身份和颜色一致。
- [ ] 没有生成 up/left/right；本任务只验收 down 基线。

### 通过后的下一步

三人 down 基线全部通过后，才补齐：

- 每人的 left、right、up。
- 四向 idle/walk/interact metadata。
- 三人的统一脚底锚点和 collision footprint。
- 桐人伐木、尤吉欧伐木、爱丽丝送餐/施救等专属动作。

---

## T03：抓捕终点关键图上色

### 任务输入

```text
任务类型：关键图 / 过场图 / 抓捕终点上色
项目：UW 0.5.0 卢利特村序章
request_id：VIS-KA-002
任务名称：爱丽丝被带走终点关键图上色
用途：N10 抓捕终点事件面板；不是地图，不是角色 sprite
参考文件：
- materials/inbox/visual/keyart/current/VIS-KA-002_capture_desktop_bw.png
- materials/inbox/visual/keyart/current/VIS-KA-002_capture_mobile_bw.png
- materials/inbox/visual/keyart/current/VIS-KA-002_delivery.md
- docs/art/ASSET_REVIEW.md
```

### 生成目标

在已经通过的黑白关系构图基础上制作上色版，不重做人物关系，不改变事件顺序，不增加树洞、魔法门或山侧骑士。

必须保留并清楚表达：

- 卢利特村、教会书库或村庄建筑环境。
- 整合骑士和两名随从。
- 爱丽丝。
- 爱丽丝的家人/父亲。
- 桐人。
- 尤吉欧。
- 公开宣罪、告别、带走的叙事顺序。

### 颜色方向

- 村庄和家人：雨后晨光、暖灰、湿石板、柔和木色。
- 爱丽丝：暖金头发、金白蓝识别色，不能发灰或变成银白。
- 桐人：深墨黑发、冷蓝识别色。
- 尤吉欧：浅金发、明显天蓝服装。
- 整合骑士：冷银、深蓝或冷灰金属色，与村庄暖色形成叙事对比。
- 画面不使用浓重血腥、过度黑暗或纯黑背景。

### 桌面构图

- 2560x1440，16:9，RGB。
- 继续保留 lower-left 对白安全区。
- 不要让右侧随从完全被裁掉；可以保留部分裁切，但至少要能读出其“押送随从”身份。
- 主要关系集中在画面中右区域，但不能互相遮挡。

### 移动构图

- 1440x1920，3:4，RGB。
- lower-third 预留按钮和对白安全区。
- 可以采用更近的叙事特写，但爱丽丝、骑士、父亲、桐人和尤吉欧的关系必须仍然可读。
- 人物下半身可以有控制性的裁切，但不能把关键动作裁成无法判断。

### 禁止项

- 禁止添加画面标题、对白、UI、按钮、Logo、水印。
- 禁止把骑士画成现代军人、科幻机甲或激光武器角色。
- 禁止把“宣罪”变成战斗场面。
- 禁止把爱丽丝画成死亡、昏迷或被魔法传送。
- 禁止把桐人和尤吉欧从画面中删除。

### 输出文件

- `materials/inbox/visual/keyart/candidate/VIS-KA-002_capture_desktop_color.png`，2560x1440 RGB。
- `materials/inbox/visual/keyart/candidate/VIS-KA-002_capture_mobile_color.png`，1440x1920 RGB。
- 1440x900 事件面板接入示意图。
- 390x844 事件面板接入示意图。
- `materials/inbox/visual/keyart/candidate/VIS-KA-002_delivery.md`。

### 验收标准

- [ ] 黑白版人物关系完整保留。
- [ ] 三段事件顺序无需长文字说明也能理解。
- [ ] 爱丽丝、桐人、尤吉欧的识别色正确。
- [ ] 桌面和移动端安全区可用。
- [ ] 没有水印、文字、Logo、现代物件或科幻化误读。
- [ ] 颜色与已通过的村庄关键图、人物肖像处于同一光照方向和色温。
- [ ] 仍然只能标记 `sample_candidate`，等待人工故事事实审查。

---

## T04：VFX alpha 和静默线修复

### 任务输入

```text
任务类型：VFX / frame sheet / alpha 修复 / 语义重做
项目：UW 0.5.0 卢利特村序章
request_id：VIS-VFX-001
任务名称：神圣术透明度修复 + 静默线重做
参考文件：
- materials/inbox/visual/vfx/current/VIS-VFX-001_holy_arts.png
- materials/inbox/visual/vfx/current/VIS-VFX-001_silence_line.png
- materials/inbox/visual/vfx/current/VIS-VFX-001_delivery.md
```

### T04-A：神圣术 alpha 修复

保持当前神圣术的金色墨痕和四帧节奏，但重新处理背景和边缘。

必须满足：

- 1024x256，4x1，cell 256x256。
- RGBA。
- 背景是真透明，不是灰底、棋盘格或伪透明。
- 每帧四角 alpha 为 0。
- 光效边缘不能有明显灰色或白色矩形。
- 暖金色光晕可以存在，但必须只存在于效果主体附近，并且透明度渐变自然。
- loop 顺序保持 0 -> 1 -> 2 -> 3 -> 0。

### T04-B：静默线重做

重新设计 4 帧，不沿用当前候选的科幻激光/声波形状。

语义必须是：森林中突然出现一条不自然的安静边界。中心是“空、无、听不到”，边缘是自然环境被截断的迹象。可使用低饱和冷蓝灰、薄雾、断裂的草叶、飞鸟或虫群散开的暗示，但不能画成攻击技能。

四帧语义：

- frame 0：边界刚刚出现，环境细节开始断裂。
- frame 1：边界扩大，薄雾和草叶运动被截断。
- frame 2：边界达到最大宽度，中心保持空，不要黑色能量核心。
- frame 3：边界减弱，只留下冷雾和不自然的安静感。

静默线负向提示词：

```text
cyan laser, sci-fi beam, sound wave visualization, radar ring, energy shield, glowing core, black hole, digital portal, magical gate, attack spell, explosion, neon technology, electric weapon, text, watermark, checkerboard, gray matte, white background, opaque rectangle, hard rectangular edge
```

### T04 输出文件

- `materials/inbox/visual/vfx/candidate/VIS-VFX-001_holy_arts.png`。
- `materials/inbox/visual/vfx/candidate/VIS-VFX-001_silence_line.png`。
- 两份 frame metadata JSON。
- 两份 alpha 检查说明。
- `materials/inbox/visual/vfx/candidate/VIS-VFX-001_delivery.md`。

### 验收标准

- [ ] 两张 sheet 都是 1024x256 RGBA。
- [ ] 每个 cell 为 256x256。
- [ ] 四角和主体外部背景真正透明。
- [ ] holy arts 保留暖金墨痕语义。
- [ ] silence line 不再像激光、声波或能量护盾。
- [ ] 深色背景和浅色背景下都没有灰底/白边。
- [ ] 不接入 runtime，直到 alpha 和实际播放检查通过。

---

## 推荐执行节奏

### 第一轮

只做 T01 的一张无网格地图 master 和 T02 的三人 down sprite 基线。两项都不通过时，不继续批量生产。

### 第二轮

如果 T01/T02 通过，做 T03 抓捕图上色版，并同时做 T04 的 VFX alpha/静默线修复。

### 第三轮

把通过人工验收的资产交给工程接入，生成 1440x900 和 390x844 的真实游戏内截图；截图通过后再整理正式 manifest 和 runtime 路径。

### 第四轮

完成三位陌生玩家的全新 run 盲测，再决定是否继续做 NPC、完整 UI 图标、更多 SFX、全角色肖像和营销图。

---

## 智能体最终回复模板

每个任务结束时必须回复：

```text
任务：
状态：draft / sample_candidate / review / changes_requested

已生成：
- 文件名、尺寸、格式、帧数

已确认：
- 内容：pass / pending / fail
- 视觉：pass / pending / fail
- 技术：pass / pending / fail
- 移动端：pass / pending / fail

已知问题：
- 逐条列出；没有问题时也写“未发现”，不要省略检查项

不在本次范围：
- 明确列出没有生成的方向、图层或变体

下一步：
- 只写一项最小必要动作

runtime：不允许 / 有条件允许 / 允许
```
