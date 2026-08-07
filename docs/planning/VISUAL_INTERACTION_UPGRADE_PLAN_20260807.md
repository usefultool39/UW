# UW「边境回声」全面升级总方案（唯一执行版）

统一执行版本：UW-UPGRADE-1.0  
文档状态：Current / 项目唯一升级方案  
日期：2026-08-07  
适用项目：C:\Users\liang\Desktop\UW

统一执行索引：`docs/planning/UW_UPGRADE_1_0_EXECUTION_INDEX.md`  
全素材目录：`materials/UW_UPGRADE_1_0_ASSET_CATALOG.md`  
最终素材智能体 Prompt：`materials/UW_UPGRADE_1_0_ASSET_AGENT_PROMPT.md`  

> 本文第 10-11 节保留为方案内提示词历史；实际交给素材智能体时，以独立 Master Prompt 为准。

产品阶段 0.5.0-pre-capture 只是现有故事阶段名称，不是第二套素材版本。
从本方案开始，所有新生成、重构、接入和验收都只使用 UW-UPGRADE-1.0。
旧的 v002、v003、v004、v005、v006、v007、v008 文件只保留为审计历史，
不再继续生成、不再互相替换、不再进入 runtime，也不作为新的执行编号。

## 1. 结论先行

当前 UW 的故事合同已经达到 story=ready：四幕、10 个关键节点、唯一 alice_captured 终点和 46 个跨节点回响均已接入。真正阻碍“好看、好玩”的不是再增加剧情数量，而是运行时仍缺少一套统一的视觉语言、可读的可玩地图、真实角色动作、场景反馈和有取舍的短循环。

本方案采用一条可验收的“视觉与玩法垂直切片”路线：

1. 先冻结一套原创的 Rulid Storybook 2D 美术圣经和 UI token。
2. 只制作一张可走的卢利特村地图、三名核心角色、六张活动背景、32 枚图标、六类 VFX、两组 BGM、两组环境声和一组 SFX。
3. 以“移动到目标 -> 观察线索 -> 做一个有代价的选择 -> 看到即时结果 -> 在后续节点认出回响”为前 10 分钟的核心循环。
4. 用一个代表场景先完成桌面与 390x844 触控验收，再批量扩展。
5. 所有未批准素材继续留在 materials/inbox；只有完整通过来源、技术、内容、游戏内和 hash 链路后才能复制到 frontend/public/assets/runtime。

这不是把项目改成 3D，也不是把静态关键图直接铺在地图上。当前技术边界继续保持 Vue 3 + Phaser 3 + FastAPI；“建模”在本阶段指 2.5D 场景模块、建筑体块、遮挡层和可复用 props 的建模规范，最终输出仍是网页可用的 2D 贴图和数据。

## 2. 现状与问题证据

### 2.1 工程和内容基线

- 当前运行时规格合同：materials/runtime_asset_requirements.json。
- 当前合同文件仍记录着历史资产文件名。开始执行本方案前，先把它转换为
  UW-UPGRADE-1.0 的单一合同；后续不再沿用地图/角色/环境/音频各自的版本后缀。
- 最新整理门禁：runtime asset specs 为 ready、issues=0；7 个历史中间文件已带 hash 移入审计归档，materials check 通过 40 requests；Pre-Capture readiness 仍为 materials=pending, story=ready。
- 现有正式 runtime 主要是关键图、六张肖像、12 枚图标和少量音频；它们只能算候选或内测素材，不能替代可走地图、动画 Sprite、VFX 和完整音频层。
- 旧版本交付必须保留为审计证据。新收件即使文件存在，也不能直接写成 approved 或 integrated。

### 2.1.1 唯一版本规则

- 唯一计划、资产、数据、runtime 和验收版本：UW-UPGRADE-1.0。
- 历史文件可以存在于 materials/archive 或当前 inbox 的审计目录，但不属于当前生产。
- 新文件使用统一前缀 UW-UPGRADE-1.0，例如
  UW-UPGRADE-1.0_map.json、UW-UPGRADE-1.0_kirito_sheet.png、
  UW-UPGRADE-1.0_scenes.json、UW-UPGRADE-1.0_audio_meta.json。
- 旧 request_id 只用于追溯原始需求；执行清单只使用统一资产组名：
  MAP、CHARACTERS、SCENES、UI、VFX、PORTRAITS、KEYART、ANIMATION、
  MUSIC、AMBIENCE、SFX、WORLD-DATA。
- 不创建“临时版、候选版、试验版、最终版”并列目录。每次重做都覆盖
  UW-UPGRADE-1.0 的待验收工作区，历史证据另行归档。
- 正式 runtime 只允许一套 UW-UPGRADE-1.0 文件；回滚使用 Git/manifest 记录，
  不再通过增加 v009、v010 等后缀解决问题。

### 2.2 试玩中可见的视觉问题

当前首屏能够启动并进入地图，但地图主要依赖程序化网格、色块、token 和文字叠层；小角色在缩小后无法形成稳定轮廓，建筑、道路、树木和交互物的材质层级不够。结果是玩家看到的是“调试可视化”，而不是一个有地点记忆点的村庄。

HUD、任务卡、底部快捷栏和场景操作面板都能工作，但屏幕上同时出现的卡片层级较多；重要按钮、行动代价、地图目标和反馈没有始终保持一个明确焦点。活动完成后已有关系、记忆和资源结果，但缺少足够强的动画、音效、局部镜头和可回访提示来让玩家感到选择真正改变了世界。

### 2.3 试玩中可见的交互问题

