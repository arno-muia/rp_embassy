# A1 — Academy Authentication & Authorization Plan

> **Status:** DRAFT — Awaiting manual review and go-ahead before implementation.
> **Date:** 2026-07-30
> **Owner:** Engineering
> **Related:** `AI_RULES.md`, `MEMORY.md`, `B1_PERMISSION_MATRIX.md`

---

## 1. Objective

Make the **Academy** (`/academy`) a members-only learning portal. Only
authorized, authenticated members of Royal Priesthood Embassy may access the
academy page and its module catalog. Unauthenticated visitors are redirected to
the sign-in page; unauthorized (e.g. inactive) accounts are shown a clear
"access required" state.

This plan covers the **full vertical slice**: backend authentication
infrastructure (which is currently missing), authorization rules, frontend
route protection, and mobile-menu integration.

---

## 2. Current State Audit

### 2.1 What exists today

| Layer | File | Current behavior |
|-------|------|-----------------|
| Backend `User` model | `backend/apps/accounts/models.py` | Custom model with `password_hash` (bcrypt, `db_column='passwordHash'`), `role`, `is_active`, `failed_login_attempts`, `locked_until`, `must_change_password`. `managed=False` (maps to Prisma-owned `User` table). |
| Backend `Member` model | `backend/apps/members/models.py` | OneToOne `user` FK to `accounts.User`; has `status` (ACTIVE/INACTIVE/TRANSFERRED/DECEASED) and `discipleship_level`. |
| Backend academy API | `backend/apps/content/views.py` → `AcademyModuleViewSet` | `permission_classes = [AllowAny]` — **fully public**. |
| Backend URL routing | `backend/urls.py` | Includes content, events, prayer, health. **No auth URLs.** |
| Backend accounts app | `backend/apps/accounts/` | Has `models.py`, `repositories.py`, `services.py`, `serializers.py`. **No `views.py`, no `urls.py`.** |
| Frontend login | `website/src/pages/login.astro` + `LoginForm.astro` | POSTs to `API_ENDPOINTS.login` (`/api/auth/login`). On success redirects to `/dashboard`. **Endpoint does not exist on backend.** |
| Frontend academy | `website/src/pages/academy.astro` | Public. Fetches `getAcademyModules()` and renders catalog. CTA links to external `site.academyUrl`. |
| Frontend mobile menu | `website/src/components/layout/SiteHeader.astro` | Shows Academy link to everyone; "Sign In →" link to `/login`. |
| Frontend API client | `website/src/lib/api.ts` | Defines `login` and `changePassword` endpoints. No session/token handling, no `credentials: 'include'`. |
| Settings | `backend/settings.py` | DRF installed, sessions middleware present, `CORS_ALLOW_CREDENTIALS=True`. **No `REST_FRAMEWORK` config, no `AUTHENTICATION_BACKENDS`, no `AUTH_USER_MODEL`.** |

### 2.2 Key gaps

1. **No backend auth endpoints** — login/logout/session-check/change-password
   do not exist, even though the frontend already calls them.
2. **No custom auth backend** — Django's default backend authenticates against
   `password` on `django.contrib.auth.User`, but our `User` model stores the
   hash in `password_hash`. A custom backend is required.
3. **Academy API is public** — `AllowAny` must be replaced with an authorization
   rule.
4. **No frontend auth state** — no session cookie handling, no protected-route
   guard, no "current user" concept.
5. **No Astro middleware** — `/academy` is reachable by anyone.

---

## 3. Design Decisions

### 3.1 Authentication mechanism: **Session-based**

**Choice:** Django server-side sessions (cookie-based).

**Rationale:**
- Session middleware is already configured.
- `CORS_ALLOW_CREDENTIALS = True` is already set.
- The frontend uses `fetch` (can send/receive cookies with `credentials: 'include'`).
- This is a church website with modest scale — JWT complexity is not warranted.
- Aligns with the existing `LoginForm` which expects a simple POST + redirect flow.

**Rejected alternatives:**
- *JWT tokens* — adds a token-refresh layer and storage decisions that are
  unnecessary for this use case.
- *Django default auth* — cannot work because the `User` model does not use
  Django's `password` field.

### 3.2 Who is an "authorized member"?

**Definition (proposed):** A user is *authorized for academy access* when **all** are true:

1. Authenticated (valid session).
2. `User.is_active = True`.
3. Account is not locked (`locked_until` is null or in the past).
4. Has a linked `Member` record with `status = ACTIVE`.

