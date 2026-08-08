import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const componentPath = new URL('../src/components/FishingMiniGamePanel.vue', import.meta.url)
const source = await readFile(componentPath, 'utf8')
const registry = await readFile(new URL('../src/field/activityRegistry.js', import.meta.url), 'utf8')
const fieldSlice = await readFile(new URL('../src/components/FieldSlice.vue', import.meta.url), 'utf8')

 test('fishing panel keeps the scene activity completion contract and settles both fish tiers', () => {
  for (const field of [
    "choice_id: caughtOutcome.value.choiceId",
    "fish_id:",
    "fish_rarity:",
    "label: caughtOutcome.value.label",
    "score: caughtOutcome.value.score",
    "timing_ms: caughtOutcome.value.timingMs"
  ]) {
    assert.match(source, new RegExp(field.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&')))
  }
  assert.match(source, /emit\('complete'/)
  assert.match(source, /catch_common_fish/)
  assert.match(source, /catch_rare_fish/)
  assert.match(source, /rareWindowMs = 240/)
})

test('fishing panel has a visible bite QTE, retry path and mobile bottom sheet', () => {
  assert.match(source, /现在提竿！/)
  assert.match(source, /再抛一竿/)
  assert.match(source, /phase === 'bite'/)
  assert.match(source, /window\.setTimeout\(beginBite/)
  assert.match(source, /window\.setInterval\(/)
  assert.match(source, /max-height: min\(80dvh, 650px\)/)
  assert.match(source, /env\(safe-area-inset-bottom\)/)
  assert.match(source, /touch-action: manipulation/)
})

test('activity registry and FieldSlice route fishing through the shared panel contract', () => {
  assert.match(registry, /south_lake_fishing: \{[\s\S]*panel: 'fishing'[\s\S]*resultField: 'fishing_result'/)
  assert.match(registry, /fishing_qte: ACTIVITY_PRESENTATIONS\.south_lake_fishing/)
  assert.match(fieldSlice, /import FishingMiniGamePanel from '\.\/FishingMiniGamePanel\.vue'/)
  assert.match(fieldSlice, /fishing: fishingGameOpen/)
  assert.match(fieldSlice, /@complete="onActivityComplete"/)
  assert.match(fieldSlice, /mini_game_result:/)
  assert.match(fieldSlice, /mini_game_result_mismatch/)
  assert.match(fieldSlice, /choice_id: extra\.mini_game_result\.choice_id/)
  assert.match(fieldSlice, /fishingGameOpen\.value \|\|/)
})
