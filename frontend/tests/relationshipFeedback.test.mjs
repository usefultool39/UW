import assert from 'node:assert/strict'
import test from 'node:test'
import {
  normalizeRelationshipChanges,
  relationshipFieldLabel,
  relationshipPercent
} from '../src/utils/relationshipFeedback.js'

test('normalizes the backend relationship change contract', () => {
  assert.deepEqual(
    normalizeRelationshipChanges([
      { npc_id: 'alice', field: 'trust', before: 4, after: 7, delta: 3 },
      { npc_id: 'eugeo', field: 'tension', before: 8, after: 6, delta: -2 }
    ]),
    [
      { npc_id: 'alice', field: 'trust', before: 4, after: 7, delta: 3 },
      { npc_id: 'eugeo', field: 'tension', before: 8, after: 6, delta: -2 }
    ]
  )
})

test('supports nested and aliased payloads without inventing unknown dimensions', () => {
  assert.deepEqual(
    normalizeRelationshipChanges({
      relationship_changes: [
        { agent_id: 'alice', dimension: 'affinity', previous: 2, current: 5 },
        { npc_id: 'eugeo', stat: 'trust', change: -1 }
      ]
    }),
    [
      { npc_id: 'alice', field: 'affinity', before: 2, after: 5, delta: 3 },
      { npc_id: 'eugeo', field: 'trust', before: null, after: null, delta: -1 }
    ]
  )
  assert.deepEqual(normalizeRelationshipChanges({ alice: { mood: 4 } }), [])
})

test('maps relationship values into stable visual ranges', () => {
  assert.equal(relationshipPercent(-100, 'trust'), 0)
  assert.equal(relationshipPercent(0, 'affinity'), 50)
  assert.equal(relationshipPercent(55, 'tension'), 55)
  assert.equal(relationshipFieldLabel('trust'), '信任')
})
