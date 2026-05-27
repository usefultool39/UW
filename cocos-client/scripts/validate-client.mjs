import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const required = [
  'project.json',
  'assets/scripts/api/contracts.ts',
  'assets/scripts/api/GameApi.ts',
  'assets/scripts/boot/Boot.ts',
  'assets/scripts/field/FieldController.ts',
  'assets/scripts/field/LocalPath.ts',
  'assets/scripts/field/MapRenderer.ts',
  'assets/scripts/ui/OverlayUI.ts',
  'assets/scenes/Boot.scene',
  'assets/scenes/Boot.scene.meta',
  'assets/scenes/Field.scene',
  'assets/scenes/Field.scene.meta',
  'assets/scenes/field.scene-manifest.json',
  'scripts/offline-contract-smoke.mjs',
  'scripts/cross-client-contract-smoke.mjs',
  'scripts/live-contract-smoke.mjs'
]

const missing = required.filter((rel) => !fs.existsSync(path.join(root, rel)))
if (missing.length) {
  console.error(`Missing Cocos client files:\n${missing.map((item) => `- ${item}`).join('\n')}`)
  process.exit(1)
}

const project = JSON.parse(fs.readFileSync(path.join(root, 'project.json'), 'utf8'))
if (project.contract !== 'client-contract-2026-05-15-v2') {
  console.error(`Unexpected contract version: ${project.contract}`)
  process.exit(1)
}

const apiSource = fs.readFileSync(path.join(root, 'assets/scripts/api/GameApi.ts'), 'utf8')
for (const method of [
  'getSceneActivities',
  'chooseStoryEvent',
  'sendDialogue',
  'getNpcProfile',
  'exportSave',
  'importSave'
]) {
  if (!apiSource.includes(method)) {
    console.error(`GameApi is missing method: ${method}`)
    process.exit(1)
  }
}

const fieldSource = fs.readFileSync(path.join(root, 'assets/scripts/field/FieldController.ts'), 'utf8')
for (const method of [
  'ensureRuntimeWiring',
  'uiToTile',
  'makeRuntimeButton',
  'advanceUntilTimeBand',
  'chooseFirstStoryChoice',
  'runReadingDemo',
  'runTrainingDemo',
  'runLunchDemo',
  'runDinnerDemo',
  'restUntilNextDay',
  'showNearestNpcProfile',
  'greetNearestNpc'
]) {
  if (!fieldSource.includes(method)) {
    console.error(`FieldController is missing button-bindable method: ${method}`)
    process.exit(1)
  }
}

function readScene(rel, expectedName, expectedComponentType) {
  const scenePath = path.join(root, rel)
  const scene = JSON.parse(fs.readFileSync(scenePath, 'utf8'))
  if (!Array.isArray(scene) || scene[0]?.__type__ !== 'cc.SceneAsset') {
    console.error(`${rel} is not a Cocos scene asset`)
    process.exit(1)
  }
  if (scene[0]._name !== expectedName || scene[1]?._name !== expectedName) {
    console.error(`${rel} has unexpected scene name`)
    process.exit(1)
  }
  if (!scene.some((entry) => entry?.__type__ === expectedComponentType)) {
    console.error(`${rel} is missing component type ${expectedComponentType}`)
    process.exit(1)
  }
  return scene
}

function readSceneMeta(rel, expectedUuid) {
  const meta = JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'))
  if (meta.importer !== 'scene' || meta.uuid !== expectedUuid) {
    console.error(`${rel} has unexpected importer or uuid`)
    process.exit(1)
  }
}

readScene('assets/scenes/Boot.scene', 'Boot', 'a6b0b6yJn1KkbPlh9rklHy5')
readSceneMeta('assets/scenes/Boot.scene.meta', '8a4c79e5-187b-43a7-8c5e-570cc3a9cfb1')
readScene('assets/scenes/Field.scene', 'Field', 'd5e71DTeIVAwpIxXQl4iwky')
readSceneMeta('assets/scenes/Field.scene.meta', '6b1cdb7f-1bda-48ad-a7d7-7e5b0c7ec001')

const manifest = JSON.parse(fs.readFileSync(path.join(root, 'assets/scenes/field.scene-manifest.json'), 'utf8'))
if (manifest.contract !== 'client-contract-2026-05-15-v2') {
  console.error(`Unexpected scene manifest contract: ${manifest.contract}`)
  process.exit(1)
}
for (const method of manifest.buttonMethods || []) {
  if (!fieldSource.includes(method)) {
    console.error(`Scene manifest references missing method: ${method}`)
    process.exit(1)
  }
}

console.log('Cocos client scaffold ok')
