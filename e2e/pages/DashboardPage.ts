/**
 * pages/DashboardPage.ts
 * Page Object Model for the main dashboard (post-login).
 */
import { type Page, type Locator, expect } from '@playwright/test';

type Tab = 'dashboard' | 'cases' | 'causelist' | 'analytics';

export class DashboardPage {
  readonly page: Page;

  readonly header:         Locator;
  readonly welcomeText:    Locator;
  readonly navBar:         Locator;
  readonly signOutButton:  Locator;

  constructor(page: Page) {
    this.page           = page;
    this.header         = page.locator('header');
    this.welcomeText    = page.getByText(/welcome,/i);
    this.navBar         = page.locator('nav');
    this.signOutButton  = page.getByRole('button', { name: /sign out|logout/i });
  }

  async expectLoaded(): Promise<void> {
    await expect(this.header).toBeVisible({ timeout: 20_000 });
    // Either the welcome message or the nav bar must be present
    await expect(
      this.page.getByText(/court automation suite/i)
    ).toBeVisible({ timeout: 15_000 });
  }

  async navigateTo(tab: Tab): Promise<void> {
    const labels: Record<Tab, string | RegExp> = {
      dashboard:  /dashboard/i,
      cases:      /case search/i,
      causelist:  /cause list/i,
      analytics:  /analytics/i,
    };
    await this.navBar.getByRole('button', { name: labels[tab] }).click();
    await this.page.waitForLoadState('networkidle');
  }

  async signOut(): Promise<void> {
    await this.signOutButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /** Wait for dashboard stats cards to load */
  async expectStatsVisible(): Promise<void> {
    // At least one stat-like number should appear on the dashboard
    await expect(
      this.page.locator('[data-testid="stat-card"], .stat-value, h2, h3').first()
    ).toBeVisible({ timeout: 15_000 });
  }
}
