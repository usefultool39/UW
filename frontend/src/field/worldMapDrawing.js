/** 寮€鏀句笘鐣屽湴鍧楃粯鍒朵笌鍦板浘缇庢湳锛圥haser Graphics 鐢級 */

import {
  AGENT_ART_KEYS,
  AGENT_TEXTURE_FALLBACKS,
  LANDMARK_ART_CONFIGS,
  SCENE_DEFINITIONS,
  getSceneLabel
} from './gameContentConfig.js'

export const ZOOM_MIN = 0.42
export const ZOOM_MAX = 2.35
export const ZOOM_WHEEL = 0.055

export const MINI_COL = {
  0: 0x6f9362,
  1: 0x223c2d,
  2: 0x4b8fa0,
  3: 0xbca982,
  4: 0x766f65
}

export { AGENT_ART_KEYS }

/** 浼殢鏈?0..1锛屼笌鍧愭爣缁戝畾锛屼繚璇佽创鍥剧粏鑺傜ǔ瀹氥€?*/
export function tileHash(x, y, salt = 0) {
  let n = x * 374761393 + y * 668265263 + salt * 1442695041
  n = (n ^ (n >>> 13)) >>> 0
  return (n & 0xfffffff) / 0xfffffff
}

function codeAt(rows, x, y) {
  if (y < 0 || y >= rows.length || x < 0 || x >= (rows[0]?.length || 0)) return null
  const ch = rows[y]?.[x] || '0'
  return ch >= '0' && ch <= '9' ? parseInt(ch, 10) : 0
}

function strokeGrassBlade(g, x, y, s, color, alpha = 0.62) {
  g.lineStyle(Math.max(1, s * 0.06), color, alpha)
  g.lineBetween(x, y, x + s * 0.12, y - s * 0.28)
  g.lineBetween(x + s * 0.12, y, x + s * 0.03, y - s * 0.24)
}

export function drawStyledTile(g, x, y, ts, code) {
  const px = x * ts
  const py = y * ts
  const pad = 0
  const w = ts
  const h = ts
  const h0 = tileHash(x, y)

  const drawGrassBase = () => {
    g.fillStyle(0x6d9565, 1)
    g.fillRect(px + pad, py + pad, w, h)
    g.fillStyle(0xb9d28e, 0.026)
    g.fillTriangle(px, py, px + w * 0.9, py, px, py + h * 0.62)
    g.fillStyle(0x314d35, 0.025)
    g.fillTriangle(px + w, py + h, px + w * 0.15, py + h, px + w, py + h * 0.24)
    if (h0 > 0.64) {
      strokeGrassBlade(g, px + ts * (0.22 + h0 * 0.18), py + ts * 0.74, ts, 0x31583c, 0.18)
    }
    if (h0 > 0.82) {
      g.fillStyle(h0 > 0.91 ? 0xd9c474 : 0xc5d99c, 0.56)
      g.fillCircle(px + ts * 0.68, py + ts * 0.42, Math.max(1.2, ts * 0.045))
    }
  }

  if (code === 0) {
    drawGrassBase()
  } else if (code === 1) {
    g.fillStyle(0x223a2b, 1)
    g.fillRect(px, py, w, h)
    g.fillStyle(0x16271d, 0.82)
    g.fillEllipse(px + ts * 0.5, py + ts * 0.72, ts * 0.72, ts * 0.34)
    g.fillStyle(0x604735, 1)
    g.fillRoundedRect(px + ts * 0.43, py + ts * 0.48, ts * 0.14, ts * 0.42, Math.max(1, ts * 0.03))
    g.fillStyle(h0 > 0.55 ? 0x31583d : 0x2d4f39, 1)
    g.fillCircle(px + ts * 0.5, py + ts * 0.34, ts * 0.31)
    g.fillStyle(0x4d7650, 0.62)
    g.fillCircle(px + ts * 0.36, py + ts * 0.43, ts * 0.2)
    g.fillCircle(px + ts * 0.64, py + ts * 0.45, ts * 0.19)
    g.fillStyle(0xc6d58f, 0.12)
    g.fillCircle(px + ts * 0.39, py + ts * 0.24, ts * 0.1)
    g.lineStyle(Math.max(1, ts * 0.035), 0x132017, 0.34)
    g.lineBetween(px + ts * 0.38, py + ts * 0.67, px + ts * 0.25, py + ts * 0.82)
    g.lineBetween(px + ts * 0.57, py + ts * 0.66, px + ts * 0.72, py + ts * 0.81)
  } else if (code === 2) {
    g.fillStyle(0x4b8fa0, 1)
    g.fillRect(px, py, w, h)
    g.fillStyle(0x275f73, 0.32)
    g.fillTriangle(px + w, py + h, px + w * 0.2, py + h, px + w, py + h * 0.2)
    g.fillStyle(0x1f6b83, 0.18)
    g.fillEllipse(px + ts * 0.5, py + ts * 0.52, ts * 0.88, ts * 0.5)
    g.lineStyle(Math.max(1, ts * 0.04), 0xc0e3e8, 0.17)
    const wave = ((x + y) % 3) * ts * 0.08
    g.lineBetween(px + ts * 0.14, py + ts * 0.32 + wave, px + ts * 0.86, py + ts * 0.28 + wave)
    g.lineStyle(Math.max(1, ts * 0.03), 0xd8f3f3, 0.13)
    g.lineBetween(px + ts * 0.22, py + ts * 0.62, px + ts * 0.68, py + ts * 0.58)
  } else if (code === 3) {
    drawGrassBase()
    g.fillStyle(0x9b8157, 1)
    g.fillRoundedRect(px + ts * 0.18, py + ts * 0.18, ts * 0.64, ts * 0.64, Math.max(3, ts * 0.16))
    g.fillStyle(0xd2bf91, 0.18)
    g.fillRoundedRect(px + ts * 0.27, py + ts * 0.22, ts * 0.46, ts * 0.18, Math.max(2, ts * 0.08))
    g.fillStyle(0x6b573b, 0.12)
    g.fillRoundedRect(px + ts * 0.24, py + ts * 0.59, ts * 0.5, ts * 0.15, Math.max(2, ts * 0.07))
    if (h0 > 0.7) {
      g.fillStyle(0x5f5139, 0.22)
      g.fillCircle(px + ts * 0.68, py + ts * 0.72, Math.max(1.2, ts * 0.035))
    }
  } else {
    g.fillStyle(0x6d6a62, 1)
    g.fillRect(px, py, w, h)
    g.fillStyle(0x938b7a, 0.5)
    g.fillTriangle(px + ts * 0.13, py + ts * 0.82, px + ts * 0.54, py + ts * 0.16, px + ts * 0.92, py + ts * 0.78)
    g.fillStyle(0x47423a, 0.22)
    g.fillTriangle(px + ts * 0.54, py + ts * 0.16, px + ts * 0.92, py + ts * 0.78, px + ts * 0.58, py + ts * 0.72)
    g.fillStyle(0xb8b19e, 0.35)
    g.fillCircle(px + ts * 0.27, py + ts * 0.32, ts * 0.08)
  }
}

