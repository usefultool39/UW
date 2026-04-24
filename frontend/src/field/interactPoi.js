/** 与 FieldSlice 中「附近可互动」判定一致（切比雪夫距离） */
export function findNearbyInteractPoi(map, player) {
  if (!map?.pois || !player) return null
  const px = Number(player.tile_x) ?? 0
  const py = Number(player.tile_y) ?? 0
  for (const poi of map.pois) {
    if (poi.kind !== 'interact') continue
    const tx = Number(poi.tile_x) || 0
    const ty = Number(poi.tile_y) || 0
    const r = Number(poi.radius) || 1
    if (Math.max(Math.abs(px - tx), Math.abs(py - ty)) <= r) return poi
  }
  return null
}
