import {
  AGENT_ART_KEYS,
  drawLandmarkArt,
  drawExplorationAtmosphere,
  drawNavigationOverlay,
  drawStyledTile,
  drawTerrainOverlays,
  drawWaterRipples,
  ensureWorldArtTextures,
  MINI_COL,
  ZOOM_MAX,
  ZOOM_MIN,
  ZOOM_WHEEL
} from './worldMapDrawing.js'
import { AGENTS, getAgentConfig, shouldLoadAgentSpriteAsset } from './gameContentConfig.js'
import { DEFAULT_MAP_ID, getSceneDefinition, getWorldBackgroundAsset } from './sceneRegistry.js'

function distance(a, b) {
  const dx = a.x - b.x
  const dy = a.y - b.y
  return Math.sqrt(dx * dx + dy * dy)
}

function compressTilePath(path) {
  if (!Array.isArray(path) || path.length <= 2) return path || []
  const out = [path[0]]
  for (let i = 1; i < path.length - 1; i++) {
    const prev = path[i - 1]
    const cur = path[i]
    const next = path[i + 1]
    const dx1 = Math.sign(cur.x - prev.x)
    const dy1 = Math.sign(cur.y - prev.y)
    const dx2 = Math.sign(next.x - cur.x)
    const dy2 = Math.sign(next.y - cur.y)
    if (dx1 !== dx2 || dy1 !== dy2) out.push(cur)
  }
  out.push(path[path.length - 1])
  return out
}

function sceneIdForTile(map, tx, ty) {
  const zones = Array.isArray(map?.scene_zones) ? map.scene_zones : []
  for (const zone of zones) {
    const x1 = Number(zone.x1 ?? 0)
    const y1 = Number(zone.y1 ?? 0)
    const x2 = Number(zone.x2 ?? x1)
    const y2 = Number(zone.y2 ?? y1)
    if (
      tx >= Math.min(x1, x2) &&
      tx <= Math.max(x1, x2) &&
      ty >= Math.min(y1, y2) &&
      ty <= Math.max(y1, y2)
    ) {
      return String(zone.scene_id || '')
    }
  }
  return ''
}

function zoneForTile(map, tx, ty) {
  const zones = Array.isArray(map?.scene_zones) ? map.scene_zones : []
  for (const zone of zones) {
    const x1 = Number(zone.x1 ?? 0)
    const y1 = Number(zone.y1 ?? 0)
    const x2 = Number(zone.x2 ?? x1)
    const y2 = Number(zone.y2 ?? y1)
    if (
      tx >= Math.min(x1, x2) &&
      tx <= Math.max(x1, x2) &&
      ty >= Math.min(y1, y2) &&
      ty <= Math.max(y1, y2)
    ) {
      return zone
    }
  }
  return null
}

function isBlockedZone(zone) {
  const type = String(zone?.regionType || '')
  return type === 'locked' || type === 'forbidden'
}

function mapBounds(map) {
  const rows = Array.isArray(map?.rows) ? map.rows : []
  const height = rows.length
  const width = height > 0 ? String(rows[0] || '').length : 0
  return { rows, width, height }
}

function codeAtMap(map, x, y) {
  const { rows, width, height } = mapBounds(map)
  if (x < 0 || y < 0 || x >= width || y >= height) return null
  const ch = String(rows[y] || '')[x] || '0'
  return ch >= '0' && ch <= '9' ? Number(ch) : 0
}

function isWorldTileWalkable(map, x, y, opts = {}) {
  const code = codeAtMap(map, x, y)
  if (code == null) return false
  const walkable = new Set((map?.walkable || [0, 3]).map((v) => Number(v)))
  if (!walkable.has(code)) return false
  if (!opts.allowBlockedZone && isBlockedZone(zoneForTile(map, x, y))) return false
  return '不可通行区域'
}

function terrainLabelAt(map, x, y) {
  const code = codeAtMap(map, x, y)
  if (code === 1) return '森林'
  if (code === 2) return '水域'
  if (code === 4) return '岩石障碍'
  if (isBlockedZone(zoneForTile(map, x, y))) return zoneForTile(map, x, y)?.label || '边界区域'
  return '不可通行区域'
}

function findNearestDisplayTile(map, tx, ty, opts = {}) {
  const x0 = Math.floor(Number(tx))
  const y0 = Math.floor(Number(ty))
  if (!Number.isFinite(x0) || !Number.isFinite(y0)) return { x: 0, y: 0, snapped: false }
  const radius = Number(opts.radius ?? 7)
  const preferRoad = opts.preferRoad !== false
  if (isWorldTileWalkable(map, x0, y0, opts)) return { x: x0, y: y0, snapped: false }

  let best = null
  let bestScore = Infinity
  const { width, height } = mapBounds(map)
  for (let r = 1; r <= radius; r++) {
    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue
        const x = x0 + dx
        const y = y0 + dy
        if (x < 0 || y < 0 || x >= width || y >= height) continue
        if (!isWorldTileWalkable(map, x, y, opts)) continue
        const code = codeAtMap(map, x, y)
        let score = Math.abs(dx) + Math.abs(dy)
        if (preferRoad && code === 3) score -= 0.45
        if (!isBlockedZone(zoneForTile(map, x, y))) score -= 0.15
        if (score < bestScore) {
          bestScore = score
          best = { x, y, snapped: true }
        }
      }
    }
    if (best) return best
  }
  return { x: x0, y: y0, snapped: false }
}

function localBfsPath(map, sx, sy, tx, ty) {
  const rows = Array.isArray(map?.rows) ? map.rows : []
  const height = rows.length
  const width = height > 0 ? String(rows[0] || '').length : 0
  if (!width || !height) return null
  const walkable = new Set((map?.walkable || [0, 3]).map((v) => Number(v)))
  const inBounds = (x, y) => x >= 0 && y >= 0 && x < width && y < height
  const codeAt = (x, y) => {
    const ch = String(rows[y] || '')[x] || '0'
    return ch >= '0' && ch <= '9' ? Number(ch) : 0
  }
  const passable = (x, y) => {
    if (!inBounds(x, y)) return false
    if (!walkable.has(codeAt(x, y))) return false
    return !isBlockedZone(zoneForTile(map, x, y))
  }
  sx = Math.floor(Number(sx))
  sy = Math.floor(Number(sy))
  tx = Math.floor(Number(tx))
  ty = Math.floor(Number(ty))
  if (!passable(sx, sy) || !passable(tx, ty)) return null
  const startKey = `${sx},${sy}`
  const endKey = `${tx},${ty}`
  if (startKey === endKey) return [{ x: sx, y: sy }]
  const q = [{ x: sx, y: sy }]
  const came = new Map([[startKey, null]])
  const dirs = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1]
  ]
  for (let qi = 0; qi < q.length; qi++) {
    const cur = q[qi]
    for (const [dx, dy] of dirs) {
      const nx = cur.x + dx
      const ny = cur.y + dy
      const key = `${nx},${ny}`
      if (came.has(key) || !passable(nx, ny)) continue
      came.set(key, `${cur.x},${cur.y}`)
      if (key === endKey) {
        const out = []
        let k = key
        while (k) {
          const [px, py] = k.split(',').map(Number)
          out.push({ x: px, y: py })
          k = came.get(k)
        }
        return out.reverse()
      }
      q.push({ x: nx, y: ny })
    }
  }
  return null
}

function drawBlockedZoneWarnings(scene, map, ts) {
  const layer = scene.add.container(0, 0).setDepth(9)
  const zones = Array.isArray(map?.scene_zones) ? map.scene_zones : []
  for (const zone of zones) {
    if (!isBlockedZone(zone)) continue
    const x1 = Number(zone.x1 ?? 0)
    const y1 = Number(zone.y1 ?? 0)
    const x2 = Number(zone.x2 ?? x1)
    const y2 = Number(zone.y2 ?? y1)
    const left = Math.min(x1, x2) * ts
    const top = Math.min(y1, y2) * ts
    const width = (Math.abs(x2 - x1) + 1) * ts
    const height = (Math.abs(y2 - y1) + 1) * ts
    const color = String(zone.regionType) === 'forbidden' ? 0xef4444 : 0xc084fc
    const fill = scene.add.graphics()
    fill.fillStyle(0x050816, 0.12)
    fill.fillRoundedRect(left + 2, top + 2, width - 4, height - 4, Math.max(8, ts * 0.22))
    fill.lineStyle(Math.max(2, ts * 0.06), color, 0.38)
    fill.strokeRoundedRect(left + 3, top + 3, width - 6, height - 6, Math.max(8, ts * 0.22))
    fill.lineStyle(1, 0xfff7d6, 0.08)
    for (let d = -height; d < width; d += ts * 0.82) {
      fill.lineBetween(left + d, top + height, left + d + height, top)
    }
    layer.add(fill)

    const label = scene.add
      .text(left + width / 2, top + height / 2, zone.label || '未开放区域', {
        fontSize: '15px',
        color: '#fff7d6',
        fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
        fontStyle: 'bold',
        stroke: '#16081f',
        strokeThickness: 5,
        align: 'center'
      })
      .setOrigin(0.5)
      .setAlpha(0.62)
    layer.add(label)
  }
  return layer
}

