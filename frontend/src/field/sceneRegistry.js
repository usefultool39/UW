export const DEFAULT_MAP_ID = 'novice_open'

export const MAP_DEFINITIONS = {
  novice_open: {
    id: 'novice_open',
    label: '卢利特村外野',
    regionId: 'novice_village',
    mode: 'field',
    background: '/assets/game/field-bg-tv-v3.jpg'
  }
}

export const SCENE_DEFINITIONS = {
  reading_hall: {
    id: 'reading_hall',
    mapId: 'novice_open',
    regionId: 'novice_village',
    label: '教会书库与村西',
    playMode: 'field',
    status: 'open'
  },
  church_library: {
    id: 'church_library',
    mapId: 'novice_open',
    regionId: 'novice_village',
    label: '教会书库',
    playMode: 'field',
    status: 'open'
  },
  home_hearth: {
    id: 'home_hearth',
    mapId: 'novice_open',
    regionId: 'novice_village',
    label: '家中炉火',
    playMode: 'field',
    status: 'open'
  },
  village_square: {
    id: 'village_square',
    mapId: 'novice_open',
    regionId: 'novice_village',
    label: '村道广场',
    playMode: 'field',
    status: 'open'
  },
  gigas_clearing: {
    id: 'gigas_clearing',
    mapId: 'novice_open',
    regionId: 'novice_village',
    label: '基家斯西达清场',
    playMode: 'field',
    status: 'open'
  },
  north_gate: {
    id: 'north_gate',
    mapId: 'novice_open',
    regionId: 'novice_village',
    label: '北境边门',
    playMode: 'field',
    status: 'open'
  },
  goblin_cave_stub: {
    id: 'goblin_cave_stub',
    mapId: 'north_cave_stub',
    regionId: 'novice_village',
    label: '北境洞窟',
    playMode: 'instance',
    status: 'locked'
  }
}

export const SCENE_TRANSITION_BLUEPRINTS = [
  {
    from: 'reading_hall',
    to: 'gigas_clearing',
    kind: 'same-map-zone',
    ui: 'walk'
  },
  {
    from: 'gigas_clearing',
    to: 'goblin_cave_stub',
    kind: 'map-gate',
    ui: 'boundary-prompt',
    status: 'planned'
  }
]

export function getMapDefinition(mapId = DEFAULT_MAP_ID) {
  return MAP_DEFINITIONS[mapId] || {
    id: mapId || DEFAULT_MAP_ID,
    label: mapId || DEFAULT_MAP_ID,
    regionId: '',
    mode: 'field',
    background: MAP_DEFINITIONS[DEFAULT_MAP_ID].background
  }
}

export function getWorldBackgroundAsset(mapId = DEFAULT_MAP_ID) {
  return getMapDefinition(mapId).background
}

export function getSceneDefinition(sceneId) {
  return SCENE_DEFINITIONS[sceneId] || {
    id: sceneId || '',
    mapId: DEFAULT_MAP_ID,
    regionId: '',
    label: sceneId || '未知地点',
    playMode: 'field',
    status: 'unknown'
  }
}

export function getSceneLabel(sceneId) {
  return getSceneDefinition(sceneId).label
}
