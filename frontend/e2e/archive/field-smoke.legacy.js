// @ts-check
import { test, expect } from '@playwright/test'

const API = process.env.E2E_API_URL || `http://127.0.0.1:${process.env.E2E_BACKEND_PORT || 8765}`

async function resetWorld(request) {
  const res = await request.post(`${API}/api/reset`)
  expect(res.ok()).toBeTruthy()
}

async function playerAction(request, body) {
  const res = await request.post(`${API}/api/player/action`, { data: body })
  expect(res.ok()).toBeTruthy()
  const json = await res.json()
  expect(json.ok).toBeTruthy()
  return json
}

async function storyChoose(request, body) {
  const res = await request.post(`${API}/api/story/choose`, { data: body })
  expect(res.ok()).toBeTruthy()
  const json = await res.json()
  expect(json.ok).toBeTruthy()
  return json
}

async function restToDay(request, day) {
  let state = await (await request.get(`${API}/api/state`)).json()
  while (Number(state.day || 1) < day) {
    const out = await playerAction(request, { kind: 'rest_until_next_day' })
    state = out.state
  }
}

async function setFlags(request, flags) {
  for (const flag of flags) {
    await playerAction(request, { kind: 'set_flag', flag_key: flag, flag_value: 1 })
  }
}

async function advanceToExpeditionPrep(request) {
  await storyChoose(request, { event_id: 'ch1_d1_reading_clue', choice_id: 'ask_alice' })
  await playerAction(request, { kind: 'rest_until_next_day' })
  await storyChoose(request, { event_id: 'ch1_d2_forest_anomaly', choice_id: 'investigate_together' })
  await playerAction(request, { kind: 'rest_until_next_day' })
  await storyChoose(request, { event_id: 'ch1_d3_boundary_choice', choice_id: 'cross_boundary' })
  await restToDay(request, 4)
  await storyChoose(request, { event_id: 'ch1_d4_after_boundary_debrief', choice_id: 'write_truth' })
  await restToDay(request, 7)
  await storyChoose(request, { event_id: 'ch1_d7_first_boundary_drill', choice_id: 'mark_safe_route' })
  await restToDay(request, 12)
  await storyChoose(request, { event_id: 'ch1_d12_village_trust', choice_id: 'public_patrol_board' })
  await restToDay(request, 18)
  await storyChoose(request, { event_id: 'ch1_d18_silent_line_rehearsal', choice_id: 'calibrate_sacred_arts' })
  await restToDay(request, 24)
  await playerAction(request, { kind: 'move_scene', scene_id: 'home_hearth' })
}

async function advanceToMonthGate(request) {
  await advanceToExpeditionPrep(request)
  await storyChoose(request, { event_id: 'ch1_d24_expedition_pack', choice_id: 'pack_for_safety' })
  await restToDay(request, 28)
  await playerAction(request, { kind: 'move_scene', scene_id: 'north_gate' })
}

async function advanceToDay31OrderRoute(request) {
  await advanceToMonthGate(request)
  await playerAction(request, { kind: 'scene_activity', activity_id: 'north_gate_month_end_vigil', activity_choice: 'review_promises' })
  await storyChoose(request, { event_id: 'ch1_d30_first_month_gate', choice_id: 'route_report_first' })
  await restToDay(request, 31)
  await playerAction(request, { kind: 'move_scene', scene_id: 'north_gate' })
}

async function dismissOpeningBrief(page) {
  const btn = page.getByRole('button', { name: '定位第一条线索' })
  await btn.click({ timeout: 1_500 }).catch(() => {})
}

async function expectCanvasNonBlank(page) {
  const canvas = page.locator('.phaser-host canvas')
  await expect(canvas).toBeVisible({ timeout: 30_000 })
  const nonBlank = await canvas.evaluate((node) => {
    const c = /** @type {HTMLCanvasElement} */ (node)
    if (c.width < 64 || c.height < 64) return false
    const url = c.toDataURL('image/png')
    return typeof url === 'string' && url.length > 2000
  })
  expect(nonBlank).toBeTruthy()
}

async function expectNoCoreOverlap(page) {
  const boxes = await page.evaluate(() => {
    const pick = (selector) => {
      const el = document.querySelector(selector)
      if (!el) return null
      const style = window.getComputedStyle(el)
      if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity || 1) === 0) return null
      const r = el.getBoundingClientRect()
      if (r.width <= 1 || r.height <= 1) return null
      return { selector, x: r.x, y: r.y, w: r.width, h: r.height }
    }
    return [
      '.quest-tracker',
      '.action-hotbar',
      '.field-header',
      '.dom-minimap',
      '.map-readability-key',
      '.opening-brief'
    ]
      .map(pick)
      .filter(Boolean)
  })
  const overlap = (a, b) => {
    const x = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x))
    const y = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y))
    return x * y
  }
  for (let i = 0; i < boxes.length; i += 1) {
    for (let j = i + 1; j < boxes.length; j += 1) {
      expect(overlap(boxes[i], boxes[j]), `${boxes[i].selector} overlaps ${boxes[j].selector}`).toBe(0)
    }
  }
}

