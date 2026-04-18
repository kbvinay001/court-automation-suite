/**
 * pages/CaseSearchPage.ts
 * Page Object Model for the Case Search & Tracking tab.
 */
import { type Page, type Locator, expect } from '@playwright/test';

export class CaseSearchPage {
  readonly page: Page;

  readonly caseNumberInput: Locator;
  readonly courtSelect:     Locator;
  readonly searchButton:    Locator;
  readonly clearButton:     Locator;
  readonly resultsSection:  Locator;
  readonly noResultsText:   Locator;
  readonly errorBanner:     Locator;
  readonly loadingSpinner:  Locator;
  readonly firstResultCard: Locator;
  readonly trackButton:     Locator;

  constructor(page: Page) {
    this.page             = page;
    this.caseNumberInput  = page.getByRole('textbox', { name: /case number/i });
    this.courtSelect      = page.getByRole('combobox', { name: /court/i });
    this.searchButton     = page.getByRole('button',   { name: /search/i });
    this.clearButton      = page.getByRole('button',   { name: /clear|reset/i });
    this.resultsSection   = page.locator('[data-testid="case-results"], .case-results, table');
    this.noResultsText    = page.getByText(/no cases found|no results/i);
    this.errorBanner      = page.locator('[role="alert"], .error-message, [data-testid="error"]');
    this.loadingSpinner   = page.locator('.loading, [aria-label="loading"], .spinner');
    this.firstResultCard  = page.locator('[data-testid="case-card"], .case-card, tbody tr').first();
    this.trackButton      = page.getByRole('button', { name: /track|follow/i }).first();
  }

  async searchByCaseNumber(caseNumber: string): Promise<void> {
    await this.caseNumberInput.fill(caseNumber);
    await this.searchButton.click();
    // Wait for loading to finish
    await this.page.waitForLoadState('networkidle');
  }

  async expectResultsVisible(): Promise<void> {
    await expect(this.resultsSection).toBeVisible({ timeout: 20_000 });
  }

  async expectNoResults(): Promise<void> {
    await expect(this.noResultsText).toBeVisible({ timeout: 15_000 });
  }

  async expectErrorBanner(): Promise<void> {
    await expect(this.errorBanner).toBeVisible({ timeout: 10_000 });
  }

  /**
   * Returns the text of all visible case number cells / result cards.
   * Useful for asserting a specific case appears in results.
   */
  async getResultCaseNumbers(): Promise<string[]> {
    const cards = this.page.locator('[data-testid="case-number"], .case-number, td:first-child');
    const count = await cards.count();
    const texts: string[] = [];
    for (let i = 0; i < count; i++) {
      texts.push(await cards.nth(i).textContent() ?? '');
    }
    return texts.map(t => t.trim()).filter(Boolean);
  }
}
