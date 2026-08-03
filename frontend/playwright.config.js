// @ts-check
import { existsSync } from 'node:fs'
import { defineConfig, devices } from '@playwright/test'

const backendPython = process.env.PYTHON_BIN || (process.platform === 'win32'
  ? '..\\.conda\\uw-runtime\\python.exe'
  : '.venv/bin/python')

const browserChannel = process.env.PLAYWRIGHT_CHANNEL || (
  process.platform === 'darwin' && existsSync('/Applications/Google Chrome.app')
    ? 'chrome'
    : ''
)

/**
 * E2E：默认只起 Vite；世界状态需后端时可先启动 uvicorn 再跑测试。
 * CI 中可设 CI=1 强制新起 dev 服务。
 */
export default defineConfig({
  testDir: 'e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: 'list',
  use: {
    ...devices['Desktop Chrome'],
    ...(browserChannel ? { channel: browserChannel } : {}),
    baseURL: 'http://127.0.0.1:3000',
    trace: 'on-first-retry'
  },
  webServer: [
    {
      command: `${backendPython} -m uvicorn app.main:app --host 127.0.0.1 --port 8765`,
      cwd: '../backend',
      url: 'http://127.0.0.1:8765/api/health',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000
    },
    {
      command: 'npm run dev',
      url: 'http://127.0.0.1:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000
    }
  ]
})
