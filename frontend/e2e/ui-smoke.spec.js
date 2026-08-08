import { test, expect } from '@playwright/test'

const API = process.env.E2E_API_URL || `http://127.0.0.1:${process.env.E2E_BACKEND_PORT || 8765}`

async function resetWorld(request) {
  const response = await request.post(`${API}/api/reset`)
  expect(response.ok()).toBeTruthy()
}

async function expectCoreLayout(page) {
  await expect(page.locator('.phaser-host canvas')).toBeVisible({ timeout: 30_000 })
  await expect(page.locator('.quest-tracker')).toBeVisible()
  await expect(page.locator('.action-hotbar')).toBeVisible()
  await expect(page.getByText('见习记录员', { exact: true })).toHaveCount(0)
  await expect(page.getByText('桐人', { exact: true }).first()).toBeVisible()

  const metrics = await page.evaluate(() => ({
    viewport: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    header: document.querySelector('.field-header')?.getBoundingClientRect().toJSON(),
    quest: document.querySelector('.quest-tracker')?.getBoundingClientRect().toJSON(),
    hotbar: document.querySelector('.action-hotbar')?.getBoundingClientRect().toJSON()
  }))
  expect(metrics.scrollWidth).toBeLessThanOrEqual(metrics.viewport + 1)

  const overlaps = (a, b) => {
    if (!a || !b) return false
    const width = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x))
    const height = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y))
    return width * height > 1
  }
  expect(overlaps(metrics.header, metrics.quest)).toBeFalsy()
  expect(overlaps(metrics.quest, metrics.hotbar)).toBeFalsy()
}

test.describe('current UI smoke', () => {
  test.beforeEach(async ({ request }) => {
    await resetWorld(request)
  })

  test('desktop opening and field use the consolidated canon-facing copy', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await page.goto('/')
    await expect(page.getByRole('heading', { name: '卢利特村', level: 1 })).toBeVisible()
    await expect(page.getByText('UNDERWORLD · 序章').first()).toBeVisible()
    await expect(page.getByRole('button', { name: '前往巨神树' })).toBeVisible()
    await expect(page.getByText('点击地图上的金色标记移动，抵达后选择行动。')).toBeVisible()
    await page.getByRole('button', { name: '前往巨神树' }).click()
    await expectCoreLayout(page)
  })

  test('touch-sized viewport keeps the first objective reachable', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto('/')
    await page.getByRole('button', { name: '前往巨神树' }).click()
    await expectCoreLayout(page)
    await expect(page.locator('.quest-primary-btn')).toBeVisible()
  })
})
