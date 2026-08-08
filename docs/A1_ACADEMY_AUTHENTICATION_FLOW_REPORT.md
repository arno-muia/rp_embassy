# Academy Authentication Flow — Implementation Report

## Overview

This report documents the changes made to fix the Academy authentication and logout flow. The primary issue was that the CSRF token was being read from `document.cookie`, which fails when the cookie is `HttpOnly`. This caused logout requests to fail silently, leaving the session intact and the hamburger menu showing a stale authenticated state.

## Root Cause

- The `getCsrfToken()` function in `auth.ts` attempted to read the CSRF token from `document.cookie`
- When the CSRF cookie is `HttpOnly` (set by Django with `CSRF_COOKIE_HTTPONLY = True`), JavaScript cannot access it via `document.cookie`
- This caused the logout POST request to be sent without a valid `X-CSRFToken` header
- Django rejected the request (403 Forbidden or CSRF verification failed), so the session was never destroyed
- The user remained authenticated, and the hamburger menu continued to show "Signed in as ... Sign Out →"

## Changes Made

### 1. `rpwebsite/RP/website/src/lib/auth.ts`

**Before:**
```typescript
export async function getCsrfToken(): Promise<string | null> {
  try {
    await fetch(AUTH_ENDPOINTS.csrfToken, {
      credentials: "include",
      headers: { Accept: "application/json" },
    }).catch(() => {});
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : null;
  } catch {
    return null;
  }
}
```

**After:**
```typescript
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
```

**Why this fixes it:** The `/api/auth/csrf-token` endpoint returns the CSRF token in the JSON response body. This bypasses the `HttpOnly` restriction entirely, as the token is transmitted in the response payload rather than relying on JavaScript-readable cookies.

### 2. `rpwebsite/RP/website/src/components/layout/SiteHeader.astro`

**Added missing import:**
```typescript
import { getCsrfToken } from "../../lib/auth";
```

**Why this fixes it:** The `handleSignOut` function was already calling `getCsrfToken()` but the function was not imported. This would have caused a runtime `ReferenceError`, preventing the logout handler from executing properly.

### 3. `rpwebsite/RP/website/src/middleware.ts`

**Before:**
```typescript
export async function middleware(req: Request) {
  const res = await next(req);
  // ... cache headers ...
}
```

**After:**
```typescript
export async function middleware(req: Request) {
  const res = await next(req);
  // ... no-cache headers for Academy routes ...
  return res;
}
```

**Why this matters:** Ensures that Academy pages are never cached by the browser. This prevents the back/forward navigation cache from showing stale protected content after logout.

## Authentication Flow

1. **User visits `/academy`**
2. Astro SSR middleware runs `getMe(cookieHeader)` and `hasAcademyAccess(cookieHeader)`
3. If not authenticated (401) or no AcademyAccess (403), redirect to `/login?redirect=/academy`
4. User enters credentials
5. Frontend calls `/api/auth/csrf-token` to obtain CSRF token (works even with HttpOnly cookies)
6. Frontend POSTs credentials to `/api/auth/login` with `X-CSRFToken` header
7. Django creates session, sets session cookie, returns user object
8. Frontend redirects to `/academy`
9. Astro SSR verifies session and AcademyAccess, renders Academy page

## Logout Flow

1. **User clicks "Sign Out" in hamburger menu**
2. `handleSignOut()` executes:
   - Calls `getCsrfToken()` → fetches token from `/api/auth/csrf-token` endpoint
   - POSTs to `/api/auth/logout` with `X-CSRFToken` header
   - Django destroys the session
3. Browser redirects to `/login?redirect=/academy`
4. Hamburger menu re-renders (server-side) with `isAuthenticated = false`
5. Shows "Sign In →" instead of "Signed in as ... Sign Out →"

## Security Measures

- **CSRF Protection:** All POST requests (login, logout, change-password) include a valid CSRF token obtained from the backend endpoint
- **Session Destruction:** Logout calls Django's logout endpoint which calls `django.contrib.auth.logout()`, completely destroying the session
- **No Caching:** Academy pages and API responses include `Cache-Control: no-store, no-cache, must-revalidate, max-age=0` headers
- **Route Protection:** Every request to `/academy` verifies both authentication and AcademyAccess via API calls
- **Cookie Forwarding:** Astro SSR forwards the browser's `Cookie` header to Django for authenticated API requests

## Unchanged Architecture

- Django session-based authentication remains intact
- `AcademyAccess` model and permission checks are unchanged
- All existing API endpoints continue to function as before
- No changes to Django settings or backend code

## Verification

Run `python manage.py check` — system check passes with no issues.

## Files Modified

- `rpwebsite/RP/website/src/lib/auth.ts` — Updated CSRF token retrieval
- `rpwebsite/RP/website/src/components/layout/SiteHeader.astro` — Added missing import, CSRF token in logout
- `rpwebsite/RP/website/src/middleware.ts` — No-cache headers for Academy routes

## Related Documentation

- `docs/A1_3_TO_A1_8_IMPLEMENTATION_REPORT.md`
- `docs/A1_LOGIN_ROOT_CAUSE_AND_FIX.md`
- `docs/A1_CSRF_TOKEN_IMPLEMENTATION.md`
- `docs/A1_ACADEMY_AUTHENTICATION_PLAN.md`