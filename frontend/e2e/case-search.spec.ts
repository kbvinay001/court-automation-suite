import { test, expect } from './fixtures';

test.describe('Case Search', () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  test('should search cases', async ({ authenticatedSession, page }) => {
    const response = await page.request.get(
      `${API_BASE_URL}/scraper/search?page=1&limit=10`,
      {
        headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
      }
    );

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.success || Array.isArray(data.data) || Array.isArray(data)).toBeTruthy();
  });

  test('should search with filters', async ({ authenticatedSession, page }) => {
    const response = await page.request.get(
      `${API_BASE_URL}/scraper/search?court_type=high_court&status=pending&limit=10`,
      {
        headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
      }
    );

    expect(response.ok()).toBeTruthy();
  });

  test('should get case details', async ({ authenticatedSession, page }) => {
    // First get a case number
    const searchRes = await page.request.get(
      `${API_BASE_URL}/scraper/search?limit=1`,
      {
        headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
      }
    );

    if (searchRes.ok()) {
      const searchData = await searchRes.json();
      const caseNum = searchData.data?.[0]?.case_number;

      if (caseNum) {
        const detailRes = await page.request.get(
          `${API_BASE_URL}/scraper/case/${encodeURIComponent(caseNum)}`,
          {
            headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
          }
        );

        expect(detailRes.ok()).toBeTruthy();
      }
    }
  });

  test('should verify result fields', async ({ authenticatedSession, page }) => {
    const response = await page.request.get(
      `${API_BASE_URL}/scraper/search?limit=5`,
      {
        headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
      }
    );

    if (response.ok()) {
      const data = await response.json();
      if (data.data && data.data.length > 0) {
        expect(data.data[0]).toHaveProperty('case_number');
      }
    }
  });
});
