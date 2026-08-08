import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { dedupeActivityActions } from '../src/field/interactActionMerge.js'

const fieldSliceSource = await readFile(new URL('../src/components/FieldSlice.vue', import.meta.url), 'utf8')

test('keeps the NPC wrapper and removes the duplicate POI activity', () => {
  const actions = [
    { id: 'intent:alice_invites_reading', type: 'scene_activity', activity_id: 'church_read_sacred_arts', source: 'npc_intent' },
    { id: 'church_read_sacred_arts', type: 'scene_activity', activity_id: 'church_read_sacred_arts' },
    { id: 'church_ask_alice_lunch', type: 'scene_activity', activity_id: 'church_ask_alice_lunch' }
  ]

  assert.deepEqual(
    dedupeActivityActions(actions).map((action) => action.id),
    ['intent:alice_invites_reading', 'church_ask_alice_lunch']
  )
})

test('does not hide a base activity when no NPC wrapper exists', () => {
  const action = { id: 'church_read_sacred_arts', type: 'scene_activity', activity_id: 'church_read_sacred_arts' }
  assert.deepEqual(dedupeActivityActions([action]), [action])
})

test('does not dedupe unrelated action types with the same id shape', () => {
  const actions = [
    { id: 'intent:notice', type: 'npc_dialogue', activity_id: 'church_read_sacred_arts', source: 'npc_intent' },
    { id: 'church_read_sacred_arts', type: 'scene_activity', activity_id: 'church_read_sacred_arts' }
  ]
  assert.equal(dedupeActivityActions(actions).length, 2)
})


test('mainline interaction policy keeps daily actions out of a nearby precapture node', () => {
  assert.match(fieldSliceSource, /nearbyPrecaptureEvent/)
  assert.match(fieldSliceSource, /const visibleBase = nearbyPrecaptureEvent \? \[\] : base/)
  assert.match(fieldSliceSource, /event\?\.kind === 'precapture_key'/)
})
