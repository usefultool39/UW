import { DEFAULT_MAP_ID, getSceneLabel as getRegisteredSceneLabel, getWorldBackgroundAsset } from './sceneRegistry.js'
export { MAP_DEFINITIONS, SCENE_DEFINITIONS, SCENE_TRANSITION_BLUEPRINTS } from './sceneRegistry.js'

export const GAME_CHAPTER_INFO = { kicker: '第一章 · 清晨的边境', title: '露茵村' }
export const WORLD_ASSETS = { background: getWorldBackgroundAsset(DEFAULT_MAP_ID) }

export const AGENT_ART_MODES = {
  proceduralPixel: 'procedural_pixel',
  spriteAsset: 'sprite_asset'
}

export const AGENTS = {
  player: {
    label: 'Kirito',
    artMode: AGENT_ART_MODES.proceduralPixel,
    textureKey: 'char_player_pixel',
    asset: '/assets/game/player-token-tv.png',
    haloColor: 0x5ecfff,
    tokenHeight: 48,
    palette: { hair: 0x111827, skin: 0xe8c7a6, body: 0x151a22, accent: 0x5ecfff, cape: 0x080b12, outline: 0x03050a, boots: 0x0a0f18, weapon: 0xdbeafe, style: 'dual_blades' },
    animations: { idle: null, walk: null }
  },
  alice: {
    label: '爱丽丝',
    artMode: AGENT_ART_MODES.proceduralPixel,
    textureKey: 'char_alice_pixel',
    asset: '/assets/game/alice-token-tv.png',
    haloColor: 0xf6d36e,
    tokenHeight: 48,
    palette: { hair: 0xf6d36e, skin: 0xf0d0af, body: 0xe7edf6, accent: 0x4f8ee8, cape: 0x245d63, outline: 0x172036, boots: 0x2f3a55, weapon: 0xfde68a, style: 'gold_knight' },
    animations: { idle: null, walk: null }
  },
  eugeo: {
    label: '悠吉欧',
    artMode: AGENT_ART_MODES.proceduralPixel,
    textureKey: 'char_eugeo_pixel',
    asset: '/assets/game/eugeo-token-tv.png',
    haloColor: 0x7dd3fc,
    tokenHeight: 48,
    palette: { hair: 0xd8b86b, skin: 0xe2c49e, body: 0x2f5f9f, accent: 0x7dd3fc, cape: 0x1e3a5f, outline: 0x111a2e, boots: 0x1d2638, weapon: 0x93c5fd, style: 'blue_rose' },
    animations: { idle: null, walk: null }
  },
  selka: {
    label: '赛尔卡',
    artMode: AGENT_ART_MODES.proceduralPixel,
    textureKey: 'char_selka_pixel',
    haloColor: 0xf7b7c8,
    tokenHeight: 44,
    palette: { hair: 0x5d3a2b, skin: 0xf0d0af, body: 0xf2d2db, accent: 0xf7b7c8, cape: 0x7f4f64, outline: 0x2b1a1c, boots: 0x4a2d28, weapon: 0xfde68a, style: 'healer' },
    animations: { idle: null, walk: null }
  },
  garret: {
    label: '加雷特',
    artMode: AGENT_ART_MODES.proceduralPixel,
    textureKey: 'char_garret_pixel',
    haloColor: 0xb9d57a,
    tokenHeight: 48,
    palette: { hair: 0x6d5840, skin: 0xd9b58c, body: 0x58703b, accent: 0xb9d57a, cape: 0x34452d, outline: 0x172014, boots: 0x3f3020, weapon: 0xb6c7b0, style: 'sentry' },
    animations: { idle: null, walk: null }
  },
  rulid_elder: {
    label: '罗温',
    artMode: AGENT_ART_MODES.proceduralPixel,
    textureKey: 'char_rulid_elder_pixel',
    haloColor: 0xd8b889,
    tokenHeight: 46,
    palette: { hair: 0xd8d1bf, skin: 0xd9b58c, body: 0x715a3c, accent: 0xd8b889, cape: 0x4b3b28, outline: 0x24180f, boots: 0x3a2a1c, weapon: 0xe8d7ad, style: 'elder' },
    animations: { idle: null, walk: null }
  },
  kirito: {
    label: 'Kirito',
    artMode: AGENT_ART_MODES.proceduralPixel,
    textureKey: 'char_kirito_pixel',
    haloColor: 0x5ecfff,
    tokenHeight: 48,
    palette: { hair: 0x111827, skin: 0xe2c49e, body: 0x151a22, accent: 0x5ecfff, cape: 0x080b12, outline: 0x03050a, boots: 0x0a0f18, weapon: 0xdbeafe, style: 'dual_blades' },
    animations: { idle: null, walk: null }
  }
}

