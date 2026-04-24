/** 开放世界地块绘制与地图美术（Phaser Graphics 用） */

import {
  AGENT_ART_KEYS,
  AGENT_TEXTURE_FALLBACKS,
  LANDMARK_ART_CONFIGS,
  SCENE_LABELS
} from './gameContentConfig.js'

export const ZOOM_MIN = 0.42
export const ZOOM_MAX = 2.35
export const ZOOM_WHEEL = 0.055

export const MINI_COL = {
  0: 0x4f9c54,
  1: 0x183d25,
  2: 0x2f7fa6,
  3: 0xc8a56a,
  4: 0x6f5947
}

export { AGENT_ART_KEYS }

/** 伪随机 0..1，与坐标绑定，保证贴图细节稳定。 */
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

  if (code === 0) {
    g.fillStyle(h0 > 0.48 ? 0x5aa65a : 0x4f9652, 1)
    g.fillRect(px + pad, py + pad, w, h)
    g.fillStyle(0x86c56b, 0.18)
    g.fillTriangle(px, py, px + w * 0.9, py, px, py + h * 0.62)
    g.fillStyle(0x2f6f3b, 0.18)
    g.fillTriangle(px + w, py + h, px + w * 0.15, py + h, px + w, py + h * 0.24)
    if (h0 > 0.64) {
      strokeGrassBlade(g, px + ts * (0.22 + h0 * 0.18), py + ts * 0.74, ts, 0x174f2d, 0.42)
    }
    if (h0 > 0.82) {
      g.fillStyle(h0 > 0.91 ? 0xf7d56a : 0xd9f99d, 0.85)
      g.fillCircle(px + ts * 0.68, py + ts * 0.42, Math.max(1.2, ts * 0.045))
    }
  } else if (code === 1) {
    g.fillStyle(0x173b25, 1)
    g.fillRect(px, py, w, h)
    g.fillStyle(0x0f2a1b, 0.82)
    g.fillEllipse(px + ts * 0.5, py + ts * 0.72, ts * 0.72, ts * 0.34)
    g.fillStyle(0x6c482c, 1)
    g.fillRoundedRect(px + ts * 0.43, py + ts * 0.48, ts * 0.14, ts * 0.42, Math.max(1, ts * 0.03))
    g.fillStyle(h0 > 0.55 ? 0x1f6d3d : 0x14522f, 1)
    g.fillCircle(px + ts * 0.5, py + ts * 0.34, ts * 0.31)
    g.fillStyle(0x2f8f51, 0.88)
    g.fillCircle(px + ts * 0.36, py + ts * 0.43, ts * 0.2)
    g.fillCircle(px + ts * 0.64, py + ts * 0.45, ts * 0.19)
    g.fillStyle(0xb7e36c, 0.16)
    g.fillCircle(px + ts * 0.39, py + ts * 0.24, ts * 0.1)
  } else if (code === 2) {
    g.fillStyle(0x2f7599, 1)
    g.fillRect(px, py, w, h)
    g.fillStyle(0x174d72, 0.42)
    g.fillTriangle(px + w, py + h, px + w * 0.2, py + h, px + w, py + h * 0.2)
    g.lineStyle(Math.max(1, ts * 0.04), 0x92e6ff, 0.23)
    const wave = ((x + y) % 3) * ts * 0.08
    g.lineBetween(px + ts * 0.14, py + ts * 0.32 + wave, px + ts * 0.86, py + ts * 0.28 + wave)
    g.lineStyle(Math.max(1, ts * 0.03), 0xc8f7ff, 0.18)
    g.lineBetween(px + ts * 0.22, py + ts * 0.62, px + ts * 0.68, py + ts * 0.58)
  } else if (code === 3) {
    g.fillStyle(0xb98e58, 1)
    g.fillRect(px, py, w, h)
    g.fillStyle(0xd3b274, 0.68)
    g.fillTriangle(px, py, px + w * 0.7, py, px, py + h * 0.52)
    g.fillStyle(0x7f5f3e, 0.28)
    g.fillTriangle(px + w, py + h, px + w * 0.12, py + h, px + w, py + h * 0.36)
    if (h0 > 0.35) {
      g.fillStyle(0x765235, 0.36)
      g.fillEllipse(px + ts * (0.24 + h0 * 0.4), py + ts * (0.2 + h0 * 0.5), ts * 0.12, ts * 0.06)
    }
  } else {
    g.fillStyle(0x645444, 1)
    g.fillRect(px, py, w, h)
    g.fillStyle(0x8b755f, 0.74)
    g.fillTriangle(px + ts * 0.13, py + ts * 0.82, px + ts * 0.54, py + ts * 0.16, px + ts * 0.92, py + ts * 0.78)
    g.fillStyle(0x3b2e24, 0.28)
    g.fillTriangle(px + ts * 0.54, py + ts * 0.16, px + ts * 0.92, py + ts * 0.78, px + ts * 0.58, py + ts * 0.72)
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

      if (code === 0) {
        const northWater = codeAt(rows, x, y - 1) === 2
        const southWater = codeAt(rows, x, y + 1) === 2
        const westWater = codeAt(rows, x - 1, y) === 2
        const eastWater = codeAt(rows, x + 1, y) === 2
        if (northWater || southWater || westWater || eastWater) {
          g.fillStyle(0xd2bd72, 0.62)
          if (northWater) g.fillRect(px, py, ts, ts * 0.18)
          if (southWater) g.fillRect(px, py + ts * 0.82, ts, ts * 0.18)
          if (westWater) g.fillRect(px, py, ts * 0.18, ts)
          if (eastWater) g.fillRect(px + ts * 0.82, py, ts * 0.18, ts)
        }
        if (h0 > 0.78) {
          strokeGrassBlade(g, px + ts * 0.22, py + ts * 0.78, ts, 0x154b2d, 0.54)
          strokeGrassBlade(g, px + ts * 0.72, py + ts * 0.58, ts * 0.8, 0x1f6b3c, 0.44)
        }
      }

      if (code === 3) {
        g.lineStyle(Math.max(1, ts * 0.04), 0x6f4b2d, 0.18)
        if (codeAt(rows, x, y - 1) !== 3) g.lineBetween(px, py + 1, px + ts, py + 1)
        if (codeAt(rows, x, y + 1) !== 3) g.lineBetween(px, py + ts - 1, px + ts, py + ts - 1)
        if (codeAt(rows, x - 1, y) !== 3) g.lineBetween(px + 1, py, px + 1, py + ts)
        if (codeAt(rows, x + 1, y) !== 3) g.lineBetween(px + ts - 1, py, px + ts - 1, py + ts)
      }
    }
  }
  return g
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
  layer.add(mist)
  scene.tweens.add({
    targets: mist,
    alpha: 0.62,
    x: ts * 0.24,
    duration: 2600,
    yoyo: true,
    repeat: -1,
    ease: 'Sine.easeInOut'
  })

  const signs = scene.add.container(0, 0)
  addBoundarySign(scene, signs, mapW * 0.5, ts * 2.2, '北境边界')
  addBoundarySign(scene, signs, mapW - ts * 4.2, mapH * 0.48, '东侧山道')
  addBoundarySign(scene, signs, mapW * 0.3, mapH - ts * 2.4, '村外渡口')
  signs.setAlpha(0.86)
  layer.add(signs)

  return layer
}

