const PORTRAIT_ROOT = '/assets/runtime/portraits'
const ICON_ROOT = '/assets/runtime/icons'

const PORTRAITS = {
  alice: {
    neutral: `${PORTRAIT_ROOT}/VIS-POR-001_alice_neutral_v002_256.png`,
    concerned: `${PORTRAIT_ROOT}/VIS-POR-001_alice_concerned_v002_256.png`
  },
  eugeo: {
    neutral: `${PORTRAIT_ROOT}/VIS-POR-001_eugeo_neutral_v002_256.png`,
    concerned: `${PORTRAIT_ROOT}/VIS-POR-001_eugeo_concerned_v002_256.png`
  },
  player: {
    neutral: `${PORTRAIT_ROOT}/VIS-POR-001_player_neutral_v002_256.png`,
    concerned: `${PORTRAIT_ROOT}/VIS-POR-001_player_concerned_v002_256.png`
  }
}

const PORTRAIT_ALIASES = {
  kirito: 'player',
  player: 'player'
}

export function getRuntimeIcon(iconName) {
  const id = String(iconName || '').trim()
  return id ? `${ICON_ROOT}/${id}.png` : ''
}

export const RUNTIME_AUDIO = {
  bgmVillageDawn: '/assets/runtime/audio/village-dawn-a.ogg',
  ambienceDrizzle: '/assets/runtime/audio/drizzle-village-a.ogg'
}

export const RUNTIME_KEYART = {
  villageDesktop: '/assets/runtime/keyart/village-desktop.png'
}

export function getPortraitAsset(agentId, mood = 'neutral') {
  const id = PORTRAIT_ALIASES[String(agentId || '')] || String(agentId || '')
  const set = PORTRAITS[id]
  if (!set) return ''
  return set[mood] || set.neutral || ''
}