export function drawTerrainOverlays(scene, map, ts) {
  const rows = map.rows || []
  const g = scene.add.graphics().setDepth(2)
  for (let y = 0; y < rows.length; y++) {
    const row = rows[y] || ''
    for (let x = 0; x < row.length; x++) {
      const code = codeAt(rows, x, y)
      const px = x * ts
      const py = y * ts
      const h0 = tileHash(x, y, 3)

      if (code === 0 || code === 3) {
        const northWater = codeAt(rows, x, y - 1) === 2
        const southWater = codeAt(rows, x, y + 1) === 2
        const westWater = codeAt(rows, x - 1, y) === 2
        const eastWater = codeAt(rows, x + 1, y) === 2
        if (northWater || southWater || westWater || eastWater) {
          g.fillStyle(0xd5c99a, 0.38)
          if (northWater) g.fillRect(px, py, ts, ts * 0.18)
          if (southWater) g.fillRect(px, py + ts * 0.82, ts, ts * 0.18)
          if (westWater) g.fillRect(px, py, ts * 0.18, ts)
          if (eastWater) g.fillRect(px + ts * 0.82, py, ts * 0.18, ts)
          g.lineStyle(Math.max(1, ts * 0.032), 0xeff6c6, 0.22)
          if (northWater) g.lineBetween(px + ts * 0.18, py + ts * 0.08, px + ts * 0.82, py + ts * 0.08)
          if (southWater) g.lineBetween(px + ts * 0.18, py + ts * 0.92, px + ts * 0.82, py + ts * 0.92)
          if (westWater) g.lineBetween(px + ts * 0.08, py + ts * 0.18, px + ts * 0.08, py + ts * 0.82)
          if (eastWater) g.lineBetween(px + ts * 0.92, py + ts * 0.18, px + ts * 0.92, py + ts * 0.82)
          if (h0 > 0.72) {
            g.lineStyle(Math.max(1, ts * 0.035), 0x2f5d3c, 0.32)
            g.lineBetween(px + ts * 0.3, py + ts * 0.84, px + ts * 0.34, py + ts * 0.58)
            g.lineBetween(px + ts * 0.39, py + ts * 0.84, px + ts * 0.32, py + ts * 0.61)
          }
        }
        if (code === 0 && h0 > 0.78) {
          strokeGrassBlade(g, px + ts * 0.22, py + ts * 0.78, ts, 0x31583c, 0.2)
          strokeGrassBlade(g, px + ts * 0.72, py + ts * 0.58, ts * 0.8, 0x3d6545, 0.16)
        }
      }

      if (code === 3) {
        const centerX = px + ts * 0.5
        const centerY = py + ts * 0.5
        const half = ts * 0.28
        const northRoad = codeAt(rows, x, y - 1) === 3
        const southRoad = codeAt(rows, x, y + 1) === 3
        const westRoad = codeAt(rows, x - 1, y) === 3
        const eastRoad = codeAt(rows, x + 1, y) === 3
        g.fillStyle(0x9b8157, 1)
        if (northRoad) g.fillRect(centerX - half, py, half * 2, ts * 0.5)
        if (southRoad) g.fillRect(centerX - half, centerY, half * 2, ts * 0.5)
        if (westRoad) g.fillRect(px, centerY - half, ts * 0.5, half * 2)
        if (eastRoad) g.fillRect(centerX, centerY - half, ts * 0.5, half * 2)
        g.fillRoundedRect(centerX - half, centerY - half, half * 2, half * 2, Math.max(3, ts * 0.14))

        g.lineStyle(Math.max(1, ts * 0.035), 0xf3dfa8, 0.28)
        if (!northRoad) g.lineBetween(px + ts * 0.22, py + ts * 0.2, px + ts * 0.78, py + ts * 0.2)
        if (!southRoad) g.lineBetween(px + ts * 0.22, py + ts * 0.8, px + ts * 0.78, py + ts * 0.8)
        if (!westRoad) g.lineBetween(px + ts * 0.2, py + ts * 0.22, px + ts * 0.2, py + ts * 0.78)
        if (!eastRoad) g.lineBetween(px + ts * 0.8, py + ts * 0.22, px + ts * 0.8, py + ts * 0.78)

        if (h0 > 0.38) {
          g.fillStyle(0x5f5139, 0.18)
          g.fillEllipse(px + ts * (0.25 + h0 * 0.42), py + ts * (0.22 + h0 * 0.48), ts * 0.13, ts * 0.06)
        }
      }

      if (code === 1) {
        const northOpen = [0, 3].includes(codeAt(rows, x, y - 1))
        const southOpen = [0, 3].includes(codeAt(rows, x, y + 1))
        const westOpen = [0, 3].includes(codeAt(rows, x - 1, y))
        const eastOpen = [0, 3].includes(codeAt(rows, x + 1, y))
        const nearOpen = northOpen || southOpen || westOpen || eastOpen
        if (nearOpen) {
          g.fillStyle(0x102116, 0.28)
          if (northOpen) g.fillRect(px, py, ts, ts * 0.16)
          if (southOpen) g.fillRect(px, py + ts * 0.84, ts, ts * 0.16)
          if (westOpen) g.fillRect(px, py, ts * 0.16, ts)
          if (eastOpen) g.fillRect(px + ts * 0.84, py, ts * 0.16, ts)
          g.lineStyle(Math.max(1, ts * 0.04), 0x9fce80, 0.22)
          g.strokeCircle(px + ts * 0.5, py + ts * 0.44, ts * 0.34)
          if (h0 > 0.5) {
            g.fillStyle(0x7db66a, 0.2)
            g.fillCircle(px + ts * 0.22, py + ts * 0.68, ts * 0.05)
            g.fillCircle(px + ts * 0.77, py + ts * 0.61, ts * 0.045)
          }
        }
      }
    }
  }
  return g
}