test.describe('开放世界质量 smoke', () => {
  test.setTimeout(150_000)

  test.beforeEach(async ({ request }) => {
    await resetWorld(request)
  })

  test('桌面与手机画布非空，关键 UI 不重叠，并保存截图', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await page.goto('/')
    await expect(page.locator('.phaser-host')).toBeVisible()
    await expectCanvasNonBlank(page)
    await expectNoCoreOverlap(page)
    await expect(page.getByRole('button', { name: '定位第一条线索' })).toHaveCount(1)
    await expect(page.getByRole('button', { name: '开始行动' })).toHaveCount(0)
    await page.getByRole('button', { name: '定位第一条线索' }).click()
    await expect(page.locator('.opening-cinematic-root')).toHaveCount(0)
    await expect(page.locator('.newcomer-guide')).toHaveCount(0)
    await expect(page.locator('.quest-tracker .quest-primary-btn')).toHaveCount(1)
    await expect(page.locator('.guide-steps')).toContainText('看金色指引')
    await expect(page.locator('.loop-ribbon')).toContainText('一条线索，做一次判断')
    await page.screenshot({ path: '../runs/quality_gate_desktop.png', fullPage: false })

    await page.setViewportSize({ width: 390, height: 844 })
    await page.reload()
    await expectCanvasNonBlank(page)
    await expectNoCoreOverlap(page)
    await page.screenshot({ path: '../runs/quality_gate_mobile.png', fullPage: false })
  })

  test('日期由剧情闸和日结算推进，不显示独立时间推进按钮', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await page.goto('/')
    await expect(page.getByRole('button', { name: /时间推进/ })).toHaveCount(0)
    await expect(page.locator('.story-progress-badge')).toHaveText('剧情推进')
    await expect(page.locator('.action-rest')).toHaveAttribute('title', /剧情闸/)
  })

  test('读书、午餐、训练、日志和 Day 2 预告可走通', async ({ page, request }) => {
    await playerAction(request, { kind: 'move_scene', scene_id: 'reading_hall' })
    await page.goto('/')
    await dismissOpeningBrief(page)

    await page.locator('.nearby-enter-btn').click()
    await expect(page.locator('.interact-action[data-action-id="read"]')).toHaveCount(0)
    await expect(page.locator('.interact-action[data-activity-id="church_read_sacred_arts"]')).toHaveCount(1)
    const readingEntry = page.locator('.interact-action').filter({ hasText: '拼接神圣术' })
    await expect(readingEntry.locator('.decision-chip.cost').filter({ hasText: '耗时 2 刻' })).toBeVisible()
    await expect(readingEntry.locator('.decision-chip.cost').filter({ hasText: '体力 -5' })).toBeVisible()
    await expect(readingEntry.locator('.decision-chip.reward').filter({ hasText: '信任 / 关系' })).toBeVisible()
    await readingEntry.click()
    await expect(page.locator('.reading-panel')).toBeVisible()
    await page.getByRole('button', { name: /鸟声消失/ }).click()
    await page.getByRole('button', { name: /静默线/ }).click()
    await page.getByRole('button', { name: /禁忌目录/ }).click()
    await page.getByRole('button', { name: '记下这条线索' }).click()
    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.impact-chip').filter({ hasText: '阅读线索' })).toBeVisible()
    const readingState = await (await request.get(`${API}/api/state`)).json()
    expect(readingState.flags.prologue_reading_done).toBe(1)
    await page.getByRole('button', { name: '继续行动' }).click()

    await page.locator('.nearby-enter-btn').click()
    await page.locator('.interact-action').filter({ hasText: '调查边界记录' }).click()
    await expect(page.locator('.event-panel')).toBeVisible()
    await page.locator('.event-choice').filter({ hasText: '把记录告诉爱丽丝' }).click()
    await expect(page.locator('.result-panel')).toBeVisible()
    await page.getByRole('button', { name: '继续行动' }).click()

    await page.locator('.nearby-enter-btn').click()
    await page.locator('.interact-action[data-activity-id="church_ask_alice_lunch"]').click()
    await expect(page.locator('.meal-panel')).toBeVisible()
    await page.getByRole('button', { name: /给尤吉欧多留一份干粮/ }).click()
    await page.getByRole('button', { name: '确认态度' }).click()
    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.impact-chip').filter({ hasText: '餐桌态度' })).toBeVisible()
    await page.getByRole('button', { name: '继续行动' }).click()

    await playerAction(request, { kind: 'move_scene', scene_id: 'gigas_clearing' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    await page.locator('.interact-action').filter({ hasText: '开始巨树训练' }).click()
    await expect(page.locator('.training-panel')).toBeVisible()
    await page.getByRole('button', { name: '出手' }).click()
    await page.getByRole('button', { name: '出手' }).click()
    await page.getByRole('button', { name: '出手' }).click()
    await page.getByRole('button', { name: '按节奏完成' }).click()
    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.impact-chip').filter({ hasText: '训练表现' })).toBeVisible()
    await page.getByRole('button', { name: '继续行动' }).click()

    await page.locator('.action-journal').click()
    await expect(page.locator('.journal-panel')).toBeVisible()
    await page.locator('.journal-close').click()

    await dismissOpeningBrief(page)
    await page.getByRole('button', { name: /休息/ }).click()
    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.next-targets')).toBeVisible()
  })

  test('Day 2 森林异常会进入边界调查小游戏并写入结果', async ({ page, request }) => {
    await storyChoose(request, { event_id: 'ch1_d1_reading_clue', choice_id: 'ask_alice' })
    await playerAction(request, { kind: 'rest_until_next_day' })
    await playerAction(request, { kind: 'move_scene', scene_id: 'gigas_clearing' })

    await page.goto('/')
    await page.getByRole('button', { name: '追踪：森林忽然安静', exact: true }).click()
    await expect(page.locator('.probe-panel')).toBeVisible()
    for (const label of ['生成光素', '追踪静默', '束定距离']) {
      const fragment = page.locator('.fragment-chip').filter({ hasText: label })
      await fragment.click()
      await expect(fragment).toHaveClass(/selected/)
    }
    const together = page.locator('.stance-card').filter({ hasText: '叫上两人一起确认' })
    await together.click()
    await expect(together).toHaveClass(/selected/)
    const confirmProbe = page.getByRole('button', { name: '确认异常' })
    await expect(confirmProbe).toBeEnabled()
    await confirmProbe.click()

    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.impact-chip').filter({ hasText: '边界读数' })).toBeVisible()

    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.forest_anomaly_seen).toBe(1)
  })

  test('Day 1 隐瞒书页会在 Day 2 提供坦白并修复信任的关系回响', async ({ page, request }) => {
    await storyChoose(request, { event_id: 'ch1_d1_reading_clue', choice_id: 'keep_note' })
    await playerAction(request, { kind: 'rest_until_next_day' })
    await playerAction(request, { kind: 'move_scene', scene_id: 'gigas_clearing' })

    await page.goto('/')
    await page.getByRole('button', { name: '追踪：森林忽然安静', exact: true }).click()
    await expect(page.locator('.probe-panel')).toBeVisible()
    await page.getByRole('button', { name: /生成光素/ }).click()
    await page.getByRole('button', { name: /追踪静默/ }).click()
    await page.getByRole('button', { name: /束定距离/ }).click()
    const confessionStance = page.locator('.stance-card').filter({ hasText: '把昨天隐瞒的书页符号告诉爱丽丝' })
    await expect(confessionStance).toBeVisible()
    await confessionStance.click()
    await expect(confessionStance).toHaveClass(/selected/)
    const confirmProbe = page.getByRole('button', { name: '确认异常' })
    await expect(confirmProbe).toBeEnabled()
    await confirmProbe.click()

    const result = page.locator('.result-panel')
    await expect(result).toBeVisible()
    await expect(result).toContainText('她不喜欢被瞒着')
    await expect(result.locator('.result-section').filter({ hasText: '关系变化' })).toContainText('爱丽丝的信任 +4')
    await expect(result).toContainText('第二天静默线真正出现时向爱丽丝坦白')
    await expect(result).toContainText('留下的暗线')

    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.confessed_hidden_note_day2).toBe(1)
    expect(state.flags.forest_anomaly_seen).toBe(1)
    expect(state.relationships.alice.trust).toBe(4)
    expect(state.relationships.alice.tension).toBe(3)

    await page.getByRole('button', { name: '继续行动' }).click()
    await playerAction(request, { kind: 'rest_until_next_day' })
    await playerAction(request, { kind: 'move_scene', scene_id: 'gigas_clearing' })
    await page.reload()
    await page.getByRole('button', { name: '追踪：第三天：边界线前', exact: true }).click()
    await expect(page.locator('.verdict-panel')).toBeVisible()
    await expect(page.locator('.verdict-context')).toContainText('坦白的书页符号已经补进')
  })

  test('Day 3 边界最终选择会进入结局判定小游戏并收束章节', async ({ page, request }) => {
    await storyChoose(request, { event_id: 'ch1_d1_reading_clue', choice_id: 'ask_alice' })
    await playerAction(request, { kind: 'rest_until_next_day' })
    await storyChoose(request, { event_id: 'ch1_d2_forest_anomaly', choice_id: 'investigate_together' })
    await playerAction(request, { kind: 'rest_until_next_day' })
    await playerAction(request, { kind: 'move_scene', scene_id: 'gigas_clearing' })

    await page.goto('/')
    await page.getByRole('button', { name: '追踪：第三天：边界线前', exact: true }).click()
    await expect(page.locator('.verdict-panel')).toBeVisible()
    await page.getByRole('button', { name: /静默线真实存在/ }).click()
    await page.getByRole('button', { name: /尤吉欧往前半步/ }).click()
    await page.getByRole('button', { name: /风声在边界后回流/ }).click()
    await page.getByRole('button', { name: /越过边界，确认源头/ }).click()
    await page.getByRole('button', { name: '执行选择' }).click()

    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.impact-chip').filter({ hasText: '终局选择' })).toBeVisible()

    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.chapter_ending_id).toBe('cross')
    expect(state.flags.boundary_rule_touched).toBe(1)

    await page.getByRole('button', { name: '继续行动' }).click()
    await page.locator('.action-journal').click()
    await expect(page.locator('.journal-panel')).toContainText('第一月路线')
    await expect(page.locator('.month-plan-entry').filter({ hasText: '第 1 周：线索与信任' })).toBeVisible()
    await expect(page.locator('.milestone-row').filter({ hasText: 'Day 4-6' })).toBeVisible()
  })

  test('Day 4、Day 7 与 Day 12 事件成为可持续主线的日期闸门', async ({ request }) => {
    await storyChoose(request, { event_id: 'ch1_d1_reading_clue', choice_id: 'ask_alice' })
    await playerAction(request, { kind: 'rest_until_next_day' })
    await storyChoose(request, { event_id: 'ch1_d2_forest_anomaly', choice_id: 'investigate_together' })
    await playerAction(request, { kind: 'rest_until_next_day' })

    const blockedDay3 = await request.post(`${API}/api/player/action`, {
      data: { kind: 'rest_until_next_day' }
    })
    const blockedDay3Body = await blockedDay3.json()
    expect(blockedDay3Body.ok).toBeFalsy()
    expect(blockedDay3Body.missing[0].key).toBe('boundary_incident_resolved')

    await storyChoose(request, { event_id: 'ch1_d3_boundary_choice', choice_id: 'cross_boundary' })
    await restToDay(request, 4)

    const blockedDay4 = await request.post(`${API}/api/player/action`, {
      data: { kind: 'rest_until_next_day' }
    })
    const blockedDay4Body = await blockedDay4.json()
    expect(blockedDay4Body.ok).toBeFalsy()
    expect(blockedDay4Body.missing[0].key).toBe('month01_debrief_done')

    await storyChoose(request, { event_id: 'ch1_d4_after_boundary_debrief', choice_id: 'write_truth' })
    await restToDay(request, 7)

    const blockedDay7 = await request.post(`${API}/api/player/action`, {
      data: { kind: 'rest_until_next_day' }
    })
    const blockedDay7Body = await blockedDay7.json()
    expect(blockedDay7Body.ok).toBeFalsy()
    expect(blockedDay7Body.missing[0].key).toBe('month01_drill_done')

    await storyChoose(request, { event_id: 'ch1_d7_first_boundary_drill', choice_id: 'mark_safe_route' })
    await restToDay(request, 12)

    const blockedDay12 = await request.post(`${API}/api/player/action`, {
      data: { kind: 'rest_until_next_day' }
    })
    const blockedDay12Body = await blockedDay12.json()
    expect(blockedDay12Body.ok).toBeFalsy()
    expect(blockedDay12Body.missing[0].key).toBe('month01_village_trust')

    await storyChoose(request, { event_id: 'ch1_d12_village_trust', choice_id: 'public_patrol_board' })
    const day13 = await playerAction(request, { kind: 'rest_until_next_day' })
    expect(day13.state.day).toBe(13)
  })

  test('数据驱动活动选择可在游戏内直接完成并写入路线回响', async ({ page, request }) => {
    await setFlags(request, ['month01_drill_done'])
    await playerAction(request, { kind: 'set_day', day: 8 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'village_square' })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const action = page.locator('.interact-action[data-activity-id="village_patrol_board_review"]')
    await expect(action).toBeVisible()
    await action.click()

    await expect(page.locator('.event-panel')).toBeVisible()
    await expect(page.locator('.event-kicker')).toContainText('场景选择')
    const choice = page.locator('.event-choice').filter({ hasText: '邀请村民补充异常记录' })
    await expect(choice).toContainText('尤吉欧 信任 +2')
    await expect(choice).toContainText('尤吉欧会记住')
    await choice.click()

    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.result-panel')).toContainText('调查开始属于整个村子')
    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.village_patrol_board_reviewed).toBe(1)
    expect(state.flags.village_notes_invited).toBe(1)
  })

  test('北境短程巡查可判断敌意、消耗资源并获得累计标记', async ({ page, request }) => {
    await setFlags(request, ['forest_anomaly_seen'])
    await playerAction(request, { kind: 'move_scene', scene_id: 'north_gate' })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const patrolAction = page.locator('.interact-action[data-activity-id="north_gate_boundary_patrol"]')
    await expect(patrolAction).toBeVisible()
    await expect(patrolAction).toContainText('短程探索')
    await patrolAction.click()

    await expect(page.locator('.patrol-panel')).toBeVisible()
    await page.getByRole('button', { name: /架势格挡/ }).click()
    await page.getByRole('button', { name: /神圣术·束光/ }).click()
    await page.getByRole('button', { name: /侧步突进/ }).click()
    await expect(page.locator('.patrol-summary')).toContainText('无伤完成巡查')
    await page.getByRole('button', { name: '带着记录返回' }).click()

    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.impact-chip').filter({ hasText: '巡查评价' })).toBeVisible()
    await expect(page.locator('.impact-chip').filter({ hasText: '边境标记' })).toContainText('+3')
    await expect(page.locator('.impact-chip').filter({ hasText: '神圣力变化' })).toContainText('-8')

    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.boundary_marks).toBe(3)
    expect(state.flags.boundary_patrol_clears).toBe(1)
    expect(state.player.hp).toBe(100)
    expect(state.player.mp).toBe(92)
    expect(state.player.stamina).toBe(86)
  })

  test('Day 24 远征准备显示 NPC 关注和选择后果预览', async ({ page, request }) => {
    await advanceToExpeditionPrep(request)
    await page.goto('/')

    await expect(page.locator('.quest-tracker')).toContainText('同伴主动事件')
    await expect(page.locator('.quest-tracker')).toContainText('远征包')
    await page.locator('.nearby-enter-btn').click()
    await page.locator('.interact-action[data-action-id="story:ch1_d24_expedition_pack"]').click()
    await expect(page.locator('.event-panel')).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '第二月撤退路线更稳定' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '第二月调查范围更远' })).toBeVisible()
  })

  test('Day 28 北门前夜显示第二月路线后果预览', async ({ page, request }) => {
    await advanceToMonthGate(request)
    await page.goto('/')

    await expect(page.locator('.quest-tracker')).toContainText('同伴主动事件')
    await expect(page.locator('.quest-tracker')).toContainText('北门前复核第一月承诺')
    await page.locator('.nearby-enter-btn').click()
    await page.locator('.interact-action[data-activity-id="north_gate_month_end_vigil"]').click()
    await expect(page.locator('.event-panel')).toBeVisible()
    await page.locator('.event-choice').filter({ hasText: '让爱丽丝复核记录与承诺' }).click()
    await expect(page.locator('.result-panel')).toBeVisible()
    await page.getByRole('button', { name: '继续行动' }).click()

    if (!(await page.locator('.event-panel').isVisible())) {
      await expect(page.getByRole('button', { name: '追踪：第三十天：北门前夜', exact: true })).toBeVisible()
      await page.getByRole('button', { name: '追踪：第三十天：北门前夜', exact: true }).click()
      await expect(page.locator('.event-panel')).toBeVisible()
    }
    await expect(page.locator('.event-kicker')).toContainText('第一月路线抉择')
    await expect(page.locator('.event-choice').filter({ hasText: '第二月村内支持更稳' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '第二月远征推进更快' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '第二月调查更隐蔽' })).toBeVisible()
    await page.locator('.event-choice').filter({ hasText: '第二月村内支持更稳' }).click()
    await expect(page.locator('.result-kicker')).toContainText('第一月收束')
    await expect(page.locator('.impact-chip').filter({ hasText: '第一月路线' })).toBeVisible()
  })

  test('Day 31 第二月入口按第一月路线解锁单一路线确认', async ({ page, request }) => {
    await advanceToDay31OrderRoute(request)
    await page.goto('/')

    await expect(page.getByRole('button', { name: /追踪：.*第三十一天/ })).toBeVisible()
    await page.getByRole('button', { name: /追踪：.*第三十一天/ }).click()
    await expect(page.locator('.event-panel')).toBeVisible()
    await expect(page.locator('.event-choice')).toHaveCount(1)
    await expect(page.locator('.event-choice').filter({ hasText: '第二月村内支持更稳' })).toBeVisible()
    await page.locator('.event-choice').filter({ hasText: '第二月村内支持更稳' }).click()
    await expect(page.locator('.result-panel')).toBeVisible()

    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.month02_day31_entry_done).toBe(1)
    expect(state.flags.month02_route_order).toBe(1)

    await page.locator('.result-primary').click()
    const monthTwoPlanRequest = page.waitForRequest((req) =>
      req.url().includes('/api/story/month_plan') && req.url().includes('month_id=month_02')
    )
    await page.locator('.action-journal').click()
    await monthTwoPlanRequest
    await expect(page.locator('.journal-panel')).toBeVisible()
    await expect(page.locator('.month-plan-entry').first()).toBeVisible()
  })

  test('Day 32 第二月稳守路线要求玩家明确选择并解除日期闸门', async ({ page, request }) => {
    await setFlags(request, ['month02_day31_entry_done', 'month02_route_order'])
    await playerAction(request, { kind: 'set_day', day: 32 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'reading_hall' })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const action = page.locator('.interact-action[data-activity-id="church_month02_briefing"]')
    await expect(action).toBeVisible()
    await action.click()
    await expect(page.locator('.event-panel')).toBeVisible()
    const choice = page.locator('.event-choice').filter({ hasText: '公开完整轮值与上报格式' })
    await expect(choice).toContainText('爱丽丝 信任 +2')
    await choice.click()
    await expect(page.locator('.result-panel')).toContainText('村子共同承担')

    const afterChoice = await (await request.get(`${API}/api/state`)).json()
    expect(afterChoice.flags.month02_order_briefing_done).toBe(1)
    expect(afterChoice.flags.month02_order_open_rotation).toBe(1)

    const advanced = await playerAction(request, { kind: 'rest_until_next_day' })
    expect(advanced.state.day).toBe(33)
  })

  test('Day 39 quiet route frequency crosscheck smoke', async ({ page, request }) => {
    await setFlags(request, [
      'month02_day31_entry_done',
      'month02_route_quiet',
      'month02_quiet_record_done'
    ])
    await playerAction(request, { kind: 'set_day', day: 39 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'reading_hall' })

    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.day).toBe(39)
    const intent = state.npc_intents.find((item) => item.id === 'alice_conducts_quiet_frequency_crosscheck')
    expect(intent).toBeTruthy()
    expect(intent.title).toContain('艾琳')
    expect(intent.scene_id).toBe('reading_hall')
    expect(intent.action).toEqual({
      type: 'scene_activity',
      activity_id: 'reading_hall_quiet_frequency_crosscheck'
    })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const action = page.locator('.interact-action[data-activity-id="reading_hall_quiet_frequency_crosscheck"]')
    await expect(action).toBeVisible()
    await expect(action).toContainText('爱丽丝要复核静默线频率')
    await action.click()
    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.result-panel')).toContainText('更接近北门')

    const after = await (await request.get(`${API}/api/state`)).json()
    expect(after.flags.month02_quiet_frequency_crosscheck_done).toBe(1)
    expect(after.flags.month02_quiet_frequency_crosschecked).toBe(1)
  })

  test('Day 46 Week07 shared anomaly convergence smoke', async ({ page, request }) => {
    await setFlags(request, [
      'month02_day31_entry_done',
      'month02_route_order',
      'month02_order_patrol_standby_done'
    ])
    await playerAction(request, { kind: 'set_day', day: 46 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'reading_hall' })

    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.day).toBe(46)
    const intent = state.npc_intents.find((item) => item.id === 'alice_calls_anomaly_convergence')
    expect(intent).toBeTruthy()
    expect(intent.scene_id).toBe('reading_hall')
    expect(intent.action).toEqual({
      type: 'scene_activity',
      activity_id: 'boundary_anomaly_convergence'
    })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const convergenceAction = page.locator('.interact-action[data-activity-id="boundary_anomaly_convergence"]')
    await expect(convergenceAction).toBeVisible()
    await convergenceAction.click()
    await expect(page.locator('.event-panel')).toBeVisible()
    const convergenceChoice = page.locator('.event-choice').filter({ hasText: '共同异常地图交给村务复核' })
    await expect(convergenceChoice).toContainText('爱丽丝 信任 +3')
    await convergenceChoice.click()
    await expect(page.locator('.result-panel')).toBeVisible()

    const after = await (await request.get(`${API}/api/state`)).json()
    expect(after.flags.month02_anomaly_convergence_done).toBe(1)
    expect(after.flags.month02_anomaly_source_documented).toBe(1)
    expect(after.flags.month02_shared_map_published).toBe(1)

    await page.locator('.result-primary').click()
    await expect(page.locator('.quest-tracker')).toContainText('\u7b2c\u4e8c\u6708\u540e\u6bb5')
    await expect(page.locator('.quest-tracker')).not.toContainText('\u7ec6\u96e8\u521a\u505c')
  })

  test('Day 47 到 Day 53 公开地图路线可完成并进入第三月', async ({ page, request }) => {
    await setFlags(request, [
      'month02_anomaly_convergence_done',
      'month02_shared_map_published'
    ])
    await playerAction(request, { kind: 'set_day', day: 47 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'village_square' })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const hearingAction = page.locator('.interact-action[data-activity-id="village_shared_map_hearing"]')
    await expect(hearingAction).toBeVisible()
    await expect(hearingAction).toContainText('共同异常地图')
    await hearingAction.click()

    await expect(page.locator('.event-panel')).toBeVisible()
    const testimony = page.locator('.event-choice').filter({ hasText: '邀请村民按亲历顺序补充证词' })
    await expect(testimony).toContainText('爱丽丝 信任 +2')
    await expect(testimony).toContainText('Day 53 正式听证')
    await testimony.click()
    await expect(page.locator('.result-panel')).toContainText('公开地图因此不再只是三个人的结论')

    let state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.month02_shared_map_hearing_done).toBe(1)
    expect(state.flags.month02_village_testimony_gathered).toBe(1)

    await playerAction(request, { kind: 'set_day', day: 53 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'reading_hall' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const resultAction = page.locator('.interact-action').filter({ hasText: '爱丽丝请你在书库写下第二月的答案' })
    await expect(resultAction).toBeVisible()
    await expect(resultAction).toContainText('第二月的答案')
    await resultAction.click()

    await expect(page.locator('.event-choice')).toHaveCount(2)
    await expect(page.locator('.event-choice').filter({ hasText: '举行正式边界听证' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '只公开警告与退路' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '继续三人源头追查' })).toHaveCount(0)
    await page.locator('.event-choice').filter({ hasText: '举行正式边界听证' }).click()
    await expect(page.locator('.result-panel')).toContainText('共同执行的边界规则')

    state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.month02_second_month_result_done).toBe(1)
    expect(state.flags.month02_result_formal_hearing).toBe(1)
    expect(state.flags.month03_route_public_boundary).toBe(1)
  })


  test('Day 54 到 Day 61 正式听证尾声可落地第三月准则', async ({ page, request }) => {
    await setFlags(request, [
      'month02_second_month_result_done',
      'month02_result_formal_hearing'
    ])
    await playerAction(request, { kind: 'set_day', day: 54 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'village_square' })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const followthrough = page.locator('.interact-action[data-activity-id="village_formal_hearing_followthrough"]')
    await expect(followthrough).toBeVisible()
    await expect(followthrough).toContainText('正式听证')
    await followthrough.click()

    const clerks = page.locator('.event-choice').filter({ hasText: '建立轮值记录与双人复核' })
    await expect(clerks).toContainText('爱丽丝 信任 +3')
    await expect(clerks).toContainText('Day 61')
    await clerks.click()
    await expect(page.locator('.result-panel')).toContainText('任何异常都必须由两个人签名')

    let state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.month02_tail_feedback_done).toBe(1)
    expect(state.flags.month02_formal_hearing_followthrough_done).toBe(1)
    expect(state.flags.month02_rotating_clerks_ready).toBe(1)

    await playerAction(request, { kind: 'set_day', day: 61 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'north_gate' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const departure = page.locator('.interact-action').filter({ hasText: '第三月准则' })
    await expect(departure).toBeVisible()
    await departure.click()

    await expect(page.locator('.event-choice')).toHaveCount(2)
    const council = page.locator('.event-choice').filter({ hasText: '启动公开边界议事试行' })
    await expect(council).toContainText('第三月公开议事路线启动')
    await council.click()
    await expect(page.locator('.result-panel')).toContainText('公开议事试行')

    state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.month02_tail_resolved).toBe(1)
    expect(state.flags.month03_departure_ready).toBe(1)
    expect(state.flags.month03_public_council_trial).toBe(1)
  })


  test('Day 62 到 Day 69 第三月资源投入会真实扣除并改变路线测试', async ({ page, request }) => {
    await setFlags(request, [
      'month03_departure_ready',
      'month03_public_council_trial'
    ])
    await playerAction(request, { kind: 'set_day', day: 62 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'village_square' })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const allocation = page.locator('.interact-action[data-activity-id="village_third_month_support_allocation"]')
    await expect(allocation).toBeVisible()
    await allocation.click()

    const sacredSignal = page.locator('.event-choice').filter({ hasText: '编织神圣术信号与远距回报' })
    await expect(sacredSignal).toContainText('体力 -3')
    await expect(sacredSignal).toContainText('神圣力 -10')
    await expect(sacredSignal).toContainText('Day 69')
    await sacredSignal.click()
    await expect(page.locator('.result-panel')).toContainText('神圣力明显下降')

    let state = await (await request.get(`${API}/api/state`)).json()
    expect(state.player.stamina).toBe(97)
    expect(state.player.mp).toBe(90)
    expect(state.flags.month03_preparation_done).toBe(1)
    expect(state.flags.month03_public_sacred_signal).toBe(1)

    await page.locator('.result-primary').click()
    await page.locator('.action-journal').click()
    await expect(page.locator('.journal-panel')).toContainText('第三月：边界方法第一次受验')
    await expect(page.locator('.journal-panel')).toContainText('公开协作族')
    await page.locator('.journal-close').click()

    await playerAction(request, { kind: 'set_day', day: 69 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'north_gate' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const routeTest = page.locator('.interact-action').filter({ hasText: '第一次资源投入带到北门测试' })
    await expect(routeTest).toBeVisible()
    await routeTest.click()

    await expect(page.locator('.event-choice')).toHaveCount(2)
    await expect(page.locator('.event-choice').filter({ hasText: '展开完整神圣术信号网' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '只启用两处信号' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '把人力轮值投入' })).toHaveCount(0)
    await page.locator('.event-choice').filter({ hasText: '只启用两处信号' }).click()
    await expect(page.locator('.result-panel')).toContainText('第三枚保持熄灭')

    state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.month03_route_test_done).toBe(1)
    expect(state.flags.month03_signal_reserve_saved).toBe(1)
  })


  test('Day 76 到 Day 83 会读取路线结果、提供资源恢复并收束第三月阶段', async ({ page, request }) => {
    await setFlags(request, [
      'month03_route_test_done',
      'month03_signal_reserve_saved'
    ])
    await playerAction(request, { kind: 'set_day', day: 76 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'village_square' })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const feedback = page.locator('.interact-action[data-activity-id="village_third_month_route_feedback"]')
    await expect(feedback).toBeVisible()
    await feedback.click()
    await page.locator('.event-choice').filter({ hasText: '把覆盖范围与资源边界写进公开报告' }).click()
    await expect(page.locator('.result-panel')).toContainText('公开协作因此更诚实')

    let state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.month03_feedback_done).toBe(1)
    expect(state.flags.month03_public_feedback_done).toBe(1)

    await playerAction(request, { kind: 'set_day', day: 78 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'home_hearth' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const recovery = page.locator('.interact-action[data-activity-id="home_third_month_recovery_debrief"]')
    await expect(recovery).toBeVisible()
    await recovery.click()
    const recoverMp = page.locator('.event-choice').filter({ hasText: '优先恢复神圣力' })
    await expect(recoverMp).toContainText('神圣力 +12')
    await expect(recoverMp).toContainText('体力 -3')
    await recoverMp.click()
    await expect(page.locator('.result-panel')).toContainText('神圣力恢复到可以应急')

    await playerAction(request, { kind: 'set_day', day: 83 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'reading_hall' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const stage = page.locator('.interact-action').filter({ hasText: '第三月下一阶段' })
    await expect(stage).toBeVisible()
    await stage.click()
    await expect(page.locator('.event-choice')).toHaveCount(2)
    await expect(page.locator('.event-choice').filter({ hasText: '扩大公开协作覆盖范围' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '先保护公开协作安全余量' })).toBeVisible()
    await page.locator('.event-choice').filter({ hasText: '扩大公开协作覆盖范围' }).click()
    await expect(page.locator('.result-panel')).toContainText('公开协作覆盖')

    state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.month03_stage_resolved).toBe(1)
    expect(state.flags.month03_public_expansion).toBe(1)

    await page.locator('.result-primary').click()
    await page.locator('.action-journal').click()
    await expect(page.locator('.journal-panel')).toContainText('公开协作进入扩大覆盖阶段')
    await expect(page.locator('.journal-panel')).toContainText('当前承诺 / 紧张点')
  })


  test('Day 90 到 Day 103 会把第三月后果变成可重复活动与阶段结算', async ({ page, request }) => {
    await setFlags(request, [
      'month03_stage_resolved',
      'month03_public_expansion'
    ])
    await playerAction(request, { kind: 'set_day', day: 90 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'village_square' })

    await page.goto('/')
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const practice = page.locator('.interact-action[data-activity-id="village_third_month_consequence_practice"]')
    await expect(practice).toBeVisible()
    await practice.click()
    await page.locator('.event-choice').filter({ hasText: '带轮值人员完成一次短段守望' }).click()
    await expect(page.locator('.result-panel')).toContainText('轮值人员完成一段最短守望')

    await playerAction(request, { kind: 'move_scene', scene_id: 'home_hearth' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const resourceStatus = page.locator('.interact-action[data-activity-id="home_third_month_resource_status"]')
    await expect(resourceStatus).toBeVisible()
    await resourceStatus.click()
    await page.locator('.event-choice').filter({ hasText: '优先恢复体力' }).click()
    await expect(page.locator('.result-panel')).toContainText('恢复后的体力')

    await playerAction(request, { kind: 'set_day', day: 94 })
    await playerAction(request, { kind: 'rest_until_next_day' })
    await playerAction(request, { kind: 'move_scene', scene_id: 'reading_hall' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const review = page.locator('[data-action-id="intent:alice_calls_third_month_consequence_review"]')
    await expect(review).toBeVisible()
    await review.click()
    await expect(page.locator('.event-choice')).toHaveCount(2)
    await page.locator('.event-choice').filter({ hasText: '让村务轮值真正参与边界判断' }).click()
    await expect(page.locator('.result-panel')).toContainText('邀请村务人员')

    await playerAction(request, { kind: 'set_day', day: 96 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'village_square' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const followup = page.locator('.interact-action[data-activity-id="village_third_month_commitment_followup"]')
    await expect(followup).toBeVisible()
    await followup.click()
    await page.locator('.event-choice').filter({ hasText: '邀请轮值人员复述疑问' }).click()
    await expect(page.locator('.result-panel')).toContainText('阶段决定变成一次短而明确的回访')

    await playerAction(request, { kind: 'set_day', day: 103 })
    await playerAction(request, { kind: 'move_scene', scene_id: 'home_hearth' })
    await page.reload()
    await dismissOpeningBrief(page)
    await page.locator('.nearby-enter-btn').click()
    const settlement = page.locator('[data-action-id="intent:eugeo_calls_third_month_boundary_decision"]')
    await expect(settlement).toBeVisible()
    await settlement.click()
    await expect(page.locator('.event-choice')).toHaveCount(2)
    await page.locator('.event-choice').filter({ hasText: '让村务轮值承担一小段守望' }).click()
    await expect(page.locator('.result-panel')).toContainText('第一次有人没有逞强')

    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.month03_day103_result_done).toBe(1)
    expect(state.flags.month03_public_steward_trial).toBe(1)
  })

})