function tilePathToSmoothWorldPoints(tilePath, ts) {
  const norm = (tilePath || [])
    .map((p) => ({ x: Number(p.x), y: Number(p.y) }))
    .filter((p) => Number.isFinite(p.x) && Number.isFinite(p.y))
  const compact = compressTilePath(norm)
  const pts = compact.map((p) => ({
    x: (p.x + 0.5) * ts,
    y: (p.y + 0.5) * ts
  }))
  if (pts.length <= 2) return pts

  const out = [pts[0]]
  const steps = 7
  for (let i = 1; i < pts.length - 1; i++) {
    const prev = pts[i - 1]
    const cur = pts[i]
    const next = pts[i + 1]
    const vx1 = prev.x - cur.x
    const vy1 = prev.y - cur.y
    const vx2 = next.x - cur.x
    const vy2 = next.y - cur.y
    const l1 = Math.max(1, Math.sqrt(vx1 * vx1 + vy1 * vy1))
    const l2 = Math.max(1, Math.sqrt(vx2 * vx2 + vy2 * vy2))
    const sameLine = Math.abs((vx1 / l1) * (vy2 / l2) - (vy1 / l1) * (vx2 / l2)) < 0.01
    if (sameLine) {
      out.push(cur)
      continue
    }
    const r = Math.min(ts * 0.44, l1 * 0.46, l2 * 0.46)
    const start = { x: cur.x + (vx1 / l1) * r, y: cur.y + (vy1 / l1) * r }
    const end = { x: cur.x + (vx2 / l2) * r, y: cur.y + (vy2 / l2) * r }
    out.push(start)
    for (let s = 1; s <= steps; s++) {
      const t = s / steps
      const a = (1 - t) * (1 - t)
      const b = 2 * (1 - t) * t
      const c = t * t
      out.push({
        x: a * start.x + b * cur.x + c * end.x,
        y: a * start.y + b * cur.y + c * end.y
      })
    }
  }
  out.push(pts[pts.length - 1])
  return out
}

function drawSmoothRoute(g, points) {
  g.clear()
  if (!points || points.length < 2) return
  const end = points[points.length - 1]

  g.lineStyle(2, 0xfff7d6, 0.2)
  g.beginPath()
  g.moveTo(points[0].x, points[0].y)
  for (let i = 1; i < points.length; i++) {
    g.lineTo(points[i].x, points[i].y)
  }
  g.strokePath()

  const stride = Math.max(5, Math.floor(points.length / 8))
  g.fillStyle(0xfff7d6, 0.34)
  for (let i = stride; i < points.length - 1; i += stride) {
    g.fillCircle(points[i].x, points[i].y, 2.2)
  }

  g.fillStyle(0xfbbf24, 0.12)
  g.fillCircle(end.x, end.y, 22)
  g.lineStyle(2, 0xfbbf24, 0.72)
  g.strokeCircle(end.x, end.y, 16)
  g.lineStyle(1, 0xfff7d6, 0.46)
  g.strokeCircle(end.x, end.y, 9)
}

function bakeGraphicsLayer(scene, key, graphics, width, height, depth, alpha = 1) {
  if (!graphics) return null
  const w = Math.max(1, Math.ceil(Number(width) || 1))
  const h = Math.max(1, Math.ceil(Number(height) || 1))
  if (scene.textures.exists(key)) scene.textures.remove(key)
  graphics.generateTexture(key, w, h)
  graphics.destroy()
  return scene.add.image(0, 0, key).setOrigin(0, 0).setDepth(depth).setAlpha(alpha)
}

function numberSetting(value, fallback, min = -Infinity, max = Infinity) {
  const n = Number(value)
  if (!Number.isFinite(n)) return fallback
  return Math.max(min, Math.min(max, n))
}

function pickGuideTarget(map, state, events) {
  const player = state?.player
  if (!player) return null
  const px = Number(player.tile_x)
  const py = Number(player.tile_y)
  if (!Number.isFinite(px) || !Number.isFinite(py)) return null

  const candidates = []
  for (const ev of Array.isArray(events) ? events : []) {
    const loc = ev?.location || {}
    const tx = Number(loc.tile_x)
    const ty = Number(loc.tile_y)
    if (!Number.isFinite(tx) || !Number.isFinite(ty)) continue
    candidates.push({ tx, ty, label: ev.title || '线索' })
  }

  if (!candidates.length) {
    const node = state?.story_node_id || ''
    for (const poi of map?.pois || []) {
      if (poi.kind !== 'quest') continue
      const activeNodes = poi.active_story_nodes
      if (Array.isArray(activeNodes) && activeNodes.length && !activeNodes.includes(node)) continue
      const tx = Number(poi.tile_x)
      const ty = Number(poi.tile_y)
      if (!Number.isFinite(tx) || !Number.isFinite(ty)) continue
      candidates.push({ tx, ty, label: poi.label || '线索' })
    }
  }

  candidates.sort((a, b) => {
    const da = Math.abs(a.tx - px) + Math.abs(a.ty - py)
    const db = Math.abs(b.tx - px) + Math.abs(b.ty - py)
    return da - db
  })
  const best = candidates[0] || null
  if (!best) return null
  const display = findNearestDisplayTile(map, best.tx, best.ty, { radius: 7, preferRoad: true })
  return { ...best, displayTx: display.x, displayTy: display.y }
}

function drawQuestGuide(scene, g, target, ts) {
  g.clear()
  if (!target || !scene.playerRoot) return
  const sx = scene.playerRoot.x
  const sy = scene.playerRoot.y
  const ex = (Number(target.displayTx ?? target.tx) + 0.5) * ts
  const ey = (Number(target.displayTy ?? target.ty) + 0.5) * ts
  const dx = ex - sx
  const dy = ey - sy
  const dist = Math.sqrt(dx * dx + dy * dy)
  if (!Number.isFinite(dist) || dist < ts * 1.8) return

  const ux = dx / dist
  const uy = dy / dist
  const px = -uy
  const py = ux
  const phase = (scene.time.now % 1200) / 1200
  const start = Math.min(ts * 1.3, dist * 0.26)
  const maxD = Math.min(dist - ts * 0.8, ts * 8.5)

  g.lineStyle(2, 0xfbbf24, 0.18)
  g.beginPath()
  g.moveTo(sx + ux * start, sy + uy * start)
  g.lineTo(sx + ux * maxD, sy + uy * maxD)
  g.strokePath()

  for (let i = 0; i < 4; i++) {
    const d = start + ts * (1.05 + i * 1.25 + phase)
    if (d >= maxD) continue
    const cx = sx + ux * d
    const cy = sy + uy * d
    const tipX = cx + ux * ts * 0.38
    const tipY = cy + uy * ts * 0.38
    const leftX = cx - ux * ts * 0.18 + px * ts * 0.18
    const leftY = cy - uy * ts * 0.18 + py * ts * 0.18
    const rightX = cx - ux * ts * 0.18 - px * ts * 0.18
    const rightY = cy - uy * ts * 0.18 - py * ts * 0.18
    g.fillStyle(0xfff7d6, 0.18 + i * 0.08)
    g.fillTriangle(tipX, tipY, leftX, leftY, rightX, rightY)
    g.lineStyle(1, 0xfbbf24, 0.38)
    g.lineBetween(leftX, leftY, tipX, tipY)
    g.lineBetween(rightX, rightY, tipX, tipY)
  }

  const pulse = 2 + Math.sin(scene.time.now / 180) * 2
  g.fillStyle(0xfbbf24, 0.07)
  g.fillCircle(ex, ey, ts * 0.62 + pulse)
  g.lineStyle(2, 0xfde047, 0.48)
  g.strokeCircle(ex, ey, ts * 0.44 + pulse)
}

