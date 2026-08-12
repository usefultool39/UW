import { DEFAULT_MAP_ID, getSceneLabel as getRegisteredSceneLabel, getWorldBackgroundAsset } from './sceneRegistry.js'
export { MAP_DEFINITIONS, SCENE_DEFINITIONS, SCENE_TRANSITION_BLUEPRINTS } from './sceneRegistry.js'

export const GAME_CHAPTER_INFO = { kicker: 'UNDERWORLD · 序章', title: '卢利特村' }
export const WORLD_ASSETS = { background: getWorldBackgroundAsset(DEFAULT_MAP_ID) }

export const AGENT_ART_MODES = {
  proceduralPixel: 'procedural_pixel',
  spriteAsset: 'sprite_asset'
}

export const AGENTS = {
  player: {
    label: '桐人',
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
    label: '尤吉欧',
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
    label: '加利塔',
    artMode: AGENT_ART_MODES.proceduralPixel,
    textureKey: 'char_garret_pixel',
    haloColor: 0xb9d57a,
    tokenHeight: 48,
    palette: { hair: 0x6d5840, skin: 0xd9b58c, body: 0x58703b, accent: 0xb9d57a, cape: 0x34452d, outline: 0x172014, boots: 0x3f3020, weapon: 0xb6c7b0, style: 'sentry' },
    animations: { idle: null, walk: null }
  },
  rulid_elder: {
    label: '加斯夫特',
    artMode: AGENT_ART_MODES.proceduralPixel,
    textureKey: 'char_rulid_elder_pixel',
    haloColor: 0xd8b889,
    tokenHeight: 46,
    palette: { hair: 0xd8d1bf, skin: 0xd9b58c, body: 0x715a3c, accent: 0xd8b889, cape: 0x4b3b28, outline: 0x24180f, boots: 0x3a2a1c, weapon: 0xe8d7ad, style: 'elder' },
    animations: { idle: null, walk: null }
  },
  kirito: {
    label: '桐人',
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
  ch1pc_n01_rulid_daily: { title: '卢利特村的清晨', clue: '雨后的村子还安静着。去北门附近与爱丽丝、尤吉欧会合，开始今天的三人之约。', scene_id: 'north_gate', day: 1 },
  ch1pc_n02_gigas_calling: { title: '巨神树的天职', clue: '尤吉欧说起巨神树的天职。砍树之外，他真正想问的是：世界是否只允许我们这样活着。', scene_id: 'gigas_clearing', day: 1 },
  ch1pc_n03_talk_index_end_mountains: { title: '禁忌目录与尽头山脉', clue: '夜里三人说起禁忌目录。目录禁止越界，可尽头山脉另一侧的事，已经让爱丽丝放不下心。', scene_id: 'home_hearth', day: 1 },
  ch1pc_n04_travel_to_end_mountains: { title: '前往尽头山脉', clue: '第二天清晨，从北门出发前往尽头山脉洞窟。出发前决定带走什么——食物、工具，还是记录。', scene_id: 'north_gate', day: 2 },
  ch1pc_n05_encounter_dark_territory_injured: { title: '暗黑界一侧的受伤者', clue: '洞窟外躺着一名受伤者。爱丽丝想救人，而规则说：跨过那条线，就是触犯禁忌。', scene_id: 'north_boundary', day: 2 },
  ch1pc_n06_alice_crosses_boundary: { title: '越界', clue: '爱丽丝跨过了界线。桐人的反应、尤吉欧的沉默，都会写进三个人此后的记忆。', scene_id: 'north_boundary', day: 2 },
  ch1pc_n07_return_to_rulid: { title: '返村', clue: '三人带着无法抹去的秘密回到卢利特村。夜里的村子灯火如常，但有些东西已经变了。', scene_id: 'village_square', day: 2 },
  ch1pc_n08_knights_arrive_village: { title: '整合骑士进村', clue: '第三天清晨，整合骑士进村宣判。广场上围满村民，爱丽丝站在你身边。', scene_id: 'village_square', day: 3 },
  ch1pc_n09_alice_farewell: { title: '告别', clue: '宣判之后，爱丽丝与你们告别。她问的不是能不能留下，而是你会不会记得。', scene_id: 'home_hearth', day: 3 },
  ch1pc_n10_alice_captured: { title: '被带走', clue: '整合骑士带走了爱丽丝。卢利特村的清晨还在，只是少了一个人。', scene_id: 'village_square', day: 3 }
}

export const FLAG_CLUE_HINTS = {
  d1_bond: { title: '三人日常', body: '第一天清晨的会合，让爱丽丝、尤吉欧与桐人的羁绊有了起点。', meta: 'Day 1 线索' },
  d2_calling_pace: { title: '巨神树的天职', body: '尤吉欧谈起天职时的语气，让桐人第一次认真去想规则之外的事。', meta: 'Day 1 线索' },
  d3_talk_about_index: { title: '禁忌目录的夜晚', body: '三人夜里谈起禁忌目录与尽头山脉。越界的念头，从这里开始发芽。', meta: 'Day 1 线索' },
  d4_pack_food: { title: '出发前的准备', body: '出发前带上的食物与记录，决定了三个人能走多远、记得多清。', meta: 'Day 2 线索' },
  d4_pack_tool: { title: '出发前的工具', body: '麻绳与备用工具被系紧在背包外侧。准备充分，不等于可以越过规则。', meta: 'Day 2 线索' },
  d4_pack_record: { title: '记录本放在最上层', body: '记录本放在背包最上层。没人知道它会写下什么，但三个人都同意不凭记忆改写事实。', meta: 'Day 2 线索' },
  d5_approach: { title: '受伤者面前的选择', body: '暗黑界一侧的受伤者面前，你们选择了如何靠近。这个选择写进了爱丽丝的救人之心。', meta: 'Day 2 线索' },
  d6_alice_crossed_instant: { title: '越界的一瞬', body: '爱丽丝跨过界线的那一瞬，桐人的反应被永远记住了。', meta: 'Day 2 线索' },
  d7_return_disclosure: { title: '返村后的坦白', body: '回到卢利特村后，你们选择如何面对自己做过的事。', meta: 'Day 2 线索' },
  d8_knight_arrival_posture: { title: '骑士面前的姿态', body: '整合骑士进村宣判时，桐人选择站在爱丽丝身边的方式。', meta: 'Day 3 线索' },
  d9_farewell_choice: { title: '告别时的承诺', body: '告别时说的话，会成为爱丽丝被带走后你们各自记住的东西。', meta: 'Day 3 线索' },
  final_log: { title: '序章终章', body: '爱丽丝被整合骑士带走。卢利特村的序章到此收束。', meta: '终章' },
  forest_anomaly_seen: { title: '北门边境异常', body: '你们在北门外确认了边境另一侧的异常。这不是传闻，是亲眼所见。', meta: 'Day 2 线索' },
  precapture_mode: { title: '序章主线', body: '故事进入卢利特村序章主线：日常、越界、宣判与告别。', meta: '主线' }
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
  const sceneHint = sceneId ? `你现在在${getSceneLabel(sceneId)}。` : ''

  if (ending === 'alice_captured') {
    return '序章的故事已经收束：爱丽丝被整合骑士带走了。你可以在村子里走走，或打开菜单查看记忆图鉴与这段日子的记录。'
  }
  if (ending) return '这一章已经结束。你仍可以在村子里走动，但故事不会再往前推进。'

  const done = new Set(simState.completed_event_ids || [])
  const has = (id) => done.has(id) || Number(flags[id.replace('ch1pc_', '')] || 0) > 0

  if (!has('ch1pc_n01_rulid_daily')) return `${sceneHint}去北门附近找爱丽丝和尤吉欧会合——新的一天从三人的约定开始。`.trim()
  if (!has('ch1pc_n02_gigas_calling')) return `${sceneHint}跟尤吉欧一起去巨神树。他今天想谈的不是砍树，而是天职。`.trim()
  if (!has('ch1pc_n03_talk_index_end_mountains')) return `${sceneHint}入夜后回家里炉火边，三人会说起禁忌目录与尽头山脉。`.trim()
  if (!has('ch1pc_n04_travel_to_end_mountains')) return `${sceneHint}第二天清晨，去北门准备出发。决定出发前带走什么。`.trim()
  if (!has('ch1pc_n05_encounter_dark_territory_injured')) return `${sceneHint}沿北门外侧前进，洞窟附近有一名受伤者。`.trim()
  if (!has('ch1pc_n06_alice_crosses_boundary')) return `${sceneHint}爱丽丝走向了界线。跟着她，还是拉住她——这一瞬很重要。`.trim()
  if (!has('ch1pc_n07_return_to_rulid')) return `${sceneHint}带着无法抹去的秘密，三人踏上返村的路。`.trim()
  if (!has('ch1pc_n08_knights_arrive_village')) return `${sceneHint}第三天清晨，整合骑士进村。去村道广场，站在爱丽丝身边。`.trim()
  if (!has('ch1pc_n09_alice_farewell')) return `${sceneHint}宣判之后，爱丽丝在等你。把该说的话说出口。`.trim()
  if (!has('ch1pc_n10_alice_captured')) return `${sceneHint}整合骑士要带爱丽丝走了。去广场，见证这个清晨。`.trim()

  return `${sceneHint}序章的故事已经收束。打开菜单可以查看记忆图鉴；也可以继续在村子里走一走。`.trim()
}

