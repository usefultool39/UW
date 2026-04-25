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

function poiDistance(player, poi) {
  const tx = Number(poi.tile_x) || 0
  const ty = Number(poi.tile_y) || 0
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
    const r = Number(poi.radius) || 1
    if (Math.max(Math.abs(px - tx), Math.abs(py - ty)) <= r) return poi
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
  return {
    ...candidates[0],
    zoneEntry: true,
    zoneLabel: activeZone.label || candidates[0].label,
    regionType: activeZone.regionType || 'interact'
  }
}
