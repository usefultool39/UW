export const DEFAULT_MAP_ID = 'novice_open'

export const MAP_DEFINITIONS = {
  novice_open: {
    id: 'novice_open',
    label: '卢利特村外野',
    regionId: 'novice_village',
    mode: 'field',
    background: '/assets/runtime/keyart/village-desktop.png'
  },
  north_boundary_stub: {
    id: 'north_boundary_stub',
    label: '北境边界',
    regionId: 'novice_village',
    mode: 'field',
    background: '/assets/runtime/keyart/village-desktop.png'
  }
}

export const SCENE_DEFINITIONS = {
  reading_hall: { id: 'reading_hall', mapId: 'novice_open', regionId: 'novice_village', role: 'explore', regionType: 'interact', roleLabel: '探索区', zoneColor: 0x7dd3fc, label: '教会回廊', playMode: 'field', status: 'open' },
  church_library: { id: 'church_library', mapId: 'novice_open', regionId: 'novice_village', role: 'study', regionType: 'interact', roleLabel: '书库研读', zoneColor: 0x60a5fa, label: '教会书库', playMode: 'field', status: 'open' },
  home_hearth: { id: 'home_hearth', mapId: 'novice_open', regionId: 'novice_village', role: 'rest', regionType: 'rest', roleLabel: '休息区', zoneColor: 0xf59e0b, label: '村中住处', playMode: 'field', status: 'open' },
  village_square: { id: 'village_square', mapId: 'novice_open', regionId: 'novice_village', role: 'social', regionType: 'interact', roleLabel: '村内交流', zoneColor: 0x34d399, label: '卢利特村广场', playMode: 'field', status: 'open' },
  teleport_plaza: { id: 'teleport_plaza', mapId: 'novice_open', regionId: 'novice_village', role: 'travel', regionType: 'travel', roleLabel: '传送阵', zoneColor: 0x8b5cf6, label: '传送阵广场', playMode: 'field', status: 'open' },
  west_fields: { id: 'west_fields', mapId: 'novice_open', regionId: 'novice_village', role: 'explore', regionType: 'explore', roleLabel: '探索区', zoneColor: 0x84cc16, label: '西侧田野', playMode: 'field', status: 'open' },
  gigas_clearing: { id: 'gigas_clearing', mapId: 'novice_open', regionId: 'novice_village', role: 'work', regionType: 'work', roleLabel: '训练区', zoneColor: 0xfacc15, label: '巨神树伐木场', playMode: 'field', status: 'open' },
  north_gate: { id: 'north_gate', mapId: 'novice_open', regionId: 'novice_village', role: 'boundary', regionType: 'boundary', roleLabel: '边界调查', zoneColor: 0xf472b6, label: '北方村门', playMode: 'field', status: 'open' },
  north_ridge_gate: { id: 'north_ridge_gate', mapId: 'novice_open', regionId: 'novice_village', role: 'boundary', regionType: 'locked', roleLabel: '未开放', zoneColor: 0xa78bfa, label: '北境山道', playMode: 'field', status: 'locked' },
  east_highroad_gate: { id: 'east_highroad_gate', mapId: 'novice_open', regionId: 'novice_village', role: 'boundary', regionType: 'locked', roleLabel: '未开放', zoneColor: 0x38bdf8, label: '东侧高路', playMode: 'field', status: 'locked' },
  south_lake_gate: { id: 'south_lake_gate', mapId: 'novice_open', regionId: 'novice_village', role: 'boundary', regionType: 'locked', roleLabel: '未开放', zoneColor: 0x2dd4bf, label: '南湖旧渡', playMode: 'field', status: 'locked' },
  north_boundary: { id: 'north_boundary', mapId: 'north_boundary_stub', regionId: 'novice_village', role: 'boundary', regionType: 'boundary', roleLabel: '边界探索', zoneColor: 0xfb923c, label: '北境边界', playMode: 'field', status: 'open' },
  goblin_cave_stub: { id: 'goblin_cave_stub', mapId: 'north_cave_stub', regionId: 'novice_village', role: 'instance', regionType: 'locked', roleLabel: '副本入口', zoneColor: 0xa78bfa, label: '北境洞窟', playMode: 'instance', status: 'locked' }
}

export const SCENE_TRANSITION_BLUEPRINTS = [
  { from: 'reading_hall', to: 'gigas_clearing', kind: 'same-map-zone', ui: 'walk' },
  { from: 'village_square', to: 'teleport_plaza', kind: 'same-map-zone', ui: 'walk' },
  { from: 'teleport_plaza', to: 'east_highroad_gate', kind: 'future-gate', ui: 'boundary-prompt', status: 'planned' },
  { from: 'north_gate', to: 'north_boundary', kind: 'map-gate', ui: 'boundary-prompt', status: 'planned' }
]

export function getMapDefinition(mapId = DEFAULT_MAP_ID) {
  return MAP_DEFINITIONS[mapId] || { id: mapId || DEFAULT_MAP_ID, label: mapId || DEFAULT_MAP_ID, regionId: '', mode: 'field', background: MAP_DEFINITIONS[DEFAULT_MAP_ID].background }
}

export function getWorldBackgroundAsset(mapId = DEFAULT_MAP_ID) {
  return getMapDefinition(mapId).background
}

export function getSceneDefinition(sceneId) {
  return SCENE_DEFINITIONS[sceneId] || { id: sceneId || '', mapId: DEFAULT_MAP_ID, regionId: '', label: sceneId || '未知地点', playMode: 'field', status: 'unknown' }
}

export function getSceneLabel(sceneId) {
  return getSceneDefinition(sceneId).label
}
