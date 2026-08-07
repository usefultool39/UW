import fs from 'node:fs'
import path from 'node:path'

const root = path.resolve(process.cwd(), '..')
const frontendContract = fs.readFileSync(path.join(root, 'frontend/src/contracts/clientContract.js'), 'utf8')
const cocosContract = fs.readFileSync(path.join(root, 'cocos-client/assets/scripts/api/contracts.ts'), 'utf8')
const docsContract = fs.readFileSync(path.join(root, 'docs/CLIENT_CONTRACT.md'), 'utf8')

function assert(condition, message) {
  if (!condition) {
    console.error(message)
    process.exit(1)
  }
}

const version = 'client-contract-2026-05-15-v2'
assert(frontendContract.includes(version), 'Frontend contract version mismatch')
assert(cocosContract.includes(version), 'Cocos contract version mismatch')
assert(docsContract.includes(version), 'Docs contract version mismatch')

for (const route of [
  '/api/state',
  '/api/world/map',
  '/api/world/maps/',
  '/api/world/scene_activities',
  '/api/story/available_events',
  '/api/player/action',
  '/api/story/choose',
  '/api/dialogue',
  '/api/npc/',
  '/api/save/export',
  '/api/save/import'
]) {
  assert(frontendContract.includes(route), `Frontend contract missing route ${route}`)
  assert(cocosContract.includes(route), `Cocos contract missing route ${route}`)
  assert(docsContract.includes(route), `Docs contract missing route ${route}`)
}

for (const action of [
  'move_map',
  'move_world',
  'move_scene',
  'enter_scene',
  'interact_with_hub',
  'scene_activity',
  'respond_npc_intent',
  'daily_tick',
  'rest_until_next_day'
]) {
  assert(frontendContract.includes(action), `Frontend contract missing action ${action}`)
  assert(cocosContract.includes(action) || action === 'move_world', `Cocos contract missing action ${action}`)
  assert(docsContract.includes(action), `Docs contract missing action ${action}`)
}

console.log('Cross-client contract smoke ok')