export function drawNavigationOverlay(scene, map, ts) {
  const rows = map.rows || []
  const walkable = new Set((map.walkable || [0, 3]).map((v) => Number(v)))
  const g = scene.add.graphics().setDepth(46)
  for (let y = 0; y < rows.length; y++) {
    const row = rows[y] || ''
    for (let x = 0; x < row.length; x++) {
      const code = codeAt(rows, x, y)
      const px = x * ts
      const py = y * ts
      if (walkable.has(code)) {
        g.fillStyle(0x22c55e, 0.13)
        g.fillRect(px + 2, py + 2, ts - 4, ts - 4)
      } else {
        g.fillStyle(code === 2 ? 0x38bdf8 : 0xef4444, 0.16)
        g.fillRect(px + 2, py + 2, ts - 4, ts - 4)
      }
    }
  }
  return g
}

export function drawWaterRipples(g, map, ts, timeMs = 0) {
  const rows = map.rows || []
  g.clear()
  const phase = timeMs / 650
  for (let y = 0; y < rows.length; y++) {
    const row = rows[y] || ''
    for (let x = 0; x < row.length; x++) {
      if (codeAt(rows, x, y) !== 2) continue
      const h0 = tileHash(x, y, 11)
      if (h0 < 0.42) continue
      const px = x * ts
      const py = y * ts
      const offset = Math.sin(phase + h0 * 6.28) * ts * 0.04
      const len = ts * (0.34 + h0 * 0.28)
      const cx = px + ts * (0.24 + h0 * 0.5)
      const cy = py + ts * (0.3 + tileHash(x, y, 12) * 0.42) + offset
      g.lineStyle(Math.max(1, ts * 0.028), 0xdff8ff, 0.11 + h0 * 0.08)
      g.lineBetween(cx - len * 0.5, cy, cx + len * 0.5, cy - ts * 0.03)
    }
  }
  return g
}

