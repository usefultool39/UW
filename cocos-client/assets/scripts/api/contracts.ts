export const CLIENT_CONTRACT_VERSION = 'client-contract-2026-05-15-v2'
export const DEFAULT_API_BASE = 'http://127.0.0.1:8765'
export const DEFAULT_WORLD_MAP_ID = 'novice_open'

export const ApiRoutes = {
  state: '/api/state',
  events: '/api/events',
  reset: '/api/reset',
  worldMap: '/api/world/map',
  worldMapById: (mapId: string) => `/api/world/maps/${encodeURIComponent(mapId)}`,
  sceneActivities: '/api/world/scene_activities',
  availableStoryEvents: '/api/story/available_events',
  playerAction: '/api/player/action',
  storyChoose: '/api/story/choose',
  dialogue: '/api/dialogue',
  npcProfile: (npcId: string) => `/api/npc/${encodeURIComponent(npcId)}/profile`,
  saveExport: '/api/save/export',
  saveImport: '/api/save/import'
} as const

export const PlayerActionKinds = {
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
} as const

export type TimeBand = 'morning' | 'afternoon' | 'evening' | 'night'

export interface PlayerState {
  map_id: string
  scene_id: string
  tile_x: number
  tile_y: number
  hp: number
  max_hp: number
  mp: number
  max_mp: number
  stamina: number
  max_stamina: number
}

export interface AgentState {
  id: string
  map_id: string
  scene_id: string
  tile_x: number
  tile_y: number
  mood?: number
  current_goal?: string | null
}

export interface WorldState {
  day: number
  tick: number
  time_band: TimeBand
  weather: string
  weather_label: string
  story_node_id: string
  flags: Record<string, number>
  player: PlayerState
  agents: AgentState[]
  npc_intents?: NpcIntent[]
  active_event_ids: string[]
  completed_event_ids: string[]
}

export interface NpcIntent {
  id: string
  npc_id: string
  kind: string
  title: string
  description?: string
  scene_id: string
  map_id?: string
  tile_x: number
  tile_y: number
  priority?: number
  reason?: string
  action?: Record<string, unknown>
  stakes?: string[]
  response_options?: Array<Record<string, unknown>>
}

export interface MapVisualConfig {
  style?: string
  background?: boolean
  tileset_manifest?: string
  scale?: Record<string, unknown>
  camera?: Record<string, number>
  movement?: Record<string, number | boolean>
  performance?: Record<string, number | boolean>
}

export interface SceneZone {
  scene_id: string
  x1: number
  y1: number
  x2: number
  y2: number
  label?: string
  regionType?: string
}

export interface MapPoi {
  id: string
  label?: string
  kind?: string
  scene_id?: string
  tile_x: number
  tile_y: number
  approach_tile_x?: number
  approach_tile_y?: number
  radius?: number
}

export interface MapData {
  id: string
  width: number
  height: number
  tile_size: number
  visual?: MapVisualConfig
  spawn: { x: number; y: number; scene_id?: string }
  walkable: number[]
  scene_zones: SceneZone[]
  pois: MapPoi[]
  rows: string[]
}

export interface StoryEvent {
  id: string
  kind: string
  title: string
  description?: string
  location?: { scene_id?: string; tile_x?: number; tile_y?: number }
  participants?: string[]
  choices?: Array<{ id: string; label: string; hint?: string }>
}

export interface SceneActivityChoice {
  id: string
  label: string
  hint?: string
  tone?: string
}

export interface SceneActivity {
  id: string
  scene_id?: string
  scene_ids?: string[]
  poi_id?: string
  title: string
  label?: string
  description?: string
  time_bands?: TimeBand[]
  interaction_kind?: 'reading_keywords' | 'meal_choice' | string
  choices?: SceneActivityChoice[]
}

export interface PlayerActionBody {
  kind: string
  map_id?: string
  entry_point?: string
  scene_id?: string
  poi_id?: string
  flag_key?: string
  flag_value?: number
  activity_id?: string
  activity_choice?: string
  intent_id?: string
  response_id?: string
  tile_x?: number
  tile_y?: number
  n?: number
  daily_n?: number
}

export interface PlayerActionResult {
  ok: boolean
  state: WorldState
  events: Array<Record<string, unknown>>
  camera: { mode: string; focus_tile: { x: number; y: number }; map_id: string; scene_id: string }
  scene_update: { changed: boolean; reason: string; map_id: string; scene_id: string; region?: Record<string, unknown> }
  path?: Array<{ x: number; y: number }>
  activity_result?: Record<string, unknown>
  intent_result?: Record<string, unknown>
  relationship_changes?: Array<Record<string, unknown>>
  memory_written?: Array<Record<string, unknown>>
  error?: string
}

export interface StoryChooseResult {
  ok: boolean
  state: WorldState
  choice?: Record<string, unknown>
  available_events?: StoryEvent[]
  relationship_changes?: Array<Record<string, unknown>>
  memory_written?: Array<Record<string, unknown>>
  error?: string
}

export interface NpcProfile {
  relationship?: Record<string, unknown>
  important_memories?: Array<Record<string, unknown>>
  promises?: Array<Record<string, unknown>>
  tensions?: Array<Record<string, unknown>>
  attitude_source?: Record<string, unknown>
}

export interface DialogueResult {
  ok: boolean
  npc_id: string
  reply?: string
  source?: string
  memory_candidate?: Record<string, unknown>
  error?: string
}

export type SaveData = Record<string, unknown>