function addStoryBeacon(scene, cont, label, ts, opts = {}) {
  const active = opts.active !== false
  const important = !!opts.important
  const showLabel = opts.showLabel === true
  const root = scene.add.container(0, 0)
  const height = ts * (important ? 2.45 : 2.08)
  const baseW = ts * (important ? 0.94 : 0.72)

  const beam = scene.add.graphics()
  beam.fillStyle(0xfbbf24, active ? (important ? 0.16 : 0.12) : 0.04)
  beam.fillTriangle(0, -height, -baseW * 0.5, -ts * 0.05, baseW * 0.5, -ts * 0.05)
  beam.fillStyle(0xfff7d6, active ? (important ? 0.12 : 0.08) : 0.03)
  beam.fillEllipse(0, -height * 0.52, baseW * 0.58, height * 0.82)

  const shadow = scene.add.ellipse(0, ts * 0.08, ts * 1.04, ts * 0.34, 0x020617, 0.28)
  const ring = scene.add
    .ellipse(0, 0, ts * (important ? 1.26 : 1.04), ts * 0.38, 0xfbbf24, active ? 0.13 : 0.04)
    .setStrokeStyle(2, 0xfde047, active ? 0.72 : 0.22)
  const core = scene.add
    .circle(0, -ts * 0.52, ts * (important ? 0.28 : 0.22), 0xfff7d6, active ? 0.92 : 0.22)
    .setStrokeStyle(important ? 2.5 : 2, 0xfbbf24, active ? 0.9 : 0.22)
  const spark = scene.add.star(0, -ts * 0.52, 4, ts * 0.07, ts * (important ? 0.22 : 0.18), 0xfff7d6, active ? 0.9 : 0.2)
  const icon = scene.add
    .text(0, -ts * 0.55, important ? '!' : '•', {
      fontSize: important ? '15px' : '12px',
      color: '#fff7d6',
      fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
      fontStyle: 'bold',
      stroke: '#0f172a',
      strokeThickness: 3,
      align: 'center'
    })
    .setOrigin(0.5)
  const text = showLabel
    ? scene.add
      .text(0, -height - ts * 0.04, compactWorldLabel(label || '线索'), {
        fontSize: important ? '10px' : '9px',
        color: '#fff7d6',
        fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
        fontStyle: 'bold',
        stroke: '#0f172a',
        strokeThickness: 3,
        align: 'center'
      })
      .setOrigin(0.5, 1)
    : null

  root.add([shadow, beam, ring, core, spark, icon])
  if (text) root.add(text)
  cont.add(root)

  if (active) {
    scene.tweens.add({
      targets: ring,
      scaleX: 1.18,
      scaleY: 1.2,
      alpha: 0.42,
      duration: important ? 820 : 980,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut'
    })
    scene.tweens.add({
      targets: core,
      y: -ts * 0.64,
      duration: 940,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut'
    })
    scene.tweens.add({
      targets: spark,
      angle: 360,
      duration: important ? 2200 : 2800,
      repeat: -1,
      ease: 'Linear'
    })
  }

  return root
}

function buildDistanceTable(points) {
  const table = [{ d: 0, x: points[0].x, y: points[0].y }]
  let total = 0
  for (let i = 1; i < points.length; i++) {
    total += distance(points[i - 1], points[i])
    table.push({ d: total, x: points[i].x, y: points[i].y })
  }
  return { table, total }
}

function pointAtDistance(table, target) {
  if (!table.length) return { x: 0, y: 0 }
  if (target <= 0) return table[0]
  const last = table[table.length - 1]
  if (target >= last.d) return last

  let lo = 0
  let hi = table.length - 1
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2)
    if (table[mid].d < target) lo = mid + 1
    else hi = mid
  }
  const b = table[lo]
  const a = table[Math.max(0, lo - 1)]
  const span = Math.max(1, b.d - a.d)
  const t = (target - a.d) / span
  return {
    x: a.x + (b.x - a.x) * t,
    y: a.y + (b.y - a.y) * t
  }
}

function compactWorldLabel(label, max = 6) {
  const text = String(label || '').trim()
  if (!text) return ''
  return text.length > max ? `${text.slice(0, max)}…` : text
}

function characterFormationOffset(agentId, slot, sameTileWithPlayer) {
  const base = {
    alice: { x: -16, y: -2 },
    eugeo: { x: 16, y: -2 },
    kirito: { x: 0, y: 0 }
  }[agentId] || { x: 0, y: 0 }
  if (sameTileWithPlayer) return base
  const spread = [
    { x: 0, y: 0 },
    { x: -14, y: -2 },
    { x: 14, y: -2 },
    { x: 0, y: -9 }
  ][slot] || { x: 0, y: 0 }
  return {
    x: base.x * 0.35 + spread.x,
    y: base.y * 0.35 + spread.y
  }
}

/**
 * @param {typeof import('phaser')} Phaser
 * @param {{
 *   getMap: () => object,
 *   onTilePick: (tx: number, ty: number) => void,
 *   getSimState: () => object,
 *   assignSceneInstance: (scene: import('phaser').Scene) => void,
 *   syncPlayerFromState: () => void,
 *   openInteractPanel: () => void,
 *   openNpcPanel: (agentId: string) => void,
 *   isBusy: () => boolean,
 *   getNearbyInteractPoi: () => object | null,
 *   getStoryEvents?: () => object[],
 *   openStoryEventPanel?: (eventId: string) => void,
 *   isDevMode?: () => boolean,
 *   onBlockedTilePick?: (payload: object) => void
 * }} deps
 */
