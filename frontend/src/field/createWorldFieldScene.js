import {
  AGENT_ART_KEYS,
  drawLandmarkArt,
  drawExplorationAtmosphere,
  drawStyledTile,
  drawTerrainOverlays,
  ensureWorldArtTextures,
  MINI_COL,
  sceneZoneLabels,
  ZOOM_MAX,
  ZOOM_MIN,
  ZOOM_WHEEL
} from './worldMapDrawing.js'
import { AGENTS, WORLD_ASSETS, getAgentConfig } from './gameContentConfig.js'

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
  const stroke = (width, color, alpha) => {
    g.lineStyle(width, color, alpha)
    g.beginPath()
    g.moveTo(points[0].x, points[0].y)
    for (let i = 1; i < points.length; i++) {
      g.lineTo(points[i].x, points[i].y)
    }
    g.strokePath()
  }
  stroke(13, 0x1f1308, 0.3)
  stroke(7, 0x9a6b2f, 0.28)
  stroke(3, 0xfde68a, 0.88)
  stroke(1, 0xfff7d6, 0.72)

  const end = points[points.length - 1]
  g.fillStyle(0xfbbf24, 0.16)
  g.fillCircle(end.x, end.y, 18)
  g.lineStyle(2, 0xfff7d6, 0.7)
  g.strokeCircle(end.x, end.y, 13)
  g.fillStyle(0xfff7d6, 0.9)
  g.fillCircle(end.x, end.y, 3)

  const stride = Math.max(5, Math.floor(points.length / 10))
  g.fillStyle(0xfff7d6, 0.52)
  for (let i = stride; i < points.length - 1; i += stride) {
    g.fillCircle(points[i].x, points[i].y, 2)
  }
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
 *   openStoryEventPanel?: (eventId: string) => void
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
    openStoryEventPanel = () => {}
  } = deps

  return class WorldFieldScene extends Phaser.Scene {
    constructor() {
      super({ key: 'WorldField' })
    }

    preload() {
      if (WORLD_ASSETS.background) {
        this.load.image('world_village_bg', WORLD_ASSETS.background)
      }
      for (const cfg of Object.values(AGENTS)) {
        if (cfg.asset) this.load.image(cfg.textureKey, cfg.asset)
      }
    }

    resumeCameraFollow() {
      const cam = this.cameras.main
      if (this.playerRoot) {
        cam.startFollow(this.playerRoot, true, 0.12, 0.12)
      }
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
      root.setPosition((tx + 0.5) * tsz, ty * tsz - tsz * 1.05)
      root.setVisible(true)
    }

    refreshMiniViewport() {
      const L = this._miniLayout
      const vp = this._miniViewport
      if (!L || !vp) return
      const c = this.cameras.main
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
        const mx = L.ox + (ax + 0.5) * this._tileSize * sx
        const my = L.oy + (ay + 0.5) * this._tileSize * sy
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
        const mx = L.ox + (tx + 0.5) * this._tileSize * sx
        const my = L.oy + (ty + 0.5) * this._tileSize * sy
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
      const map = getMap() || { rows: [], width: 0, height: 0, tile_size: 32 }
      const rows = map.rows || []
      const H = rows.length
      const W = H > 0 ? rows[0].length : 0
      const ts = Number(map.tile_size) || 32
      this._tileSize = ts
      this._mapWtiles = W
      this._mapHtiles = H
      ensureWorldArtTextures(this)

      const mapW = W * ts
      const mapH = H * ts
      const hasWorldBg = this.textures.exists('world_village_bg')
      if (hasWorldBg) {
        const bg = this.add.image(mapW / 2, mapH / 2, 'world_village_bg').setDepth(-5)
        const bgScale = Math.max(mapW / Math.max(1, bg.width), mapH / Math.max(1, bg.height))
        bg.setScale(bgScale)
        bg.setAlpha(0.96)
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
      g.setDepth(0)
      g.setAlpha(hasWorldBg ? 0.42 : 1)
      drawTerrainOverlays(this, map, ts).setAlpha(hasWorldBg ? 0.55 : 0.82)
      drawLandmarkArt(this, map, ts).setAlpha(hasWorldBg ? 0.82 : 0.92)
      drawExplorationAtmosphere(this, map, ts).setAlpha(hasWorldBg ? 1 : 0.82)
      this._pathG = this.add.graphics().setDepth(3)

      for (const zl of sceneZoneLabels(map)) {
        this.add
          .text(zl.x * ts + ts / 2, zl.y * ts - ts * 0.35, zl.text, {
            fontSize: '13px',
            color: '#f0f9ff',
            fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
            fontStyle: 'bold',
            stroke: '#0c1929',
            strokeThickness: 5
          })
          .setOrigin(0.5)
          .setDepth(6)
          .setAlpha(0.95)
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
      const playerHalo = this.add.ellipse(0, 13, 38, 18, playerCfg.haloColor, 0.1).setStrokeStyle(2, playerCfg.haloColor, 0.78)
      const playerShadow = this.add.ellipse(0, 17, 30, 10, 0x000000, 0.28)
      const playerSprite = this.add.image(0, -16, playerCfg.textureKey)
      playerSprite.setScale(playerCfg.tokenHeight / Math.max(1, playerSprite.height))
      const playerName = this.add
        .text(0, 31, playerCfg.label, {
          fontSize: '10px',
          color: '#fff7d6',
          fontStyle: 'bold',
          stroke: '#2f1d0b',
          strokeThickness: 3
        })
        .setOrigin(0.5, 0)
      this.playerRoot.add([playerHalo, playerShadow, playerSprite, playerName])

      this._npcLayer = this.add.container(0, 0).setDepth(11)
      this.syncNpcs = () => {
        if (!this._npcLayer) return
        const children = [...this._npcLayer.list]
        for (const ch of children) {
          this.tweens.killTweensOf(ch, true)
        }
        this._npcLayer.destroy(true)
        this._npcLayer = this.add.container(0, 0).setDepth(11)
        const st = getSimState()
        const agents = Array.isArray(st?.agents) ? st.agents : []
        for (const agent of agents) {
          const ax = Number(agent?.tile_x)
          const ay = Number(agent?.tile_y)
          if (!Number.isFinite(ax) || !Number.isFinite(ay)) continue
          const cont = this.add.container((ax + 0.5) * ts, (ay + 0.5) * ts)
          const npcCfg = getAgentConfig(agent.id)
          const key = npcCfg.textureKey
          const haloColor = npcCfg.haloColor
          const halo = this.add.ellipse(0, 13, 34, 15, haloColor, 0.1).setStrokeStyle(1, haloColor, 0.58)
          const shadow = this.add.ellipse(0, 17, 27, 9, 0x000000, 0.25)
          const face = key && this.textures.exists(key) ? this.add.image(0, -15, key) : this.add.image(0, -15, AGENT_ART_KEYS.kirito)
          face.setScale(npcCfg.tokenHeight / Math.max(1, face.height))
          const hit = this.add.circle(0, 0, 25, 0xffffff, 0.001).setInteractive({ useHandCursor: true })
          const mood = Number(agent.mood ?? 50)
          const moodColor = mood >= 70 ? '#bbf7d0' : mood >= 40 ? '#fde68a' : '#fecaca'
          const tag = this.add
            .text(0, 29, npcCfg.label, {
              fontSize: '10px',
              color: '#fef3c7',
              fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
              stroke: '#0f172a',
              strokeThickness: 3
            })
            .setOrigin(0.5, 0)
          const tagBg = this.add
            .rectangle(0, 37, Math.max(46, tag.width + 14), 15, 0x120f0b, 0.72)
            .setStrokeStyle(1, 0xf6d36e, 0.28)
          const moodDot = this.add
            .text(16, -24, '●', {
              fontSize: '11px',
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
          cont.add([halo, shadow, face, moodDot, tagBg, tag, hit])
          this._npcLayer.add(cont)
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
          const wx = (tx + 0.5) * tsz
          const wy = (ty + 0.5) * tsz
          const cont = this.add.container(wx, wy)
          const activeNodes = p.active_story_nodes
          const isQuest = p.kind === 'quest'
          let questActive = true
          if (isQuest && Array.isArray(activeNodes) && activeNodes.length) {
            questActive = activeNodes.includes(node)
          }
          if (p.kind === 'quest') {
            const fs = Math.min(26, Math.max(16, Math.floor(tsz * 0.68)))
            const mark = this.add
              .text(0, -6, '!', {
                fontSize: `${fs}px`,
                color: '#fde047',
                fontStyle: 'bold',
                stroke: '#422006',
                strokeThickness: 5
              })
              .setOrigin(0.5)
            cont.add(mark)
            cont.add(
              this.add
                .text(0, tsz * 0.32, p.label || '任务', {
                  fontSize: '11px',
                  color: '#fef9c3',
                  fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
                  stroke: '#0f172a',
                  strokeThickness: 3
                })
                .setOrigin(0.5, 0)
            )
            cont.setAlpha(questActive ? 1 : 0.28)
            if (questActive) {
              this.tweens.add({
                targets: mark,
                scale: 1.14,
                duration: 520,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
              })
            }
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
            gix.lineStyle(2, 0x38bdf8, 0.95)
            gix.strokeCircle(0, -2, 11)
            gix.lineStyle(1, 0xbae6fd, 0.6)
            gix.strokeCircle(0, -2, 6)
            cont.add(gix)
            cont.add(
              this.add
                .text(0, tsz * 0.28, '互动', {
                  fontSize: '9px',
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
          const cont = this.add.container((tx + 0.5) * tsz, (ty + 0.5) * tsz - tsz * 0.2)
          const pulse = this.add.circle(0, 0, 18, 0xfbbf24, 0.12).setStrokeStyle(2, 0xfde047, 0.75)
          const mark = this.add
            .text(0, -3, '!', {
              fontSize: '24px',
              color: '#fff7d6',
              fontStyle: 'bold',
              stroke: '#422006',
              strokeThickness: 5
            })
            .setOrigin(0.5)
          const label = this.add
            .text(0, tsz * 0.34, ev.title || '章节事件', {
              fontSize: '10px',
              color: '#fff7d6',
              fontFamily: 'system-ui, "Microsoft YaHei", sans-serif',
              fontStyle: 'bold',
              stroke: '#0f172a',
              strokeThickness: 3,
              align: 'center'
            })
            .setOrigin(0.5, 0)
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
          cont.add([pulse, mark, label, hit])
          this.tweens.add({
            targets: pulse,
            scale: 1.28,
            alpha: 0.28,
            duration: 720,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
          })
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
        .text(ox + 4, oy - 11, '北境地图', {
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
      this._miniLayout = { ox, oy, dispW, dispH, mapW, mapH }
      this._miniHit = {
        x: ox - 8,
        y: oy - 28,
        w: dispW + 24,
        h: dispH + 58
      }
      this._miniImgBounds = {
        left: cx - dispW / 2,
        right: cx + dispW / 2,
        top: cy - dispH / 2,
        bottom: cy + dispH / 2
      }

      const iw = 102
      const ih = 36
      this._interactBtnRoot = this.add.container(0, 0).setDepth(17).setVisible(false)
      const btnBg = this.add
        .rectangle(0, 0, iw, ih, 0x172554, 0.94)
        .setStrokeStyle(2, 0x7dd3fc, 0.95)
      const btnTx = this.add
        .text(0, 0, '对话 / 互动', {
          fontSize: '12px',
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
      this._interactBtnHalfW = iw / 2
      this._interactBtnHalfH = ih / 2

      this.cameras.main.setBounds(0, 0, mapW, mapH)
      this.cameras.main.setZoom(hasWorldBg ? 1.18 : 1.22)
      this.cameras.main.roundPixels = false
      this.cameras.main.startFollow(this.playerRoot, true, 0.12, 0.12)

      this._rmbPanning = false
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
            c.zoom + (deltaY > 0 ? -ZOOM_WHEEL : ZOOM_WHEEL),
            ZOOM_MIN,
            ZOOM_MAX
          )
          c.setZoom(next)
        },
        this
      )

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
        }
      })

      this.input.on('pointermove', (pointer) => {
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

        if (this._pendingTilePick && pointer.leftButtonReleased()) {
          const p0 = this._pendingTilePick
          const dist = Phaser.Math.Distance.Between(p0.sx, p0.sy, pointer.x, pointer.y)
          const elapsed = this.time.now - p0.t
          this._pendingTilePick = null
          if (dist < 14 && elapsed < 900 && !pointInMiniHit(pointer.x, pointer.y)) {
            if (!hitsWorldInteractButton(pointer.x, pointer.y)) {
              onTilePick(p0.tx, p0.ty)
            }
          }
        }
      })

      this.playWalkPath = (path) => {
        return new Promise((resolve) => {
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
          const speed = 280
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
                resolve()
              }
            })
          }
          const finalPoint = table[table.length - 1]
          const duration = Math.max(180, Math.min(4200, Math.floor((total / speed) * 1000)))
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
              fadePath()
            }
          })
        })
      }

      this.events.on('postupdate', () => {
        this.refreshMiniViewport()
        this.updateWorldInteractButton()
      })

      assignSceneInstance(this)
      syncPlayerFromState()
      cam.centerOn(this.playerRoot.x, this.playerRoot.y)
      this.resumeCameraFollow()
    }
  }
}
