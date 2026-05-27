export const CLIENT_CONTRACT_VERSION = 'client-contract-2026-05-15-v2'

export const DEFAULT_WORLD_MAP_ID = 'novice_open'

export const API_ROUTES = Object.freeze({
  health: '/api/health',
  config: '/api/config',
  state: '/api/state',
  events: '/api/events',
  step: '/api/step',
  reset: '/api/reset',
  saveExport: '/api/save/export',
  saveImport: '/api/save/import',
  worldMap: '/api/world/map',
  worldMapById: (mapId) => `/api/world/maps/${encodeURIComponent(mapId)}`,
  worldRegions: '/api/world/regions',
  sceneActivities: '/api/world/scene_activities',
  storyCatalog: '/api/story/catalog',
  storyMonthPlan: '/api/story/month_plan',
  availableStoryEvents: '/api/story/available_events',
  playerAction: '/api/player/action',
  storyAdvance: '/api/story/advance',
  storyChoose: '/api/story/choose',
  dailyTick: '/api/sim/daily_tick',
  npcProfile: (npcId) => `/api/npc/${encodeURIComponent(npcId)}/profile`,
  dialogue: '/api/dialogue'
})

export const PLAYER_ACTION_KINDS = Object.freeze({
  moveMap: 'move_map',
  moveWorld: 'move_world',
  moveScene: 'move_scene',
  enterScene: 'enter_scene',
  interactWithHub: 'interact_with_hub',
  sceneActivity: 'scene_activity',
  respondNpcIntent: 'respond_npc_intent',
  setFlag: 'set_flag',
  dailyTick: 'daily_tick',
  compoundSleep: 'compound_sleep',
  restUntilNextDay: 'rest_until_next_day'
})