export const FALLBACK_AGENT = {
  label: 'NPC',
  artMode: AGENT_ART_MODES.proceduralPixel,
  textureKey: 'char_generic_pixel',
  haloColor: 0x5ecfff,
  tokenHeight: 40,
  palette: { hair: 0x29313f, skin: 0xe6c7a4, body: 0x344256, accent: 0xf6d36e, cape: 0x1f6f68, outline: 0x101827, boots: 0x111827 },
  animations: { idle: null, walk: null }
}
export const AGENT_ART_KEYS = Object.fromEntries(Object.entries(AGENTS).map(([id, cfg]) => [id, cfg.textureKey]))

export const AGENT_TEXTURE_FALLBACKS = Object.fromEntries(
  [...Object.values(AGENTS), FALLBACK_AGENT]
    .filter((cfg) => cfg.artMode === AGENT_ART_MODES.proceduralPixel)
    .map((cfg) => [cfg.textureKey, { ...(cfg.palette || {}), label: cfg.label }])
)

export function shouldLoadAgentSpriteAsset(cfg) {
  return cfg?.artMode === AGENT_ART_MODES.spriteAsset && !!cfg.asset
}

export const TIME_BAND_LABELS = { morning: '清晨', afternoon: '白昼', evening: '傍晚', night: '深夜' }

export const STORY_EVENT_HINTS = {
  ch1_d1_reading_clue: { title: '书库里的边界记录', clue: '旧记录写到北方边界会突然失去鸟声，像规则被按住。', scene_id: 'church_library', day: 1 },
  ch1_d1_training_with_eugeo: { title: '古誓树旁的训练', clue: '尤里把训练看成确认世界仍按规则运转的方式。', scene_id: 'gigas_clearing', day: 1 },
  ch1_d2_forest_anomaly: { title: '森林忽然安静', clue: '古誓树清场附近的风声断了一瞬。', scene_id: 'gigas_clearing', day: 2 },
  ch1_d2_npc_disagreement: { title: '晚餐桌边的分歧', clue: '异常变成了餐桌边没说出口的话。', scene_id: 'home_hearth', day: 2 },
  ch1_d3_boundary_choice: { title: '第三天：边界线前', clue: '你们终于站到那条看不见的边界前。', scene_id: 'north_gate', day: 3 },
  ch1_d4_after_boundary_debrief: { title: '第四天：书库复盘', clue: '边界事件被写成会影响后续一个月的记录。', scene_id: 'reading_hall', day: 4 },
  ch1_d7_first_boundary_drill: { title: '北门巡查演练', clue: '你们把安全距离、信号和撤退路线变成三人流程。', scene_id: 'north_gate', day: 7 },
  ch1_d12_village_trust: { title: '把巡查变成村务', clue: '北门巡查开始影响村里对你们的信任。', scene_id: 'village_square', day: 12 },
  ch1_d18_silent_line_rehearsal: { title: '静默线演练', clue: '你们用记录、刻印和同伴分工复核静默线。', scene_id: 'north_gate', day: 18 },
  ch1_d24_expedition_pack: { title: '第二十四天：远征包', clue: '静默线演练结束，第一次正式远征已经近在眼前。小屋里的补给选择会决定第二月是稳妥推进，还是深入调查。', scene_id: 'home_hearth', day: 24 },
  ch1_d30_first_month_gate: { title: '北门前夜', clue: '第一月的结尾会把第二月路线定下来。', scene_id: 'north_gate', day: 30 }
}