> **Open question for reviewer:** Should academy access also be gated by
> `discipleship_level` (e.g. only DISCIPLE and above), or is "active member"
> sufficient? The default plan assumes **active member = authorized**. This is
> easy to tighten later via a single permission class.

### 3.3 Password verification

The `User.password_hash` field stores a bcrypt hash. The custom auth backend
will use `bcrypt.checkpw()` to verify submitted passwords against
`user.password_hash`. We will **not** use `django.contrib.auth.hashers` because
the hash format/column differs from Django's default.

### 3.4 Security hardening (reusing existing model fields)

The `User` model already has lockout fields. The login service will enforce:
- Increment `failed_login_attempts` on bad password.
- Lock the account (set `locked_until` = now + lockout window) after N failed
  attempts (configurable, default 5).
- Reset `failed_login_attempts` on successful login.
- Record `AuditLog` entries for LOGIN, LOGOUT, ACCOUNT_LOCKED.
- Enforce `must_change_password` by returning a flag the frontend uses to
  force the change-password flow before academy access.

---

## 4. Implementation Plan

### Phase A1.1 — Backend authentication infrastructure

#### A1.1.1 Custom authentication backend
**New file:** `backend/apps/accounts/backends.py`

- `PasswordHashBackend` — authenticates using `email` + `password` against
  `User.password_hash` via `bcrypt.checkpw`.
- Returns the `User` instance on success, `None` on failure.
- Registered in `settings.AUTHENTICATION_BACKENDS`.

#### A1.1.2 Auth services
**Edit:** `backend/apps/accounts/services.py`

Add an `AuthService` (or extend `UserService`) with:
- `login(email, password, request)` → verifies credentials, checks lockout,
  updates `last_login`, resets fail counter, writes `AuditLog`, calls
  `django.contrib.auth.login()` to create the session.
- `logout(request)` → writes `AuditLog`, calls `django.contrib.auth.logout()`.
- `current_user(request)` → returns the authenticated `User` or `None`.
- `change_password(user, old_password, new_password)` → verifies old password,
  sets new `password_hash`, clears `must_change_password`, writes `AuditLog`.

#### A1.1.3 Auth serializers
**Edit:** `backend/apps/accounts/serializers.py`

Add:
- `LoginSerializer` — `email`, `password` (write-only).
- `UserSerializer` — public user fields (`id`, `email`, `name`, `role`,
  `must_change_password`).
- `ChangePasswordSerializer` — `old_password`, `new_password` (with validators).

#### A1.1.4 Auth views
**New file:** `backend/apps/accounts/views.py`

- `POST /api/auth/login` — accepts credentials, returns `UserSerializer` +
  session cookie. Honors `must_change_password` flag.
- `POST /api/auth/logout` — destroys session.
- `GET /api/auth/me` — returns current user or `401`.
- `POST /api/auth/change-password` — requires auth; changes password.

#### A1.1.5 Auth URLs
**New file:** `backend/apps/accounts/urls.py`

Wire the four views above under `auth/`.

#### A1.1.6 URL include
**Edit:** `backend/urls.py`

Add `path('api/', include('backend.apps.accounts.urls'))`.

#### A1.1.7 Settings
**Edit:** `backend/settings.py`

- Add `AUTHENTICATION_BACKENDS = ['backend.apps.accounts.backends.PasswordHashBackend']`.
- Add `REST_FRAMEWORK = { 'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'], 'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'] }`.
- Add session cookie hardening: `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE='LAX'`, `SESSION_COOKIE_SECURE` (prod), `SESSION_COOKIE_AGE`.
- Add `ACADEMY_LOCKOUT_THRESHOLD = 5`, `ACADEMY_LOCKOUT_DURATION_MINUTES = 15`.

> **Note:** Setting `DEFAULT_PERMISSION_CLASSES` to `IsAuthenticated` is safe
> because every existing public view explicitly declares `AllowAny`.

---

### Phase A1.2 — Academy authorization

#### A1.2.1 Permission class
**New file:** `backend/apps/accounts/permissions.py`

- `IsAuthorizedMember` — allows access only when the authenticated user has an
  active `Member` record (`status = ACTIVE`). Returns `403` otherwise.

#### A1.2.2 Academy viewset lockdown
**Edit:** `backend/apps/content/views.py`

Change `AcademyModuleViewSet.permission_classes` from `[AllowAny]` to
`[IsAuthenticated, IsAuthorizedMember]`.

> **Impact:** The public academy page will no longer be able to fetch modules
  anonymously. The frontend must authenticate first (see A1.3).

---

### Phase A1.3 — Frontend auth state & API client

