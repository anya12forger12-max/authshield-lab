import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  API_BASE,
  ApiError,
  TOKEN_KEY,
  USER_KEY,
  clearSession,
  extractErrorMessage,
  getSessionId,
  login,
  logout,
  normalizeUser,
  readStoredUser,
  register,
  validateSession,
} from './authApi';

/**
 * Regression tests for the authentication client.
 *
 * The class of bug these lock down: the UI posted to ``/api/auth/login`` while
 * the backend mounts at ``/api/v1/auth``, so sign-in 404'd. Asserting the exact
 * request path is the point of the first test in each group.
 */

function fakeStorage(): Storage {
  const map = new Map<string, string>();
  return {
    get length() {
      return map.size;
    },
    clear: () => map.clear(),
    getItem: (key: string) => map.get(key) ?? null,
    key: (index: number) => Array.from(map.keys())[index] ?? null,
    removeItem: (key: string) => {
      map.delete(key);
    },
    setItem: (key: string, value: string) => {
      map.set(key, value);
    },
  } as unknown as Storage;
}

function jsonResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    text: async () => JSON.stringify(body),
  } as unknown as Response;
}

const fetchMock = vi.fn();

function lastCall(): { url: string; init: RequestInit } {
  const [url, init] = fetchMock.mock.calls.at(-1) as [string, RequestInit];
  return { url, init };
}

beforeEach(() => {
  vi.stubGlobal('localStorage', fakeStorage());
  vi.stubGlobal('fetch', fetchMock);
  fetchMock.mockReset();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('API_BASE', () => {
  it('targets the versioned auth router, not the bare /api prefix', () => {
    expect(API_BASE).toBe('/api/v1');
  });
});

describe('login', () => {
  const success = {
    message: 'Login successful.',
    data: {
      success: true,
      session_id: 'sess-123',
      user: { user_id: 'u-1', username: 'alice', display_name: 'Alice A' },
    },
  };

  it('posts to /api/v1/auth/login', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, success));

    await login('alice', 'Str0ng!Passw0rd#2026');

    const { url, init } = lastCall();
    expect(url).toBe('/api/v1/auth/login');
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body as string)).toEqual({
      username: 'alice',
      password: 'Str0ng!Passw0rd#2026',
    });
  });

  it('persists the session id and normalized user', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, success));

    const result = await login('alice', 'Str0ng!Passw0rd#2026');

    expect(result.sessionId).toBe('sess-123');
    expect(getSessionId()).toBe('sess-123');
    expect(readStoredUser()).toEqual({
      id: 'u-1',
      username: 'alice',
      displayName: 'Alice A',
      email: '',
      role: 'student',
    });
  });

  it('maps an HTTPException envelope to an ApiError with its error code', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(401, {
        detail: {
          message: 'Invalid username or password.',
          error_code: 'INVALID_CREDENTIALS',
          correlation_id: 'c-1',
        },
      }),
    );

    const error = await login('alice', 'wrong').catch((e: unknown) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).message).toBe('Invalid username or password.');
    expect((error as ApiError).errorCode).toBe('INVALID_CREDENTIALS');
    expect((error as ApiError).status).toBe(401);
  });

  it('maps a FastAPI 422 validation error to its first message', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(422, {
        detail: [{ loc: ['body', 'password'], msg: 'String should have at least 8 characters' }],
      }),
    );

    const error = (await login('alice', 'short').catch((e: unknown) => e)) as ApiError;

    expect(error.message).toBe('String should have at least 8 characters');
  });

  it('refuses a success payload with no session id', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { message: 'ok', data: {} }));

    const error = (await login('alice', 'pw').catch((e: unknown) => e)) as ApiError;

    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(500);
  });

  it('turns a transport failure into a friendly ApiError', async () => {
    fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));

    const error = (await login('alice', 'pw').catch((e: unknown) => e)) as ApiError;

    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(0);
    expect(error.message).toMatch(/network/i);
  });
});