- 目标有说明，但到达目标、靠近目标和“现在可以互动”的状态区分不够强。
- 交互入口依赖“互动”面板和文字列表，玩家对场景中哪些物体可调查缺少一眼可见的空间线索。
- 活动通常是一次面板选择，观察、判断、提交之间缺少节奏变化。
- 关系变化和记忆写入是正确的系统事实，但在视觉上更像结果清单，尚未形成“我刚才的做法会被谁记住”的情绪反馈。
- 低资源、被阻挡、行动失败和重复访问时的恢复路径需要更明确的下一步。
- 桌面与窄屏有自动化覆盖，但需要以真实素材接入后重新做文字换行、点击目标、地图缩放和安全区验收。

## 3. 升级目标与可量化验收

### 3.1 体验目标

| 指标 | 目标 | 验收方式 |
|---|---:|---|
| 首次有效互动 | 新玩家 60 秒内完成 | 从新游戏开始计时，记录第一次有效行动 |
| 目标可理解度 | 10 秒内知道下一步地点和原因 | 3 名陌生玩家盲测口述/选择记录 |
| 单次活动时长 | 30–90 秒 | Playwright 计时 + 真人记录 |
| 选择反馈 | 每次选择同时出现资源结果和人物反应 | UI E2E + 截图 |
| 跨节点回响 | 至少 3 次被玩家识别 | N01-N10 路径回放 |
| 地图可读性 | 1440x900 与 390x844 均能区分道路、建筑、目标、阻挡 | 截图审查 |
| 触控可用性 | 关键点击目标不小于 44x44 CSS px | 浏览器测量 |
| 文本可读性 | 正文对比度至少 4.5:1，重要状态不只靠颜色 | CSS/截图审查 |
| 运行时稳定性 | 无前端 uncaught error，无资产 404 | 浏览器日志和网络检查 |

### 3.2 不改变的产品边界

- 正典主线仍从卢利特村日常走到爱丽丝被带走；唯一终点仍为 alice_captured。
- 不制作抓捕后的剧情，不扩写 Day 118+。
- 战斗仍作为独立原型，不把半成品战斗塞进当前主线。
- 后端仍是位置、时间、资源、flag、关系、记忆和终点状态的唯一权威。
- scripted 模式必须无外部 API 完整可玩。

## 4. 统一视觉方向：Rulid Storybook

### 4.1 视觉定位

采用原创、明快、清晰的 2D 叙事 RPG 风格：3/4 俯视地图 + 手绘卡通场景背景 + 清晰轮廓的小比例角色 + 少量有节制的光效。画面要“温暖的村庄生活逐渐被冷静、异常的边界色侵入”，而不是平均铺满滤镜或高饱和特效。

不可直接模仿任何现成网页游戏、动画、RPG、角色、UI、截图、品牌或音乐；参考成熟作品时只提取可观察的设计方法：明确目标、稳定反馈、短活动、读得懂的资源、快速重试和分层信息。

### 4.2 色彩、线稿与材质

- 村庄主色：苔藓绿 #5E8061、雨后青 #6D9C9B、木材棕 #8A6549、麦秆金 #D7B35A、纸张暖白 #F5EAD0。
- 边界异常：深靛 #24304D、冷青 #64B9B2、低饱和紫灰 #746C8C；只用于异常区域和关键 VFX，不让全屏变紫。
- 反馈色：成功青绿 #4FB286、警告金 #E4B45F、拒绝朱红 #D96B5F、锁定蓝灰 #91A5B8。
- 线稿使用深棕黑而非纯黑；地图轮廓 1–2px，角色外轮廓在显示尺寸下保持 1–2px 可见。
- 每个物体至少有 base、shadow、highlight、occlusion 四个层级；禁止平面纯色几何占位。
- 雨天只降低饱和度并增加湿润高光，不盖住道路、角色和交互点。

### 4.3 比例与镜头

- 地图采用 28px/tile、108x64 tiles、3024x1792 world canvas；角色脚底锚点统一为 bottom-center。
- 核心角色在游戏视口中的可见高度目标 44–52px；不能缩成难以识别的彩色小点。
- 建筑入口、路口、树冠和前景遮挡必须有稳定的 z-order 规则：地面 < 角色脚底 < 角色身体 < 半遮挡物 < 前景树冠。
- 摄像机默认跟随玩家，目标附近允许 0.85–1.0 秒的缓动对焦；不能为了镜头效果把目标推出屏幕。
- 任何场景的中下部必须保留交互安全区；背景焦点不放在移动端会被 HUD 覆盖的位置。

### 4.4 2.5D 场景与“建模”规范

本项目不引入实时 3D 渲染，但所有建筑、树木、门、桥、书架、炉台和边界岩壁按可复用的 2.5D 模块制作。

- 每个模块先建立正面、侧面、俯视三个轮廓关系，再输出 2D base、shadow、highlight、occlusion 和 collision。
- 建筑体块采用“墙体高度 + 屋顶坡度 + 门窗比例 + 脚底投影”四项固定参数；同类房屋只改变材质和装饰，不改变世界比例。
- 树木分为 trunk、lower foliage、upper foliage 三层，upper foliage 进入 occlusion/foreground；树冠不能遮住玩家的脚底和目标标记。
- 道具采用 1x/2x 两档，不用单张大图压缩后充当所有尺寸；水桶、木箱、书页、餐篮、训练木桩、边界碎石各有独立碰撞和交互点。
- 所有模块在 100% 游戏缩放、移动端缩放和雨天低对比环境中通过轮廓检查；禁止只在放大原图时好看。
- 交付时同时提供模型参考图、2D 导出图、像素尺寸、锚点、遮挡类型、碰撞盒、可交互点和所属图层。

## 5. 信息架构与 UI 重构

### 5.1 三层界面

