import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const componentPath = new URL('../src/components/TrainingMiniGamePanel.vue', import.meta.url)
const source = await readFile(componentPath, 'utf8')

test('training mini-game keeps the complete payload contract while adding combo metadata', () => {
  for (const field of ['choice_id: choiceId', 'tier: tier.value.id', 'label: tier.value.label', 'score: averageScore.value', 'hits: attempts.value.length', 'text: tier.value.text']) {
    assert.match(source, new RegExp(field.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&')))
  }
  assert.match(source, /combo: maxCombo\.value/)
  assert.match(source, /stages_cleared: attempts\.value\.length/)
})

test('training rhythm has five accelerating stages and three visible judgements', () => {
  assert.match(source, /const maxAttempts = 5/)
  assert.match(source, /cycle: 1800[\s\S]*cycle: 1500[\s\S]*cycle: 1250[\s\S]*cycle: 1050[\s\S]*cycle: 900/)
  assert.match(source, /label: '正中'/)
  assert.match(source, /label: '接上'/)
  assert.match(source, /label: '偏离'/)
  assert.match(source, /const nextCombo = judgement\.className === 'miss' \? 0 : previousCombo \+ 1/)
})

test('mobile layout is bottom-sheet sized and respects the safe area', () => {
  assert.match(source, /max-height: min\(78dvh, 560px\)/)
  assert.match(source, /padding-bottom: max\(0\.5rem, env\(safe-area-inset-bottom\)\)/)
  assert.match(source, /touch-action: manipulation/)
})