function makeCharacterTexture(scene, key, p) {
  if (scene.textures.exists(key)) return
  const g = scene.make.graphics({ x: 0, y: 0, add: false })
  g.fillStyle(0x000000, 0.22)
  g.fillEllipse(32, 68, 30, 9)
  g.fillStyle(p.cape, 1)
  g.fillTriangle(17, 61, 32, 31, 47, 61)
  g.fillStyle(p.body, 1)
  g.fillRoundedRect(22, 36, 20, 26, 6)
  g.fillStyle(p.accent, 0.92)
  g.fillRoundedRect(25, 41, 14, 5, 2)
  g.fillStyle(p.skin, 1)
  g.fillEllipse(32, 25, 19, 21)
  g.fillStyle(p.hair, 1)
  g.fillEllipse(32, 18, 22, 15)
  g.fillRoundedRect(21, 19, 8, 17, 5)
  g.fillRoundedRect(35, 19, 9, 18, 5)
  g.fillStyle(0x1b2230, 0.9)
  g.fillRect(27, 27, 2, 2)
  g.fillRect(36, 27, 2, 2)
  g.fillStyle(0xf9fafb, 0.75)
  g.fillCircle(29, 26, 0.8)
  g.fillCircle(38, 26, 0.8)
  g.lineStyle(2, 0xf7d37b, 0.86)
  g.strokeCircle(32, 30, 22)
  g.generateTexture(key, 64, 76)
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
  addSmallLabel(scene, c, 0, -97 * s, '巨树', '#fef08a')
  layer.add(c)
}

export function drawLandmarkArt(scene, map, ts) {
  const layer = scene.add.container(0, 0).setDepth(5)
  const pois = map.pois || []
  const renderers = {
    library: addLibrary,
    home: addHome,
    gigasTree: addGigasTree
  }
  for (const cfg of LANDMARK_ART_CONFIGS) {
    const poi = pois.find((p) => cfg.poiIds?.includes(p.id))
    const renderer = renderers[cfg.renderer]
    if (!poi || !renderer) continue
    renderer(scene, layer, ts, Number(poi.tile_x) || 0, Number(poi.tile_y) || 0)
  }
  return layer
}

export function sceneZoneLabels(map) {
  const zones = map.scene_zones || []
  const labels = []
  for (const z of zones) {
    const sid = z.scene_id || ''
    const text = SCENE_LABELS[sid] || sid
    const cx = ((z.x1 ?? 0) + (z.x2 ?? 0)) / 2
    const cy = ((z.y1 ?? 0) + (z.y2 ?? 0)) / 2
    labels.push({ x: cx, y: cy, text })
  }
  return labels
}