1. 世界层：地图、角色、目标标记、可调查物体、路径和 VFX。
2. 行动层：只在靠近交互点时出现一个主行动按钮，显示动作、耗时和主要代价。
3. 结果层：显示人物回应、资源变化、记忆/承诺摘要和下一步可做的事情；关闭后回到世界层。

同时最多展示一个强 CTA。任务卡保留“为什么做”和“去哪”，快捷栏保留常用动作；重复解释移入可展开日志。

### 5.2 关键组件规范

- Quest tracker：标题 16–18px，目标一句话，地点名带位置图标；只显示一个主目标和最多两个可选回访。
- Action preview：每个选择卡固定显示“做法 / 耗时 / 资源代价 / 立即收益 / 谁会记住”；数值变化使用图标和正负号，不能只写抽象的“关系变化”。
- Result panel：先出现一句人物回应，再出现资源变化，最后出现“将在哪个节点回响”；动画 240–420ms，支持跳过。
- Relationship/memory：用头像、关系标签和短句，不直接把内部 flag 或永久记忆正文暴露给玩家。
- Hotbar：按钮至少 56px 高；桌面显示快捷键，触控不依赖键盘。
- Toast：只用于轻量反馈；拒绝和资源不足必须在当前行动卡内解释原因和恢复方案。
- Modal：最大宽度 680px；窄屏使用 16px 边距、按钮垂直排列，不能出现横向滚动。

### 5.3 移动端

- 390x844 视口中，地图可视区域至少占 44vh；底部操作区固定在 safe-area-inset-bottom 之上。
- 交互点使用 44px 触控命中框，视觉图标可以更小但不可缩小命中区域。
- 任务卡在移动端默认折叠为标题 + 地点 + 一个主按钮；点击后展开详细代价和回响。
- 重要状态必须同时有图标、文字和形状；不能只用红/绿。

## 6. 前 10 分钟的“好玩”循环

### 6.1 节奏

| 时段 | 玩家动作 | 设计目的 | 必须反馈 |
|---|---|---|---|
| 0:00–1:00 | 阅读目标，点击定位，移动到书库 | 建立目标和移动信心 | 金色路径、到达脉冲、地点标签 |
| 1:00–3:00 | 观察三张书页，挑 3 个词 | 让玩家做第一次判断 | 词条高亮、剩余选择槽、轻音效 |
| 3:00–4:00 | 选择公开记录或保留符号 | 建立真实取舍 | 爱丽丝/尤吉欧短反应、关系与记忆结果 |
| 4:00–6:00 | 前往巨神树，完成一次训练/协作 | 让地图不只是菜单 | 角色 walk、训练动作、体力消耗、命中反馈 |
| 6:00–8:00 | 回访 NPC，听到对早期选择的不同回应 | 证明选择有回响 | 头像表情、关键词强调、回响标签 |
| 8:00–10:00 | 回到小屋结算并解锁下一节拍 | 形成完成感和继续动机 | 日结算卡、明日目标、BGM 过渡 |

### 6.2 三个可复用短玩法

1. 线索拼接：从 6 个词中选 3 个，词之间有语义关系；错误组合不惩罚主线，只给“证据不足”并允许重试。
2. 路线观察：在地图上跟随一条安全路径，点击 2 个异常点；玩家要决定公开记录还是私下保留。
3. 关系交付：准备午餐/递送记录/陪同训练，先选择做法，再看同伴反应。选择影响关系、记忆或后续提示，但不改变固定正典事实。

每个短玩法必须是观察 -> 选择 -> 提交 -> 反馈四步，且总操作不超过 8 次；重复访问使用新上下文或快速复用，不重复播放长说明。

## 7. 素材生产与目录落位

以下路径是“制作输入”和“批准 runtime”的明确边界。生成智能体只写 materials/inbox 对应目录；项目负责人验收后才复制到 runtime。

| request_id | 制作输入位置 | 目标 runtime 位置 | 最低交付 | 关键验收 |
|---|---|---|---|---|
| VIS-MAP-001 | materials/inbox/visual/world/ | frontend/public/assets/runtime/world/rulid-village/ | 9 层图、tile/prop atlas、map JSON、collision/walkable/interaction | 3024x1792，108x64，层名和 source 可解析 |
| CHARACTERS | materials/inbox/visual/characters/ | frontend/public/assets/runtime/characters/ | RGBA sheet + UW-UPGRADE-1.0_frames.json | 4 向 idle 2 / walk 6 / interact 4，真实不同帧 |
| VIS-CHR-002 | materials/inbox/visual/characters/ | frontend/public/assets/runtime/characters/alice/ | 同上 | 同一 cell、脚底锚点、服装和轮廓一致 |
| VIS-CHR-003 | materials/inbox/visual/characters/ | frontend/public/assets/runtime/characters/eugeo/ | 同上 | 同一 cell、儿童比例可辨、动作差异清晰 |
| SCENES | materials/inbox/visual/environments/ | frontend/public/assets/runtime/environments/ | 6 张 1920x1080 + UW-UPGRADE-1.0_scenes.json | 地点身份、光照、景深、移动裁切安全区 |
| VIS-POR-002 | materials/inbox/visual/portraits/ | frontend/public/assets/runtime/portraits/ | 6 角色 x 5 表情 x 256px derivative | 线稿、光照、脸部比例统一 |
| VIS-UI-002 | materials/inbox/visual/ui/ | frontend/public/assets/runtime/icons/ | 补齐到 32 枚，24/48/96px | 24px 可读，色盲冗余，状态成对 |
| VIS-VFX-001 | materials/inbox/visual/vfx/ | frontend/public/assets/runtime/vfx/ | 6 类效果的 sprite/particle 参数 | 不遮挡文本，低闪烁模式可替代 |
| VIS-KA-002 | materials/inbox/visual/keyart/ | frontend/public/assets/runtime/keyart/ | capture scene desktop/mobile | 固定终点的情绪焦点与安全文字区 |
| VIS-ANIM-001 | materials/inbox/visual/animation/ | frontend/public/assets/runtime/animation/ | 读书、递物、调查、告别动作 | 与角色脚底锚点和触发 ID 对齐 |
| VIS-TILE-001 | materials/inbox/visual/world/props/ | frontend/public/assets/runtime/world/rulid-village/props/ | tile、建筑、道具、遮挡规则 | 不使用单张背景替代数据层 |
| AUD-BGM-002 | materials/inbox/audio/bgm/ | frontend/public/assets/runtime/audio/ | 2 stems WAV+OGG、loop samples | 75–110s，-20~-17 LUFS，peak <= -1 |
| AUD-BGM-003 | materials/inbox/audio/bgm/ | frontend/public/assets/runtime/audio/ | 2 stems WAV+OGG、loop samples | 60–100s，-20~-17 LUFS，peak <= -1 |
| AUD-AMB-002 | materials/inbox/audio/ambience/ | frontend/public/assets/runtime/audio/ | normal/silent WAV+OGG | 60–90s、等长、同 loop、-26~-22 LUFS |
| AUD-SFX-001 | materials/inbox/audio/sfx/ui/ | frontend/public/assets/runtime/audio/sfx/ | UI、线索、奖励、关系、记忆、日结算 | 48kHz mono/stereo，瞬态清楚 |
| AUD-SFX-002 | materials/inbox/audio/sfx/world/ | frontend/public/assets/runtime/audio/sfx/ | 脚步、翻页、递物、神圣术、边界 | 每个触发 ID 有文件和 fallback |

