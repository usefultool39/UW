const ACTIVITY_PRESENTATIONS = Object.freeze({
  church_read_sacred_arts: {
    panel: 'reading',
    resultField: 'reading_result',
    openMessage: '书页已经摊开，先拼出你要带走的线索。',
    completionMessage: '书库线索已经写入日志和关系。'
  },
  church_ask_alice_lunch: {
    panel: 'meal',
    resultField: 'meal_result',
    openMessage: '餐桌上的态度，会被关系和记忆记住。',
    completionMessage: '这次餐桌态度已经被记住。'
  },
  home_evening_meal: {
    panel: 'meal',
    resultField: 'meal_result',
    openMessage: '餐桌上的态度，会被关系和记忆记住。',
    completionMessage: '这次餐桌态度已经被记住。'
  },
  north_gate_boundary_patrol: {
    panel: 'patrol',
    resultField: 'patrol_result',
    openMessage: '巡查开始：先读懂敌方意图，再选择克制架势。',
    completionMessage: '巡查结果已写入资源、关系和边境记录。'
  }
})

const INTERACTION_KIND_PRESENTATIONS = Object.freeze({
  reading_keywords: ACTIVITY_PRESENTATIONS.church_read_sacred_arts,
  meal_choice: ACTIVITY_PRESENTATIONS.home_evening_meal,
  boundary_patrol: ACTIVITY_PRESENTATIONS.north_gate_boundary_patrol
})

export function activityIdForAction(action) {
  return String(action?.activity_id || action?.id || action?.activity?.id || '')
}

export function activityPresentationForAction(action) {
  const activityId = activityIdForAction(action)
  const interactionKind = String(action?.activity?.interaction_kind || '')
  return ACTIVITY_PRESENTATIONS[activityId] || INTERACTION_KIND_PRESENTATIONS[interactionKind] || null
}

export function shouldOpenActivityPanel(action) {
  return activityPresentationForAction(action) !== null
}

export function activityPanelKind(action) {
  return activityPresentationForAction(action)?.panel || ''
}

export function activityOpenMessage(action) {
  return activityPresentationForAction(action)?.openMessage || ''
}

export function activityCompletionMessage(action) {
  return activityPresentationForAction(action)?.completionMessage || ''
}

export function activityResultField(action) {
  return activityPresentationForAction(action)?.resultField || ''
}

export function activityResultExtras(action, miniGameResult) {
  const field = activityResultField(action)
  if (!field || !miniGameResult || typeof miniGameResult !== 'object') return {}
  return { [field]: miniGameResult }
}