const REGION_STYLE = {
  interact: { color: 0x38bdf8, roleLabel: '互动区', alpha: 0.08, strokeAlpha: 0.64 },
  work: { color: 0xfacc15, roleLabel: '训练区', alpha: 0.12, strokeAlpha: 0.82 },
  rest: { color: 0xf59e0b, roleLabel: '休息区', alpha: 0.12, strokeAlpha: 0.78 },
  travel: { color: 0x8b5cf6, roleLabel: '传送阵', alpha: 0.1, strokeAlpha: 0.76 },
  boundary: { color: 0xfb7185, roleLabel: '边界', alpha: 0.08, strokeAlpha: 0.72 },
  locked: { color: 0xf472b6, roleLabel: '未开放', alpha: 0.08, strokeAlpha: 0.72 },
  forbidden: { color: 0xef4444, roleLabel: '禁止区', alpha: 0.08, strokeAlpha: 0.72 }
}

function zoneStyle(zone) {
  const sceneId = String(zone?.scene_id || '')
  const def = SCENE_DEFINITIONS[sceneId] || {}
  const regionType = String(zone?.regionType || def.regionType || def.role || 'explore')
  const region = REGION_STYLE[regionType] || null
  const color = Number(zone?.zoneColor || def.zoneColor || region?.color || 0x7dd3fc)
  const role = def.role || regionType || 'explore'
  return {
    color,
    role,
    regionType,
    roleLabel: zone?.label || region?.roleLabel || def.roleLabel || '功能区',
    alpha: role === 'explore' && !region ? 0.035 : (region?.alpha ?? 0.095),
    strokeAlpha: role === 'explore' && !region ? 0.28 : (region?.strokeAlpha ?? 0.72)
  }
}

export function drawSceneZoneHighlights(scene, map, ts) {
  const layer = scene.add.container(0, 0).setDepth(4)
  const zones = Array.isArray(map.scene_zones) ? map.scene_zones : []
  for (const zone of zones) {
    const sceneId = String(zone.scene_id || '')
    if (!sceneId) continue
    const x1 = Number(zone.x1 ?? 0)
    const y1 = Number(zone.y1 ?? 0)
    const x2 = Number(zone.x2 ?? x1)
    const y2 = Number(zone.y2 ?? y1)
    const left = Math.min(x1, x2) * ts
    const top = Math.min(y1, y2) * ts
    const width = (Math.abs(x2 - x1) + 1) * ts
    const height = (Math.abs(y2 - y1) + 1) * ts
    const cx = left + width / 2
    const cy = top + height / 2
    const style = zoneStyle(zone)

    const g = scene.add.graphics()
    g.fillStyle(style.color, style.alpha)
    g.fillRoundedRect(left + 3, top + 3, Math.max(1, width - 6), Math.max(1, height - 6), Math.max(5, ts * 0.18))
    g.lineStyle(Math.max(2, ts * 0.065), style.color, style.strokeAlpha)
    g.strokeRoundedRect(left + 4, top + 4, Math.max(1, width - 8), Math.max(1, height - 8), Math.max(5, ts * 0.18))
    g.lineStyle(Math.max(1, ts * 0.035), 0xfff7d6, 0.38)
    const c = Math.min(ts * 1.4, width * 0.22, height * 0.22)
    g.lineBetween(left + 6, top + 6, left + 6 + c, top + 6)
    g.lineBetween(left + 6, top + 6, left + 6, top + 6 + c)
    g.lineBetween(left + width - 6, top + 6, left + width - 6 - c, top + 6)
    g.lineBetween(left + width - 6, top + 6, left + width - 6, top + 6 + c)
    g.lineBetween(left + 6, top + height - 6, left + 6 + c, top + height - 6)
    g.lineBetween(left + 6, top + height - 6, left + 6, top + height - 6 - c)
    g.lineBetween(left + width - 6, top + height - 6, left + width - 6 - c, top + height - 6)
    g.lineBetween(left + width - 6, top + height - 6, left + width - 6, top + height - 6 - c)
    layer.add(g)

    if (style.role !== 'explore' || style.regionType !== 'explore') {
      const label = scene.add
        .text(cx, cy, style.roleLabel, {
          fontSize: '13px',
          color: '#fff7d6',
          fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
          fontStyle: 'bold',
          stroke: '#0f172a',
          strokeThickness: 5
        })
        .setOrigin(0.5)
        .setAlpha(0.94)
      layer.add(label)
    }
  }
  return layer
}