所有包必须包含主 sidecar、真实工具/模型版本、完整 prompt、negative prompt、seed/settings、版权/许可、source_url 或无 URL 原因、intended_use，以及逐文件 18 列 manifest fragment。status 只写 received；runtime_file、approved_by、approved_at、integrated_at 在项目负责人验收前留空。

## 8. 详细素材规格

### 8.1 可玩地图 VIS-MAP-001

- 世界尺寸：3024x1792；108 列 x 64 行；28px/tile。
- 分层：terrain、water、roads、buildings、vegetation、occlusion、foreground、lighting、weather。
- alpha 层：occlusion、foreground、lighting、weather 必须含真实透明像素。
- 数据：collision、walkable、interaction 三份可解析数据；interaction 点必须带 id、tile 坐标、kind、label、action_id。
- 建筑、道路、水体不能靠黑色方块或单色矩形表达；每个主要地点至少有入口、屋檐阴影、可识别门窗和前景遮挡。
- 必须使用 UW-UPGRADE-1.0_ 前缀，禁止通用 tiles_atlas 或带旧版本后缀的文件名。

### 8.2 核心角色 VIS-CHR-001/002/003

- 使用 64x96 或 96x128 cell，透明 RGBA PNG；无棋盘格、背景、文字、烘焙阴影。
- 每个角色四方向，每方向 idle 2、walk 6、interact 4，共 48 个真实帧。
- 每帧 metadata 提供 source、rect[x,y,width,height]、anchor、collision footprint、fps、loop。
- 身高显示 44–52px；桐人、爱丽丝、尤吉欧通过发色、服装轮廓、姿态和道具区分，不能只换颜色。
- interact 动作分别体现记录/观察、递物/关心、训练/协作，不能用 idle 平移冒充。

### 8.3 活动背景 VIS-ENV-001

六张 1920x1080：church_library、gigas_clearing、home_hearth、north_gate、forest_path、end_mountains_cave。

每张需要前景、中景、背景和中下部互动安全区；无角色、无 UI、无文字、水印和版权构图。场景必须在 16:9 桌面与 390x844 窄屏裁切下保留主要叙事焦点。

### 8.4 UI 图标与状态

最终 32 枚图标分为 navigation、resource、clue、relationship、memory、promise、tension、activity、result、lock。每枚输出 SVG source、24/48/96 PNG；禁用、选中、警告至少有形状/纹理差异，不只换颜色。

### 8.5 VFX

至少制作 clue-pulse、sacred-ink、boundary-ripple、relationship-warmth、reward-spark、capture-silence 六类。每类提供 8–16 帧或粒子参数、持续时间、颜色、触发 ID、低闪烁替代和音效 ID。效果要围绕目标/角色，不铺满全屏。

### 8.6 音频

沿用当前合同中的 WAV/OGG、采样率、响度、peak 和 loop 字段。音乐层级：village morning -> library clue -> relationship warm -> boundary suspense -> capture silence；通过 1.5–2.5 秒交叉淡化和 ducking 连接，不在打开面板时突然切断。

## 9. 玩法与交互升级清单

### P0：必须在垂直切片内完成

- 地图：目标路径、到达脉冲、阻挡原因、靠近提示、可点击交互物高亮。
- 行动：所有选择卡显示耗时、体力/神圣力代价、立即收益、未来回响。
- 结果：人物回应 -> 资源变化 -> 记忆/承诺摘要 -> 下一步按钮的固定顺序。
- 活动：线索拼接、路线观察、关系交付三个短玩法至少各有一个可玩实例。
- 反馈：成功、拒绝、资源不足、重复访问、已完成均有不同视觉和音频。
- 移动：390x844 的地图、底栏、弹窗和主要 CTA 不重叠。

### P1：首轮盲测后立即优化

- 回访 NPC 的台词和表情读取前置选择。
- 日结算显示“今天做了什么”和“明天会发生什么”。
- 增加可选的环境观察点，不增加新的主线事实。
- 补齐 32 图标、五表情肖像、六名支撑 NPC 的视觉一致性。

### 暂不做

