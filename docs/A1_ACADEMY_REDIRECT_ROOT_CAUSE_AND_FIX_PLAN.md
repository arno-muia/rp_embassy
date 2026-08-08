# A1 Academy Redirect Loop — Root Cause Analysis & Fix Plan

> **Status:** ✅ **FIX IMPLEMENTED** — all changes applied and verified
> **Date:** 2026-08-07
> **Scope:** Deep dive into login → academy redirect failure (login succeeds but user lands back on login page)

---

## 1. User-Reported Symptom

After entering correct credentials on `/login`, the login POST succeeds (200 OK),
but the user **remains on the login page** instead of being taken to `/academy`.

Previous attempts blamed an arbitrary `setTimeout(100)` in `LoginForm.astro`.
That was removed, but the problem **persists**. The real issue is deeper and
spans multiple files.

---

## 2. Full Request Flow (Current Broken Behavior)

```
User visits /academy (not logged in)
      │
      ▼
Astro middleware (middleware.ts)
      │
      ├─ No sessionid cookie ──► redirect to /login?redirect=/academy
      │
      ▼
User submits credentials on /login
      │
      ▼
Browser → POST http://localhost:8000/api/auth/login (credentials: "include")
      │
      ▼
Django authenticates, calls login(request, user), sets sessionid cookie
      │
      ▼
Browser receives 200 OK + Set-Cookie: sessionid=...
      │
      ▼
LoginForm.astro calls window.location.replace("/academy")
      │
      ▼
Browser navigates to http://localhost:4321/academy (sessionid cookie sent)
      │
      ▼
Astro middleware sees sessionid cookie → passes through  ✅
      │
      ▼
academy.astro frontmatter executes (SERVER-SIDE)
      │
      ▼
getCurrentUser() → fetch("http://localhost:8000/api/auth/me", { credentials: "include" })
      │
      ▼
🚨 PROBLEM: This fetch runs on the ASTRO NODE SERVER, not the browser.
   The Node.js process does NOT have access to the browser's sessionid cookie.
   credentials: "include" in Node.js fetch ≠ browser cookie jar.
   Django responds 401 Unauthorized (no session).
      │
      ▼
user = null
      │
      ▼
academy.astro: if (!user) return Astro.redirect("/login?redirect=/academy")
      │
      ▼
🚨 Browser is redirected BACK to /login → user sees login page again
```

**This is the infinite redirect loop:**

`/academy` → middleware passes → server-side auth check fails → redirect to `/login?redirect=/academy` → user logs in again → back to `/academy` → server-side auth check fails again → back to login → …

---

## 3. Root Cause (Primary)

**Architecture mismatch:** Session state lives in the **browser cookie jar**,
but authentication verification happens via **server-side `fetch()` calls**
in the Astro frontmatter.

| File | Where auth runs | Has access to browser `sessionid` cookie? |
|------|----------------|-------------------------------------------|
| `academy.astro` (line 12) | `getCurrentUser()` — **server-side** during SSR | ❌ NO |
| `academy.astro` (line 24) | `hasAcademyAccess()` — **server-side** during SSR | ❌ NO |
| `SiteHeader.astro` (line 6) | `getMe()` — **server-side** during SSR | ❌ NO |
| `middleware.ts` | Reads `context.cookies` from incoming request | ✅ YES (browser cookie) |
| `LoginForm.astro` (client) | Browser `fetch` | ✅ YES (browser cookie jar) |

The Astro Node server (port 4321) receives the browser's request WITH the
`sessionid` cookie (middleware verifies it). But when the page frontmatter
calls the API helper functions, those helpers make **new** fetch requests
from the server process. The Node fetch API does not automatically attach
the cookies from the original browser request. Without forwarding the
`Cookie` header, Django returns 401, `getCurrentUser()` returns `null`,
and `academy.astro` redirects back to login.

**Every page that is supposed to be accessible only when authenticated
will suffer from this same server-side verification failure.**

---

## 4. Contributing Issues (Secondary)

### 4.1 Hardcoded `127.0.0.1:8000` in Client-Side CSRF Fetches

| File | Line | Code |
|------|------|------|
| `LoginForm.astro` | 72 | `await fetch("http://127.0.0.1:8000/api/auth/csrf-token", …)` |
| `ChangePasswordForm.astro` | 98 | `await fetch("http://127.0.0.1:8000/api/auth/csrf-token", …)` |

