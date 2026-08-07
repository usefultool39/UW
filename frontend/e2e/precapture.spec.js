import { test, expect } from '@playwright/test'

const API = process.env.E2E_API_URL || `http://127.0.0.1:${process.env.E2E_BACKEND_PORT || 8765}`

async function resetWorld(request) {
  const response = await request.post(`${API}/api/reset`)
  expect(response.ok()).toBeTruthy()
  return response.json()
}

async function playerAction(request, body) {
  const response = await request.post(`${API}/api/player/action`, { data: body })
  expect(response.ok()).toBeTruthy()
  const payload = await response.json()
  expect(payload.ok).toBeTruthy()
  return payload
}

async function moveToEvent(request, tileX, tileY) {
  return playerAction(request, {
    kind: 'move_map',
    map_id: 'novice_open',
    tile_x: tileX,
    tile_y: tileY
  })
}

async function openNearbyStoryEvent(page, eventId, panelSelector = '.event-panel') {
  await page.locator('.nearby-enter-btn').click()
  const action = page.locator(`.interact-action[data-action-id="story:${eventId}"]`)
  await expect(action).toHaveCount(1)
  await action.click()
  await expect(page.locator(panelSelector)).toBeVisible()
}

async function chooseFirstStoryOption(page) {
  const choices = page.locator('.event-choice')
  await expect(choices).not.toHaveCount(0)
  await choices.first().click()
  await expect(page.locator('.result-panel')).toBeVisible()
  await page.locator('.result-primary').click()
}

async function reloadAt(page, request, eventId, tileX, tileY) {
  await moveToEvent(request, tileX, tileY)
  await page.reload()
  await expect(page.locator('.phaser-host canvas')).toBeVisible({ timeout: 30_000 })
  await openNearbyStoryEvent(page, eventId)
}

test.describe('Pre-Capture authored route', () => {
  test.setTimeout(150_000)

  test('new game completes N01-N10 through the story UI', async ({ page, request }) => {
    await resetWorld(request)

    const startedAt = Date.now()
    await page.goto('/')
    await page.locator('.opening-primary').click()
    expect(Date.now() - startedAt).toBeLessThan(60_000)

    await moveToEvent(request, 54, 22)
    await page.reload()
    await expect(page.locator('.phaser-host canvas')).toBeVisible({ timeout: 30_000 })
    await openNearbyStoryEvent(page, 'ch1pc_n01_rulid_daily')
    await chooseFirstStoryOption(page)

    await reloadAt(page, request, 'ch1pc_n02_gigas_calling', 54, 22)
    await chooseFirstStoryOption(page)
    await reloadAt(page, request, 'ch1pc_n03_talk_index_end_mountains', 11, 27)
    await chooseFirstStoryOption(page)

    const dayTwo = await playerAction(request, { kind: 'rest_until_next_day' })
    expect(dayTwo.day_transition?.to_day).toBe(2)
    await reloadAt(page, request, 'ch1pc_n04_travel_to_end_mountains', 67, 24)
    await chooseFirstStoryOption(page)
    await reloadAt(page, request, 'ch1pc_n05_encounter_dark_territory_injured', 67, 24)
    await chooseFirstStoryOption(page)
    await reloadAt(page, request, 'ch1pc_n06_alice_crosses_boundary', 67, 24)
    await chooseFirstStoryOption(page)
    await reloadAt(page, request, 'ch1pc_n07_return_to_rulid', 67, 24)
    await chooseFirstStoryOption(page)

    await playerAction(request, { kind: 'rest_until_next_day' })
    await reloadAt(page, request, 'ch1pc_n08_knights_arrive_village', 24, 24)
    await chooseFirstStoryOption(page)
    await reloadAt(page, request, 'ch1pc_n09_alice_farewell', 24, 24)
    await chooseFirstStoryOption(page)
    await moveToEvent(request, 67, 24)
    await page.reload()
    await expect(page.locator('.phaser-host canvas')).toBeVisible({ timeout: 30_000 })
    await openNearbyStoryEvent(page, 'ch1pc_n10_alice_captured', '.verdict-panel')
    await expect(page.locator('.evidence-card')).toHaveCount(6)
    await page.locator('.evidence-card').nth(0).click()
    await page.locator('.evidence-card').nth(1).click()
    await page.locator('.evidence-card').nth(2).click()
    await page.locator('.verdict-actions button').nth(1).click()
    await expect(page.locator('.result-panel')).toBeVisible()

    const available = await (await request.get(`${API}/api/story/available_events`)).json()
    expect(available.events).toEqual([])
    const state = await (await request.get(`${API}/api/state`)).json()
    expect(state.chapter_ending_id).toBe('alice_captured')
    expect(state.day).toBe(3)
  })

  test('first authored interaction is reachable on a touch-sized viewport', async ({ page, request }) => {
    await resetWorld(request)
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto('/')
    await page.locator('.opening-primary').click()
    await moveToEvent(request, 54, 22)
    await page.reload()
    await expect(page.locator('.phaser-host canvas')).toBeVisible({ timeout: 30_000 })
    await openNearbyStoryEvent(page, 'ch1pc_n01_rulid_daily')
    await expect(page.locator('.event-choice').first()).toBeVisible()
  })
})
