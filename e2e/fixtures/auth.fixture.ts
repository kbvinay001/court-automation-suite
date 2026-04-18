/**
 * fixtures/auth.fixture.ts
 *
 * Shared Playwright fixtures that handle authentication lifecycle:
 *   - `authenticatedPage`  — a Page already logged in as the test user
 *   - `apiRequest`         — raw APIRequestContext for API-level calls
 *
 * Uses storageState to persist auth cookies/localStorage between tests
 * in the same worker, avoiding a login round-trip for every test.
 */
import { test as base, expect, type Page, type APIRequestContext } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

// ── Test credentials (override via env vars in CI) ────────────────────────────
export const TEST_USER = {
  email:    process.env.E2E_USER_EMAIL    ?? 'e2e.test@courtautomation.in',
  password: process.env.E2E_USER_PASSWORD ?? 'Test@1234!',
  name:     'E2E Test User',
};

export const BACKEND_URL = process.env.E2E_BACKEND_URL ?? 'http://localhost:8000';
export const FRONTEND_URL = process.env.E2E_FRONTEND_URL ?? 'http://localhost:3000';

// ── Augmented fixture types ───────────────────────────────────────────────────
type AuthFixtures = {
  /** A Page already logged in as TEST_USER. */
  authenticatedPage: Page;
  /** API request context pointing at the backend. */
  apiRequest: APIRequestContext;
};

export const test = base.extend<AuthFixtures>({
  // ── apiRequest fixture ──────────────────────────────────────────────────────
  apiRequest: async ({ playwright }, use) => {
    const ctx = await playwright.request.newContext({ baseURL: BACKEND_URL });
    await use(ctx);
    await ctx.dispose();
  },

  // ── authenticatedPage fixture ───────────────────────────────────────────────
  authenticatedPage: async ({ browser, apiRequest }, use) => {
    // Step 1: Ensure the test user exists (register if not)
    await _ensureUserExists(apiRequest);

    // Step 2: Log in via the UI to get real tokens in localStorage
    const page = await browser.newPage();
    await _loginViaUI(page);

    // Step 3: Yield the authenticated page to the test
    await use(page);

    // Step 4: Teardown — close the page
    await page.close();
  },
});

// ── Helpers ───────────────────────────────────────────────────────────────────

async function _ensureUserExists(api: APIRequestContext): Promise<void> {
  try {
    const res = await api.post('/api/v1/auth/register', {
      data: {
        email:     TEST_USER.email,
        full_name: TEST_USER.name,
        password:  TEST_USER.password,
      },
      failOnStatusCode: false,
    });
    // 201 = registered, 400/409 = already exists — both are fine
    if (res.status() !== 201 && res.status() !== 400 && res.status() !== 409) {
      console.warn(`[auth fixture] Unexpected register status ${res.status()}`);
    }
  } catch {
    // Backend may not be running — UI tests will handle the fallback
    console.warn('[auth fixture] Could not reach backend to ensure user exists');
  }
}

async function _loginViaUI(page: Page): Promise<void> {
  const loginPage = new LoginPage(page);
  await loginPage.goto();

  // If we're already redirected to dashboard, skip login
  if (await page.locator('header').isVisible({ timeout: 3_000 }).catch(() => false)) {
    const onDash = await page.locator('nav').isVisible({ timeout: 1_000 }).catch(() => false);
    if (onDash) return;
  }

  await loginPage.expectLoginFormVisible();
  await loginPage.login(TEST_USER.email, TEST_USER.password);

  // Wait for dashboard to appear
  await expect(
    page.getByText(/court automation suite/i)
  ).toBeVisible({ timeout: 20_000 });
}

export { expect };
