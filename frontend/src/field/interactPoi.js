function zoneContains(zone, x, y) {
  const x1 = Number(zone?.x1 ?? 0)
  const y1 = Number(zone?.y1 ?? 0)
  const x2 = Number(zone?.x2 ?? x1)
  const y2 = Number(zone?.y2 ?? y1)
  return (
    x >= Math.min(x1, x2) &&
    x <= Math.max(x1, x2) &&
    y >= Math.min(y1, y2) &&
    y <= Math.max(y1, y2)
  )
}

function codeAt(map, x, y) {
  const rows = Array.isArray(map?.rows) ? map.rows : []
  const height = rows.length
  const width = height > 0 ? String(rows[0] || '').length : 0
  if (x < 0 || y < 0 || x >= width || y >= height) return null
  const ch = String(rows[y] || '')[x] || '0'
  return ch >= '0' && ch <= '9' ? Number(ch) : 0
}

function isBlockedZone(zone) {
  const type = String(zone?.regionType || '')
  return type === 'locked' || type === 'forbidden'
}

function zoneForTile(map, x, y) {
  const zones = Array.isArray(map?.scene_zones) ? map.scene_zones : []
  return zones.find((zone) => zoneContains(zone, x, y)) || null
}

function isWalkableTile(map, x, y) {
  const tileCode = codeAt(map, x, y)
  if (tileCode == null) return false
  const walkable = new Set((map?.walkable || [0, 3]).map((v) => Number(v)))
  return walkable.has(tileCode) && !isBlockedZone(zoneForTile(map, x, y))
}

function nearestDisplayTile(map, tx, ty, radius = 7) {
  const x0 = Math.floor(Number(tx))
  const y0 = Math.floor(Number(ty))
  if (!Number.isFinite(x0) || !Number.isFinite(y0)) return { x: 0, y: 0 }
  if (isWalkableTile(map, x0, y0)) return { x: x0, y: y0 }
  const rows = Array.isArray(map?.rows) ? map.rows : []
  const height = rows.length
  const width = height > 0 ? String(rows[0] || '').length : 0
  let best = null
  let bestScore = Infinity
  for (let r = 1; r <= radius; r++) {
    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue
        const x = x0 + dx
        const y = y0 + dy
        if (x < 0 || y < 0 || x >= width || y >= height) continue
        if (!isWalkableTile(map, x, y)) continue
        let score = Math.abs(dx) + Math.abs(dy)
        if (codeAt(map, x, y) === 3) score -= 0.45
        if (score < bestScore) {
          bestScore = score
          best = { x, y }
        }
      }
    }
    if (best) return best
  }
  return { x: x0, y: y0 }
}

function poiDistance(player, poi) {
  const tx = Number(poi.display_tile_x ?? poi.approach_tile_x ?? poi.tile_x) || 0
  const ty = Number(poi.display_tile_y ?? poi.approach_tile_y ?? poi.tile_y) || 0
  return Math.max(Math.abs((Number(player.tile_x) || 0) - tx), Math.abs((Number(player.tile_y) || 0) - ty))
}

/** 与 FieldSlice 中「附近可互动」判定一致，并允许在高亮区域内打开入口。 */
export function findNearbyInteractPoi(map, player) {
  if (!map?.pois || !player) return null
  const rawPx = Number(player.tile_x)
  const rawPy = Number(player.tile_y)
  const px = Number.isFinite(rawPx) ? rawPx : 0
  const py = Number.isFinite(rawPy) ? rawPy : 0
  for (const poi of map.pois) {
    if (poi.kind !== 'interact') continue
    const tx = Number(poi.tile_x) || 0
    const ty = Number(poi.tile_y) || 0
    const approachX = Number(poi.approach_tile_x ?? tx)
    const approachY = Number(poi.approach_tile_y ?? ty)
    const display = Number.isFinite(approachX) && Number.isFinite(approachY)
      ? nearestDisplayTile(map, approachX, approachY)
      : nearestDisplayTile(map, tx, ty)
    const r = Number(poi.radius) || 1
    const rawDist = Math.max(Math.abs(px - tx), Math.abs(py - ty))
    const displayDist = Math.max(Math.abs(px - display.x), Math.abs(py - display.y))
    if (Math.min(rawDist, displayDist) <= r) {
      return {
        ...poi,
        display_tile_x: display.x,
        display_tile_y: display.y
      }
    }
  }

  const zones = Array.isArray(map.scene_zones) ? map.scene_zones : []
  const activeZone = zones.find((zone) => {
    const type = String(zone?.regionType || '')
    return type && type !== 'forbidden' && zoneContains(zone, px, py)
  })
  if (!activeZone?.scene_id) return null

  const candidates = map.pois
    .filter((poi) => poi.kind === 'interact')
    .filter((poi) => poi.scene_id === activeZone.scene_id || zoneContains(activeZone, Number(poi.tile_x) || 0, Number(poi.tile_y) || 0))
    .sort((a, b) => poiDistance(player, a) - poiDistance(player, b))

  if (!candidates.length) return null
  const picked = candidates[0]
  const display = nearestDisplayTile(
    map,
    Number(picked.approach_tile_x ?? picked.tile_x) || 0,
    Number(picked.approach_tile_y ?? picked.tile_y) || 0
  )
  return {
    ...picked,
    display_tile_x: display.x,
    display_tile_y: display.y,
    zoneEntry: true,
    zoneLabel: activeZone.label || picked.label,
    regionType: activeZone.regionType || 'interact'
  }
}