export function createWorldFieldSceneClass(Phaser, deps) {
  const {
    getMap,
    onTilePick,
    getSimState,
    assignSceneInstance,
    syncPlayerFromState,
    openInteractPanel,
    openNpcPanel,
    isBusy,
    getNearbyInteractPoi,
    getStoryEvents = () => [],
    openStoryEventPanel = () => {},
    isDevMode = () => false,
    onBlockedTilePick = () => {}
  } = deps

  return class WorldFieldScene extends Phaser.Scene {
    constructor() {
      super({ key: 'WorldField' })
    }

    preload() {
      const mapId = getMap()?.id || DEFAULT_MAP_ID
      const visual = getMap()?.visual || {}
      this._worldBackgroundKey = `world_bg_${String(mapId).replace(/[^a-zA-Z0-9_-]/g, '_')}`
      const background = getWorldBackgroundAsset(mapId)
      if (background && visual.background !== false && !this.textures.exists(this._worldBackgroundKey)) {
        this.load.image(this._worldBackgroundKey, background)
      }
      for (const cfg of Object.values(AGENTS)) {
        if (shouldLoadAgentSpriteAsset(cfg) && !this.textures.exists(cfg.textureKey)) {
          this.load.image(cfg.textureKey, cfg.asset)
        }
      }
    }

    resumeCameraFollow() {
      const cam = this.cameras.main
      if (this.playerRoot) {
        const lerp = this._cameraFollowLerp ?? 0.18
        cam.startFollow(this.playerRoot, true, lerp, lerp)
      }
    }

    handleViewportResize() {
      const cam = this.cameras.main
      if (!cam) return
      cam.setBounds(0, 0, this._mapWtiles * this._tileSize, this._mapHtiles * this._tileSize)
      this.refreshMiniViewport?.()
    }

    updateWorldInteractButton() {
      const root = this._interactBtnRoot
      if (!root) return
      const poi = !isBusy() && getNearbyInteractPoi()
      if (!poi) {
        root.setVisible(false)
        return
      }
      const tsz = this._tileSize
      const tx = Number(poi.tile_x) || 0
      const ty = Number(poi.tile_y) || 0
      const displayX = Number(poi.display_tile_x ?? poi.approach_tile_x)
      const displayY = Number(poi.display_tile_y ?? poi.approach_tile_y)
      const display = Number.isFinite(displayX) && Number.isFinite(displayY)
        ? { x: displayX, y: displayY }
        : findNearestDisplayTile(getMap(), tx, ty, { radius: 7, preferRoad: true })
      const sceneId = String(poi.scene_id || sceneIdForTile(getMap(), tx, ty))
      const sceneDef = getSceneDefinition(sceneId)
      const roleLabel = sceneDef.role && sceneDef.role !== 'explore' ? sceneDef.roleLabel : ''
      const zoneLabel = poi.zoneLabel || sceneDef.roleLabel || sceneDef.label || roleLabel
      const actionLabel = poi.regionType === 'locked' ? '调查' : '进入'
      const buttonLabel = `${actionLabel} ${compactWorldLabel(zoneLabel || '场景', 5)}`
      this._interactBtnText?.setText?.(buttonLabel)

      const baseX = (display.x + 0.5) * tsz
      const baseY = (display.y + 0.5) * tsz
      const mapW = Math.max(tsz, (this._mapWtiles || 1) * tsz)
      const mapH = Math.max(tsz, (this._mapHtiles || 1) * tsz)
      const halfW = this._interactBtnHalfW || 54
      const halfH = this._interactBtnHalfH || 14
      const people = [this.playerRoot, ...Object.values(this._npcContainers || {})].filter(Boolean)
      const offsets = [
        { x: tsz * 3.05, y: -tsz * 0.35 },
        { x: -tsz * 3.05, y: -tsz * 0.35 },
        { x: tsz * 2.55, y: tsz * 1.65 },
        { x: -tsz * 2.55, y: tsz * 1.65 },
        { x: 0, y: -tsz * 3.0 }
      ]
      let best = null
      for (const off of offsets) {
        let x = baseX + off.x
        let y = baseY + off.y
        let score = Math.abs(off.x) * 0.01 + Math.abs(off.y) * 0.008
        if (Math.abs(off.x) < tsz) score += 140
        if (x - halfW < 6 || x + halfW > mapW - 6 || y - halfH < 6 || y + halfH > mapH - 6) score += 400
        for (const person of people) {
          const d = Math.hypot((person.x || 0) - x, (person.y || 0) - y)
          if (d < tsz * 2.15) score += (tsz * 2.15 - d) * 8
        }
        x = Phaser.Math.Clamp(x, halfW + 8, mapW - halfW - 8)
        y = Phaser.Math.Clamp(y, halfH + 8, mapH - halfH - 8)
        if (!best || score < best.score) best = { x, y, score }
      }
      root.setPosition(best?.x ?? baseX, best?.y ?? baseY)
      root.setVisible(true)
    }

    refreshMiniViewport() {
      const L = this._miniLayout
      const vp = this._miniViewport
      if (!L || !vp) return
      const c = this.cameras.main
      const fixedScale = 1 / Math.max(0.001, c.zoom)
      for (const obj of this._miniFixedObjects || []) {
        const baseScaleX = obj._miniBaseScaleX ?? 1
        const baseScaleY = obj._miniBaseScaleY ?? baseScaleX
        obj.setScale?.(baseScaleX * fixedScale, baseScaleY * fixedScale)
      }
      const wv = c.worldView
      const sx = L.dispW / L.mapW
      const sy = L.dispH / L.mapH
      vp.clear()
      const st = getSimState()
      const agents = Array.isArray(st?.agents) ? st.agents : []
      for (const agent of agents) {
        const ax = Number(agent?.tile_x)
        const ay = Number(agent?.tile_y)
        if (!Number.isFinite(ax) || !Number.isFinite(ay)) continue
        const cfg = getAgentConfig(agent.id)
        const display = findNearestDisplayTile(getMap(), ax, ay, { radius: 7, preferRoad: true })
        const mx = L.ox + (display.x + 0.5) * this._tileSize * sx
        const my = L.oy + (display.y + 0.5) * this._tileSize * sy
        vp.fillStyle(cfg.haloColor || 0x5ecfff, 0.88)
        vp.fillCircle(mx, my, 3)
        vp.lineStyle(1, 0x05111c, 0.85)
        vp.strokeCircle(mx, my, 3)
      }
      const events = Array.isArray(getStoryEvents()) ? getStoryEvents() : []
      for (const ev of events) {
        const loc = ev?.location || {}
        const tx = Number(loc.tile_x)
        const ty = Number(loc.tile_y)
        if (!Number.isFinite(tx) || !Number.isFinite(ty)) continue
        const display = findNearestDisplayTile(getMap(), tx, ty, { radius: 7, preferRoad: true })
        const mx = L.ox + (display.x + 0.5) * this._tileSize * sx
        const my = L.oy + (display.y + 0.5) * this._tileSize * sy
        vp.fillStyle(0xfde047, 0.95)
        vp.fillTriangle(mx, my - 5, mx + 5, my, mx, my + 5)
        vp.fillTriangle(mx, my - 5, mx - 5, my, mx, my + 5)
        vp.lineStyle(1, 0x422006, 0.9)
        vp.strokeCircle(mx, my, 5)
      }
      if (this.playerRoot) {
        const px = this.playerRoot.x * sx
        const py = this.playerRoot.y * sy
        vp.fillStyle(0xfbbf24, 1)
        vp.fillCircle(L.ox + px, L.oy + py, 4)
        vp.lineStyle(1, 0x1a1209, 0.9)
        vp.strokeCircle(L.ox + px, L.oy + py, 4)
      }
      vp.lineStyle(1, 0x5ecfff, 0.36)
      vp.strokeRect(L.ox + wv.x * sx - 0.5, L.oy + wv.y * sy - 0.5, wv.width * sx + 1, wv.height * sy + 1)
      vp.lineStyle(2, 0xfbbf24, 0.92)
      vp.strokeRect(L.ox + wv.x * sx, L.oy + wv.y * sy, wv.width * sx, wv.height * sy)
      vp.lineStyle(1, 0xffffff, 0.28)
      vp.strokeRect(L.ox - 1, L.oy - 1, L.dispW + 2, L.dispH + 2)
    }

    create() {
      const map = getMap() || { rows: [], width: 0, height: 0, tile_size: 28 }
      const rows = map.rows || []
      const H = rows.length
      const W = H > 0 ? rows[0].length : 0
      const ts = Number(map.tile_size) || 28
      const visual = map?.visual || {}
      const cameraCfg = visual.camera || {}
      const movementCfg = visual.movement || {}
      const perfCfg = visual.performance || {}
      this._zoomMin = numberSetting(cameraCfg.min_zoom, ZOOM_MIN, 0.25, 4)
      this._zoomMax = numberSetting(cameraCfg.max_zoom, ZOOM_MAX, this._zoomMin, 4)
      this._zoomWheel = numberSetting(cameraCfg.wheel_step, ZOOM_WHEEL, 0.01, 0.25)
      this._cameraFollowLerp = numberSetting(cameraCfg.follow_lerp, 0.18, 0.01, 1)
      this._walkSpeed = numberSetting(movementCfg.walk_speed, 720, 120, 2400)
      this._walkMinMs = numberSetting(movementCfg.min_walk_ms, 110, 40, 800)
      this._walkMaxMs = numberSetting(movementCfg.max_walk_ms, 2400, this._walkMinMs, 8000)
      this._leftDragPanEnabled = movementCfg.left_drag_pan !== false
      this._guideIntervalMs = numberSetting(perfCfg.guide_interval_ms, 180, 60, 1000)
      this._waterIntervalMs = numberSetting(perfCfg.water_interval_ms, 180, 60, 1600)
      this._weatherIntervalMs = numberSetting(perfCfg.weather_interval_ms, 80, 32, 1200)
      this._tileSize = ts
      this._mapWtiles = W
      this._mapHtiles = H
      ensureWorldArtTextures(this)

      const mapW = W * ts
      const mapH = H * ts
      const bgKey = this._worldBackgroundKey || 'world_bg_novice_open'
      const hasWorldBg = this.textures.exists(bgKey)
      const useWorldBg = hasWorldBg && map?.visual?.background !== false
      if (useWorldBg) {
        const bg = this.add.image(mapW / 2, mapH / 2, bgKey).setDepth(-5)
        const bgScale = Math.max(mapW / Math.max(1, bg.width), mapH / Math.max(1, bg.height))
        bg.setScale(bgScale)
        bg.setAlpha(0.18)
        this.add.rectangle(mapW / 2, mapH / 2, mapW, mapH, 0x071019, 0.08).setDepth(-4)
      }

      const g = this.add.graphics()
      for (let y = 0; y < H; y++) {
        const row = rows[y] || ''
        for (let x = 0; x < W; x++) {
          const ch = row[x] || '0'
          const code = ch >= '0' && ch <= '9' ? parseInt(ch, 10) : 0
          drawStyledTile(g, x, y, ts, code)
        }
      }
      const bakeStaticLayers = perfCfg.bake_static_layers !== false
      if (bakeStaticLayers) {
        bakeGraphicsLayer(
          this,
          `world_static_base_${map.id || 'map'}_${W}x${H}_${ts}`,
          g,
          mapW,
          mapH,
          0,
          useWorldBg ? 0.92 : 1
        )
        bakeGraphicsLayer(
          this,
          `world_static_overlay_${map.id || 'map'}_${W}x${H}_${ts}`,
          drawTerrainOverlays(this, map, ts),
          mapW,
          mapH,
          2,
          useWorldBg ? 0.92 : 1
        )
      } else {
        g.setDepth(0)
        g.setAlpha(useWorldBg ? 0.92 : 1)
        drawTerrainOverlays(this, map, ts).setAlpha(useWorldBg ? 0.92 : 1)
      }
      this._waterRippleG = this.add.graphics().setDepth(2.5).setBlendMode(Phaser.BlendModes.SCREEN)
      drawWaterRipples(this._waterRippleG, map, ts, 0)
      // Keep zone data interactive, but do not paint large debug-like frames over the world.
      drawBlockedZoneWarnings(this, map, ts)
      drawLandmarkArt(this, map, ts).setAlpha(0.92)
      drawExplorationAtmosphere(this, map, ts).setAlpha(useWorldBg ? 0.22 : 0.64)
      this._navDebugOverlay = bakeStaticLayers
        ? bakeGraphicsLayer(
            this,
            `world_nav_overlay_${map.id || 'map'}_${W}x${H}_${ts}`,
            drawNavigationOverlay(this, map, ts),
            mapW,
            mapH,
            46,
            1
          )
        : drawNavigationOverlay(this, map, ts)
      this._navDebugOverlay?.setVisible(false)
      this.toggleNavigationOverlay = () => {
        this._navDebugOverlay?.setVisible(!this._navDebugOverlay.visible)
      }
      this._pathG = this.add.graphics().setDepth(3)
      this._guideG = this.add.graphics().setDepth(10)
      this._targetG = this.add.graphics().setDepth(16)
      this._weatherG = this.add.graphics().setDepth(47).setScrollFactor(0).setBlendMode(Phaser.BlendModes.SCREEN)
      this._rainDrops = Array.from({ length: 86 }, (_, i) => ({
        x: (i * 73) % 1440,
        y: (i * 131) % 900,
        len: 10 + (i % 5) * 4,
        speed: 5.2 + (i % 7) * 0.45,
        drift: 1.2 + (i % 4) * 0.16,
        alpha: 0.08 + (i % 5) * 0.025
      }))

      this.previewMoveTarget = (tx, ty) => {
        if (!this._targetG) return
        const x = (Number(tx) + 0.5) * this._tileSize
        const y = (Number(ty) + 0.5) * this._tileSize
        this.tweens.killTweensOf(this._targetG, true)
        this._targetG.clear()
        this._targetG.setAlpha(1)
        this._targetG.fillStyle(0xfbbf24, 0.14)
        this._targetG.fillCircle(x, y, this._tileSize * 0.54)
        this._targetG.lineStyle(3, 0xfff7d6, 0.82)
        this._targetG.strokeCircle(x, y, this._tileSize * 0.36)
        this._targetG.lineStyle(1, 0xfbbf24, 0.95)
        this._targetG.strokeCircle(x, y, this._tileSize * 0.18)
        this.tweens.add({
          targets: this._targetG,
          alpha: 0.48,
          duration: 300,
          yoyo: true,
          repeat: 2,
          ease: 'Sine.easeInOut'
        })
      }

      this.cancelWalk = () => {
        if (this._walkTween) {
          this._walkTween.stop()
          this._walkTween = null
        }
        this.tweens.killTweensOf(this.playerRoot, true)
        this.tweens.killTweensOf(this._pathG, true)
        this.tweens.killTweensOf(this._targetG, true)
        this._pathG?.clear()
        this._pathG?.setAlpha(1)
        this._guideG?.setAlpha(1)
        this._targetG?.clear()
        this._targetG?.setAlpha(1)
      }

      this.buildLocalPathTo = (tx, ty) => {
        const st = getSimState()
        const p = st?.player || {}
        return localBfsPath(getMap(), p.tile_x, p.tile_y, tx, ty)
      }

      this.refreshQuestGuide = () => {
        const target = pickGuideTarget(getMap(), getSimState(), getStoryEvents())
        drawQuestGuide(this, this._guideG, target, this._tileSize)
      }

      this.updateWeatherAtmosphere = () => {
        const wg = this._weatherG
        if (!wg) return
        const st = getSimState() || {}
        const weatherText = `${st.weather || ''} ${st.weather_label || ''}`.toLowerCase()
        const isRainy = weatherText.includes('rain') || weatherText.includes('drizzle') || weatherText.includes('雨')
        wg.clear()
        if (!isRainy) return

        const camNow = this.cameras.main
        const w = Math.max(1, camNow.width)
        const h = Math.max(1, camNow.height)
        const delta = Math.min(2.1, Math.max(0.45, (this.game.loop.delta || 16) / 16))
        const phase = this.time.now / 1000

        wg.fillStyle(0xbfe7ff, 0.026)
        wg.fillEllipse(w * 0.28 + Math.sin(phase * 0.42) * 18, h * 0.18, w * 0.62, h * 0.18)
        wg.fillEllipse(w * 0.76 + Math.sin(phase * 0.35) * 22, h * 0.64, w * 0.5, h * 0.14)

        for (const drop of this._rainDrops) {
          drop.x += drop.drift * delta
          drop.y += drop.speed * delta
          if (drop.y > h + 32 || drop.x > w + 32) {
            drop.y = -24 - ((drop.x + drop.len) % 36)
            drop.x = (drop.x * 1.37 + 47) % w
          }
          wg.lineStyle(1, 0xc7edff, drop.alpha)
          wg.lineBetween(drop.x, drop.y, drop.x - drop.len * 0.42, drop.y - drop.len)
        }
      }

      const hudW = Math.min(mapW, 720)
      this.add.rectangle(mapW / 2, 18, hudW, 30, 0x24180f, 0.78).setDepth(20)
      this.add
        .rectangle(mapW / 2, 18, hudW, 30, 0x000000, 0)
        .setStrokeStyle(1, 0xf6d36e, 0.36)
        .setDepth(20)
      this._hudText = this.add
        .text(mapW / 2, 18, '', {
          fontSize: '11px',
          color: '#fef3c7',
          align: 'center',
          fontFamily: 'system-ui, "Microsoft YaHei", sans-serif'
        })
        .setOrigin(0.5)
        .setDepth(21)

      this.playerRoot = this.add.container(0, 0)
      this.playerRoot.setDepth(15)
      const playerCfg = getAgentConfig('player')
      const playerHalo = this.add.ellipse(0, 13, 40, 17, playerCfg.haloColor, 0.1).setStrokeStyle(2, playerCfg.haloColor, 0.68)
      const playerShadow = this.add.ellipse(0, 18, 31, 9, 0x000000, 0.3)
      const playerSprite = this.add.image(0, -18, playerCfg.textureKey)
      playerSprite.setScale(playerCfg.tokenHeight / Math.max(1, playerSprite.height))
      const playerName = this.add
        .text(0, -51, playerCfg.label, {
          fontSize: '11px',
          color: '#fff7d6',
          fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
          fontStyle: 'bold',
          stroke: '#020617',
          strokeThickness: 3
        })
        .setOrigin(0.5)
      const playerNameBg = this.add
        .rectangle(0, -51, Math.max(52, playerName.width + 14), 16, 0x020617, 0.72)
        .setStrokeStyle(1, playerCfg.haloColor, 0.38)
      this.playerRoot.add([playerHalo, playerShadow, playerSprite, playerNameBg, playerName])

      this._npcLayer = this.add.container(0, 0).setDepth(11)
      // Store existing NPC containers by id for delta updates
      this._npcContainers = {}
      this.syncNpcs = () => {
        if (!this._npcLayer) return
        const st = getSimState()
        const agents = Array.isArray(st?.agents) ? st.agents : []
        const aliveIds = new Set(agents.map(a => a.id))
        // Remove NPCs that are no longer present
        for (const id of Object.keys(this._npcContainers)) {
          if (!aliveIds.has(id)) {
            const cont = this._npcContainers[id]
            if (cont) {
              this.tweens.killTweensOf(cont, true)
              cont.destroy(true)
              delete this._npcContainers[id]
            }
          }
        }
        // Update or create each NPC
        const displaySlots = new Map()
        const player = st?.player || {}
        const playerDisplay = Number.isFinite(Number(player.tile_x)) && Number.isFinite(Number(player.tile_y))
          ? findNearestDisplayTile(getMap(), Number(player.tile_x), Number(player.tile_y), { radius: 7, preferRoad: true })
          : null
        for (const agent of agents) {
          const ax = Number(agent?.tile_x)
          const ay = Number(agent?.tile_y)
          if (!Number.isFinite(ax) || !Number.isFinite(ay)) continue
          const display = findNearestDisplayTile(getMap(), ax, ay, { radius: 7, preferRoad: true })
          const displayKey = `${display.x},${display.y}`
          const slot = displaySlots.get(displayKey) || 0
          displaySlots.set(displayKey, slot + 1)
          const sameTileWithPlayer = !!playerDisplay && playerDisplay.x === display.x && playerDisplay.y === display.y
          const offset = characterFormationOffset(agent.id, slot + (sameTileWithPlayer ? 1 : 0), sameTileWithPlayer)
          const wx = (display.x + 0.5) * ts + offset.x
          const wy = (display.y + 0.5) * ts + offset.y
          const cont = this._npcContainers[agent.id]
          if (cont) {
            // Delta update: only move position
            cont.setPosition(wx, wy)
          } else {
            // Create new NPC container
            const newCont = this.add.container(wx, wy)
            const npcCfg = getAgentConfig(agent.id)
            const key = npcCfg.textureKey
            const haloColor = npcCfg.haloColor
            const halo = this.add.ellipse(0, 13, 36, 15, haloColor, 0.09).setStrokeStyle(1, haloColor, 0.5)
            const shadow = this.add.ellipse(0, 18, 28, 8, 0x000000, 0.26)
            const face = key && this.textures.exists(key) ? this.add.image(0, -18, key) : this.add.image(0, -18, AGENT_ART_KEYS.kirito)
            face.setScale(npcCfg.tokenHeight / Math.max(1, face.height))
            const hit = this.add.circle(0, 0, 20, 0xffffff, 0.001).setInteractive({ useHandCursor: true })
            const mood = Number(agent.mood ?? 50)
            const moodColor = mood >= 70 ? '#bbf7d0' : mood >= 40 ? '#fde68a' : '#fecaca'
            const tag = this.add
              .text(0, -51, npcCfg.label, {
                fontSize: '10px',
                color: '#fef3c7',
                fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
                stroke: '#0f172a',
                strokeThickness: 3
              })
              .setOrigin(0.5)
            const tagBg = this.add
              .rectangle(0, -51, Math.max(48, tag.width + 12), 15, 0x020617, 0.68)
              .setStrokeStyle(1, haloColor, 0.32)
            const moodDot = this.add
              .text(17, -36, '●', {
                fontSize: '10px',
                color: moodColor,
                stroke: '#0f172a',
                strokeThickness: 3
              })
              .setOrigin(0.5)
            hit.on('pointerdown', (pointer) => {
              pointer.event?.preventDefault?.()
              this._pendingTilePick = null
            })
            hit.on('pointerup', (pointer) => {
              pointer.event?.preventDefault?.()
              this._pendingTilePick = null
              if (!isBusy()) openNpcPanel(agent.id)
            })
            newCont.add([halo, shadow, face, moodDot, tagBg, tag, hit])
            this._npcLayer.add(newCont)
            this._npcContainers[agent.id] = newCont
          }
        }
      }
      this.syncNpcs()

      this.rebuildPois = () => {
        const m = getMap()
        const tsz = this._tileSize
        if (this._poiLayer) {
          const chs = [...this._poiLayer.list]
          for (const ch of chs) {
            this.tweens.killTweensOf(ch, true)
          }
          this._poiLayer.destroy(true)
        }
        this._poiLayer = this.add.container(0, 0).setDepth(13)
        const st = getSimState()
        const node = st?.story_node_id || ''
        for (const p of m.pois || []) {
          if (!['quest', 'landmark', 'interact'].includes(p.kind)) continue
          const tx = Number(p.tile_x) || 0
          const ty = Number(p.tile_y) || 0
          const baseX = Number(p.approach_tile_x ?? tx)
          const baseY = Number(p.approach_tile_y ?? ty)
          const display = findNearestDisplayTile(m, baseX, baseY, {
            radius: p.kind === 'interact' ? 7 : 5,
            preferRoad: p.kind !== 'landmark'
          })
          const wx = (display.x + 0.5) * tsz
          const wy = (display.y + 0.5) * tsz
          const cont = this.add.container(wx, wy)
          const activeNodes = p.active_story_nodes
          const isQuest = p.kind === 'quest'
          let questActive = true
          if (isQuest && Array.isArray(activeNodes) && activeNodes.length) {
            questActive = activeNodes.includes(node)
          }
          if (p.kind === 'quest') {
            addStoryBeacon(this, cont, p.label || '线索', tsz, { active: questActive })
            cont.setAlpha(questActive ? 1 : 0.28)
          } else if (p.kind === 'landmark') {
            const gg = this.add.graphics()
            const sc = tsz / 34
            gg.fillStyle(0x3f2e22, 1)
            gg.fillRect(-3 * sc, -2 * sc, 6 * sc, 16 * sc)
            gg.fillStyle(0x166534, 1)
            gg.fillTriangle(0, -30 * sc, -16 * sc, -4 * sc, 16 * sc, -4 * sc)
            gg.fillStyle(0x29a35a, 0.95)
            gg.fillTriangle(0, -26 * sc, -12 * sc, -7 * sc, 12 * sc, -7 * sc)
            cont.add(gg)
            cont.add(
              this.add
                .text(0, tsz * 0.45, p.label || '', {
                  fontSize: '12px',
                  color: '#fef08a',
                  fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
                  fontStyle: 'bold',
                  stroke: '#0f172a',
                  strokeThickness: 4
                })
                .setOrigin(0.5, 0)
            )
          } else if (p.kind === 'interact') {
            const gix = this.add.graphics()
            const sceneId = String(p.scene_id || sceneIdForTile(m, tx, ty))
            const sceneDef = getSceneDefinition(sceneId)
            const markerColor = sceneDef.regionType === 'rest'
              ? 0xf59e0b
              : sceneDef.regionType === 'work'
                ? 0xfacc15
                : sceneDef.regionType === 'locked'
                  ? 0xf472b6
                  : 0x38bdf8
            gix.lineStyle(2, markerColor, 0.95)
            gix.strokeCircle(0, -2, 11)
            gix.lineStyle(1, 0xbae6fd, 0.6)
            gix.strokeCircle(0, -2, 6)
            cont.add(gix)
            cont.add(
              this.add
                .text(0, tsz * 0.28, p.label || p.title || '互动', {
                  fontSize: '10px',
                  color: '#e0f2fe',
                  fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
                  stroke: '#0c4a6e',
                  strokeThickness: 3
                })
                .setOrigin(0.5, 0)
            )
          }
          this._poiLayer.add(cont)
        }
        const events = Array.isArray(getStoryEvents()) ? getStoryEvents() : []
        for (const ev of events) {
          const loc = ev?.location || {}
          const tx = Number(loc.tile_x)
          const ty = Number(loc.tile_y)
          if (!Number.isFinite(tx) || !Number.isFinite(ty)) continue
          const display = findNearestDisplayTile(m, tx, ty, { radius: 7, preferRoad: true })
          const cont = this.add.container((display.x + 0.5) * tsz, (display.y + 0.5) * tsz - tsz * 0.2)
          addStoryBeacon(this, cont, ev.title || '章节事件', tsz, { important: true })
          const hit = this.add.circle(0, 0, 27, 0xffffff, 0.001).setInteractive({ useHandCursor: true })
          hit.on('pointerdown', (pointer) => {
            pointer.event?.preventDefault?.()
            this._pendingTilePick = null
          })
          hit.on('pointerup', (pointer) => {
            pointer.event?.preventDefault?.()
            this._pendingTilePick = null
            if (!isBusy()) openStoryEventPanel(ev.id)
          })
          cont.add(hit)
          this._poiLayer.add(cont)
        }
      }
      this.rebuildPois()

      const miniKey = `minimap_${map.id || 'm'}`
      if (this.textures.exists(miniKey)) {
        this.textures.remove(miniKey)
      }
      const miniG = this.make.graphics({ x: 0, y: 0, add: false })
      for (let y = 0; y < H; y++) {
        const row = rows[y] || ''
        for (let x = 0; x < W; x++) {
          const ch = row[x] || '0'
          const code = ch >= '0' && ch <= '9' ? parseInt(ch, 10) : 0
          miniG.fillStyle(MINI_COL[code] ?? 0x333333, 1)
          miniG.fillRect(x, y, 1, 1)
        }
      }
      miniG.generateTexture(miniKey, W, H)
      miniG.destroy()

      const cam = this.cameras.main
      const pad = 14
      const innerW = 236
      const innerH = 146
      const scale = Math.min(innerW / mapW, innerH / mapH)
      const dispW = mapW * scale
      const dispH = mapH * scale
      const ox = Math.max(8, cam.width - pad - dispW - 16)
      const oy = pad + 28
      const cx = ox + dispW / 2
      const cy = oy + dispH / 2

      this.add
        .rectangle(cx, cy, dispW + 20, dispH + 54, 0x07111c, 0.9)
        .setStrokeStyle(1, 0xf6d36e, 0.32)
        .setScrollFactor(0)
        .setDepth(50)
      this.add
        .rectangle(cx, cy + 6, dispW + 8, dispH + 8, 0x020617, 0.5)
        .setStrokeStyle(1, 0x5ecfff, 0.22)
        .setScrollFactor(0)
        .setDepth(50)
      this.add
        .text(ox + 4, oy - 11, '卢利特村地图', {
          fontSize: '10px',
          color: '#fde68a',
          fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
          fontStyle: 'bold'
        })
        .setOrigin(0, 1)
        .setScrollFactor(0)
        .setDepth(52)
      this.add
        .text(ox + dispW - 2, oy - 11, 'N', {
          fontSize: '11px',
          color: '#bae6fd',
          fontFamily: 'Georgia, serif',
          fontStyle: 'bold',
          stroke: '#020617',
          strokeThickness: 3
        })
        .setOrigin(1, 1)
        .setScrollFactor(0)
        .setDepth(52)
      this.add
        .text(ox + 5, oy + dispH + 16, '边界区域 · 尚未开放', {
          fontSize: '9px',
          color: '#cbd5e1',
          fontFamily: 'system-ui, "Microsoft YaHei", sans-serif'
        })
        .setOrigin(0, 0.5)
        .setScrollFactor(0)
        .setDepth(52)

      this.add
        .image(cx, cy, miniKey)
        .setScrollFactor(0)
        .setDisplaySize(dispW, dispH)
        .setDepth(51)
        .setName('minimapImg')

      this._miniViewport = this.add.graphics().setScrollFactor(0).setDepth(53)
      this._miniFixedObjects = this.children.list.filter((obj) => obj.depth >= 50 && obj.depth <= 53)
      for (const obj of this._miniFixedObjects) {
        obj._miniBaseX = obj.x || 0
        obj._miniBaseY = obj.y || 0
        obj._miniBaseScaleX = obj.scaleX || 1
        obj._miniBaseScaleY = obj.scaleY || 1
        obj.setVisible(false)
      }
      this._miniViewport = null
      this._miniLayout = null
      this._miniHit = { x: -9999, y: -9999, w: 0, h: 0 }
      this._miniImgBounds = {
        left: cx - dispW / 2,
        right: cx + dispW / 2,
        top: cy - dispH / 2,
        bottom: cy + dispH / 2
      }

      const iw = 108
      const ih = 28
      this._interactBtnRoot = this.add.container(0, 0).setDepth(17).setVisible(false)
      const btnBg = this.add
        .rectangle(0, 0, iw, ih, 0x083344, 0.92)
        .setStrokeStyle(2, 0xfde68a, 0.78)
      const btnTx = this.add
        .text(0, 0, '进入场景', {
          fontSize: '11px',
          color: '#f8fafc',
          fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
          fontStyle: 'bold',
          stroke: '#0f172a',
          strokeThickness: 3
        })
        .setOrigin(0.5)
      btnBg.setInteractive({ useHandCursor: true })
      btnBg.on('pointerup', (pointer) => {
        pointer.event?.preventDefault?.()
        openInteractPanel()
      })
      this._interactBtnRoot.add([btnBg, btnTx])
      this._interactBtnText = btnTx
      this._interactBtnHalfW = iw / 2
      this._interactBtnHalfH = ih / 2

      this.cameras.main.setBounds(0, 0, mapW, mapH)
      const defaultZoom = useWorldBg
        ? numberSetting(cameraCfg.background_zoom, 1.18, this._zoomMin, this._zoomMax)
        : numberSetting(cameraCfg.default_zoom, 1.24, this._zoomMin, this._zoomMax)
      this.cameras.main.setZoom(defaultZoom)
      this.cameras.main.roundPixels = false
      this.cameras.main.startFollow(this.playerRoot, true, this._cameraFollowLerp, this._cameraFollowLerp)

      this._rmbPanning = false
      this._lmbPanning = false
      this._rmbPanLast = { x: 0, y: 0 }
      this._miniPointerDown = false
      this._miniDragCamera = false
      this._miniStart = { x: 0, y: 0 }
      this._pendingTilePick = null

      this.game.canvas.addEventListener('contextmenu', (e) => e.preventDefault())

      const pointInMiniHit = (sx, sy) => {
        const hb = this._miniHit
        return sx >= hb.x && sy >= hb.y && sx <= hb.x + hb.w && sy <= hb.y + hb.h
      }

      const screenToMiniNorm = (sx, sy) => {
        const B = this._miniImgBounds
        if (!B) return null
        if (sx < B.left || sx > B.right || sy < B.top || sy > B.bottom) return null
        return {
          u: (sx - B.left) / (B.right - B.left),
          v: (sy - B.top) / (B.bottom - B.top)
        }
      }

      const centerCamFromNorm = (u, v) => {
        cam.stopFollow()
        cam.centerOn(Phaser.Math.Clamp(u, 0, 1) * mapW, Phaser.Math.Clamp(v, 0, 1) * mapH)
      }
      this.centerCameraOnTile = (tx, ty) => {
        cam.stopFollow()
        cam.centerOn((Number(tx) + 0.5) * ts, (Number(ty) + 0.5) * ts)
      }

      this.tryKeyboardStep = (dx, dy) => {
        if (isBusy() || this._walkTween) return
        const st = getSimState()
        const p = st?.player || {}
        const sx = Number(p.tile_x)
        const sy = Number(p.tile_y)
        if (!Number.isFinite(sx) || !Number.isFinite(sy)) return
        const tx = sx + dx
        const ty = sy + dy
        const blockedZone = zoneForTile(getMap(), tx, ty)
        if (isBlockedZone(blockedZone)) {
          onBlockedTilePick({ tile_x: tx, tile_y: ty, zone: blockedZone })
          return
        }
        if (!isWorldTileWalkable(getMap(), tx, ty, { allowBlockedZone: true })) {
          onBlockedTilePick({
            tile_x: tx,
            tile_y: ty,
            reason: 'terrain_blocked',
            terrainLabel: terrainLabelAt(getMap(), tx, ty)
          })
          return
        }
        const path = localBfsPath(getMap(), sx, sy, tx, ty)
        if (!path || path.length < 2) return
        this.previewMoveTarget?.(tx, ty)
        onTilePick(tx, ty)
      }

      const hitsWorldInteractButton = (sx, sy) => {
        const root = this._interactBtnRoot
        if (!root || !root.visible) return false
        const wp = cam.getWorldPoint(sx, sy)
        const x = root.x
        const y = root.y
        const hw = this._interactBtnHalfW
        const hh = this._interactBtnHalfH
        return wp.x >= x - hw && wp.x <= x + hw && wp.y >= y - hh && wp.y <= y + hh
      }

      this.input.on(
        'wheel',
        (_pointer, _gameObjects, _deltaX, deltaY) => {
          const c = this.cameras.main
          const next = Phaser.Math.Clamp(
            c.zoom + (deltaY > 0 ? -this._zoomWheel : this._zoomWheel),
            this._zoomMin,
            this._zoomMax
          )
          c.setZoom(next)
        },
        this
      )

      const keyMoveMap = {
        ArrowUp: [0, -1],
        ArrowDown: [0, 1],
        ArrowLeft: [-1, 0],
        ArrowRight: [1, 0],
        w: [0, -1],
        s: [0, 1],
        a: [-1, 0],
        d: [1, 0]
      }
      this.input.keyboard?.on('keydown', (event) => {
        if (event.__uwHandled) return
        if (typeof window !== 'undefined' && window.__uwModalOpen) return
        const tag = event.target?.tagName?.toLowerCase?.()
        if (tag === 'input' || tag === 'textarea' || tag === 'select') return
        const key = event.key === 'ArrowUp' || event.key === 'ArrowDown' || event.key === 'ArrowLeft' || event.key === 'ArrowRight'
          ? event.key
          : String(event.key || '').toLowerCase()
        if (isDevMode() && key === 'v' && (event.ctrlKey || event.metaKey)) {
          event.preventDefault?.()
          this.toggleNavigationOverlay?.()
          return
        }
        const delta = keyMoveMap[key]
        if (!delta) return
        const now = this.time.now
        if (this._lastKeyMoveAt && now - this._lastKeyMoveAt < 95) return
        this._lastKeyMoveAt = now
        event.preventDefault?.()
        this.tryKeyboardStep(delta[0], delta[1])
      })

      this.input.on('pointerdown', (pointer) => {
        const sx = pointer.x
        const sy = pointer.y

        if (pointInMiniHit(sx, sy)) {
          this._miniPointerDown = true
          this._miniDragCamera = false
          this._miniStart = { x: sx, y: sy }
          this._pendingTilePick = null
          return
        }

        if (hitsWorldInteractButton(sx, sy)) {
          this._pendingTilePick = null
          return
        }

        const wx = pointer.worldX
        const wy = pointer.worldY
        const tx = Math.floor(wx / ts)
        const ty = Math.floor(wy / ts)
        const inMap = tx >= 0 && ty >= 0 && tx < W && ty < H

        const right = pointer.rightButtonDown()
        const middle = pointer.middleButtonDown()

        if ((right || middle) && inMap) {
          this._rmbPanning = true
          this._rmbPanLast = { x: sx, y: sy }
          cam.stopFollow()
          this._pendingTilePick = null
          return
        }

        if (pointer.leftButtonDown() && inMap) {
          this._pendingTilePick = {
            sx,
            sy,
            tx,
            ty,
            t: this.time.now
          }
          const mapNow = getMap()
          const blockedZone = zoneForTile(mapNow, tx, ty)
          if (!isBlockedZone(blockedZone) && isWorldTileWalkable(mapNow, tx, ty, { allowBlockedZone: true })) {
            this.previewMoveTarget?.(tx, ty)
          }
        }
      })

      this.input.on('pointermove', (pointer) => {
        if (this._leftDragPanEnabled && this._pendingTilePick && pointer.leftButtonDown() && !this._lmbPanning) {
          const moved = Phaser.Math.Distance.Between(this._pendingTilePick.sx, this._pendingTilePick.sy, pointer.x, pointer.y)
          if (moved > 8) {
            this._lmbPanning = true
            this._rmbPanLast = { x: pointer.x, y: pointer.y }
            cam.stopFollow()
            this._targetG?.clear()
          }
        }

        if (this._lmbPanning && pointer.leftButtonDown()) {
          const dx = pointer.x - this._rmbPanLast.x
          const dy = pointer.y - this._rmbPanLast.y
          this._rmbPanLast = { x: pointer.x, y: pointer.y }
          const z = cam.zoom
          cam.scrollX -= dx / z
          cam.scrollY -= dy / z
          return
        }

        if (this._rmbPanning && (pointer.rightButtonDown() || pointer.middleButtonDown())) {
          const dx = pointer.x - this._rmbPanLast.x
          const dy = pointer.y - this._rmbPanLast.y
          this._rmbPanLast = { x: pointer.x, y: pointer.y }
          const z = cam.zoom
          cam.scrollX -= dx / z
          cam.scrollY -= dy / z
          return
        }

        if (this._miniPointerDown) {
          const n = screenToMiniNorm(pointer.x, pointer.y)
          if (n) {
            const moved = Phaser.Math.Distance.Between(this._miniStart.x, this._miniStart.y, pointer.x, pointer.y)
            if (moved > 5) this._miniDragCamera = true
            if (this._miniDragCamera) {
              cam.stopFollow()
              centerCamFromNorm(n.u, n.v)
            }
          }
        }

        const tx = Math.floor(pointer.worldX / ts)
        const ty = Math.floor(pointer.worldY / ts)
        const mapNow = getMap()
        const hoverZone = zoneForTile(mapNow, tx, ty)
        const blockedHover = isBlockedZone(hoverZone) || !isWorldTileWalkable(mapNow, tx, ty, { allowBlockedZone: true })
        this.input.setDefaultCursor(blockedHover ? 'not-allowed' : 'default')
      })

      this.input.on('pointerup', (pointer) => {
        if (this._miniPointerDown) {
          if (!this._miniDragCamera) {
            const n = screenToMiniNorm(pointer.x, pointer.y)
            if (n) {
              cam.stopFollow()
              centerCamFromNorm(n.u, n.v)
            }
          }
          this._miniPointerDown = false
          this._miniDragCamera = false
        }

        if (this._rmbPanning) {
          this._rmbPanning = false
        }

        if (this._lmbPanning) {
          this._lmbPanning = false
          this._pendingTilePick = null
          return
        }

        if (this._pendingTilePick && pointer.leftButtonReleased()) {
          const p0 = this._pendingTilePick
          const dist = Phaser.Math.Distance.Between(p0.sx, p0.sy, pointer.x, pointer.y)
          const elapsed = this.time.now - p0.t
          this._pendingTilePick = null
          if (dist < 14 && elapsed < 900 && !pointInMiniHit(pointer.x, pointer.y)) {
            if (!hitsWorldInteractButton(pointer.x, pointer.y)) {
              const blockedZone = zoneForTile(getMap(), p0.tx, p0.ty)
              if (isBlockedZone(blockedZone)) {
                onBlockedTilePick({
                  tile_x: p0.tx,
                  tile_y: p0.ty,
                  zone: blockedZone
                })
              } else if (!isWorldTileWalkable(getMap(), p0.tx, p0.ty, { allowBlockedZone: true })) {
                onBlockedTilePick({
                  tile_x: p0.tx,
                  tile_y: p0.ty,
                  reason: 'terrain_blocked',
                  terrainLabel: terrainLabelAt(getMap(), p0.tx, p0.ty)
                })
              } else {
                this.previewMoveTarget?.(p0.tx, p0.ty)
                onTilePick(p0.tx, p0.ty)
              }
            }
          }
        }
      })

      this.playWalkPath = (path) => {
        return new Promise((resolve) => {
          const perfStart = typeof performance !== 'undefined' ? performance.now() : 0
          const tsLocal = this._tileSize
          if (!path?.length || !this.playerRoot) {
            resolve()
            return
          }
          const norm = path.map((p) => ({
            x: Number(p.x),
            y: Number(p.y)
          }))
          const smooth = tilePathToSmoothWorldPoints(norm, tsLocal)
          const seq = smooth.length > 1 ? smooth.slice(1) : []
          if (seq.length === 0) {
            resolve()
            return
          }
          const gPath = this._pathG
          if (gPath) {
            drawSmoothRoute(gPath, smooth)
          }
          const speed = this._walkSpeed
          const { table, total } = buildDistanceTable(smooth)
          if (!Number.isFinite(total) || total <= 0) {
            resolve()
            return
          }
          const progress = { d: 0 }
          this.tweens.killTweensOf(this.playerRoot, true)
          if (this._walkTween) {
            this._walkTween.stop()
            this._walkTween = null
          }
          const fadePath = () => {
            if (!gPath) {
              resolve()
              return
            }
            this.tweens.add({
              targets: gPath,
              alpha: 0,
              duration: 260,
              onComplete: () => {
                gPath.clear()
                gPath.setAlpha(1)
                this._targetG?.clear()
                this._targetG?.setAlpha(1)
                resolve()
              }
            })
          }
          const finalPoint = table[table.length - 1]
          const duration = Math.max(this._walkMinMs, Math.min(this._walkMaxMs, Math.floor((total / speed) * 1000)))
          this._walkTween = this.tweens.add({
            targets: progress,
            d: total,
            duration,
            ease: 'Linear',
            onUpdate: () => {
              const p = pointAtDistance(table, progress.d)
              this.playerRoot.setPosition(p.x, p.y)
            },
            onComplete: () => {
              this.playerRoot.setPosition(finalPoint.x, finalPoint.y)
              this._walkTween = null
              if (typeof window !== 'undefined' && perfStart) {
                window.__UW_PERF = {
                  ...(window.__UW_PERF || {}),
                  lastWalkMs: Math.round(performance.now() - perfStart),
                  lastWalkPoints: smooth.length,
                  lastWalkDistance: Math.round(total)
                }
              }
              fadePath()
            }
          })
        })
      }

      this.events.on('postupdate', () => {
        const now = this.time.now
        if (!this._lastInteractUiAt || now - this._lastInteractUiAt > 90) {
          this._lastInteractUiAt = now
          this.updateWorldInteractButton()
        }
        if (!this._lastGuideAt || now - this._lastGuideAt > this._guideIntervalMs) {
          this._lastGuideAt = now
          this.refreshQuestGuide()
        }
        if (!this._lastWaterRippleAt || now - this._lastWaterRippleAt > this._waterIntervalMs) {
          this._lastWaterRippleAt = now
          drawWaterRipples(this._waterRippleG, getMap(), this._tileSize, now)
        }
        if (!this._lastWeatherAt || now - this._lastWeatherAt > this._weatherIntervalMs) {
          this._lastWeatherAt = now
          this.updateWeatherAtmosphere()
        }
      })

      assignSceneInstance(this)
      syncPlayerFromState()
      cam.centerOn(this.playerRoot.x, this.playerRoot.y)
      this.resumeCameraFollow()
    }
  }
}
