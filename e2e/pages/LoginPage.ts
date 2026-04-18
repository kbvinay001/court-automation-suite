/**
 * pages/LoginPage.ts
 * Page Object Model for the login screen.
 */
import { type Page, type Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;

  // ── Locators ──────────────────────────────────────────────────────────────
  readonly emailInput:    Locator;
  readonly passwordInput: Locator;
  readonly loginButton:   Locator;
  readonly errorMessage:  Locator;
  readonly registerLink:  Locator;
  readonly heading:       Locator;

  constructor(page: Page) {
    this.page          = page;
    this.emailInput    = page.getByRole('textbox', { name: /email/i });
    this.passwordInput = page.getByRole('textbox', { name: /password/i });
    this.loginButton   = page.getByRole('button',  { name: /sign in|log in/i });
    this.errorMessage  = page.locator('[data-testid="login-error"], .error-message, [role="alert"]');
    this.registerLink  = page.getByRole('button',  { name: /register|create account/i });
    this.heading       = page.getByRole('heading',  { name: /sign in|login|court automation/i });
  }

  // ── Actions ───────────────────────────────────────────────────────────────

  async goto(): Promise<void> {
    await this.page.goto('/');
    // Wait for either the login form OR the dashboard (already authenticated)
    await this.page.waitForLoadState('networkidle');
  }

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async expectLoginFormVisible(): Promise<void> {
    await expect(this.emailInput).toBeVisible({ timeout: 10_000 });
    await expect(this.passwordInput).toBeVisible();
    await expect(this.loginButton).toBeVisible();
  }

  async expectError(text?: string): Promise<void> {
    await expect(this.errorMessage).toBeVisible({ timeout: 8_000 });
    if (text) {
      await expect(this.errorMessage).toContainText(text);
    }
  }

  async switchToRegister(): Promise<void> {
    await this.registerLink.click();
  }
}
