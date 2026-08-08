import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const componentPath = new URL('../src/components/InventoryPanel.vue', import.meta.url)
const appPath = new URL('../src/App.vue', import.meta.url)
const source = await readFile(componentPath, 'utf8')
const appSource = await readFile(appPath, 'utf8')

test('inventory panel exposes live inventory categories and eight visual slots', () => {
  assert.match(source, /props\.simState\?\.inventory/)
  assert.match(source, /const SLOT_COUNT = 8/)
  for (const category of ["id: 'material'", "id: 'consumable'", "id: 'key'"]) {
    assert.match(source, new RegExp(category.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
  }
  assert.match(source, /v-for="\(slot, index\) in slots"/)
  assert.match(source, /class="empty-slot"/)
  assert.match(source, /slot\.description/)
  assert.match(source, /slot\.quantity/)
  assert.match(source, /dried_rations:/)
  assert.match(source, /herb_soup:/)
  assert.match(source, /record_notebook:/)
})

test('using a consumable follows the playerAction use_item contract and reports feedback', () => {
  assert.match(source, /kind: 'use_item'/)
  assert.match(source, /item_id: item\.id/)
  assert.match(source, /quantity: 1/)
  assert.match(source, /await props\.playerAction\(/)
  assert.match(source, /class="inventory-feedback"/)
  assert.match(source, /role="status"/)
  assert.match(source, /feedback-success/)
  assert.match(source, /feedback-error/)
  assert.match(source, /response\?\.item_result\?\.result_text/)
})

test('field mode uses a compact trigger and mobile bottom drawer instead of a map-covering overlay', () => {
  assert.match(source, /fieldMode/)
  assert.match(source, /class="inventory-trigger"/)
  assert.match(source, /max-height: min\(56dvh, 520px\)/)
  assert.match(source, /border-radius: 18px 18px 0 0/)
  assert.match(source, /env\(safe-area-inset-bottom\)/)
  assert.doesNotMatch(source, /class="result-backdrop"/)
})

test('App exposes inventory in overview and as a field-mode trigger', () => {
  assert.equal((appSource.match(/<InventoryPanel/g) || []).length, 2)
  assert.match(appSource, /:sim-state="state"/)
  assert.match(appSource, /:player-action="playerAction"/)
  assert.match(appSource, /field-mode/)
  assert.match(appSource, /v-if="appTab === 'overview'"/)
})
