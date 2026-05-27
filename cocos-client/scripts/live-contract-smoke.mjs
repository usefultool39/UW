const baseUrl = process.env.UW_API_BASE || 'http://127.0.0.1:8765'

function assert(condition, message) {
  if (!condition) {
    console.error(message)
    process.exit(1)
  }
}

async function json(path, options = {}) {
  const res = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  })
  const payload = await res.json().catch(() => null)
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status} ${JSON.stringify(payload)}`)
  return payload
}

async function action(body) {
  const out = await json('/api/player/action', {
    method: 'POST',
    body: JSON.stringify(body)
  })
  assert(out.ok, `Player action failed: ${JSON.stringify(body)} -> ${out.error}`)
  return out
}

await json('/api/reset', { method: 'POST', body: '{}' })
const state = await json('/api/state')
assert(state.player?.map_id === 'novice_open', 'Expected novice_open after reset')

const map = await json('/api/world/map')
assert(map.visual?.tileset_manifest, 'Map must expose tileset manifest')

const catalog = await json('/api/world/scene_activities')
assert(catalog.activities?.length >= 4, 'Expected scene activities')

await action({ kind: 'enter_scene', scene_id: 'reading_hall' })
let out = await action({
  kind: 'interact_with_hub',
  poi_id: 'ix_reading_desk',
  activity_id: 'church_read_sacred_arts',
  activity_choice: 'trace_silence'
})
assert(out.state.flags.reading_keyword_silence === 1, 'Reading choice flag missing')

out = await action({
  kind: 'interact_with_hub',
  poi_id: 'ix_reading_desk',
  activity_id: 'church_ask_alice_lunch',
  activity_choice: 'support_eugeo'
})
assert(out.state.flags.lunch_packed_for_eugeo === 1, 'Lunch choice flag missing')

await action({ kind: 'enter_scene', scene_id: 'gigas_clearing' })
out = await action({
  kind: 'interact_with_hub',
  poi_id: 'ix_gigas_tree',
  activity_id: 'gigas_chop_rhythm'
})
assert(out.activity_result?.tree_damage === 8, 'Training tree damage mismatch')

let current = out.state
for (let i = 0; i < 60 && !['evening', 'night'].includes(current.time_band); i += 1) {
  current = (await action({ kind: 'daily_tick', n: 1 })).state
}
assert(['evening', 'night'].includes(current.time_band), 'Failed to reach dinner time band')

await action({ kind: 'enter_scene', scene_id: 'home_hearth' })
out = await action({
  kind: 'interact_with_hub',
  poi_id: 'ix_home_bed',
  activity_id: 'home_evening_meal',
  activity_choice: 'side_alice'
})
assert(out.state.flags.dinner_sided_alice_day1 === 1, 'Dinner choice flag missing')

const profile = await json('/api/npc/alice/profile')
assert(profile.profile?.relationship, 'NPC profile missing relationship')

const dialogue = await json('/api/dialogue', {
  method: 'POST',
  body: JSON.stringify({ npc_id: 'alice', message: '今天村里有什么需要我记录的吗？', context: { client: 'cocos-live-smoke' } })
})
assert(dialogue.ok && dialogue.reply, 'Dialogue smoke failed')

console.log('Cocos live contract smoke ok')

