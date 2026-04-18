import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Court Automation Suite E2E tests.
 *
 * Targets:
 *   Frontend:  http://localhost:3000  (Next.js dev server)
 *   Backend:   http://localhost:8000  (FastAPI)
 *
 * Run:
 *   npx playwright test               # headless, all browsers
 *   npx playwright test --headed      # visible browser
 *   npx playwright test --project=chromium  # single browser
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: false,   // court portal tests are stateful — run sequentially
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  timeout: 60_000,        // 60 s per test (court pages can be slow)
  expect: { timeout: 15_000 },

  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['list'],
  ],

  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',   // #20 requirement: screenshots on failure
    video: 'retain-on-failure',
    trace: 'on-first-retry',
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 7'] },
    },
  ],
});
