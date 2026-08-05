import assert from 'node:assert/strict'
import test from 'node:test'
import {
  activityCompletionMessage,
  activityIdForAction,
  activityOpenMessage,
  activityPanelKind,
  activityResultExtras,
  activityResultField,
  shouldOpenActivityPanel
} from '../src/field/activityRegistry.js'

test('resolves configured activity ids to their panel and result field', () => {
  assert.equal(activityPanelKind({ activity_id: 'church_read_sacred_arts' }), 'reading')
  assert.equal(activityResultField({ activity_id: 'church_read_sacred_arts' }), 'reading_result')
  assert.equal(activityResultField({ activity_id: 'home_evening_meal' }), 'meal_result')
  assert.equal(activityResultField({ activity_id: 'north_gate_boundary_patrol' }), 'patrol_result')
})

test('maps a mini-game result through the configured result field', () => {
  const result = { label: '清晰', score: 100 }
  assert.deepEqual(
    activityResultExtras({ activity_id: 'church_read_sacred_arts' }, result),
    { reading_result: result }
  )
  assert.match(activityCompletionMessage({ activity_id: 'north_gate_boundary_patrol' }), /巡查结果/)
})

test('falls back to interaction kind for data-driven activities', () => {
  const action = { id: 'future_patrol', activity: { interaction_kind: 'boundary_patrol' } }
  assert.equal(activityIdForAction(action), 'future_patrol')
  assert.equal(activityPanelKind(action), 'patrol')
  assert.equal(activityResultField(action), 'patrol_result')
  assert.match(activityOpenMessage(action), /巡查开始/)
})

test('unknown activity does not invent a panel, result field or result payload', () => {
  const action = { activity_id: 'village_notice_board' }
  assert.equal(shouldOpenActivityPanel(action), false)
  assert.equal(activityPanelKind(action), '')
  assert.equal(activityResultField(action), '')
  assert.deepEqual(activityResultExtras(action, { label: 'unknown' }), {})
})