- 完整战斗、装备、技能树、开放世界和抓捕后剧情。
- 通过大量随机事件掩盖核心活动不够有趣的问题。

## 10. 资产生成智能体总提示词

以下提示词可以整体复制给后续视觉/音频智能体。它要求对方先读合同再生成，且不越过项目负责人边界。

~~~
你是 UW「边境回声」项目的视觉、2.5D 场景和音频素材制作智能体。
项目根目录：C:\Users\liang\Desktop\UW
唯一执行版本：UW-UPGRADE-1.0
主线终点：alice_captured（爱丽丝被整合骑士带走）

你的职责仅是生成或重导 VIS-*、AUD-* 素材，以及包内 sidecar、metadata、measurement 和 MANIFEST fragment。
你不得修改代码、剧情、REQUESTS.csv、正式 MANIFEST.csv、frontend/public/assets/runtime；
不得删除、覆盖或改名任何历史文件；不得宣称 approved、integrated、materials=ready 或第一阶段完成。

开始前必须完整阅读：
1. docs/delivery/PROJECT_HANDOFF_20260807.md
2. docs/delivery/ASSET_HANDOFF_SNAPSHOT_20260807.md
3. docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md
4. materials/runtime_asset_requirements.json
5. docs/delivery/MATERIALS_AUDIT_20260807.md
6. frontend/src/field/runtimeAssetPaths.js
7. frontend/src/field/gameAssetPaths.js

以 materials/runtime_asset_requirements.json 的当前内容为唯一技术合同。
当前合同必须先被项目负责人归一化为 UW-UPGRADE-1.0；
不要再按地图、角色、环境、音频分别递增版本，也不要猜测隐藏版本。

统一视觉方向：原创 Rulid Storybook 2D。
这是明快、清晰、适合网页 RPG 的 3/4 俯视手绘卡通风格：
温暖村庄使用苔藓绿、雨后青、木材棕和麦秆金；
边界异常使用深靛、冷青和低饱和紫灰作为局部点缀；
深棕黑线稿、柔和环境光、明确脚底阴影、可读的材质层级；
禁止纯几何占位、黑色调试块、烘焙文字/UI、水印、棋盘格、官方截图、
现成游戏/动画/角色临摹、未授权拆包素材和不可追溯的参考图。

先只完成以下 P0 垂直切片：
A. VIS-MAP-001 卢利特村可玩地图
B. VIS-CHR-001 桐人、VIS-CHR-002 爱丽丝、VIS-CHR-003 尤吉欧核心 Sprite
C. VIS-ENV-001 六张活动背景
D. VIS-UI-002 补齐 32 枚图标
E. VIS-VFX-001 六类反馈效果
F. AUD-BGM-002、AUD-BGM-003、AUD-AMB-002 和 AUD-SFX-001/002

每个 request 单独放在对应 materials/inbox 子目录。
每个包必须有一个主 sidecar，列出包内全部文件，并记录：
request_id、版本、creator/source、created_at、tool/model/version、完整 prompt、
negative prompt、seed/settings、edits、license、source_url 或无 URL 原因、
intended_use、rights statement。
每个包提供 18 列 manifest fragment：
asset_id,request_id,status,source_file,runtime_file,sha256,creator,tool_model,
created_at,license,source_url,attribution_required,attribution_text,approved_by,
approved_at,integrated_at,replaces_asset_id,notes。
status 只写 received；审核和 runtime 字段保持空白。

交付前自行运行：
backend\.venv\python.exe materials\tools\check_materials.py
backend\.venv\python.exe materials\tools\check_runtime_asset_specs.py --require-complete
不要修改正式台账；报告真实命令输出、未通过项和每个文件的尺寸/hash。
~~~

## 11. 分包生成提示词

### 11.1 地图包提示词

~~~
生成 VIS-MAP-001 卢利特村 3/4 俯视可玩地图资产包。
输出 3024x1792、108x64 tiles、28px/tile 的分层数据，不要输出一张合并图代替图层。
地点必须包含村道广场、教会书库、巨神树伐木场、小屋、北门、通往森林的道路和可辨识的河流/边界方向。
交付 terrain、water、roads、buildings、vegetation、occlusion、foreground、lighting、weather 九层；
其中 occlusion、foreground、lighting、weather 必须是带真实透明像素的 RGBA PNG。
另外交 request-prefixed 的 terrain/water/road tile atlas、buildings/props atlas、
collision、walkable、interaction 数据。
建筑有屋顶、墙面、门窗、投影和入口；道路有湿润边缘和可读路口；
树木有树干、冠层和遮挡规则；水面有重复但不刺眼的雨滴/波纹；
地图整体留出玩家和 NPC 的行走宽度，目标地点不能被装饰堵住。
不要文字、UI、角色、光斑、棋盘格、黑块、平直矩形占位或版权构图。
所有 source 路径从项目根可解析，metadata 顶层包含 runtime_size、layers 和 data.collision/walkable/interaction。
~~~

### 11.2 三名核心角色 Sprite 提示词

~~~
生成统一比例的原创 2D RPG RGBA Sprite。
角色：{角色名}，request_id：{VIS-CHR-001 或 002 或 003}。
cell 只能使用 64x96 或 96x128；四方向 down/left/right/up。
每方向 idle 2 帧、walk 6 帧、interact 4 帧，共 48 个真实不同帧；
frames JSON 中每帧都写 source、rect、anchor、collision footprint、fps、loop。
脚底 anchor 为 bottom-center，所有角色脚底对齐；显示高度 44–52px。
桐人：黑发、深色短斗篷/简洁训练服、谨慎观察姿态、记录或指向动作。
爱丽丝：金发、浅色村落服装、蓝色/金色小配件、端正而关心的姿态、递物和查看记录动作。
尤吉欧：儿童阶段的浅棕/青灰服装、短发、轻便伐木装备、向前协作和训练动作。
三人必须靠轮廓、发型、服装层次和姿态区分，不得只改颜色。
透明背景，无棋盘格、无烘焙阴影、无文字、无武器攻击特效、无官方动画临摹。
~~~