export const FLAG_CLUE_HINTS = {
  clue_boundary_record: { title: '北境异常记录', body: '你读到了北方边界的异常记录：鸟声会突然消失，安静得不自然。', meta: '来自书库调查' },
  alice_warned_boundary: { title: '艾琳知道了边界记录', body: '你把书页内容告诉了艾琳，她开始担心北边今天太安静。', meta: '艾琳会记住' },
  kept_boundary_note: { title: '暂时隐瞒的书页线索', body: '你把边界记录先记在心里，决定观察村子和森林的变化。', meta: '关系里可能留下暗线' },
  trained_with_eugeo: { title: '古誓树训练完成', body: '你在古誓树旁完成了第一天训练，尤里会根据你的做法重新看你。', meta: '来自古誓树清场' },
  eugeo_heard_boundary_question: { title: '训练时追问边界', body: '你把古誓树训练和北方异常连了起来，尤里开始认真看待这件事。', meta: '尤里会记住' },
  forest_anomaly_seen: { title: '森林异常被确认', body: '你们看见古誓树清场附近的风声突然断掉，异常不再只是书页传闻。', meta: 'Day 2 线索' },
  promise_investigate_with_eugeo: { title: '继续调查的约定', body: '你答应和尤里继续确认北方边界的异常。', meta: '承诺' },
  boundary_risk_taken: { title: '独自靠近异常', body: '你曾独自往异常方向多走了几步，这会让同伴担心。', meta: '紧张点' },
  month01_debrief_done: { title: '第一月复盘完成', body: '你们把边界事件整理成后续一个月可以执行的路线。', meta: 'Day 4-6' },
  month01_drill_done: { title: '北门巡查流程', body: '北门安全距离、信号和撤退路线已经被三人演练过。', meta: 'Day 7-10' },
  month01_village_trust: { title: '村内信任推进', body: '北门巡查不再只是三人的秘密，村子开始被卷入后续准备。', meta: 'Day 12-16' },
  month01_silent_line_rehearsed: { title: '静默线演练完成', body: '你们用记录、刻印和同伴复核确认了静默线仍在变化。', meta: 'Day 18-22' },
  month01_expedition_ready: { title: '远征包备好', body: '第一次正式边境行动需要的补给和退路已经准备好。', meta: 'Day 24-27' },
  month01_gate_resolved: { title: '第一月路线收束', body: '北门前夜的选择已经决定第二月会从哪条路线展开。', meta: 'Day 28-30' }
}

export const LANDMARK_ART_CONFIGS = [
  { renderer: 'library', poiIds: ['poi_reading_quest', 'ix_reading_desk'] },
  { renderer: 'home', poiIds: ['ix_home_bed'] },
  { renderer: 'gigasTree', poiIds: ['ix_gigas_tree'] },
  { renderer: 'teleportGate', poiIds: ['ix_teleport_gate'] },
  { renderer: 'boundaryGate', poiIds: ['ix_north_gate'] },
  { renderer: 'boundaryGate', poiIds: ['ix_east_highroad_gate'] },
  { renderer: 'ferryGate', poiIds: ['ix_south_lake_gate'] }
]