function addBoundarySign(scene, layer, x, y, label, align = 'center') {
  const c = scene.add.container(x, y)
  const g = scene.add.graphics()
  g.fillStyle(0x000000, 0.28)
  g.fillEllipse(0, 18, 112, 20)
  g.fillStyle(0x5a3a22, 1)
  g.fillRoundedRect(-48, -11, 96, 25, 5)
  g.fillStyle(0x8b5e34, 0.92)
  g.fillRoundedRect(-42, -7, 84, 17, 4)
  g.fillStyle(0x3f2819, 1)
  g.fillRect(-36, 10, 5, 18)
  g.fillRect(31, 10, 5, 18)
  g.lineStyle(1, 0xf6d36e, 0.42)
  g.strokeRoundedRect(-48, -11, 96, 25, 5)
  const text = scene.add
    .text(0, 1, label, {
      fontSize: '10px',
      color: '#fff7d6',
      fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
      fontStyle: 'bold',
      stroke: '#24170d',
      strokeThickness: 3,
      align
    })
    .setOrigin(0.5)
  c.add([g, text])
  layer.add(c)
  return c
}

export function drawExplorationAtmosphere(scene, map, ts) {
  const rows = map.rows || []
  const W = rows[0]?.length || 0
  const H = rows.length
  const mapW = W * ts
  const mapH = H * ts
  const layer = scene.add.container(0, 0).setDepth(8)

  const edge = scene.add.graphics()
  for (let i = 0; i < 9; i++) {
    const a = 0.025 + i * 0.018
    const inset = i * ts * 0.52
    edge.fillStyle(0x07111c, a)
    edge.fillRect(inset, inset, Math.max(0, mapW - inset * 2), ts * 0.7)
    edge.fillRect(inset, Math.max(0, mapH - inset - ts * 0.7), Math.max(0, mapW - inset * 2), ts * 0.7)
    edge.fillRect(inset, inset, ts * 0.7, Math.max(0, mapH - inset * 2))
    edge.fillRect(Math.max(0, mapW - inset - ts * 0.7), inset, ts * 0.7, Math.max(0, mapH - inset * 2))
  }
  edge.lineStyle(2, 0xb7d8b8, 0.18)
  edge.strokeRect(ts * 1.1, ts * 1.1, mapW - ts * 2.2, mapH - ts * 2.2)
  layer.add(edge)

  const mist = scene.add.graphics()
  const mistSeeds = [
    [0.16, 0.08, 180, 42],
    [0.5, 0.05, 240, 48],
    [0.86, 0.18, 190, 46],
    [0.92, 0.67, 220, 54],
    [0.42, 0.92, 270, 50],
    [0.1, 0.75, 185, 42]
  ]
  for (const [ux, uy, w, h] of mistSeeds) {
    mist.fillStyle(0xdbeafe, 0.08)
    mist.fillEllipse(mapW * ux, mapH * uy, w, h)
    mist.fillStyle(0x86efac, 0.045)
    mist.fillEllipse(mapW * ux + ts * 0.7, mapH * uy + ts * 0.2, w * 0.74, h * 0.72)
  }
  mist.setAlpha(0.62)
  layer.add(mist)

  const signs = scene.add.container(0, 0)
  addBoundarySign(scene, signs, mapW * 0.5, ts * 2.2, '北境边界')
  addBoundarySign(scene, signs, mapW - ts * 4.2, mapH * 0.48, '东侧山道')
  addBoundarySign(scene, signs, mapW * 0.3, mapH - ts * 2.4, '村外渡口')
  signs.setAlpha(0.86)
  layer.add(signs)

  return layer
}