### 11.3 六张场景背景提示词

~~~
为 VIS-ENV-001 生成六张原创 1920x1080 2D RPG 活动背景：
church_library、gigas_clearing、home_hearth、north_gate、forest_path、end_mountains_cave。
每张都使用 Rulid Storybook 风格，具有前景/中景/背景三层、清晰地点身份、
柔和方向光、可读材质和中下部互动安全区。
church_library：木书架、湿润窗光、旧纸页、阅读台、北境记录焦点。
gigas_clearing：巨大神树根系、木屑、训练空地、雨后草地和可站立区域。
home_hearth：温暖炉火、三人生活痕迹、桌面和可放置午餐篮的空位。
north_gate：村门、岗哨、湿石路、远方山线和可观察的警戒点。
forest_path：林间小径、被雨打湿的叶片、异常安静的鸟栖息点、可调查痕迹。
end_mountains_cave：冷色洞窟入口、岩壁层理、边界光线和施救关注区域。
禁止角色、文字、UI、水印、纯色块、三角形/矩形占位和不可裁切的中心小物体。
~~~

### 11.4 UI 图标提示词

~~~
补齐 UW 32 枚原创 UI 图标，使用同一 24px 基准网格、2px 深棕轮廓、
少量内部高光和清晰负空间。类别包括 navigation、resource、clue、
relationship、memory、promise、tension、activity、result、lock。
每枚输出 SVG source 与 24/48/96 PNG；提供 default、selected、disabled、
warning 状态。图标必须在 24px 下仍可识别，不能使用文字、渐变噪点或复杂细节。
为体力、神圣力、线索、记忆、承诺和紧张分别提供非颜色冗余形状。
~~~

### 11.5 VFX 提示词

~~~
生成六类轻量、可循环控制的 2D VFX：clue-pulse、sacred-ink、
boundary-ripple、relationship-warmth、reward-spark、capture-silence。
每类提供 8–16 帧或等价 Phaser 粒子参数、持续时长、触发 ID、音效 ID、
低闪烁替代方案和透明背景。效果半径不超过角色高度的 1.8 倍，
不遮挡对话和按钮；boundary/capture 使用冷色和留白，reward 使用少量金色，
relationship-warmth 使用暖光而不是大面积光球。
~~~

### 11.6 音频提示词

~~~
为 UW 生成原创、可无缝循环的网页 RPG 音频，不模仿现成游戏旋律。
AUD-BGM-002 两版 75–110 秒，AUD-BGM-003 两版 60–100 秒；
AUD-AMB-002 normal/silent 两版 60–90 秒且完全等长、loop samples 相同。
所有 WAV 为 48kHz/24-bit，OGG 必须能被标准解码器读取；
BGM -20 到 -17 LUFS、peak <= -1 dBFS；ambience -26 到 -22 LUFS、peak <= -2 dBFS。
boundary suspense：低密度木质打击、稀疏低音、远处雨和冷空气，不能持续轰鸣。
relationship daily：温暖木管/拨弦和轻微雨后空间感，避免广告式大旋律。
forest normal/silent：normal 有叶片、远鸟、脚下湿地；silent 保留空气压力和细枝，
但形成不自然的中高频空缺，不得是数字静音。
交付 loop_start_sample、loop_end_sample、ducking 建议和两轮人耳循环记录。
~~~

### 11.7 肖像与角色表情提示词

~~~
生成 UW-UPGRADE-1.0 肖像包，统一 1024x1024 RGBA source 和 256x256 runtime derivative。
角色包含桐人、爱丽丝、尤吉欧、赛尔卡、村民长者和玩家角色，共六人；
每人五个表情：neutral、concerned、warm、focused、farewell。
保持同一头身比例、脸部结构、线稿粗细、光向和透明边缘；
表情变化必须来自眉眼、嘴角、视线和肩颈姿态，不能只改变颜色。
neutral 用于普通对话，concerned 用于边界异常，warm 用于关系回响，
focused 用于调查/训练，farewell 只用于抓捕前告别。
输出 source、256 derivative、expression metadata、角色显示名和运行时路径；
无文字、气泡、UI、水印、官方角色临摹或烘焙背景。
~~~

### 11.8 抓捕关键图提示词

~~~
生成 UW-UPGRADE-1.0 的唯一终点关键图，主题是整合骑士到场、告别和爱丽丝被带走。
只表现抓捕前到抓捕瞬间，不表现任何抓捕后剧情、中央大教堂后期状态或战争内容。
提供 desktop 2560x1440 和 mobile 1440x1920 两个构图；
视觉焦点是爱丽丝、桐人、尤吉欧之间的距离变化，整合骑士以压迫但不血腥的远景/剪影出现。
左上和下方保留 UI/标题安全区，中间和右侧保留人物情绪焦点；
村庄温暖色与边界冷色形成渐变式对照，但禁止大面积紫色光球和电影海报式文字。
无标题、logo、UI、对白文字、水印、版权构图；交付构图说明、裁切安全框和焦点坐标。
~~~

### 11.9 互动动作与道具提示词

~~~
生成 UW-UPGRADE-1.0 interaction/props 包，严格绑定地图 interaction id。
动作包含 reading、writing、hand_item、inspect_boundary、training、concern、
farewell 六类；每类给出角色、朝向、持续时间、起始/结束姿势和触发 VFX/SFX id。
道具包含书页、记录板、餐篮、木桩、训练剑、村门扣件、边界碎石和雨滴标记。
道具按 28px tile 网格输出 1x/2x PNG/SVG source，记录 anchor、collision、
occlusion、interaction radius 和适用场景。
动作不能用角色整体平移冒充；需要手臂、头部、道具或重心的真实变化。
~~~

