import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const panel = await readFile(new URL('../src/components/ClueJournalPanel.vue', import.meta.url), 'utf8')
const field = await readFile(new URL('../src/components/FieldSlice.vue', import.meta.url), 'utf8')
const api = await readFile(new URL('../src/composables/useGameApi.js', import.meta.url), 'utf8')

test('journal exposes a visible memory codex switch with locked entries', () => {
  assert.match(panel, /记忆图鉴/)
  assert.match(panel, /activeTab === 'codex'/)
  assert.match(panel, /codexProgress/)
  assert.match(panel, /codexMainline/)
  assert.match(panel, /codexFragments/)
  assert.match(panel, /codexActivities/)
  assert.match(panel, /codexNpcs/)
  assert.match(panel, /未解锁记忆/)
  assert.match(panel, /解锁条件：\{\{ entry\.condition \}\}/)
  assert.match(panel, /safe-area-inset-bottom|@media \(max-width: 620px\)/)
})

test('field journal receives server codex and refreshes before opening', () => {
  assert.match(field, /<ClueJournalPanel/)
  assert.match(field, /:codex="simState\?\.codex"/)
  assert.match(field, /await props\.refresh\(\)/)
})

test('game API reads the codex endpoint and attaches it to live state', () => {
  assert.match(api, /async function fetchCodex\(\)/)
  assert.match(api, /requestJson\('\/api\/codex'\)/)
  assert.match(api, /fetchState\(\), fetchEvents\(\), fetchCodex\(\)/)
  assert.match(api, /state\.value = \{ \.\.\.state\.value, codex: codex\.value \}/)
})
