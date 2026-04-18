/**
 * pages/CauseListPage.ts
 * Page Object Model for the Cause List Monitor tab.
 */
import { type Page, type Locator, expect } from '@playwright/test';

export class CauseListPage {
  readonly page: Page;

  readonly courtFilter:    Locator;
  readonly dateInput:      Locator;
  readonly fetchButton:    Locator;
  readonly causeListTable: Locator;
  readonly noListText:     Locator;
  readonly errorBanner:    Locator;
  readonly pdfDownloadBtn: Locator;
  readonly totalCasesText: Locator;

  constructor(page: Page) {
    this.page            = page;
    this.courtFilter     = page.getByRole('combobox', { name: /court/i });
    this.dateInput       = page.getByRole('textbox',  { name: /date/i });
    this.fetchButton     = page.getByRole('button',   { name: /fetch|load|search/i });
    this.causeListTable  = page.locator('[data-testid="causelist-table"], table, .causelist-entries');
    this.noListText      = page.getByText(/no cause list|not available|no entries/i);
    this.errorBanner     = page.locator('[role="alert"], .error-message, [data-testid="error"]');
    this.pdfDownloadBtn  = page.getByRole('button', { name: /download pdf|export/i });
    this.totalCasesText  = page.getByText(/total cases|entries|cases listed/i);
  }

  async selectCourt(courtName: string): Promise<void> {
    await this.courtFilter.selectOption({ label: courtName });
  }

  async setDate(isoDate: string): Promise<void> {
    // isoDate = "YYYY-MM-DD"
    await this.dateInput.fill(isoDate);
    await this.dateInput.press('Tab');  // trigger onChange
  }

  async fetch(): Promise<void> {
    await this.fetchButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async downloadPdf(): Promise<void> {
    // Playwright can intercept the download
    const [download] = await Promise.all([
      this.page.waitForEvent('download', { timeout: 15_000 }),
      this.pdfDownloadBtn.click(),
    ]);

    const path = await download.path();
    expect(path).toBeTruthy();
    expect(download.suggestedFilename()).toMatch(/\.pdf$/i);
  }

  async expectTableVisible(): Promise<void> {
    await expect(this.causeListTable).toBeVisible({ timeout: 20_000 });
  }

  async expectNotAvailable(): Promise<void> {
    await expect(this.noListText).toBeVisible({ timeout: 15_000 });
  }

  async getRowCount(): Promise<number> {
    const rows = this.page.locator(
      '[data-testid="causelist-table"] tbody tr, table tbody tr'
    );
    return rows.count();
  }
}
