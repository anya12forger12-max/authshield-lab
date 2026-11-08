/**
 * Single source of truth for every authentication HTTP call.
 *
 * The backend mounts the authentication router under `/api/v1/auth`
 * (``app/api/v1/__init__.py``), but the UI previously posted to
 * ``/api/auth/login`` — one path segment short, so every sign-in 404'd before a
 * single credential was checked. Every request path now lives in this module
 * and is covered by ``authApi.test.ts``.
 *
 * In development ``vite.config.ts`` proxies ``/api`` to the FastAPI server on
 * port 8000. Set ``VITE_API_URL`` to point at a different origin (e.g. a
 * packaged Electron build talking to a hosted backend).
 */

/** Base URL for the versioned API. */
export const API_BASE: string = import.meta.env?.VITE_API_URL || '/api/v1';

/** ``localStorage`` key holding the session id returned by ``/auth/login``. */
export const TOKEN_KEY = 'authshield_token';

/** ``localStorage`` key holding the serialized authenticated user. */
export const USER_KEY = 'authshield_user';

/** A user as the UI store consumes it. */
export interface AuthUser {
  id: string;
  username: string;
  displayName: string;
  email: string;
  role: string;
}

/** Shape of the ``data`` payload returned by ``POST /auth/login``. */
export interface LoginResponseData {
  session_id?: string | null;
  user?: {
    user_id?: string;
    username?: string;
    display_name?: string | null;
  } | null;
}

/** Payload for ``POST /auth/register``. */
export interface RegisterPayload {
  username: string;
  password: string;
  confirm_password: string;
  display_name: string;
  email?: string;
  privacy_policy_accepted: boolean;
}

/** Result of a successful registration. */
export interface RegisterResult {
  userId: string;
  username: string;
}

/** Result of a successful login. */
export interface LoginResult {
  sessionId: string;
  user: AuthUser;
}

/** An API failure carrying the HTTP status and the backend error code. */
export class ApiError extends Error {
  readonly status: number;
  readonly errorCode?: string;

  constructor(message: string, status: number, errorCode?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.errorCode = errorCode;
  }
}

interface SuccessEnvelope<T> {
  message?: string;
  data?: T;
}

/** Backend errors are either ``{detail: {message, error_code}}`` or FastAPI's
 * ``{detail: [{msg}]}``, or a bare string for the header-validation cases. */
interface ErrorEnvelope {
  detail?:
    | string
    | { message?: string; error_code?: string }
    | Array<{ msg?: string }>;
}

function str(value: unknown): string {
  return typeof value === 'string' ? value : '';
}

function safeJsonParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

/**
 * Turn an error response body into a message and error code.
 *
 * Exported for direct testing: the three envelope shapes above are easy to get
 * wrong and are what the UI actually shows the user.
 */
export function extractErrorMessage(
  body: unknown,
  status: number,
): { message: string; errorCode?: string } {
  const detail = (body as ErrorEnvelope | null)?.detail;

  if (typeof detail === 'string' && detail.trim()) {
    return { message: detail };
  }

  if (Array.isArray(detail)) {
    const message = detail[0]?.msg;
    if (message) return { message };
  } else if (detail && typeof detail === 'object') {
    return {
      message: detail.message || `Request failed (HTTP ${status}).`,
      errorCode: detail.error_code,
    };
  }

  return { message: `Request failed (HTTP ${status}).` };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers ?? {}),
      },
    });
  } catch {
    throw new ApiError('Network error. Please check your connection and try again.', 0);
  }

  const text = await response.text();
  const body = text ? safeJsonParse(text) : null;

  if (!response.ok) {
    const { message, errorCode } = extractErrorMessage(body, response.status);
    throw new ApiError(message, response.status, errorCode);
  }

  return body as T;
}

function getStorage(): Storage | null {
  try {
    return typeof globalThis.localStorage === 'undefined' ? null : globalThis.localStorage;
  } catch {
    // Accessing localStorage can throw for opaque origins / disabled cookies.
    return null;
  }
}

/** Map the backend's snake_case user payload onto the store's camelCase shape. */
export function normalizeUser(raw: unknown): AuthUser {
  const record = (raw ?? {}) as Record<string, unknown>;
  const username = str(record.username);
  return {
    id: str(record.user_id ?? record.id),
    username,
    displayName: str(record.display_name ?? record.displayName) || username,
    email: str(record.email),
    role: str(record.role) || 'student',
  };
}

/** Persist the session id and user so a reload keeps the user signed in. */
export function persistSession(sessionId: string, user: AuthUser): void {
  const store = getStorage();
  if (!store) return;
  store.setItem(TOKEN_KEY, sessionId);
  store.setItem(USER_KEY, JSON.stringify(user));
}

/** Remove every persisted credential. */
export function clearSession(): void {
  const store = getStorage();
  if (!store) return;
  store.removeItem(TOKEN_KEY);
  store.removeItem(USER_KEY);
}

/** The persisted session id, or ``null`` when signed out. */
export function getSessionId(): string | null {
  return getStorage()?.getItem(TOKEN_KEY) ?? null;
}

/** The persisted user, or ``null`` when absent/corrupt. */
export function readStoredUser(): AuthUser | null {
  const raw = getStorage()?.getItem(USER_KEY);
  if (!raw) return null;
  const parsed = safeJsonParse(raw) as AuthUser | null;
  return parsed && typeof parsed === 'object' ? parsed : null;
}

/** ``POST /auth/login`` — authenticate and persist the session. */
export async function login(username: string, password: string): Promise<LoginResult> {
  const envelope = await request<SuccessEnvelope<LoginResponseData>>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });

  const sessionId = envelope.data?.session_id;
  if (!sessionId) {
    throw new ApiError('Login succeeded but the server returned no session.', 500);
  }

  const user = normalizeUser(envelope.data?.user);
  persistSession(sessionId, user);
  return { sessionId, user };
}

/** ``POST /auth/register`` — create an account. Does not sign the user in. */
export async function register(payload: RegisterPayload): Promise<RegisterResult> {
  const envelope = await request<
    SuccessEnvelope<{ user_id?: string; username?: string }>
  >('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });

  return {
    userId: str(envelope.data?.user_id),
    username: str(envelope.data?.username) || payload.username,
  };
}

/**
 * ``POST /auth/logout``.
 *
 * The backend requires the ``X-User-ID`` header; without it the request is
 * rejected with a 400. Callers should still clear local state in a ``finally``
 * block so a network failure cannot strand the user in a signed-in shell.
 */
export async function logout(sessionId: string | null, userId: string): Promise<void> {
  await request('/auth/logout', {
    method: 'POST',
    headers: { 'X-User-ID': userId },
    body: JSON.stringify({ session_id: sessionId, terminate_all: false }),
  });
}

/** ``POST /auth/session/validate`` — ``true`` only for an active session. */
export async function validateSession(sessionId: string): Promise<boolean> {
  try {
    const envelope = await request<SuccessEnvelope<{ success?: boolean }>>(
      '/auth/session/validate',
      {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId }),
      },
    );    return envelope.data?.success === true;
  } catch {
    return false;
  }
}
