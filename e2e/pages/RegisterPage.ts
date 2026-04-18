/**
 * pages/RegisterPage.ts
 * Page Object Model for the user registration screen.
 */
import { type Page, type Locator, expect } from '@playwright/test';

export class RegisterPage {
  readonly page: Page;

  readonly fullNameInput:      Locator;
  readonly emailInput:         Locator;
  readonly passwordInput:      Locator;
  readonly confirmInput:       Locator;
  readonly phoneInput:         Locator;
  readonly registerButton:     Locator;
  readonly loginLink:          Locator;
  readonly successMessage:     Locator;
  readonly errorMessage:       Locator;

  constructor(page: Page) {
    this.page               = page;
    this.fullNameInput      = page.getByRole('textbox', { name: /full name|name/i });
    this.emailInput         = page.getByRole('textbox', { name: /email/i });
    this.passwordInput      = page.getByRole('textbox', { name: /^password$/i });
    this.confirmInput       = page.getByRole('textbox', { name: /confirm password/i });
    this.phoneInput         = page.getByRole('textbox', { name: /phone|mobile/i });
    this.registerButton     = page.getByRole('button',  { name: /create account|register/i });
    this.loginLink          = page.getByRole('button',  { name: /sign in|login/i });
    this.successMessage     = page.locator('[data-testid="register-success"], .success-message');
    this.errorMessage       = page.locator('[data-testid="register-error"], [role="alert"]');
  }

  async fill(opts: {
    fullName: string;
    email: string;
    password: string;
    confirmPassword?: string;
    phone?: string;
  }): Promise<void> {
    await this.fullNameInput.fill(opts.fullName);
    await this.emailInput.fill(opts.email);
    await this.passwordInput.fill(opts.password);
    if (opts.confirmPassword !== undefined) {
      await this.confirmInput.fill(opts.confirmPassword);
    }
    if (opts.phone !== undefined) {
      await this.phoneInput.fill(opts.phone);
    }
  }

  async submit(): Promise<void> {
    await this.registerButton.click();
  }

  async expectError(text?: string): Promise<void> {
    await expect(this.errorMessage).toBeVisible({ timeout: 8_000 });
    if (text) {
      await expect(this.errorMessage).toContainText(text);
    }
  }
}
