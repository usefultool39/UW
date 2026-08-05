import assert from 'node:assert/strict'
import test from 'node:test'
import { getPortraitAsset, getRuntimeIcon, RUNTIME_AUDIO, RUNTIME_KEYART } from '../src/field/runtimeAssetPaths.js'

test('approved runtime portrait paths use the v002 transparent derivatives', () => {
  assert.match(getPortraitAsset('alice', 'neutral'), /alice_neutral_v002_256\.png$/)
  assert.match(getPortraitAsset('alice', 'concerned'), /alice_concerned_v002_256\.png$/)
  assert.match(getPortraitAsset('eugeo', 'concerned'), /eugeo_concerned_v002_256\.png$/)
  assert.equal(getPortraitAsset('kirito', 'neutral'), getPortraitAsset('player', 'neutral'))
  assert.equal(getPortraitAsset('unknown', 'neutral'), '')
})

test('runtime audio, key art and icon paths are stable public assets', () => {
  assert.match(RUNTIME_AUDIO.bgmVillageDawn, /village-dawn-a\.ogg$/)
  assert.match(RUNTIME_AUDIO.ambienceDrizzle, /drizzle-village-a\.ogg$/)
  assert.match(RUNTIME_KEYART.villageDesktop, /village-desktop\.png$/)
  assert.match(getRuntimeIcon('time'), /runtime\/icons\/time\.png$/)
})
