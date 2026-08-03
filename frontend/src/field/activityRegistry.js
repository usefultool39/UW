const ACTIVITY_PRESENTATIONS = Object.freeze({
  church_read_sacred_arts: {
    panel: 'reading',
    openMessage: '书页已经摊开，先拼出你要带走的线索。'
  },
  church_ask_alice_lunch: {
    panel: 'meal',
    openMessage: '餐桌上的态度，会被关系和记忆记住。'
  },
  home_evening_meal: {
    panel: 'meal',
    openMessage: '餐桌上的态度，会被关系和记忆记住。'
  },
  north_gate_boundary_patrol: {
    panel: 'patrol',
    openMessage: '巡查开始：先读懂敌方意图，再选择克制架势。'
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