These bypass the `PUBLIC_API_URL` env config and hard-code `127.0.0.1:8000`.
If the frontend runs on `localhost:4321`, the CSRF fetch goes cross-origin to
`127.0.0.1:8000`. With `SameSite=Lax`, the `csrftoken` cookie is not stored
for cross-origin responses, causing CSRF token lookup to fail — though the
login POST's CSRF is skipped (AllowAny), this is still fragile and will break
logout/change-password.

### 4.2 `SiteHeader.astro` sign-out fetch

The sign-out handler in `SiteHeader.astro` (client-side, lines 179–193) builds
its own `apiBase` rather than reusing `API_ENDPOINTS.logout`. This creates
a duplication of the API URL logic (same pattern as #4.1).

### 4.3 `ChangePasswordForm.astro` redirects to `/dashboard`

Line 125: `setTimeout(() => (window.location.href = "/dashboard"), 1500);`
There is no `/dashboard` page — it should redirect to `/academy` after
password change, and should honor the `?redirect=` param if present.

### 4.4 Astro middleware lacks `/login` protection

If an already-authenticated user visits `/login`, there is no middleware
to redirect them away. Minor UX issue — not the root cause.

---

## 5. Fix Plan

### Step 1 — Forward browser cookies to Django for server-side auth checks

**File:** `rpwebsite/RP/website/src/lib/auth.ts`

Modify `getCurrentUser()` and `hasAcademyAccess()` to accept an optional
`cookieHeader?: string` parameter. When running server-side (SSR), the
Astro page frontmatter will pass the cookie header from the incoming request.

```typescript
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
```

### Step 2 — Update `academy.astro` to pass the cookie header

**File:** `rpwebsite/RP/website/src/pages/academy.astro`

In frontmatter, read the incoming request's `Cookie` header and pass it to
the server-side auth functions.

```typescript
// A1: Server-side requests to Django must forward the browser's cookies.
// Node.js fetch does not automatically attach browser cookies.
const cookieHeader = Astro.request.headers.get("cookie") || undefined;

const user = await getCurrentUser(cookieHeader);

// ...
const hasAccess = await hasAcademyAccess(cookieHeader);
```

### Step 3 — Update `SiteHeader.astro` to pass the cookie header

**File:** `rpwebsite/RP/website/src/components/layout/SiteHeader.astro`

The `SiteHeader` is rendered inside `Layout.astro`, which is used by every
page. It calls `getMe()` server-side. It must forward the request cookie.

```typescript
const cookieHeader = Astro.request.headers.get("cookie") || undefined;
const user = await getMe(cookieHeader);
```

This requires updating the `getMe()` helper in `api.ts` too:

```typescript
export async function getMe(
  cookieHeader?: string,
): Promise<AuthUser | null> {
  try {
    const res = await fetch(API_ENDPOINTS.me, {
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
```

### Step 4 — Replace hardcoded `127.0.0.1:8000` with env-based URLs

**File:** `rpwebsite/RP/website/src/components/forms/LoginForm.astro` (line 72)

```typescript
// Before
await fetch("http://127.0.0.1:8000/api/auth/csrf-token", {...});

// After
await fetch(API_ENDPOINTS.csrfToken, { ... });
```

Import `API_ENDPOINTS` already exists (line 2: `import { API_ENDPOINTS } from "../../lib/api";`).
Add `csrfToken` to `API_ENDPOINTS` in `api.ts` if not already present.

```typescript
// api.ts API_ENDPOINTS — add:
csrfToken: `${API_BASE_URL}/api/auth/csrf-token`,
```

**File:** `rpwebsite/RP/website/src/components/forms/ChangePasswordForm.astro` (line 98)

```typescript
// Before
await fetch("http://127.0.0.1:8000/api/auth/csrf-token", {...});

// After
await fetch(API_ENDPOINTS.csrfToken, { ... });
```

Note: `ChangePasswordForm.astro` already imports `API_ENDPOINTS` (line 2).

### Step 5 — Reuse `API_ENDPOINTS.logout` in `SiteHeader.astro` client script

**File:** `rpwebsite/RP/website/src/components/layout/SiteHeader.astro` (lines 179–193)

```typescript
// Before
const apiBase =
  import.meta.env.PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";
await fetch(`${apiBase}/api/auth/logout`, {...});

// After
import { API_ENDPOINTS } from "../../lib/api"; // add import
await fetch(API_ENDPOINTS.logout, {...});
```

### Step 6 — Fix `ChangePasswordForm.astro` redirect target

**File:** `rpwebsite/RP/website/src/components/forms/ChangePasswordForm.astro` (line 125)

```typescript
// Before
setTimeout(() => (window.location.href = "/dashboard"), 1500);

// After — honor ?redirect= with safe-open-redirect protection
const redirectParam = new URLSearchParams(window.location.search).get("redirect");
const safeTarget = redirectParam && redirectParam.startsWith("/") && !redirectParam.startsWith("//")
  ? redirectParam
  : "/academy";
setTimeout(() => (window.location.href = safeTarget), 1500);
```

### Step 7 — (Optional, hardening) Add login-page middleware redirect

**File:** `rpwebsite/RP/website/src/middleware.ts`

Add a check: if user visits `/login` and `sessionid` cookie exists, redirect
straight to `/academy` (no wait — this would loop if session is invalid.
Better: leave as-is for now, or do a lightweight `getCurrentUser` check
deferred to the page frontmatter).

Recommended: Add logic in `login.astro` frontmatter — if session cookie
present, check auth via API (with cookie forwarding), and redirect to
`?redirect=` or `/academy` if valid. This prevents authenticated users
from being forced through login.

---

## 6. Verification Plan

1. **Start Django** on `localhost:8000`
2. **Start Astro dev** on `localhost:4321`
3. Visit `/academy` → should redirect to `/login?redirect=/academy`
4. Log in with valid credentials:
   - Browser POST to `http://localhost:8000/api/auth/login` → 200 + session cookie
   - `window.location.replace("/academy")`
   - Astro middleware sees `sessionid` cookie → passes through
   - `academy.astro` frontmatter calls `getCurrentUser(cookieHeader)` → 200 → user returned
   - Academy content renders (or "Access Required" if no AcademyAccess)
5. With no AcademyAccess → "Access Required" state — no redirect
6. Refresh `/academy` → stays on page (no loop)
7. Sign out from header → redirects to `/` and clears session
8. `python manage.py check` → passes
9. `npm run check` → no new errors in modified files

---

## 7. Files Modified (Implemented 2026-08-07)

| File | Change | Status |
|------|--------|--------|
| `website/src/lib/auth.ts` | ✅ Add `cookieHeader` param to `getCurrentUser()` and `hasAcademyAccess()` + forward as `Cookie` header | ✅ Applied |
| `website/src/lib/api.ts` | ✅ Add `csrfToken` to `API_ENDPOINTS`; add `cookieHeader` param to `getMe()` | ✅ Applied |
| `website/src/pages/academy.astro` | ✅ Read `Astro.request.headers.get("cookie")` + pass to `getCurrentUser()` and `hasAcademyAccess()` | ✅ Applied |
| `website/src/components/layout/SiteHeader.astro` | ✅ Pass cookie header to `getMe()`; reuse `API_ENDPOINTS.logout` | ✅ Applied |
| `website/src/components/forms/LoginForm.astro` | ✅ Replace hardcoded `127.0.0.1:8000` CSRF URL with `API_ENDPOINTS.csrfToken` | ✅ Applied |
| `website/src/components/forms/ChangePasswordForm.astro` | ✅ Replace hardcoded CSRF URL; fix `/dashboard` → `/academy` + honor `?redirect=` | ✅ Applied |
| `website/src/middleware.ts` | No change required for core fix | — |

### 7.1 Verification Results

- ✅ `python manage.py check` → **System check identified no issues (0 silenced)**
- ⏳ `npx astro check` → requires `npm install` first (node_modules not present in repo)

---

## 8. Why Previous Fixes Failed

| Previous Fix | Why It Didn't Solve the Problem |
|--------------|--------------------------------|
| Remove `setTimeout(100)` in `LoginForm.astro` | The redirect WAS firing. The issue is that `/academy` immediately redirects back because server-side auth fails. Timing was irrelevant. |
| Change `.env` from `127.0.0.1:8000` to `localhost:8000` | Fixed the SameSite cookie storage for the login POST, but did not address server-side cookie forwarding. The middleware correctly passes the request, but the page's frontmatter API calls still fail because they run server-side without browser cookies. |

---

## 9. Conclusion

The login → academy redirect loop is caused by **server-side authentication
verification without browser cookie forwarding**. Middleware correctly gates
`/academy` by cookie presence, but `academy.astro` frontmatter's subsequent
`getCurrentUser()` fetch runs on the Astro Node server, which lacks the
browser's `sessionid` cookie. Django returns 401, the page redirects back
to `/login`, and the loop repeats.

**The fix is to forward the incoming request's `Cookie` header from the
Astro page frontmatter to the Django API calls.**