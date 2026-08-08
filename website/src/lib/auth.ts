/**
 * Frontend authentication helpers.
 *
 * Integrates with the Django session-based authentication backend.
 * All fetch calls use `credentials: "include"` so the session cookie
 * is sent cross-origin (Astro :4321 → Django :8000).
 *
 * A1.8: CSRF token handling — the Astro frontend cannot read the Django
 * CSRF cookie directly due to cross-origin restrictions.  The `getCsrfToken()`
 * function fetches the token from the backend so it can be included in the
 * X-CSRFToken header for authenticated POST requests (logout, change-password).
 */

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  must_change_password: boolean;
  last_login: string | null;
}

const API_BASE_URL =
  import.meta.env.PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

export const AUTH_ENDPOINTS = {
  login: `${API_BASE_URL}/api/auth/login`,
  logout: `${API_BASE_URL}/api/auth/logout`,
  me: `${API_BASE_URL}/api/auth/me`,
  changePassword: `${API_BASE_URL}/api/auth/change-password`,
  csrfToken: `${API_BASE_URL}/api/auth/csrf-token`,
  academy: `${API_BASE_URL}/api/academy`,
} as const;

/**
 * A1.8: Ensure the CSRF cookie is set and return its value.
 *
 * The cookie is the single source of truth.  We call the backend
 * endpoint to ensure the cookie exists, then read it directly from
 * ``document.cookie`` so the returned value always matches what will
 * be sent back in the ``X-CSRFToken`` header.
 */
export async function getCsrfToken(): Promise<string | null> {
  try {
    // Fetch the token from the backend endpoint which returns the
    // CSRF token value in the response body.  This works even if
    // the cookie is HttpOnly and not accessible via document.cookie.
    const res = await fetch(AUTH_ENDPOINTS.csrfToken, {
      credentials: "include",
      headers: { Accept: "application/json" },
    });
    if (!res.ok) return null;
    const data = await res.json().catch(() => ({}));
    return data.csrfToken ?? null;
  } catch {
    return null;
  }
}

/**
 * Fetch the currently authenticated user from the backend.
 * Returns `null` if not authenticated (401) or on error.
 *
 * A1: When called server-side (Astro SSR), `cookieHeader` must be the
 * incoming request's `Cookie` header.  Node.js `fetch` does not attach
 * browser cookies automatically, so without forwarding them Django
 * returns 401 and the page redirects back to login (redirect loop).
 */
export async function getCurrentUser(
  cookieHeader?: string,
): Promise<AuthUser | null> {
  try {
    const res = await fetch(AUTH_ENDPOINTS.me, {
      credentials: "include",
      headers: {
        Accept: "application/json",
        ...(cookieHeader ? { Cookie: cookieHeader } : {}),
      },
    });
    if (!res.ok) return null;
    return (await res.json()) as AuthUser;
  } catch {
    return null;
  }
}

/**
 * Authenticate with email + password.  On success the backend sets a
 * session cookie and returns the user object.
 *
 * A1.8: Fetches CSRF token first, then includes it in the X-CSRFToken header.
 */
export async function login(
  email: string,
  password: string,
): Promise<{ user: AuthUser } | { error: string }> {
  try {
    const csrfToken = await getCsrfToken();
    const res = await fetch(AUTH_ENDPOINTS.login, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
      },
      body: JSON.stringify({
        email: email.toLowerCase().trim(),
        password,
      }),
    });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      return { error: body.error ?? "Invalid email or password." };
    }
    return { user: body as AuthUser };
  } catch {
    return { error: "Network error. Please try again." };
  }
}

/**
 * Destroy the current session by calling the backend logout endpoint.
 * A1.8: Fetches the CSRF token first and includes it in the request header.
 */
export async function logout(): Promise<boolean> {
  try {
    const csrfToken = await getCsrfToken();
    const res = await fetch(AUTH_ENDPOINTS.logout, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
      },
    });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Check if the Academy API is accessible for the current user.
 * Returns `true` if the user has AcademyAccess (200), `false` otherwise
 * (401 = not authenticated, 403 = no AcademyAccess).
 *
 * A1: When called server-side (Astro SSR), `cookieHeader` must be the
 * incoming request's `Cookie` header to authenticate the Django request.
 */
export async function hasAcademyAccess(
  cookieHeader?: string,
): Promise<boolean> {
  try {
    const res = await fetch(AUTH_ENDPOINTS.academy, {
      credentials: "include",
      headers: {
        Accept: "application/json",
        ...(cookieHeader ? { Cookie: cookieHeader } : {}),
      },
    });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Lightweight check: does the browser have a session cookie?
 * This does NOT call the API — it only checks cookie presence
 * for middleware-level route protection.
 */
export function hasSessionCookie(): boolean {
  // Django session cookie is typically "sessionid"
  return document.cookie.includes("sessionid=");
}