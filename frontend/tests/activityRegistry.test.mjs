import assert from 'node:assert/strict'
import test from 'node:test'
import {
  activityIdForAction,
  activityOpenMessage,
  activityPanelKind,
  shouldOpenActivityPanel
} from '../src/field/activityRegistry.js'

test('resolves configured activity ids to their panel', () => {
  assert.equal(activityPanelKind({ activity_id: 'church_read_sacred_arts' }), 'reading')
  assert.equal(activityPanelKind({ activity_id: 'home_evening_meal' }), 'meal')
  assert.equal(activityPanelKind({ activity_id: 'north_gate_boundary_patrol' }), 'patrol')
})

test('falls back to interaction kind for data-driven activities', () => {
  const action = { id: 'future_patrol', activity: { interaction_kind: 'boundary_patrol' } }
  assert.equal(activityIdForAction(action), 'future_patrol')
  assert.equal(activityPanelKind(action), 'patrol')
  assert.match(activityOpenMessage(action), /巡查开始/)
})

test('ordinary scene activities do not open a special panel', () => {
  assert.equal(shouldOpenActivityPanel({ activity_id: 'village_notice_board' }), false)
  assert.equal(activityPanelKind({ activity_id: 'village_notice_board' }), '')
})
