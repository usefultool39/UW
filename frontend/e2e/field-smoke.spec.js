// @ts-check
import { test, expect } from '@playwright/test'

test.describe('开放世界 Tab', () => {
  test('默认进入地图主界面后画布容器可见', async ({ page }) => {
    await page.goto('/')
    const host = page.locator('.phaser-host')
    await expect(host).toBeVisible()
    // Phaser 注入 canvas；无后端时可能无地图内容，但宿主应存在
    await expect(host.locator('canvas')).toBeVisible({ timeout: 30_000 })
  })
})
