import { DEFAULT_MAP_ID, getSceneLabel as getRegisteredSceneLabel, getWorldBackgroundAsset } from './sceneRegistry.js'
export { MAP_DEFINITIONS, SCENE_DEFINITIONS, SCENE_TRANSITION_BLUEPRINTS } from './sceneRegistry.js'

export const GAME_CHAPTER_INFO = {
  kicker: '30小镇 · 第一章',
  title: '北境新手村'
}

export const WORLD_ASSETS = {
  background: getWorldBackgroundAsset(DEFAULT_MAP_ID)
}

export const AGENTS = {
  player: {
    label: '你',
    textureKey: 'char_player_traveler',
    asset: '/assets/game/player-token-tv.png',
    haloColor: 0xfbbf24,
    tokenHeight: 58
  },
  alice: {
    label: '爱丽丝',
    textureKey: 'char_alice_village',
    asset: '/assets/game/alice-token-tv.png',
    haloColor: 0x70e0bb,
    tokenHeight: 52
  },
  eugeo: {
    label: '优吉欧',
    textureKey: 'char_eugeo_woodsman',
    asset: '/assets/game/eugeo-token-tv.png',
    haloColor: 0xa78bfa,
    tokenHeight: 52
  },
  kirito: {
    label: '桐人',
    textureKey: 'char_kirito_swordsman',
    haloColor: 0x5ecfff,
    tokenHeight: 52
  }
}

export const FALLBACK_AGENT = {
  label: 'NPC',
  textureKey: 'char_generic_npc',
  haloColor: 0x5ecfff,
  tokenHeight: 52
}

export const AGENT_ART_KEYS = Object.fromEntries(
  Object.entries(AGENTS).map(([id, cfg]) => [id, cfg.textureKey])
)

export const AGENT_TEXTURE_FALLBACKS = {
  [AGENTS.player.textureKey]: {
    hair: 0x182033,
    skin: 0xe9c8a5,
    body: 0x25324d,
    accent: 0xf2b84b,
    cape: 0x14505a
  },
  [AGENTS.alice.textureKey]: {
    hair: 0xf1c86a,
    skin: 0xf0d0af,
    body: 0x2a6669,
    accent: 0x70e0bb,
    cape: 0x376b87
  },
  [AGENTS.eugeo.textureKey]: {
    hair: 0x91a9db,
    skin: 0xd9bd93,
    body: 0x3d3a66,
    accent: 0xa78bfa,
    cape: 0x2f4d6a
  },
  [AGENTS.kirito.textureKey]: {
    hair: 0x141820,
    skin: 0xe2c49e,
    body: 0x1c2332,
    accent: 0x5ecfff,
    cape: 0x0c111b
  },
  [FALLBACK_AGENT.textureKey]: {
    hair: 0x29313f,
    skin: 0xe6c7a4,
    body: 0x344256,
    accent: 0xf6d36e,
    cape: 0x1f6f68
  }
}

export const TIME_BAND_LABELS = {
  morning: '清晨',
  afternoon: '白昼',
  evening: '傍晚',
  night: '深夜'
}

export const LANDMARK_ART_CONFIGS = [
  { renderer: 'library', poiIds: ['poi_reading_quest', 'ix_reading_desk'] },
  { renderer: 'home', poiIds: ['ix_home_bed'] },
  { renderer: 'gigasTree', poiIds: ['ix_gigas_tree'] }
]

export function getAgentConfig(agentId) {
  if (agentId && AGENTS[agentId]) return AGENTS[agentId]
  return {
    ...FALLBACK_AGENT,
    label: agentId || FALLBACK_AGENT.label
  }
}

export function getAgentLabel(agentId) {
  return getAgentConfig(agentId).label
}

export function getTimeBandLabel(timeBand) {
  return TIME_BAND_LABELS[timeBand] || timeBand || '未知'
}

export function getSceneLabel(sceneId) {
  return getRegisteredSceneLabel(sceneId)
}

export function getQuestGuide(simState) {
  if (!simState) return '加载中…'
  const ending = simState.chapter_ending_id
  if (ending === 'order') return '第一章已收束：你选择遵守规则并回村报告。可以查看 NPC 关系，看看这件事留下了什么。'
  if (ending === 'cross') return '第一章已收束：你选择越过边界确认异常。NPC 已经记住这个决定。'
  if (ending === 'hide') return '第一章已收束：你选择隐瞒异常。关系里会留下不容易说清的紧张。'
  const active = simState.active_event_ids || []
  if (active.length) return '地图上出现了金色章节事件标记。靠近或直接点击标记，做出会被 NPC 记住的选择。'
  const node = simState.story_node_id || ''
  const flags = simState.flags || {}
  const doneRead = flags.prologue_reading_done === 1
  if (node === 'mq00_tutorial' && !doneRead) {
    return '去西北书库翻那本被反复翻过的旧书，或沿主路去东侧巨树找优吉欧训练。金色「！」代表会推进第一章的关键事件。'
  }
  if (node === 'mq00_tutorial' && doneRead) {
    return '书页里的规则让你有些在意。去巨树旁找优吉欧，或点击地图上的章节事件，把线索真正带进今天的选择。'
  }
  if (node === 'mq01_tree_arc' || String(node).startsWith('mq01')) {
    return '到巨树旁找优吉欧。你可以和他谈谈训练、巨树，或问问最近村边的异常。'
  }
  return `当前章节节点：${node}。在地图上寻找可互动的 NPC 或地点。`
}
