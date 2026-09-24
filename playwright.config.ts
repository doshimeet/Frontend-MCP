import { defineConfig, devices } from '@playwright/test';

/**
 * Enterprise Playwright Configuration
 * Leverages system Edge browser (channel: 'msedge') with graceful fallback to Chrome/Chromium
 * for corporate workstation compliance and headless CI/CD execution.
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['list']
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    headless: true,
  },
  projects: [
    {
      name: 'Microsoft Edge (Corporate System Browser)',
      use: {
        ...devices['Desktop Edge'],
        channel: process.env.PLAYWRIGHT_BROWSER_CHANNEL || 'msedge',
      },
    },
    {
      name: 'Google Chrome (System Fallback)',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
