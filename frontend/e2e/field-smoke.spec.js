// @ts-check
import { test, expect } from '@playwright/test'

const API = 'http://127.0.0.1:8765'

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

async function dismissOpeningBrief(page) {
  const btn = page.getByRole('button', { name: '开始行动' })
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
    await page.screenshot({ path: '../runs/quality_gate_desktop.png', fullPage: false })

    await page.setViewportSize({ width: 390, height: 844 })
    await page.reload()
    await expectCanvasNonBlank(page)
    await expectNoCoreOverlap(page)
    await page.screenshot({ path: '../runs/quality_gate_mobile.png', fullPage: false })
  })

  test('读书、午餐、训练、日志和 Day 2 预告可走通', async ({ page, request }) => {
    await playerAction(request, { kind: 'move_scene', scene_id: 'reading_hall' })
    await page.goto('/')
    await dismissOpeningBrief(page)

    await page.locator('.nearby-enter-btn').click()
    await page.locator('.interact-action').filter({ hasText: '拼接刻印术' }).click()
    await expect(page.locator('.reading-panel')).toBeVisible()
    await page.getByRole('button', { name: /鸟声消失/ }).click()
    await page.getByRole('button', { name: /静默线/ }).click()
    await page.getByRole('button', { name: /北境律令/ }).click()
    await page.getByRole('button', { name: '记下这条线索' }).click()
    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.impact-chip').filter({ hasText: '阅读线索' })).toBeVisible()
    await page.getByRole('button', { name: '继续行动' }).click()

    await page.locator('.nearby-enter-btn').click()
    await page.locator('.interact-action').filter({ hasText: '调查边界记录' }).click()
    await expect(page.locator('.event-panel')).toBeVisible()
    await page.locator('.event-choice').filter({ hasText: '把记录告诉艾琳' }).click()
    await expect(page.locator('.result-panel')).toBeVisible()
    await page.getByRole('button', { name: '继续行动' }).click()

    await page.locator('.nearby-enter-btn').click()
    await page.locator('.interact-action[data-action-id="church_ask_alice_lunch"]').click()
    await expect(page.locator('.meal-panel')).toBeVisible()
    await page.getByRole('button', { name: /给尤里多留一份干粮/ }).click()
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
    await page.locator('.event-btn').filter({ hasText: '森林忽然安静' }).click()
    await expect(page.locator('.probe-panel')).toBeVisible()
    await page.getByRole('button', { name: /生成光素/ }).click()
    await page.getByRole('button', { name: /追踪静默/ }).click()
    await page.getByRole('button', { name: /束定距离/ }).click()
    await page.getByRole('button', { name: /叫上两人一起确认/ }).click()
    await page.getByRole('button', { name: '确认异常' }).click()

    await expect(page.locator('.result-panel')).toBeVisible()
    await expect(page.locator('.impact-chip').filter({ hasText: '边界读数' })).toBeVisible()

    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.flags.forest_anomaly_seen).toBe(1)
  })

  test('Day 3 边界最终选择会进入结局判定小游戏并收束章节', async ({ page, request }) => {
    await storyChoose(request, { event_id: 'ch1_d1_reading_clue', choice_id: 'ask_alice' })
    await playerAction(request, { kind: 'rest_until_next_day' })
    await storyChoose(request, { event_id: 'ch1_d2_forest_anomaly', choice_id: 'investigate_together' })
    await playerAction(request, { kind: 'rest_until_next_day' })
    await playerAction(request, { kind: 'move_scene', scene_id: 'gigas_clearing' })

    await page.goto('/')
    await page.locator('.event-btn').filter({ hasText: '第三天：边界线前' }).click()
    await expect(page.locator('.verdict-panel')).toBeVisible()
    await page.getByRole('button', { name: /静默线真实存在/ }).click()
    await page.getByRole('button', { name: /尤里往前半步/ }).click()
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

  test('Day 24 远征准备显示 NPC 关注和选择后果预览', async ({ page, request }) => {
    await advanceToExpeditionPrep(request)
    await page.goto('/')

    await expect(page.locator('.quest-tracker')).toContainText('NPC 关注')
    await expect(page.locator('.quest-tracker')).toContainText('远征包')
    await expect(page.locator('.event-btn').filter({ hasText: '第二十四天：远征包' })).toBeVisible()

    await page.locator('.event-btn').filter({ hasText: '第二十四天：远征包' }).click()
    await expect(page.locator('.event-panel')).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '第二月撤退路线更稳定' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '第二月调查范围更远' })).toBeVisible()
  })

  test('Day 28 北门前夜显示第二月路线后果预览', async ({ page, request }) => {
    await advanceToMonthGate(request)
    await page.goto('/')

    await expect(page.locator('.event-btn').filter({ hasText: '第三十天：北门前夜' })).toBeVisible()
    await page.locator('.event-btn').filter({ hasText: '第三十天：北门前夜' }).click()
    await expect(page.locator('.event-panel')).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '第二月村内支持更稳' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '第二月远征推进更快' })).toBeVisible()
    await expect(page.locator('.event-choice').filter({ hasText: '第二月调查更隐蔽' })).toBeVisible()
  })
})