function makeCharacterTexture(scene, key, p) {
  if (scene.textures.exists(key)) scene.textures.remove(key)
  const g = scene.make.graphics({ x: 0, y: 0, add: false })

  const outline = p.outline ?? 0x121826
  const body = p.body ?? 0x273449
  const cape = p.cape ?? body
  const accent = p.accent ?? 0xf6d36e
  const hair = p.hair ?? 0x29313f
  const skin = p.skin ?? 0xe6c7a4
  const boots = p.boots ?? outline
  const weapon = p.weapon ?? accent
  const style = p.style || 'traveler'
  const w = 44
  const h = 52

  g.fillStyle(0x000000, 0.2)
  g.fillEllipse(22, 46, 24, 6)

  if (style === 'dual_blades') {
    g.lineStyle(3, outline, 0.92)
    g.lineBetween(10, 11, 32, 40)
    g.lineBetween(34, 11, 12, 40)
    g.lineStyle(1, weapon, 0.95)
    g.lineBetween(10, 11, 32, 40)
    g.lineBetween(34, 11, 12, 40)
  } else if (style === 'blue_rose') {
    g.lineStyle(4, outline, 0.9)
    g.lineBetween(35, 9, 18, 43)
    g.lineStyle(2, weapon, 0.96)
    g.lineBetween(35, 9, 18, 43)
    g.fillStyle(0xbfdbfe, 0.86)
    g.fillCircle(31, 18, 2)
    g.fillCircle(33, 22, 1.6)
  } else if (style === 'gold_knight') {
    g.lineStyle(4, outline, 0.92)
    g.lineBetween(35, 13, 30, 42)
    g.lineStyle(2, weapon, 0.96)
    g.lineBetween(35, 13, 30, 42)
  }

  g.fillStyle(outline, 1)
  g.fillRoundedRect(10, 20, 24, 22, 4)
  g.fillRect(8, 24, 5, 13)
  g.fillRect(31, 24, 5, 13)
  g.fillRect(13, 40, 7, 7)
  g.fillRect(24, 40, 7, 7)

  g.fillStyle(cape, 1)
  g.fillRoundedRect(11, 19, 22, 25, 5)
  if (style === 'gold_knight') {
    g.fillStyle(0xf8fafc, 1)
    g.fillRoundedRect(13, 20, 18, 20, 3)
    g.fillStyle(accent, 1)
    g.fillRect(14, 21, 16, 3)
    g.fillRect(19, 23, 6, 16)
    g.fillStyle(0xfde68a, 0.72)
    g.fillRect(15, 27, 14, 2)
  } else {
    g.fillStyle(body, 1)
    g.fillRoundedRect(13, 20, 18, 20, 3)
    g.fillStyle(accent, 1)
    g.fillRect(15, 23, 14, 2)
    g.fillRect(20, 26, 4, 12)
  }

  g.fillStyle(skin, 1)
  g.fillRoundedRect(15, 9, 14, 12, 3)
  g.fillRect(8, 27, 4, 7)
  g.fillRect(32, 27, 4, 7)

  g.fillStyle(hair, 1)
  if (style === 'gold_knight') {
    g.fillRoundedRect(12, 4, 20, 9, 4)
    g.fillRect(10, 9, 5, 16)
    g.fillRect(29, 9, 5, 17)
    g.fillRect(17, 3, 11, 3)
  } else if (style === 'blue_rose') {
    g.fillRoundedRect(13, 5, 18, 8, 3)
    g.fillRect(11, 9, 5, 10)
    g.fillRect(28, 9, 4, 9)
    g.fillRect(20, 4, 9, 3)
  } else {
    g.fillRoundedRect(13, 5, 18, 8, 3)
    g.fillRect(11, 9, 6, 10)
    g.fillRect(27, 9, 6, 10)
    g.fillRect(18, 4, 11, 3)
  }

  g.fillStyle(0x0f172a, 1)
  g.fillRect(17, 14, 2, 2)
  g.fillRect(25, 14, 2, 2)
  g.fillStyle(0xf8fafc, 0.72)
  g.fillRect(18, 13, 1, 1)
  g.fillRect(26, 13, 1, 1)

  g.fillStyle(boots, 1)
  g.fillRect(12, 46, 9, 3)
  g.fillRect(23, 46, 9, 3)
  g.fillStyle(accent, style === 'gold_knight' ? 0.72 : 0.44)
  g.fillRect(15, 39, 14, 1)

  g.generateTexture(key, w, h)
  g.destroy()
}

export function ensureWorldArtTextures(scene) {
  for (const [key, palette] of Object.entries(AGENT_TEXTURE_FALLBACKS)) {
    makeCharacterTexture(scene, key, palette)
  }
}

function addSmallLabel(scene, parent, x, y, text, color = '#fef3c7') {
  const label = scene.add
    .text(x, y, text, {
      fontSize: '11px',
      color,
      fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
      fontStyle: 'bold',
      stroke: '#24170d',
      strokeThickness: 4
    })
    .setOrigin(0.5)
  parent.add(label)
  return label
}

function addLibrary(scene, layer, ts, tx, ty) {
  const c = scene.add.container((tx + 0.5) * ts, (ty + 0.5) * ts)
  const g = scene.add.graphics()
  const s = ts / 34
  g.fillStyle(0x000000, 0.28)
  g.fillEllipse(0, 28 * s, 124 * s, 34 * s)
  g.fillStyle(0x7a4c2d, 1)
  g.fillRoundedRect(-44 * s, -8 * s, 88 * s, 42 * s, 5 * s)
  g.fillStyle(0xc78b49, 1)
  g.fillRect(-38 * s, 0, 76 * s, 27 * s)
  g.fillStyle(0x5b2f25, 1)
  g.fillTriangle(-55 * s, -8 * s, 0, -40 * s, 55 * s, -8 * s)
  g.fillStyle(0xdb9b4f, 0.92)
  g.fillTriangle(-44 * s, -10 * s, 0, -31 * s, 44 * s, -10 * s)
  g.fillStyle(0x2b2018, 0.76)
  g.fillRoundedRect(-12 * s, 7 * s, 24 * s, 27 * s, 3 * s)
  g.fillStyle(0xf9e7b2, 0.75)
  g.fillRoundedRect(-35 * s, 5 * s, 14 * s, 12 * s, 2 * s)
  g.fillRoundedRect(22 * s, 5 * s, 14 * s, 12 * s, 2 * s)
  g.lineStyle(2 * s, 0xf6d36e, 0.9)
  g.strokeRoundedRect(-45 * s, -9 * s, 90 * s, 44 * s, 5 * s)
  c.add(g)
  addSmallLabel(scene, c, 0, -50 * s, '书库')
  layer.add(c)
}