describe('register', () => {
  const payload = {
    username: 'bobby',
    password: 'Str0ng!Passw0rd#2026',
    confirm_password: 'Str0ng!Passw0rd#2026',
    display_name: 'Bobby B',
    email: 'bobby@example.com',
    privacy_policy_accepted: true,
  };

  it('posts to /api/v1/auth/register with the backend field names', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(201, {
        message: 'Registration successful.',
        data: { success: true, user_id: 'u-9', username: 'bobby' },
      }),
    );

    const result = await register(payload);

    const { url, init } = lastCall();
    expect(url).toBe('/api/v1/auth/register');
    // The backend requires this exact snake_case flag; a mismatch 422s.
    expect(JSON.parse(init.body as string)).toMatchObject({
      confirm_password: payload.confirm_password,
      privacy_policy_accepted: true,
    });
    expect(result).toEqual({ userId: 'u-9', username: 'bobby' });
  });

  it('surfaces a duplicate-username conflict with its error code', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(409, {
        detail: { message: 'Username already taken.', error_code: 'USERNAME_TAKEN' },
      }),
    );

    const error = (await register(payload).catch((e: unknown) => e)) as ApiError;

    expect(error.status).toBe(409);
    expect(error.errorCode).toBe('USERNAME_TAKEN');
  });
});

describe('logout', () => {
  it('posts to /api/v1/auth/logout with the X-User-ID header', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(200, { message: 'Logout successful.', data: { success: true } }),
    );

    await logout('sess-123', 'u-1');

    const { url, init } = lastCall();
    expect(url).toBe('/api/v1/auth/logout');
    const headers = init.headers as Record<string, string>;
    expect(headers['X-User-ID']).toBe('u-1');
  });
});

describe('validateSession', () => {
  it('returns true only for an explicitly successful payload', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(200, { data: { success: true, message: 'ok' } }),
    );
    expect(await validateSession('sess-123')).toBe(true);

    fetchMock.mockResolvedValueOnce(
      jsonResponse(200, { data: { success: false, message: 'expired' } }),
    );
    expect(await validateSession('sess-123')).toBe(false);
  });

  it('returns false instead of throwing when the server rejects the session', async () => {
    fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    expect(await validateSession('sess-123')).toBe(false);
  });
});

describe('extractErrorMessage', () => {
  it('reads the object envelope', () => {
    expect(
      extractErrorMessage({ detail: { message: 'Nope', error_code: 'X' } }, 400),
    ).toEqual({ message: 'Nope', errorCode: 'X' });
  });

  it('reads a bare string detail', () => {
    expect(extractErrorMessage({ detail: 'X-User-ID header is required.' }, 400)).toEqual({
      message: 'X-User-ID header is required.',
    });
  });

  it('reads a validation array', () => {
    expect(extractErrorMessage({ detail: [{ msg: 'bad input' }] }, 422)).toEqual({
      message: 'bad input',
    });
  });

  it('falls back to the status when the body is empty or unexpected', () => {
    expect(extractErrorMessage(null, 503).message).toMatch(/503/);
    expect(extractErrorMessage({}, 500).message).toMatch(/500/);
  });
});

describe('normalizeUser', () => {
  it('maps snake_case to camelCase', () => {
    expect(normalizeUser({ user_id: 'u-1', username: 'alice', display_name: 'Alice' })).toEqual({
      id: 'u-1',
      username: 'alice',
      displayName: 'Alice',
      email: '',
      role: 'student',
    });
  });

  it('falls back to the username and a default role', () => {
    const user = normalizeUser({ user_id: 'u-2', username: 'bob' });
    expect(user.displayName).toBe('bob');
    expect(user.role).toBe('student');
  });

  it('tolerates a missing payload', () => {
    expect(normalizeUser(null)).toEqual({
      id: '',
      username: '',
      displayName: '',
      email: '',
      role: 'student',
    });
  });
});

describe('session storage', () => {
  it('clears both keys', () => {
    localStorage.setItem(TOKEN_KEY, 'sess-1');
    localStorage.setItem(USER_KEY, '{"id":"u-1"}');

    clearSession();

    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
    expect(localStorage.getItem(USER_KEY)).toBeNull();
    expect(getSessionId()).toBeNull();
    expect(readStoredUser()).toBeNull();
  });

  it('returns null for a corrupt user payload rather than throwing', () => {
    localStorage.setItem(USER_KEY, '{not json');
    expect(readStoredUser()).toBeNull();
  });

  it('is safe when localStorage is unavailable', () => {
    vi.stubGlobal('localStorage', undefined);

    expect(() => clearSession()).not.toThrow();
    expect(getSessionId()).toBeNull();
    expect(readStoredUser()).toBeNull();
  });
});
