import { test as base, expect } from '@playwright/test';

interface TestUser {
  email: string;
  password: string;
  full_name: string;
  phone: string;
  role: string;
}

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
}

function generateTestUser(): TestUser {
  const timestamp = Date.now();
  return {
    email: `test-${timestamp}@court-automation.test`,
    password: `TestPassword${timestamp}!`,
    full_name: `Test User ${timestamp}`,
    phone: '+919876543210',
    role: 'advocate',
  };
}

async function makeApiRequest<T>(
  method: string,
  path: string,
  body?: any,
  token?: string
): Promise<ApiResponse<T>> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  const url = `${baseUrl}${path}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    return { success: false, message: `HTTP ${response.status}` };
  }

  return await response.json();
}

export type TestFixtures = {
  testUser: TestUser;
  authenticatedSession: {
    user: TestUser;
    access_token: string;
    refresh_token: string;
  };
};

export const test = base.extend<TestFixtures>({
  testUser: async ({}, use) => {
    const user = generateTestUser();
    await makeApiRequest('/auth/register', user);
    await use(user);
  },

  authenticatedSession: async ({ testUser }, use) => {
    const loginRes = await makeApiRequest('/auth/login', {
      email: testUser.email,
      password: testUser.password,
    });

    if (!loginRes.success || !loginRes.data) {
      throw new Error(`Failed to authenticate: ${loginRes.message}`);
    }

    const data = loginRes.data as any;
    await use({
      user: testUser,
      access_token: data.access_token,
      refresh_token: data.refresh_token,
    });
  },
});

export { expect };
