import { test, expect } from './fixtures';

test.describe('Cause List Monitoring', () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  test('should get today cause list', async ({ authenticatedSession, page }) => {
    const response = await page.request.get(
      `${API_BASE_URL}/causelist/today?court_name=Delhi%20High%20Court`,
      {
        headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
      }
    );

    if (response.ok()) {
      const data = await response.json();
      expect(data.success || Array.isArray(data.data)).toBeTruthy();
    }
  });

  test('should search cause lists', async ({ authenticatedSession, page }) => {
    const response = await page.request.get(
      `${API_BASE_URL}/causelist/search?court_name=Delhi%20High%20Court&limit=10`,
      {
        headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
      }
    );

    expect(response.ok()).toBeTruthy();
  });

  test('should get supported courts', async ({ authenticatedSession, page }) => {
    const response = await page.request.get(`${API_BASE_URL}/causelist/courts`, {
      headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
    });

    expect(response.ok()).toBeTruthy();
  });

  test('should get upcoming hearings', async ({ authenticatedSession, page }) => {
    const response = await page.request.get(
      `${API_BASE_URL}/scraper/upcoming?days=7&limit=10`,
      {
        headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
      }
    );

    expect(response.ok()).toBeTruthy();
  });

  test('should get tracked cases', async ({ authenticatedSession, page }) => {
    const response = await page.request.get(`${API_BASE_URL}/scraper/tracked?limit=10`, {
      headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
    });

    expect(response.ok()).toBeTruthy();
  });
});