### 11.10 UI/SFX 绑定提示词

~~~
生成 UW-UPGRADE-1.0 的 UI/SFX 绑定表，不新增内部版本号。
为以下触发 id 各提供文件、fallback、音量建议和可跳过设置：
ui_open、ui_confirm、ui_cancel、ui_locked、clue_select、clue_complete、
relationship_up、tension_up、memory_write、promise_write、resource_low、
arrival_pulse、footstep_grass、footstep_wood、page_turn、hand_item、
sacred_ink、boundary_ripple、day_settle、capture_silence。
声音必须短、干净、有层次，不使用刺耳高频或持续轰鸣；每个文件注明 WAV/OGG
格式、采样率、峰值和触发场景。低音量和关闭音效时仍要保留文字/图标反馈。
~~~

## 12. 运行时接入方案

### 12.1 接入顺序

1. 只接地图 + 三名角色 + church_library 一个背景 + clue-pulse + BGM-003 A。
2. 用此切片完成首个 10 分钟路线，记录 1440x900 和 390x844 截图。
3. 修复最常见的遮挡、目标迷失、按钮过小和反馈不明显问题。
4. 再接其余五个背景、森林 ambience、boundary VFX 和 BGM-002。
5. 最后接 capture key art、整合骑士表现、SFX 和补齐肖像/图标。

### 12.2 代码接入边界

- runtimeAssetPaths.js 只引用已批准的稳定路径，不扫描 materials/inbox。
- 地图层和数据通过 sceneRegistry/createWorldFieldScene 接入；不在 FieldSlice.vue 中硬编码新地图数据。
- 新活动先登记 scene_activities.json；只有新交互形态才新增 activityRegistry 项。
- VFX 使用稳定 trigger id；前端只触发表现，资源/关系/剧情结果仍由后端返回。
- 音频由 useAudio 统一管理，支持 loop、ducking、失败 fallback 和独立音量。

## 13. 验收门

### 技术门

- PNG 尺寸、色彩模式、alpha、透明像素和可见像素符合合同。
- JSON 所有 source 从项目根解析，frame rect 不越界，anchor/collision 有效。
- WAV/OGG 可解码，时长、采样率、响度、peak、loop 字段与实物一致。
- materials check 无未登记文件；runtime 目录无 orphan、无未批准路径、hash 一致。

### 内容与视觉门

- 代表场景在 100% 和浏览器实际缩放下均能区分地点、道路、角色和交互点。
- 三名角色在下雨、树荫、室内和边界冷光下仍可辨。
- 背景焦点不被 HUD、任务卡、弹窗或移动端安全区遮挡。
- 没有官方截图、未授权素材、烘焙文字、棋盘格或纯几何占位。

### 交互门

- 新游戏 60 秒内完成首次有效互动。
- 每个行动可在提交前看到代价和收益；提交后有资源、关系、记忆和人物反应。
- 失败、拒绝、低资源、重复活动有恢复路径且不部分写状态。
- 关键流程可用键鼠和触控完成，44px 命中框和焦点顺序正确。

### 运行门

~~~powershell
backend\.venv\python.exe materials\tools\check_materials.py
backend\.venv\python.exe materials\tools\check_runtime_asset_specs.py --require-complete
backend\.venv\python.exe materials\tools\check_precapture_readiness.py
backend\.venv\python.exe -m pytest -q
npm.cmd --prefix frontend run test:unit
npm.cmd --prefix frontend run build
$env:CI='1'; $env:E2E_BACKEND_PORT='8034'; $env:E2E_FRONTEND_PORT='4194'
npm.cmd --prefix frontend run test:e2e -- --reporter=line
git -c safe.directory='C:/Users/liang/Desktop/UW' diff --check
~~~

### 真人试玩门

邀请 3 名没有读过开发文档的玩家，从新游戏完成 N01-N10，记录首次互动、目标理解、选择代价、跨节点回响、抓捕原因、卡点和继续意愿。自动化测试、开发者代玩和素材智能体报告都不能代替真人证据。

## 14. 交付节奏与责任

| 阶段 | 产出 | 完成条件 |
|---|---|---|
| A 视觉冻结 | art bible、UI token、角色比例、地图 z-order | 代表场景评审通过 |
| B 垂直切片 | 地图、三角色、书库背景、线索 VFX、BGM | 10 分钟流程可玩 |
| C 反馈增强 | 其余背景、活动 VFX、SFX、回响 UI | 结果和回访可识别 |
| D 内容完整 | capture art、整合骑士、图标/肖像补齐 | N01-N10 视觉闭环 |
| E 盲测优化 | 3 人记录、最高频问题修复 | readiness 与真人证据齐全 |

素材智能体负责生成和交付证据；项目负责人负责审查、接入、代码和状态更新；最终玩家测试必须由真实玩家完成。

## 15. 风险与取舍

- 大量一次性生成会放大风格返工：先做一张地图、一名角色和一张背景的 golden slice。
- 关键图很漂亮但不能玩：关键图仅用于 opening/capture，地图必须保留 tile、碰撞、交互和遮挡数据。
- 过度特效会降低可读性：所有 VFX 有半径、时长、低闪烁版本和禁用状态。
- 玩法膨胀会稀释正典：当前只优化三个短玩法，不新增战斗和开放世界。
- 版本漂移会破坏审计：每次生成前读取 runtime_asset_requirements.json；文件名、sidecar、manifest 和 hash 同步交付。

