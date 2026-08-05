import test from 'node:test'
import assert from 'node:assert/strict'
import { buildActionDecisionPreview, recoveryAdvice } from '../src/field/actionDecisionPreview.js'

test('scene activity exposes concrete time, resource cost and relationship reward', () => {
  const preview = buildActionDecisionPreview({
    type: 'scene_activity',
    activity: {
      time_cost: 2,
      effects: {
        stamina_cost: 5,
        flags: { studied: 1 },
        relationship: { 'alice.trust': 2 },
        memory: { alice: { summary: '记住' } }
      }
    }
  }, { player: { stamina: 100 } })
  assert.deepEqual(preview.costs, ['耗时 2 刻', '体力 -5'])
  assert.deepEqual(preview.rewards, ['信任 / 关系', '写入记忆', '线索 / 进度'])
  assert.equal(preview.affordable, true)
})

test('insufficient resources produce a readable recovery path', () => {
  const preview = buildActionDecisionPreview({
    type: 'scene_activity',
    activity: { effects: { mp_cost: 12 } }
  }, { player: { mp: 4 } })
  assert.equal(preview.affordable, false)
  assert.equal(preview.blockedReason, '神圣力不足')
  assert.match(preview.recovery, /恢复神圣力/)
})

test('blocked reason maps to a concrete next action', () => {
  assert.match(recoveryAdvice('开放时段：傍晚'), /推进时段|休息/)
  assert.match(recoveryAdvice('需要先完成前置线索'), /右侧主线/)
  assert.match(recoveryAdvice('今天已完成'), /下一天/)
})

test('story event previews choice consequences without inventing costs', () => {
  const preview = buildActionDecisionPreview({
    type: 'story_event',
    storyEvent: {
      choices: [{ preview: { relationship: { 'alice.trust': 2 }, remembered_by: ['alice'] } }]
    }
  })
  assert.deepEqual(preview.costs, ['选择后结算'])
  assert.deepEqual(preview.rewards, ['关系 / 记忆'])
})

test('public activity preview drives UI without exposing authored effects', () => {
  const preview = buildActionDecisionPreview({
    type: 'scene_activity',
    activity: {
      time_cost: 2,
      preview: {
        resource_costs: { stamina: 5 },
        reward_kinds: ['relationship', 'memory', 'progress'],
        variable_resource_cost: false
      }
    }
  }, { player: { stamina: 100 } })
  assert.deepEqual(preview.costs, ['耗时 2 刻', '体力 -5'])
  assert.deepEqual(preview.rewards, ['信任 / 关系', '写入记忆', '线索 / 进度'])
})
