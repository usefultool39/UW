import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const panelPath = new URL('../src/components/CookingMiniGamePanel.vue', import.meta.url)
const source = await readFile(panelPath, 'utf8')
const registry = await readFile(new URL('../src/field/activityRegistry.js', import.meta.url), 'utf8')
const fieldSlice = await readFile(new URL('../src/components/FieldSlice.vue', import.meta.url), 'utf8')

test('cooking panel keeps the scene activity completion contract and two result tiers', () => {
  for (const field of [
    "choice_id: pendingResult.value.choiceId",
    "tier,",
    "quantity,",
    "cuttingHits:",
    "heatPower:",
    "outputItemId:"
  ]) {
    assert.match(source, new RegExp(field.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&')))
  }
  assert.match(source, /emit\('complete'/)
  assert.match(source, /cook_herb_soup_normal/)
  assert.match(source, /cook_herb_soup_perfect/)
  assert.match(source, /cook_dried_rations_common_normal/)
  assert.match(source, /cook_dried_rations_rare_perfect/)
})

test('cooking panel has real cutting rhythm, heat control and empty-inventory refusal', () => {
  assert.match(source, /function startCutting\(\)/)
  assert.match(source, /window\.setInterval\(tickCutting, 50\)/)
  assert.match(source, /function tapCut\(\)/)
  assert.match(source, /function confirmHeat\(\)/)
  assert.match(source, /heatPower\.value >= 68 && heatPower\.value <= 82/)
  assert.match(source, /data-testid="cooking-empty-state"/)
  assert.match(source, /材料不足：本次烹饪被明确拒绝，库存保持不变。/)
  assert.match(source, /field_mint/)
  assert.match(source, /south_lake_common_fish/)
  assert.match(source, /south_lake_rare_fish/)
})

test('cooking panel routes through activityRegistry and FieldSlice shared wiring', () => {
  assert.match(registry, /home_hearth_cooking: \{[\s\S]*panel: 'cooking'[\s\S]*resultField: 'cooking_result'/)
  assert.match(registry, /cooking_qte: ACTIVITY_PRESENTATIONS\.home_hearth_cooking/)
  assert.match(fieldSlice, /import CookingMiniGamePanel from '\.\/CookingMiniGamePanel\.vue'/)
  assert.match(fieldSlice, /cooking: cookingGameOpen/)
  assert.match(fieldSlice, /:inventory="simState\?\.inventory"/)
  assert.match(fieldSlice, /@complete="onActivityComplete"/)
  assert.match(fieldSlice, /mini_game_result:/)
  assert.match(fieldSlice, /mini_game_result_mismatch/)
  assert.match(fieldSlice, /choice_id: extra\.mini_game_result\.choice_id/)
  assert.match(fieldSlice, /cookingGameOpen\.value \|\|/)
})

test('cooking panel is a mobile bottom sheet with safe-area padding', () => {
  assert.match(source, /max-height: min\(82dvh, 720px\)/)
  assert.match(source, /env\(safe-area-inset-bottom\)/)
  assert.match(source, /touch-action: manipulation/)
})
