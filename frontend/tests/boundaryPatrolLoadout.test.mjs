import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const panel = await readFile(new URL('../src/components/BoundaryPatrolMiniGamePanel.vue', import.meta.url), 'utf8')
const fieldSlice = await readFile(new URL('../src/components/FieldSlice.vue', import.meta.url), 'utf8')
const registry = await readFile(new URL('../src/field/activityRegistry.js', import.meta.url), 'utf8')

test('patrol panel requires a pre-departure loadout choice and caps it at two items', () => {
  assert.match(panel, /data-testid="patrol-loadout"/)
  assert.match(panel, /选择最多两件随身道具/)
  assert.match(panel, /loadoutMax/)
  assert.match(panel, /selectedLoadout\.value\.length >= loadoutMax\.value/)
  assert.match(panel, /function startPatrol\(\)/)
  assert.match(panel, /确认出发/)
})

test('patrol panel only enables owned authored options and submits loadout with the existing result contract', () => {
  assert.match(panel, /props\.inventory\?\./)
  assert.match(panel, /hasInventory\(option\.item_id\)/)
  assert.match(panel, /materials cannot be used|材料不能作为巡查装备/)
  assert.match(panel, /choice_id: grade\.value\.id/)
  assert.match(panel, /loadout: \[\.\.\.selectedLoadout\.value\]/)
  assert.match(panel, /emit\('complete'/)
})

test('FieldSlice forwards inventory and candidate loadout without changing the shared activity route', () => {
  assert.match(fieldSlice, /import BoundaryPatrolMiniGamePanel from '\.\/BoundaryPatrolMiniGamePanel\.vue'/)
  assert.match(fieldSlice, /:inventory="simState\?\.inventory"/)
  assert.match(fieldSlice, /loadout: Array\.isArray\(extra\.loadout\) \? extra\.loadout : undefined/)
  assert.match(fieldSlice, /loadout: payload\?\.loadout \|\| payload\?\.result\?\.loadout \|\| \[\]/)
  assert.match(fieldSlice, /patrol: boundaryPatrolOpen/)
})

test('activity registry explains loadout preparation while keeping the patrol result field', () => {
  assert.match(registry, /north_gate_boundary_patrol: \{[\s\S]*panel: 'patrol'[\s\S]*resultField: 'patrol_result'/)
  assert.match(registry, /最多两件随身道具/)
})