#### A1.3.1 Auth API helpers
**Edit:** `website/src/lib/api.ts`

- Add `credentials: 'include'` to all `fetch` calls (so the session cookie is sent).
- Add `login(email, password)`, `logout()`, `getMe()`, `changePassword(old, new)`.
- Add `API_ENDPOINTS.me`, `API_ENDPOINTS.logout`.

#### A1.3.2 Auth utilities
**New file:** `website/src/lib/auth.ts`

- `getCurrentUser()` — calls `/api/auth/me`; returns user or `null`.
- `requireAuth()` — used by protected pages; throws/redirects if not authed.
- Types: `AuthUser` (`id`, `email`, `name`, `role`, `mustChangePassword`).

---

### Phase A1.4 — Frontend route protection

#### A1.4.1 Astro middleware
**New file:** `website/src/middleware.ts`

- Intercept requests to `/academy` (and `/academy/**`).
- Call `/api/auth/me` (server-side, forwarding cookies) to check the session.
- If not authenticated → redirect to `/login?redirect=/academy`.
- If authenticated but `must_change_password` → redirect to `/change-password`.
- If authenticated but no active member → render an "access required" page
  (or redirect to `/academy?unauthorized=1`).

> **Astro note:** Middleware runs on every request; the `/api/auth/me` call is
> cheap (single DB lookup). Alternatively, we can read the session cookie
> directly via a server endpoint — but calling the API keeps a single source
> of truth.

#### A1.4.2 Academy page update
**Edit:** `website/src/pages/academy.astro`

- In frontmatter, call `getCurrentUser()`; if null, the middleware already
  redirected, but keep a defensive check.
- Pass the user to the UI (e.g. show "Welcome, {name}").
- Keep the public "What is Kingdom Formation?" intro visible to all, but gate
  the **Module Catalog** behind auth (the API will 401/403 if not authorized).
- Add an "Access required" state for users who are authenticated but not active
  members.

#### A1.4.3 Login flow update
**Edit:** `website/src/components/forms/LoginForm.astro`

- Read `?redirect=` query param; after successful login, redirect there
  (default `/dashboard`).
- If response includes `must_change_password: true`, redirect to
  `/change-password?redirect=<original>`.

---

### Phase A1.5 — Mobile menu & navigation

#### A1.5.1 SiteHeader update
**Edit:** `website/src/components/layout/SiteHeader.astro`

- The Academy link in the mobile menu should indicate it is members-only
  (e.g. a small lock icon or "Members" badge).
- Optionally fetch `/api/auth/me` on the client to show "Sign Out" instead of
  "Sign In →" when authenticated. (Client-side only; server middleware remains
  the real gate.)

#### A1.5.2 Sign-out affordance
**New file:** `website/src/components/auth/SignOutButton.astro` (or inline in header)

- Calls `logout()`, then redirects to `/`.

---

## 5. Affected Files Summary

### New files
| File | Purpose |
|------|---------|
| `backend/apps/accounts/backends.py` | Custom bcrypt auth backend |
| `backend/apps/accounts/views.py` | Login/logout/me/change-password views |
| `backend/apps/accounts/urls.py` | Auth URL routing |
| `backend/apps/accounts/permissions.py` | `IsAuthorizedMember` permission |
| `website/src/lib/auth.ts` | Frontend auth helpers & types |
| `website/src/middleware.ts` | Astro route protection for `/academy` |
| `website/src/components/auth/SignOutButton.astro` | Sign-out UI |

### Edited files
| File | Change |
|------|--------|
| `backend/apps/accounts/services.py` | Add `AuthService` (login/logout/change-password) |
| `backend/apps/accounts/serializers.py` | Add login/user/change-password serializers |
| `backend/apps/content/views.py` | Lock down `AcademyModuleViewSet` |
| `backend/urls.py` | Include accounts urls |
| `backend/settings.py` | Auth backends, DRF session auth, cookie hardening, lockout config |
| `website/src/lib/api.ts` | `credentials: 'include'`, auth endpoints, auth fetch helpers |
| `website/src/pages/academy.astro` | Gated catalog, user-aware UI, access-required state |
| `website/src/components/forms/LoginForm.astro` | `redirect` param, `must_change_password` handling |
| `website/src/components/layout/SiteHeader.astro` | Members-only Academy indicator, sign-out |

---

## 6. Data Flow (post-implementation)