function addHome(scene, layer, ts, tx, ty) {
  const c = scene.add.container((tx + 0.5) * ts, (ty + 0.5) * ts)
  const g = scene.add.graphics()
  const s = ts / 34
  g.fillStyle(0x000000, 0.25)
  g.fillEllipse(0, 25 * s, 86 * s, 27 * s)
  g.fillStyle(0x7b5133, 1)
  g.fillRoundedRect(-32 * s, -6 * s, 64 * s, 38 * s, 5 * s)
  g.fillStyle(0x314f42, 1)
  g.fillTriangle(-42 * s, -6 * s, 0, -34 * s, 42 * s, -6 * s)
  g.fillStyle(0x5f8d5d, 0.88)
  g.fillTriangle(-31 * s, -8 * s, 0, -26 * s, 31 * s, -8 * s)
  g.fillStyle(0x2a1f18, 0.85)
  g.fillRoundedRect(-8 * s, 10 * s, 16 * s, 22 * s, 3 * s)
  g.fillStyle(0xf8df96, 0.8)
  g.fillRoundedRect(13 * s, 5 * s, 12 * s, 10 * s, 2 * s)
  g.lineStyle(2 * s, 0xe6c06a, 0.85)
  g.strokeRoundedRect(-32 * s, -6 * s, 64 * s, 38 * s, 5 * s)
  c.add(g)
  addSmallLabel(scene, c, 0, -42 * s, '小屋')
  layer.add(c)
}

function addGigasTree(scene, layer, ts, tx, ty) {
  const c = scene.add.container((tx + 0.5) * ts, (ty + 0.5) * ts)
  const g = scene.add.graphics()
  const s = ts / 34
  g.fillStyle(0x000000, 0.32)
  g.fillEllipse(0, 43 * s, 138 * s, 40 * s)
  g.fillStyle(0x6d4229, 1)
  g.fillRoundedRect(-17 * s, -8 * s, 34 * s, 58 * s, 9 * s)
  g.fillStyle(0x8c5b37, 0.95)
  g.fillRoundedRect(-8 * s, -5 * s, 12 * s, 56 * s, 7 * s)
  g.fillStyle(0x0f3b25, 1)
  g.fillCircle(0, -50 * s, 44 * s)
  g.fillStyle(0x1f6f3a, 0.96)
  g.fillCircle(-34 * s, -36 * s, 34 * s)
  g.fillCircle(35 * s, -34 * s, 33 * s)
  g.fillCircle(0, -20 * s, 36 * s)
  g.fillStyle(0xa4d46f, 0.2)
  g.fillCircle(-18 * s, -62 * s, 13 * s)
  g.fillCircle(26 * s, -42 * s, 10 * s)
  g.lineStyle(3 * s, 0xd8b567, 0.78)
  g.strokeCircle(0, -40 * s, 54 * s)
  c.add(g)
  addSmallLabel(scene, c, 0, -97 * s, '古誓树', '#fef08a')
  layer.add(c)
}

function compactLandmarkLabel(text, max = 5) {
  const value = String(text || '').replace(/\s+/g, '').trim()
  if (!value) return ''
  return value.length > max ? `${value.slice(0, max)}…` : value
}

function addTeleportGate(scene, layer, ts, tx, ty) {
  const c = scene.add.container((tx + 0.5) * ts, (ty + 0.5) * ts)
  const g = scene.add.graphics()
  const s = ts / 34
  g.fillStyle(0x000000, 0.28)
  g.fillEllipse(0, 25 * s, 92 * s, 28 * s)
  g.fillStyle(0x40375f, 1)
  g.fillRoundedRect(-36 * s, -6 * s, 72 * s, 22 * s, 4 * s)
  g.fillStyle(0x6d5fa8, 0.92)
  g.fillRoundedRect(-30 * s, -10 * s, 60 * s, 18 * s, 4 * s)
  g.lineStyle(5 * s, 0xd8c48a, 0.9)
  g.beginPath()
  g.arc(0, -10 * s, 27 * s, Math.PI, 0, false)
  g.strokePath()
  g.lineStyle(3 * s, 0x3b2f5f, 0.9)
  g.lineBetween(-27 * s, -9 * s, -27 * s, 15 * s)
  g.lineBetween(27 * s, -9 * s, 27 * s, 15 * s)
  g.fillStyle(0x5eead4, 0.18)
  g.fillEllipse(0, -12 * s, 42 * s, 52 * s)
  g.lineStyle(2 * s, 0x93c5fd, 0.68)
  g.strokeEllipse(0, -12 * s, 37 * s, 48 * s)
  g.lineStyle(1 * s, 0xfef9c3, 0.46)
  g.strokeEllipse(0, -12 * s, 22 * s, 31 * s)
  c.add(g)

  const core = scene.add.ellipse(0, -12 * s, 18 * s, 32 * s, 0x67e8f9, 0.18)
  const ring = scene.add.ellipse(0, -12 * s, 45 * s, 57 * s, 0x8b5cf6, 0).setStrokeStyle(2 * s, 0xddd6fe, 0.6)
  c.add([core, ring])
  scene.tweens.add({
    targets: [core, ring],
    scaleX: 1.1,
    scaleY: 1.06,
    alpha: 0.62,
    duration: 1200,
    yoyo: true,
    repeat: -1,
    ease: 'Sine.easeInOut'
  })
  addSmallLabel(scene, c, 0, -57 * s, '传送阵', '#ddd6fe')
  layer.add(c)
}