export function getAgentConfig(agentId) {
  if (agentId && AGENTS[agentId]) return AGENTS[agentId]
  return { ...FALLBACK_AGENT, label: agentId || FALLBACK_AGENT.label }
}
export function getAgentLabel(agentId) { return getAgentConfig(agentId).label }
export function getTimeBandLabel(timeBand) { return TIME_BAND_LABELS[timeBand] || timeBand || '未知' }
export function getSceneLabel(sceneId) { return getRegisteredSceneLabel(sceneId) }
export function getStoryEventHint(eventId) { return STORY_EVENT_HINTS[eventId] || { title: eventId || '未知事件', clue: '这条剧情已经被记录。', day: 1 } }
export function getFlagClueHint(flagKey) { return FLAG_CLUE_HINTS[flagKey] || null }

export function getQuestGuide(simState) {
  if (!simState) return '加载中'
  const ending = simState.chapter_ending_id
  const flags = simState.flags || {}
  const sceneId = simState.player?.scene_id || simState.scene_id || ''
  const day = Number(simState.day || 1)
  const sceneHint = sceneId ? `你现在在${getSceneLabel(sceneId)}。` : ''
  if (ending && !flags.month01_debrief_done) return '第一章已经收束。休息到第四天后，在书库把边界事件复盘成第一月路线。'
  if (flags.month01_debrief_done && !flags.month01_drill_done) return '第一月推进中：休息到第七天后去北门，把安全距离和撤退信号演练成流程。'
  if (flags.month01_drill_done && !flags.month01_village_trust) return '第一月推进中：第十二天起到村广场处理巡查公开度和补给问题。'
  if (flags.month01_village_trust && !flags.month01_silent_line_rehearsed) return '第一月推进中：第十八天起回到北门，复核静默线和同伴分工。'
  if (flags.month01_silent_line_rehearsed && !flags.month01_expedition_ready) return '远征准备：静默线演练已经结束。第二十四天起回小屋整理远征包，先确认同伴担心，再决定第二月走稳妥路线还是深入调查。'
  if (flags.month01_expedition_ready && !flags.month01_gate_resolved) return '第一月末：第二十八天后去北门前夜。先回应同伴的最后复核，再把第二月路线定下来。'
  if (flags.month01_gate_resolved) {
    if (flags.month01_route_order) return '第一月已经收束：第二月从稳守北门和村务协同展开。先确认巡查公开度、补给线和同伴分工。'
    if (flags.month01_route_expedition) return '第一月已经收束：第二月从边境远征展开。先确认远征包、撤退路线和静默线复核。'
    if (flags.month01_route_quiet) return '第一月已经收束：第二月从静默观察展开。先整理记录、标注异常频率，再决定是否越过北门。'
    return '第一月已经收束：第二月边境远征入口已经埋好。'
  }
  const active = simState.active_event_ids || []
  if (active.length) return `${sceneHint}村子里有新的抉择在等你：靠近金色标记，或先回应附近同伴的主动邀约。`.trim()
  const intents = Array.isArray(simState.npc_intents) ? simState.npc_intents : []
  if (intents.length) {
    const intent = intents[0]
    return `${sceneHint}${getAgentLabel(intent.npc_id)}正在等你的回应：${intent.title}。走近同伴，先把这一步说清楚。`.trim()
  }
  const node = simState.story_node_id || ''
  const doneRead = flags.prologue_reading_done === 1
  if (node === 'mq00_tutorial' && !doneRead) return '细雨刚停。先去村西书库看看旧记录，或沿主路去古誓树清场找尤里。'
  if (node === 'mq00_tutorial' && doneRead) return '书页里的边界记录让人不安。把这件事告诉谁，会改变今天的气氛。'
  if (node === 'mq01_tree_arc' || String(node).startsWith('mq01')) return '到古誓树旁找尤里。训练只是表面，真正的问题是北边为什么突然安静下来。'
  if (day <= 3) return `${sceneHint}沿主路在书库、古誓树和家中之间走一圈；若没有新线索，就休息推进到下一个时段。`.trim()
  return `${sceneHint}查看日志里的第一月路线，去北门、村广场或小屋寻找下一处金色标记；没有新事时先休息推进时间。`.trim()
}
