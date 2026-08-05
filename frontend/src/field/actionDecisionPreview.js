const RESOURCE_FIELDS = Object.freeze({
  hp_cost: { key: 'hp', label: '生命' },
  mp_cost: { key: 'mp', label: '神圣力' },
  stamina_cost: { key: 'stamina', label: '体力' }
})

function asNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function effectsForAction(action) {
  if (action?.type === 'npc_intent_response') return action?.responseOption?.effects || {}
  return action?.activity?.effects || {}
}

function publicPreviewForAction(action) {
  return action?.activity?.preview || {}
}

function unique(items) {
  return [...new Set(items.filter(Boolean))]
}

function relationshipReward(effects) {
  const keys = Object.keys(effects?.relationship || {})
  if (!keys.length) return ''
  return keys.some((key) => key.endsWith('.trust')) ? '信任 / 关系' : '关系变化'
}

function choiceReward(action) {
  const choices = Array.isArray(action?.storyEvent?.choices) ? action.storyEvent.choices : []
  const remembered = choices.some((choice) => (choice?.preview?.remembered_by || []).length)
  const relationship = choices.some((choice) => Object.keys(choice?.preview?.relationship || {}).length)
  if (remembered && relationship) return '关系 / 记忆'
  if (relationship) return '关系变化'
  return remembered ? '写入记忆' : '剧情推进'
}

export function recoveryAdvice(blockedReason = '') {
  const reason = String(blockedReason || '')
  if (!reason) return ''
  if (reason.includes('地点') || reason.includes('走到') || reason.includes('范围')) return '先跟随金色标记进入对应地点，再重新打开互动。'
  if (reason.includes('时段') || reason.includes('开放')) return '先完成一个短活动推进时段，或回小屋休息到合适时间。'
  if (reason.includes('前置') || reason.includes('线索')) return '先完成右侧主线目标；结算后这里会自动解锁。'
  if (reason.includes('今天已完成') || reason.includes('每日')) return '回小屋休息进入下一天后可以再次进行。'
  if (reason.includes('已经完成')) return '这项内容已结算，可在日志中查看留下的线索与关系变化。'
  if (reason.includes('体力')) return '回小屋休息恢复体力，或先选择低消耗活动。'
  if (reason.includes('神圣力') || reason.includes('MP')) return '先休息恢复神圣力，再挑战需要术式的行动。'
  if (reason.includes('生命') || reason.includes('HP')) return '先休息恢复生命，避免在危险活动中倒下。'
  return '先处理当前主线或调整地点、时段和资源后重试。'
}

export function buildActionDecisionPreview(action, simState = {}) {
  const effects = effectsForAction(action)
  const publicPreview = publicPreviewForAction(action)
  const player = simState?.player || {}
  const costs = []
  const rewards = []
  let affordable = true
  const shortages = []

  const timeCost = asNumber(action?.activity?.time_cost)
  if (timeCost > 0) costs.push(`耗时 ${timeCost} 刻`)

  for (const [effectKey, meta] of Object.entries(RESOURCE_FIELDS)) {
    const publicAmount = publicPreview?.resource_costs?.[meta.key]
    const amount = asNumber(publicAmount ?? effects?.[effectKey])
    if (amount <= 0) continue
    costs.push(`${meta.label} -${amount}`)
    const rawAvailable = player?.[meta.key]
    if (Number.isFinite(Number(rawAvailable))) {
      const available = Number(rawAvailable)
      const floor = meta.key === 'hp' ? 1 : 0
      if (available - amount < floor) {
        affordable = false
        shortages.push(meta.label)
      }
    }
  }

  if (publicPreview?.variable_resource_cost || action?.activity?.interaction_kind === 'boundary_patrol') {
    costs.push('资源依表现结算')
    rewards.push('边境标记')
  }

  const publicRewardLabels = {
    relationship: '信任 / 关系',
    memory: '写入记忆',
    progress: '线索 / 进度',
    resources: '资源变化'
  }
  for (const kind of Array.isArray(publicPreview?.reward_kinds) ? publicPreview.reward_kinds : []) {
    rewards.push(publicRewardLabels[kind] || '')
  }
  if (publicPreview?.benefit_text) rewards.unshift(String(publicPreview.benefit_text))

  const relationship = relationshipReward(effects)
  if (relationship) rewards.push(relationship)
  if (effects?.memory && Object.keys(effects.memory).length) rewards.push('写入记忆')
  if (effects?.flags && Object.keys(effects.flags).length) rewards.push('线索 / 进度')

  if (action?.type === 'story_event') rewards.push(choiceReward(action))
  if (action?.type === 'npc_intent_response') rewards.push('后续态度')
  if (action?.source === 'npc_intent' && action?.type !== 'npc_intent_response') rewards.push('同伴事件')

  if (!costs.length && action?.type === 'story_event') costs.push('选择后结算')
  if (!costs.length && action?.type === 'npc_intent_response') costs.push('不消耗资源')
  if (!costs.length && action?.type === 'scene_activity') costs.push('不消耗资源')
  if (!rewards.length && action?.type === 'scene_activity') rewards.push('活动进展')
  if (!rewards.length) rewards.push('世界状态变化')

  const blockedReason = action?.blockedReason || (!affordable ? `${unique(shortages).join('、')}不足` : '')
  return {
    costs: unique(costs).slice(0, 3),
    rewards: unique(rewards).slice(0, 3),
    affordable,
    blockedReason,
    recovery: recoveryAdvice(blockedReason)
  }
}