function addBoundaryGate(scene, layer, ts, tx, ty, poi = {}) {
  const c = scene.add.container((tx + 0.5) * ts, (ty + 0.5) * ts)
  const g = scene.add.graphics()
  const s = ts / 34
  g.fillStyle(0x000000, 0.3)
  g.fillEllipse(0, 21 * s, 92 * s, 24 * s)
  g.fillStyle(0x5a3b2a, 1)
  g.fillRoundedRect(-34 * s, -20 * s, 9 * s, 43 * s, 3 * s)
  g.fillRoundedRect(25 * s, -20 * s, 9 * s, 43 * s, 3 * s)
  g.fillStyle(0x8b5a3c, 1)
  g.fillRoundedRect(-41 * s, -24 * s, 82 * s, 14 * s, 4 * s)
  g.fillRoundedRect(-37 * s, -5 * s, 74 * s, 12 * s, 4 * s)
  g.lineStyle(2 * s, 0xf6d36e, 0.54)
  g.lineBetween(-28 * s, 3 * s, 28 * s, -16 * s)
  g.lineBetween(-28 * s, -16 * s, 28 * s, 3 * s)
  g.fillStyle(0x0f172a, 0.62)
  g.fillRoundedRect(-30 * s, -38 * s, 60 * s, 18 * s, 4 * s)
  g.lineStyle(1.5 * s, 0xfde68a, 0.6)
  g.strokeRoundedRect(-30 * s, -38 * s, 60 * s, 18 * s, 4 * s)
  c.add(g)
  addSmallLabel(scene, c, 0, -29 * s, compactLandmarkLabel(poi.label || '边界门'), '#fde68a')
  layer.add(c)
}

function addFerryGate(scene, layer, ts, tx, ty, poi = {}) {
  const c = scene.add.container((tx + 0.5) * ts, (ty + 0.5) * ts)
  const g = scene.add.graphics()
  const s = ts / 34
  g.fillStyle(0x000000, 0.24)
  g.fillEllipse(0, 23 * s, 88 * s, 24 * s)
  g.fillStyle(0x2f5f73, 0.92)
  g.fillEllipse(0, 7 * s, 70 * s, 18 * s)
  g.fillStyle(0x7c5438, 1)
  g.fillRoundedRect(-34 * s, -4 * s, 68 * s, 12 * s, 3 * s)
  g.fillRoundedRect(-30 * s, 8 * s, 8 * s, 18 * s, 2 * s)
  g.fillRoundedRect(22 * s, 8 * s, 8 * s, 18 * s, 2 * s)
  g.lineStyle(2 * s, 0xd6b16f, 0.72)
  for (let x = -24; x <= 24; x += 12) g.lineBetween(x * s, -4 * s, x * s, 8 * s)
  g.fillStyle(0x0f172a, 0.68)
  g.fillRoundedRect(-27 * s, -31 * s, 54 * s, 17 * s, 4 * s)
  g.lineStyle(1.5 * s, 0x5eead4, 0.72)
  g.strokeRoundedRect(-27 * s, -31 * s, 54 * s, 17 * s, 4 * s)
  c.add(g)
  addSmallLabel(scene, c, 0, -22 * s, compactLandmarkLabel(poi.label || '旧渡口'), '#ccfbf1')
  layer.add(c)
}

export function drawLandmarkArt(scene, map, ts) {
  const layer = scene.add.container(0, 0).setDepth(5)
  const pois = map.pois || []
  const renderers = {
    library: addLibrary,
    home: addHome,
    gigasTree: addGigasTree,
    teleportGate: addTeleportGate,
    boundaryGate: addBoundaryGate,
    ferryGate: addFerryGate
  }
  for (const cfg of LANDMARK_ART_CONFIGS) {
    const poi = pois.find((p) => cfg.poiIds?.includes(p.id))
    const renderer = renderers[cfg.renderer]
    if (!poi || !renderer) continue
    renderer(scene, layer, ts, Number(poi.tile_x) || 0, Number(poi.tile_y) || 0, poi)
  }
  return layer
}

export function sceneZoneLabels(map) {
  const zones = map.scene_zones || []
  const labels = []
  for (const z of zones) {
    const sid = z.scene_id || ''
    const text = getSceneLabel(sid)
    const cx = ((z.x1 ?? 0) + (z.x2 ?? 0)) / 2
    const cy = ((z.y1 ?? 0) + (z.y2 ?? 0)) / 2
    labels.push({ x: cx, y: cy, text })
  }
  return labels
}
