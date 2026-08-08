const READING_CHAIN_FALLBACK = Object.freeze({
  intro: '把每一页先放在它能证明的层级：现象、规则、结论。',
  steps: [
    {
      id: 'phenomenon', label: '现象',
      prompt: '先找出纸页直接记录的异常，不要急着解释。',
      helper: '现象应该是能被听见、看见，或在记录中复述的事实。',
      options: [
        { id: 'bird_silence', label: '鸟声消失', note: '北侧边界附近突然听不到鸟声。', feedback: '这是可以直接观察的异常。' },
        { id: 'ancient_tree', label: '巨神树', note: '村里每天都要清理、伐木的共同地标。', feedback: '巨神树是地点，不是正在发生的现象。' },
        { id: 'blank_margin', label: '空白注记', note: '纸页边缘留下了像被擦掉的空处。', feedback: '空白是记录痕迹，还不足以说明发生了什么。' }
      ]
    },
    {
      id: 'rule', label: '规则',
      prompt: '再找出会约束或解释这个现象的旧记录规则。',
      helper: '规则不是地点或情绪，而是反复出现、会要求人们照做的文字。',
      options: [
        { id: 'silent_line', label: '静默线', note: '多份旧记录里被反复涂改、却总在同一处出现的词。', feedback: '这条记录线能把异常和书页空白接起来。' },
        { id: 'north_law', label: '北境律令', note: '村民不愿多谈、却必须遵守的边界规则。', feedback: '这是一条真实的规则，但要先找到与现象相连的记录线。' },
        { id: 'village_record', label: '村史断页', note: '年份缺了一段的旧纸。', feedback: '断页说明资料不完整，却没有说明现象为何发生。' }
      ]
    },
    {
      id: 'conclusion', label: '结论',
      prompt: '最后选一个不超过证据范围的结论。',
      helper: '好的结论会回扣前两步，不替纸页说出它没有证明的事。',
      options: [
        { id: 'trace_silence', label: '北边静默与禁忌目录有关', note: '把异常线索留在证据能支持的范围内。', feedback: '这个结论跳得太远了。' },
        { id: 'map_boundary', label: '边界规则先从日常失真处显形', note: '先定位变化如何落到村庄日常。', feedback: '这个结论移到了另一条线索。' },
        { id: 'quiet_observe', label: '先记录空白，不提前宣布答案', note: '保留疑问，也保留下一次交叉验证的余地。', feedback: '谨慎并不等于跳过证据。' }
      ]
    }
  ],
  paths: [
    { choice_id: 'trace_silence', steps: ['bird_silence', 'silent_line', 'trace_silence'], label: '异常线索完整', success_text: '鸟声、静默线和北境律令终于扣在同一条证据链上。' },
    { choice_id: 'map_boundary', steps: ['ancient_tree', 'north_law', 'map_boundary'], label: '边界规则偏重', success_text: '你先把边界规则落回村庄日常，没有把空白急着解释成答案。' },
    { choice_id: 'quiet_observe', steps: ['blank_margin', 'village_record', 'quiet_observe'], label: '保留疑问', success_text: '你把空白和断页记下来，给下一次交叉验证留下了位置。' }
  ]
})

const ACTIVITY_PRESENTATIONS = Object.freeze({
  church_read_sacred_arts: {
    panel: 'reading',
    resultField: 'reading_result',
    openMessage: '书页已经摊开：先辨认现象，再找规则，最后收束成结论。',
    completionMessage: '这条推理链已经写入日志、关系和记忆。',
    readingChain: READING_CHAIN_FALLBACK
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
  home_hearth_cooking: {
    panel: 'cooking',
    resultField: 'cooking_result',
    openMessage: '炉火已经点稳：先跟上切菜节奏，再把火候收住。',
    completionMessage: '烹饪结果已写入行囊；成品可以在物品栏中使用。'
  },
  north_gate_boundary_patrol: {
    panel: 'patrol',
    resultField: 'patrol_result',
    openMessage: '巡查开始前先准备最多两件随身道具，再读懂敌方意图并选择克制架势。',
    completionMessage: '巡查结果已写入资源、关系和边境记录。'
  },
  south_lake_fishing: {
    panel: 'fishing',
    resultField: 'fishing_result',
    openMessage: '鱼线已经落进雾里。听见咬钩后，抓住那一瞬提竿。',
    completionMessage: '钓鱼结果已写入行囊；南湖旧渡每天只能试一次。'
  }
})

const INTERACTION_KIND_PRESENTATIONS = Object.freeze({
  reading_keywords: ACTIVITY_PRESENTATIONS.church_read_sacred_arts,
  meal_choice: ACTIVITY_PRESENTATIONS.home_evening_meal,
  cooking_qte: ACTIVITY_PRESENTATIONS.home_hearth_cooking,
  boundary_patrol: ACTIVITY_PRESENTATIONS.north_gate_boundary_patrol,
  fishing_qte: ACTIVITY_PRESENTATIONS.south_lake_fishing
})

export function activityIdForAction(action) {
  return String(action?.activity_id || action?.id || action?.activity?.id || '')
}

export function activityPresentationForAction(action) {
  const activityId = activityIdForAction(action)
  const interactionKind = String(action?.activity?.interaction_kind || '')
  return ACTIVITY_PRESENTATIONS[activityId] || INTERACTION_KIND_PRESENTATIONS[interactionKind] || null
}

export function readingChainForAction(action) {
  const authored = action?.activity?.reading_chain
  if (authored?.steps?.length === 3 && Array.isArray(authored.paths)) return authored
  return activityPresentationForAction(action)?.readingChain || null
}

export function shouldOpenActivityPanel(action) {
  return activityPresentationForAction(action) !== null
}

export function shouldOpenActivityChoicePanel(action) {
  const choices = Array.isArray(action?.activity?.choices) ? action.activity.choices : []
  return action?.type === 'scene_activity' && choices.length > 0 && !shouldOpenActivityPanel(action)
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
