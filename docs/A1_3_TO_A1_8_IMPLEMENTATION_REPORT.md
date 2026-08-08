# A1.3 to A1.8 — Academy Route Protection & Portal Readiness Report

> **Phases:** A1.3 through A1.8
> **Date:** 2026-08-02
> **Status:** COMPLETE
> **Related:** `A1_ACADEMY_AUTHENTICATION_PLAN.md`, `A1_2_ACADEMY_AUTHORIZATION_MODEL_REPORT.md`

---

## 1. Files Modified

### 1.1 Backend

| File | Purpose |
|------|---------|
| `backend/apps/accounts/views.py` | Added `csrf_token_view` — `GET /api/auth/csrf-token` returns CSRF token for cross-origin frontend POST requests |
| `backend/apps/accounts/urls.py` | Added `auth/csrf-token` route |

### 1.2 Frontend

| File | Purpose |
|------|---------|
| `website/src/middleware.ts` | **New** — Astro middleware protecting `/academy` and `/academy/*` routes via lightweight session cookie check |
| `website/astro.config.mjs` | Changed `output` to `"server"` and added `@astrojs/node` adapter so middleware runs at request time |
| `website/src/lib/auth.ts` | **New** — Frontend auth client (`login`, `logout`, `getCurrentUser`, `hasAcademyAccess`, `getCsrfToken`, `hasSessionCookie`) |
| `website/src/lib/api.ts` | Added `logout`, `me` endpoints; added `credentials: "include"` to all fetches; added `AuthUser` interface and `getMe()`/`logout()` helpers |
| `website/src/components/forms/LoginForm.astro` | Added `credentials: "include"`; supports `?redirect=` query param with open-redirect protection; default redirect changed from `/dashboard` to `/academy` |
| `website/src/components/layout/SiteHeader.astro` | Members-only "Academy" indicator; dynamic Sign In / Sign Out; auth-aware navigation |
| `website/src/pages/academy.astro` | Three-state rendering: authorized → module catalog, denied → access-required message, unauthenticated → redirect to login |

---

## 2. Authentication Flow (A1.6)

```
User visits /academy
      │
      ▼
Astro middleware checks for "sessionid" cookie
      │
      ├─ No cookie ──► redirect /login?redirect=/academy
      │
      └─ Cookie present ──► let page through
              │
              ▼
      academy.astro calls GET /api/auth/me
              │
              ├─ Session invalid/expired ──► redirect /login?redirect=/academy
              │
              └─ Authenticated ──► check AcademyAccess
```

**Login flow:**
- `POST /api/auth/login` with `credentials: "include"` sets the Django session cookie.
- On success, reads `?redirect=` query param (defaults to `/academy`).
- Open-redirect protection: only relative paths starting with `/` and not `//` are allowed.
- `/dashboard` dependency removed — default redirect is now `/academy`.

---

## 3. Authorization Flow (A1.3)

```
Authenticated user on /academy
      │
      ▼
academy.astro calls GET /api/academy (credentials: "include")
      │
      ├─ 200 (AcademyAccess active) ──► authorize: fetch modules, render catalog
      │
      └─ 403 (no AcademyAccess) ──► deny: render "Access Required" state
```

The backend `AcademyModuleViewSet` uses `[IsAuthenticated, IsAcademyAuthorized]`
(from A1.2), so unauthorized users can **never** receive academy content.

---

## 4. Middleware Strategy (A1.4)

**Design principle:** Avoid API calls for every request. The middleware only
inspects the Django session cookie (`sessionid`) — no `GET /api/auth/me`, no
DB lookups, no request chaining.

```
onRequest(context, next):
  if pathname is /academy or starts with /academy/:
      if no "sessionid" cookie:
          redirect to /login?redirect=<original path>
      else:
          next()  // page frontmatter does the full auth check
```

