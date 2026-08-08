import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const component = await readFile(new URL('../src/components/ReadingMiniGamePanel.vue', import.meta.url), 'utf8')
const registry = await readFile(new URL('../src/field/activityRegistry.js', import.meta.url), 'utf8')
const fieldSlice = await readFile(new URL('../src/components/FieldSlice.vue', import.meta.url), 'utf8')

const escaped = (value) => new RegExp(value.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&'))

test('reading panel is a three-step phenomenon-rule-conclusion chain', () => {
  for (const label of ['phenomenon', 'rule', 'conclusion', '现象', '规则', '结论']) {
    assert.match(component, escaped(label))
  }
  assert.match(component, /const steps = computed\(\(\) => chain\.value\.steps\)/)
  assert.match(component, /path\.steps\?\.\[stepIndex\.value\] === option\.id/)
  assert.match(component, /choice_id: path\.choice_id/)
  assert.match(component, /inference_chain: selectedIds\.value\.slice\(\)/)
})

test('wrong inference stays local and gives concrete feedback', () => {
  assert.match(component, /feedbackOpen\.value = true/)
  assert.match(component, /option\.feedback \|\| '这条记录不能接在当前步骤后面。回到当前证据/)
  assert.match(component, /错误选择只会停留在当前步骤，不会写入关系、记忆或剧情 flag。/)
  assert.match(component, /if \(props\.busy \|\| feedbackOpen\.value \|\| !option\?\.id\) return/)
})

test('successful reading keeps the existing activity result contract', () => {
  assert.match(component, /emit\('complete', \{/) 
  assert.match(component, /path_id: path\.choice_id/)
  assert.match(component, /explanation:/)
  assert.match(registry, /panel: 'reading'/)
  assert.match(registry, /resultField: 'reading_result'/)
  assert.match(registry, /readingChain: READING_CHAIN_FALLBACK/)
  assert.match(fieldSlice, /readingPanelActivity/)
  assert.match(fieldSlice, /readingChainForAction/)
  assert.match(registry, /这条推理链已经写入日志、关系和记忆/)
  assert.match(fieldSlice, /@complete="onReadingComplete"/)
  assert.match(fieldSlice, /await onActivityComplete\(payload\)/)
})

test('reading panel is a mobile bottom sheet with safe-area padding', () => {
  assert.match(component, /align-items: flex-end/)
  assert.match(component, /max-height: min\(82dvh, 720px\)/)
  assert.match(component, /env\(safe-area-inset-bottom\)/)
  assert.match(component, /touch-action: manipulation/)
})
