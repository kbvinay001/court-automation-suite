import { test, expect } from './fixtures';

test.describe('Authentication', () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  test('should register and login', async ({ testUser, page }) => {
    const response = await page.request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        email: testUser.email,
        password: testUser.password,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.success || data.access_token).toBeTruthy();
  });

  test('should get user profile', async ({ authenticatedSession, page }) => {
    const response = await page.request.get(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${authenticatedSession.access_token}` },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.data.email || data.email).toBe(authenticatedSession.user.email);
  });

  test('should refresh token', async ({ authenticatedSession, page }) => {
    const response = await page.request.post(`${API_BASE_URL}/auth/refresh`, {
      data: { refresh_token: authenticatedSession.refresh_token },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.success || data.access_token).toBeTruthy();
  });
});