```
Visitor opens /academy
        │
        ▼
Astro middleware ──► GET /api/auth/me (with session cookie)
        │
        ├─ 401 (no session) ──► 302 /login?redirect=/academy
        │
        ├─ 200 + must_change_password ──► 302 /change-password
        │
        └─ 200 + active member ──► render academy page
                                    │
                                    ▼
                              GET /api/academy (with cookie)
                                    │
                                    ▼
                              IsAuthorizedMember ✓ ──► module catalog
```

---

## 7. API Contract (new endpoints)

| Method | Path | Auth | Body | Success | Error |
|--------|------|------|------|---------|-------|
| POST | `/api/auth/login` | None | `{email, password}` | `200 {user}` + session cookie | `401 {error}` |
| POST | `/api/auth/logout` | Session | — | `200 {success:true}` | — |
| GET | `/api/auth/me` | Session | — | `200 {user}` | `401` |
| POST | `/api/auth/change-password` | Session | `{old_password, new_password}` | `200 {success:true}` | `400 {errors}` |
| GET | `/api/academy` | `IsAuthorizedMember` | — | `200 [modules]` | `401` / `403` |

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Changing `DEFAULT_PERMISSION_CLASSES` could accidentally lock public endpoints. | Every existing public view already declares `AllowAny` explicitly; audit via `grep` before/after. |
| `bcrypt` may not be installed. | Verify `bcrypt` in `Pipfile`/`requirements`; add if missing. The `password_hash` is bcrypt, so it is required. |
| Session cookie not sent cross-origin (Astro :4321 → Django :8000). | `CORS_ALLOW_CREDENTIALS=True` already set; ensure `SameSite=Lax` and both origins in `CORS_ALLOWED_ORIGINS`. |
| `User` model is `managed=False` — cannot add fields via migration. | We add **no** new columns to `User`; we only read existing fields. New models (if any) are Django-owned. |
| Academy page SEO — gating content may reduce crawlability. | Keep the intro/hero public; only the module catalog is gated. Add a public landing description. |
| Existing `/dashboard` redirect in `LoginForm` may not exist. | Keep `/dashboard` as default but prefer `?redirect=` param. |

---

## 9. Validation Plan

After implementation, verify:

1. **Backend**
   - `python manage.py check` passes.
   - `POST /api/auth/login` with valid creds returns 200 + `Set-Cookie`.
   - `POST /api/auth/login` with bad creds returns 401 and increments
     `failed_login_attempts`.
   - `GET /api/auth/me` without cookie returns 401; with cookie returns user.
   - `GET /api/academy` without auth returns 401; with auth + active member
     returns 200; with auth + inactive member returns 403.
2. **Frontend**
   - `npm run check` and `npm run build` pass.
   - Visiting `/academy` while logged out redirects to `/login?redirect=/academy`.
   - After login, user is returned to `/academy`.
   - `must_change_password` users are sent to `/change-password` first.
   - Mobile menu shows the Academy link with a members-only indicator.
3. **Security**
   - Lockout triggers after 5 failed attempts.
   - `AuditLog` entries are written for login/logout/lockout.
   - Session cookie is `HttpOnly` and `SameSite=Lax`.

---

## 10. Out of Scope (explicitly)

- Academy **content authoring** (lessons, videos, progress tracking) — this
  plan is only about **access control**.
- The external `rpacademy.vercel.app` LMS — the "Enroll at Academy" CTA remains
  external and is unaffected.
- Password reset / forgot-password flow — can be a follow-up phase.
- Member self-registration — accounts are created by admins (existing pattern).

---

## 11. Open Questions for Reviewer

1. **Authorization rule:** Is "active member" sufficient, or should academy
   access require a minimum `discipleship_level` (e.g. DISCIPLE+)?
2. **Public preview:** Should the "What is Kingdom Formation?" intro remain
   public, or should the entire `/academy` page require login?
3. **Lockout policy:** Are 5 attempts / 15 minutes acceptable, or does the
   church have an existing policy?
4. **Session lifetime:** Default Django session age (2 weeks) — acceptable, or
   shorter for a church portal?
5. **`/dashboard`:** Does this page exist? If not, where should login redirect
   by default (e.g. `/academy`)?

---

## 12. Implementation Order (once approved)

1. A1.1 — Backend auth infrastructure (backend can be tested in isolation).
2. A1.2 — Academy authorization (lock the endpoint).
3. A1.3 — Frontend auth client (wire up the API).
4. A1.4 — Route protection (middleware + academy page).
5. A1.5 — Mobile menu + sign-out.
6. Validation per §9.
7. Update `MEMORY.md` with phase summary.

---

**End of plan.** No code will be changed until this document is reviewed and
explicit go-ahead is given.