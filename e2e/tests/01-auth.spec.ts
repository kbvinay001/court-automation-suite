/**
 * tests/01-auth.spec.ts
 *
 * Flow covered:
 *   ✅ Happy: Register new account → auto-login → land on Dashboard
 *   ✅ Happy: Login with valid credentials
 *   ❌ Error: Login with wrong password → error message shown
 *   ❌ Error: Login with unknown email → error message shown
 *   ❌ Error: Register with mismatched passwords
 *   ❌ Error: Register with already-used email
 *   ✅ Happy: Sign out → back to login page
 */
import { test, expect } from '@playwright/test';
import { LoginPage }    from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';
import { DashboardPage } from '../pages/DashboardPage';
import { TEST_USER, BACKEND_URL } from '../fixtures/auth.fixture';

// Unique email for each test run so repeated CI runs don't conflict
const UNIQUE_EMAIL = `e2e.${Date.now()}@courttest.in`;

// ── Registration flow ─────────────────────────────────────────────────────────
test.describe('Registration', () => {
  test('happy path: new user registers and lands on dashboard', async ({ page }) => {
    const login    = new LoginPage(page);
    const register = new RegisterPage(page);
    const dash     = new DashboardPage(page);

    await login.goto();
    await login.expectLoginFormVisible();
    await login.switchToRegister();

    await register.fill({
      fullName:        'New E2E User',
      email:           UNIQUE_EMAIL,
      password:        'Test@1234!',
      confirmPassword: 'Test@1234!',
      phone:           '+919876543210',
    });
    await register.submit();

    // After register, should land on dashboard or show success then auto-login
    await dash.expectLoaded();
  });

  test('error: mismatched passwords shows validation error', async ({ page }) => {
    const login    = new LoginPage(page);
    const register = new RegisterPage(page);

    await login.goto();
    await login.switchToRegister();

    await register.fill({
      fullName:        'Mismatch User',
      email:           `mismatch.${Date.now()}@courttest.in`,
      password:        'Test@1234!',
      confirmPassword: 'WrongPass999!',
    });
    await register.submit();
    await register.expectError();
  });

  test('error: duplicate email shows appropriate error', async ({ page, request }) => {
    // First register via API to guarantee the email exists
    await request.post(`${BACKEND_URL}/api/v1/auth/register`, {
      data: {
        email:     TEST_USER.email,
        full_name: TEST_USER.name,
        password:  TEST_USER.password,
      },
      failOnStatusCode: false,
    });

    const login    = new LoginPage(page);
    const register = new RegisterPage(page);

    await login.goto();
    await login.switchToRegister();

    await register.fill({
      fullName:        TEST_USER.name,
      email:           TEST_USER.email,  // already exists
      password:        TEST_USER.password,
      confirmPassword: TEST_USER.password,
    });
    await register.submit();
    await register.expectError();
  });
});

// ── Login flow ────────────────────────────────────────────────────────────────
test.describe('Login', () => {
  test('happy path: valid credentials → dashboard', async ({ page }) => {
    const login = new LoginPage(page);
    const dash  = new DashboardPage(page);

    await login.goto();
    await login.expectLoginFormVisible();
    await login.login(TEST_USER.email, TEST_USER.password);
    await dash.expectLoaded();
  });

  test('error: wrong password → error message', async ({ page }) => {
    const login = new LoginPage(page);

    await login.goto();
    await login.expectLoginFormVisible();
    await login.login(TEST_USER.email, 'WrongPassword123!');
    await login.expectError();
  });

  test('error: unknown email → error message', async ({ page }) => {
    const login = new LoginPage(page);

    await login.goto();
    await login.expectLoginFormVisible();
    await login.login('nobody@doesnotexist.in', 'AnyPassword123!');
    await login.expectError();
  });

  test('error: empty form submission → validation messages', async ({ page }) => {
    const login = new LoginPage(page);

    await login.goto();
    await login.expectLoginFormVisible();
    await login.loginButton.click();

    // Either HTML5 required validation or app-level error
    const hasValidation = await page.evaluate(() =>
      document.querySelector('input[type="email"]')?.checkValidity() === false ||
      document.querySelector('input[type="text"][required]')?.checkValidity() === false
    );
    expect(hasValidation).toBeTruthy();
  });
});

// ── Sign-out flow ─────────────────────────────────────────────────────────────
test.describe('Sign out', () => {
  test('happy path: sign out returns to login screen', async ({ page }) => {
    const login = new LoginPage(page);
    const dash  = new DashboardPage(page);

    await login.goto();
    await login.login(TEST_USER.email, TEST_USER.password);
    await dash.expectLoaded();

    await dash.signOut();

    // Should be back on login page
    await login.expectLoginFormVisible();
  });
});