## 16. 立即执行清单

- [ ] 冻结 Rulid Storybook 色板、线稿、角色比例和 z-order。
- [x] 清理或隔离 7 个历史中间文件，使 materials check 变为 0 errors（已移到 `materials/archive/2026-08-07-v003-intermediate/` 并保留 SHA-256）。
- [ ] 将当前地图、角色、环境和音频收件统一整理为 UW-UPGRADE-1.0，再做人工审查并保留失败记录。
- [ ] 接入第一处 golden slice：教会书库 + 桐人/爱丽丝/尤吉欧 + clue-pulse + BGM-003。
- [ ] 完成桌面/390x844 截图和操作日志。
- [ ] 再批量接入其余背景、音频、VFX 和 capture 表现。
- [ ] 组织 3 人真人盲测，按最高频问题迭代。

## 17. 后续由我执行的统一重构路线

本节是方案完成后的唯一实施顺序。后续优化不再另开一套编号，也不再并行维护多份 TODO。

### 阶段一：版本与资料归一

1. 将 runtime_asset_requirements.json、资产路径、sidecar、manifest fragment 和交付目录统一到 UW-UPGRADE-1.0。
2. 将历史 v002–v008 文件移入已有审计归档规则，保留 hash 和失败原因；不删除、不覆盖。
3. 清理 7 个历史中间文件的扫描污染，使 materials check 回到 0 errors。
4. 建立唯一资产索引：资产组、文件名、尺寸、锚点、触发 ID、runtime 路径、hash、审核状态。

阶段完成标准：任何新文件只出现 UW-UPGRADE-1.0 前缀；任何旧版本只能在审计目录中出现。

### 阶段二：视觉基础和场景模块

1. 先制作地图、一个角色和一张书库背景的 golden slice。
2. 在 Phaser 中统一图层深度、脚底锚点、碰撞盒、遮挡规则、摄像机缓动和目标路径。
3. 将程序化色块、token 和调试网格降级为仅在资源加载失败时使用的 fallback。
4. 建立建筑、树、道路、道具和交互点的 2.5D 模块注册表。
5. 以桌面和窄屏截图检查目标可见性、角色识别度、文本安全区和场景裁切。

阶段完成标准：玩家能从村道移动到书库和巨神树；两个地点无需说明即可区分；没有地图/角色资产 404。

### 阶段三：玩法和交互重构

1. 将活动统一成 preview -> observe -> choose -> commit -> result 五段流程。
2. 所有活动在提交前显示时间、资源、立即收益和回响对象；拒绝时不写任何状态。
3. 把线索拼接、路线观察和关系交付做成三个 30–90 秒短玩法。
4. 将 NPC 回访、表情、记忆摘要和关系变化绑定到同一个 result DTO。
5. 为到达、阻挡、资源不足、重复访问、完成和回响增加统一 toast/VFX/SFX 触发 ID。
6. 重新整理移动端底栏和弹窗，确保一个屏幕只有一个强 CTA。

阶段完成标准：新玩家 60 秒内完成一次有效互动；每个选择都能在当下看到代价和人物反应；自动测试能证明失败不部分写状态。

### 阶段四：设定和内容表现统一

1. 以当前四幕 N01-N10 为唯一正典事实表，整理角色年龄、服装、关系动机、地点名称和时间锚点。
2. 让村庄生活活动只补充人物关系、线索和世界规则，不新增抓捕后事实。
3. 为六个场景建立统一地点短句、环境音、交互物和可回访变化。
4. 将早期选择的回响写成玩家可读的短句和表情，不暴露内部 flag。
5. 以终点关键图、整合骑士表现和告别动作收束情绪，不制作终点之后的剧情。

阶段完成标准：新玩家能说出为什么越界、谁记住了什么以及为什么爱丽丝仍会被带走。

### 阶段五：完整素材接入

1. 按 MAP、CHARACTERS、SCENES、UI、VFX、PORTRAITS、KEYART、ANIMATION、MUSIC、AMBIENCE、SFX、WORLD-DATA 资产组依次接入。
2. 每接入一组只做最小可用切片，先完成游戏内桌面/触控验收，再扩展同类资产。
3. 用 useAudio 统一 loop、ducking、独立音量和失败 fallback；用 trigger id 统一 VFX/SFX。
4. 所有正式文件写入唯一 manifest，runtime 目录只保留一套 UW-UPGRADE-1.0。

阶段完成标准：地图、角色、背景、UI、VFX、BGM、ambience、SFX 和终点表现在同一视觉语言下工作，没有候选素材冒充正式素材。

### 阶段六：质量门和真人优化

1. 重跑材料、runtime specs、readiness、后端 pytest、前端 unit、build、Playwright 和 diff check。
2. 用新游戏跑完整 N01-N10，验证 alice_captured 后剧情、日期、NPC 和 authored 写入均被拒绝。
3. 组织 3 名陌生玩家试玩，记录卡点和完成率，不用自动化结果替代真人数据。
4. 只修复最高频问题；每轮更新本文件、CURRENT_STATUS.md、CHANGELOG.md 和唯一 manifest。

阶段完成标准：materials=ready、story=ready、自动质量门全部通过、三名玩家完成记录齐全，才能宣称本轮升级完成。

## 18. 最终执行原则

以后所有重构都遵循同一个判断顺序：先保证可读，再增加表现；先保证选择有后果，再增加内容数量；先完成一处可玩的垂直切片，再批量生成素材；先通过游戏内验收，再提高台账状态。

本文件就是 UW 的唯一升级方案。后续实现、素材生成、地图重构、玩法优化和试玩修复均以 UW-UPGRADE-1.0 为唯一目标，历史版本只用于追溯，不再作为工作入口。
