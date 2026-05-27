import { MapData } from '../api/contracts'

export interface TilePoint {
  x: number
  y: number
}

export function terrainCodeAt(map: MapData, x: number, y: number): number {
  if (x < 0 || y < 0 || x >= map.width || y >= map.height) return 9
  const ch = String(map.rows[y] || '')[x] || '0'
  const code = Number.parseInt(ch, 10)
  return Number.isFinite(code) ? code : 0
}

export function isWalkableTile(map: MapData, x: number, y: number): boolean {
  return map.walkable.includes(terrainCodeAt(map, x, y))
}

export function localBfsPath(map: MapData, start: TilePoint, target: TilePoint): TilePoint[] | null {
  const sx = Math.floor(start.x)
  const sy = Math.floor(start.y)
  const tx = Math.floor(target.x)
  const ty = Math.floor(target.y)
  if (!isWalkableTile(map, sx, sy) || !isWalkableTile(map, tx, ty)) return null

  const key = (x: number, y: number) => `${x},${y}`
  const q: TilePoint[] = [{ x: sx, y: sy }]
  const prev = new Map<string, string | null>()
  prev.set(key(sx, sy), null)
  const dirs = [
    { x: 1, y: 0 },
    { x: -1, y: 0 },
    { x: 0, y: 1 },
    { x: 0, y: -1 }
  ]

  for (let head = 0; head < q.length; head += 1) {
    const cur = q[head]
    if (cur.x === tx && cur.y === ty) break
    for (const d of dirs) {
      const nx = cur.x + d.x
      const ny = cur.y + d.y
      const nk = key(nx, ny)
      if (prev.has(nk) || !isWalkableTile(map, nx, ny)) continue
      prev.set(nk, key(cur.x, cur.y))
      q.push({ x: nx, y: ny })
    }
  }

  const endKey = key(tx, ty)
  if (!prev.has(endKey)) return null
  const out: TilePoint[] = []
  let cursor: string | null = endKey
  while (cursor) {
    const [x, y] = cursor.split(',').map(Number)
    out.push({ x, y })
    cursor = prev.get(cursor) || null
  }
  return out.reverse()
}