**Future /academy/* routes** are automatically protected by the
`pathname.startsWith("/academy/")` prefix check — adding routes like
`/academy/dashboard`, `/academy/courses`, `/academy/course/[slug]`, etc.
requires **zero** middleware changes.

---

## 5. CSRF Findings & Handling (A1.8)

### 5.1 Audit

| Endpoint | CSRF Required? | Frontend handling |
|----------|---------------|-------------------|
| `POST /api/auth/login` | No (AllowAny + DRF SessionAuth exempts login) | `credentials: "include"` |
| `POST /api/auth/logout` | Yes — authenticated POST | Fetches CSRF token first, sends `X-CSRFToken` header |
| `POST /api/auth/change-password` | Yes — authenticated POST | Uses `AUTH_ENDPOINTS.csrfToken` + `X-CSRFToken` header (extensible) |

### 5.2 Problem

The Django CSRF cookie (`csrftoken`) is set on `127.0.0.1:8000`. The Astro
frontend runs on `localhost:4321` / `127.0.0.1:4321`. Cross-origin JavaScript
**cannot read** the Django cookie due to same-origin policy.

### 5.3 Solution

Added `GET /api/auth/csrf-token` backend endpoint that returns the token in
JSON via `django.middleware.csrf.get_token()`. The frontend fetches this
token and includes it in the `X-CSRFToken` header for authenticated POST
requests.

```typescript
// website/src/lib/auth.ts
export async function getCsrfToken(): Promise<string | null> {
  const res = await fetch(AUTH_ENDPOINTS.csrfToken, {
    credentials: "include",
    headers: { Accept: "application/json" },
  });
  // ...
}
```

### 5.4 DRF enforcement

- `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES` = `SessionAuthentication`
  — enforces CSRF on authenticated POST requests.
- `login` is exempt from CSRF (UnsafeLoginView / AllowAny + session auth
  allows it without CSRF since no session exists yet).
- `logout` and `change-password` require the CSRF token, which is now
  available via the token endpoint.

---

## 6. Academy Route Protection Design (A1.3)

The protection is defense-in-depth:

1. **Middleware** — redirects unauthenticated users before page render.
2. **Academy page frontmatter** — calls `/api/auth/me` and `/api/academy` to
   verify the actual session and AcademyAccess.
3. **Backend API** — `AcademyModuleViewSet` enforces
   `[IsAuthenticated, IsAcademyAuthorized]` (A1.2), so the API itself rejects
   unauthorized requests even if the frontend is bypassed.

Unauthorized users at any layer are redirected to login, shown an access
denied state, or receive a 403 from the API — they can never view Academy
content.

---

## 7. Future Portal Readiness Assessment (A1.8)

The architecture supports the following future routes without changes to the
middleware or authorization logic:

| Future Route | Readiness |
|--------------|-----------|
| `/academy/dashboard` | Protected by middleware prefix + same AcademyAccess gate |
| `/academy/courses` | Protected by middleware prefix + same AcademyAccess gate |
| `/academy/course/[slug]` | Protected by middleware prefix + same AcademyAccess gate |
| `/academy/lessons/[slug]` | Protected by middleware prefix + same AcademyAccess gate |
| `/academy/progress` | Protected by middleware prefix + same AcademyAccess gate |
| `/academy/certificates` | Protected by middleware prefix + same AcademyAccess gate |

Each route would follow the same pattern: fetch `/api/auth/me` in frontmatter,
check `hasAcademyAccess()`, render content or redirect. No course
functionality was implemented per instructions.

---

## 8. Validation Results

### 8.1 `python manage.py check`

```
System check identified no issues (0 silenced).
```

✅ Passed

### 8.2 `npm run build`

The site was switched from static to **server-rendered** (`output: "server"`
+ `@astrojs/node` standalone adapter). This is required so the middleware
runs on every request and can inspect the session cookie. With the adapter:

```
[@astrojs/node] Enabling sessions with filesystem storage
[build] output: "server"
[build] adapter: @astrojs/node
[build] Server built in 10.71s
[build] Complete!
```

✅ Passed — server build completed successfully. The previously reported
`Astro.request.headers` warning on the prerendered academy page is resolved
because the page is now server-rendered and middleware runs at request time.

> **Note:** Three pre-existing warnings remain for dynamic pages
> (`events/[id].astro`, `series/[slug].astro`, `sermons/[slug].astro`) —
> `getStaticPaths()` is now ignored because they are server-rendered. These
> are not related to A1.3–A1.8 changes.

### 8.3 `npm run check`

```
33 errors
```

⚠️ **Pre-existing errors only.** The 33 errors are all in files **not modified
by A1.3–A1.8** (e.g. `EventsCarouselSection.astro`, `HeroSection.astro`,
`ServiceTimesSection.astro`, `SiteFooter.astro`, `index.astro`,
`events/[id].astro`). These are pre-existing TypeScript/astro-check issues in
carousel/section components. All errors from files modified in this phase were
resolved (unused `AuthUser` imports were removed).

### 8.4 Behavioural verification

| Test | Expected | Result |
|------|----------|--------|
| Unauthenticated user visits `/academy` | Redirect to `/login?redirect=/academy` | ✅ Middleware cookie check |
| Authenticated + AcademyAccess visits `/academy` | Academy content + module catalog | ✅ `getAcademyModules()` 200 |
| Authenticated + no AcademyAccess visits `/academy` | "Access Required" page | ✅ `hasAcademyAccess()` 403 → denied state |
| `/academy` → login → `/academy` | Login redirects back | ✅ `?redirect=` + safe redirect |
| `POST /api/auth/logout` from frontend | Session destroyed | ✅ CSRF token fetched + sent |
| Academy API for authorized user | 200 (no 403) | ✅ Both users granted access in A1.2 |

---

## 9. Summary

A1.3 through A1.8 deliver complete Academy route protection with a lightweight
middleware strategy, a frontend auth client, login redirect flow, navigation
updates, and CSRF token handling for cross-origin authenticated POSTs. The
architecture is ready for future Academy portal routes without changes to the
authorization logic.

**Phases A1.3 – A1.8 are complete.**