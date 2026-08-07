import fs from 'node:fs'
import path from 'node:path'

const root = path.resolve(process.cwd(), '..')
const readJson = (rel) => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'))

const map = readJson('data/world/world_map.json')
const activities = readJson('data/world/scene_activities.json').activities || []
const storyEvents = readJson('data/story/events_chapter_01.json').events || []

function assert(condition, message) {
  if (!condition) {
    console.error(message)
    process.exit(1)
  }
}

function activity(id) {
  const found = activities.find((item) => item.id === id)
  assert(found, `Missing activity ${id}`)
  return found
}

function hasChoice(item, choiceId) {
  return (item.choices || []).some((choice) => choice.id === choiceId)
}

assert(map.visual?.tileset_manifest, 'world_map.visual.tileset_manifest is required')
assert(
  fs.existsSync(path.join(root, 'frontend/public', map.visual.tileset_manifest.replace(/^\//, ''))),
  `tileset manifest does not exist: ${map.visual.tileset_manifest}`
)

assert(hasChoice(activity('church_read_sacred_arts'), 'trace_silence'), 'Reading demo choice is missing')
assert(activity('gigas_chop_rhythm'), 'Training demo activity is missing')
assert(hasChoice(activity('church_ask_alice_lunch'), 'support_eugeo'), 'Lunch demo choice is missing')
assert(hasChoice(activity('home_evening_meal'), 'side_alice'), 'Dinner demo choice is missing')
assert(storyEvents.some((event) => event.choices?.length), 'At least one story event with choices is required')

const walkable = new Set((map.walkable || [0, 3]).map(Number))
function codeAt(x, y) {
  if (x < 0 || y < 0 || y >= map.rows.length || x >= String(map.rows[y] || '').length) return 9
  return Number.parseInt(String(map.rows[y])[x] || '0', 10)
}
function canWalk(x, y) {
  return walkable.has(codeAt(x, y))
}
function reachable(start, target) {
  const q = [start]
  const seen = new Set([`${start.x},${start.y}`])
  const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]]
  for (let i = 0; i < q.length; i += 1) {
    const cur = q[i]
    if (cur.x === target.x && cur.y === target.y) return true
    for (const [dx, dy] of dirs) {
      const nx = cur.x + dx
      const ny = cur.y + dy
      const key = `${nx},${ny}`
      if (seen.has(key) || !canWalk(nx, ny)) continue
      seen.add(key)
      q.push({ x: nx, y: ny })
    }
  }
  return false
}

assert(reachable(map.spawn, { x: 26, y: 24 }), 'Cocos local BFS smoke target should be reachable')
console.log('Cocos offline contract smoke ok')

