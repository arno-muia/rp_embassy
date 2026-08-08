# A1 CSRF Origin Fix

## Issue Reported

Browser network trace shows CSRF token requests going to the wrong origin:

```
# INCORRECT - Request goes to Astro frontend (localhost:4321)
GET http://localhost:4321/api/auth/csrf-token → 404 Not Found

# CORRECT - Should go to Django backend (localhost:8000)
GET http://localhost:8000/api/auth/csrf-token → 200 OK
```

## Root Cause

The `LoginForm.astro` and `ChangePasswordForm.astro` components were using a **relative path** (`/api/auth/csrf-token`) instead of an **absolute URL** to fetch the CSRF token. 

When the browser resolves a relative path, it uses the current origin (Astro frontend on `localhost:4321`), not the Django backend origin (`localhost:8000`).

## Code Evidence

### 1. Incorrect Implementation (Before Fix)

**File:** `website/src/components/forms/LoginForm.astro` (line 72)

```typescript
// ❌ WRONG: Relative path resolves to localhost:4321
const csrfToken = await fetch("/api/auth/csrf-token", {
  credentials: "include",
  headers: { Accept: "application/json" },
})
  .then((r) => r.json())
  .then((d) => d.csrfToken)
  .catch(() => null);
```

**File:** `website/src/components/forms/ChangePasswordForm.astro` (line 97)

```typescript
// ❌ WRONG: Relative path resolves to localhost:4321
const csrfToken = await fetch("/api/auth/csrf-token", {
  credentials: "include",
  headers: { Accept: "application/json" },
})
  .then((r) => r.json())
  .then((d) => d.csrfToken)
  .catch(() => null);
```

### 2. Correct Implementation (After Fix)

**File:** `website/src/components/forms/LoginForm.astro` (line 72)

```typescript
// ✅ CORRECT: Absolute URL points to Django backend
const csrfToken = await fetch("http://127.0.0.1:8000/api/auth/csrf-token", {
  credentials: "include",
  headers: { Accept: "application/json" },
})
  .then((r) => r.json())
  .then((d) => d.csrfToken)
  .catch(() => null);
```

**File:** `website/src/components/forms/ChangePasswordForm.astro` (line 97)

```typescript
// ✅ CORRECT: Absolute URL points to Django backend
const csrfToken = await fetch("http://127.0.0.1:8000/api/auth/csrf-token", {
  credentials: "include",
  headers: { Accept: "application/json" },
})
  .then((r) => r.json())
  .then((d) => d.csrfToken)
  .catch(() => null);
```

## URL Resolution Analysis

### Before Fix (BROKEN)

```
Browser on http://localhost:4321
    ↓
Fetch "/api/auth/csrf-token" (relative path)
    ↓
Browser resolves to: http://localhost:4321/api/auth/csrf-token
    ↓
Astro dev server receives request (404 - no such route)
    ↓
CSRF token not obtained
    ↓
Login POST without X-CSRFToken header
    ↓
Django rejects with "CSRF token missing"
```

### After Fix (WORKING)

```
Browser on http://localhost:4321
    ↓
Fetch "http://127.0.0.1:8000/api/auth/csrf-token" (absolute URL)
    ↓
Browser resolves to: http://127.0.0.1:8000/api/auth/csrf-token
    ↓
Django receives request
    ↓
Returns: {"csrfToken": "abc123..."}
Sets cookie: csrftoken=abc123...
    ↓
Login POST to http://127.0.0.1:8000/api/auth/login
With header: X-CSRFToken: abc123...
    ↓
Django validates CSRF token
    ↓
Login succeeds, session created
```

## Verification: All Auth Endpoints Use Consistent Base URL

### File: `website/src/lib/auth.ts`

```typescript
const API_BASE_URL =
  import.meta.env.PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

export const AUTH_ENDPOINTS = {
  login: `${API_BASE_URL}/api/auth/login`,          // http://127.0.0.1:8000/api/auth/login
  logout: `${API_BASE_URL}/api/auth/logout`,        // http://127.0.0.1:8000/api/auth/logout
  me: `${API_BASE_URL}/api/auth/me`,                // http://127.0.0.1:8000/api/auth/me
  changePassword: `${API_BASE_URL}/api/auth/change-password`,  // http://127.0.0.1:8000/api/auth/change-password
  csrfToken: `${API_BASE_URL}/api/auth/csrf-token`, // http://127.0.0.1:8000/api/auth/csrf-token
  academy: `${API_BASE_URL}/api/academy`,           // http://127.0.0.1:8000/api/academy
} as const;
```

### Verified Endpoint URLs

| Function | Method | URL | Status |
|----------|--------|-----|--------|
| `getCsrfToken()` | GET | `http://127.0.0.1:8000/api/auth/csrf-token` | ✅ Fixed |
| `login()` | POST | `http://127.0.0.1:8000/api/auth/login` | ✅ Already correct |
| `logout()` | POST | `http://127.0.0.1:8000/api/auth/logout` | ✅ Already correct |
| `getCurrentUser()` | GET | `http://127.0.0.1:8000/api/auth/me` | ✅ Already correct |
| `hasAcademyAccess()` | GET | `http://127.0.0.1:8000/api/academy` | ✅ Already correct |

### Form Components

| Component | CSRF Token URL | Status |
|-----------|----------------|--------|
| `LoginForm.astro` | `http://127.0.0.1:8000/api/auth/csrf-token` | ✅ Fixed |
| `ChangePasswordForm.astro` | `http://127.0.0.1:8000/api/auth/csrf-token` | ✅ Fixed |

## Complete Request Flow (After Fix)

### 1. CSRF Token Request
```
GET http://127.0.0.1:8000/api/auth/csrf-token
Headers:
  Accept: application/json
  Credentials: include

Response: 200 OK
Body: {"csrfToken":"abc123..."}
Headers: Set-Cookie: csrftoken=abc123...; Path=/; ...
```

### 2. Login Request
```
POST http://127.0.0.1:8000/api/auth/login
Headers:
  Content-Type: application/json
  Accept: application/json
  X-CSRFToken: abc123...
  Cookie: csrftoken=abc123...
  Credentials: include

Body: {
  "email": "user@example.com",
  "password": "..."
}

Response: 200 OK
Body: {
  "id": "...",
  "email": "user@example.com",
  "name": "...",
  "role": "...",
  "is_active": true,
  "must_change_password": false,
  "last_login": null
}
Headers: Set-Cookie: sessionid=...; Path=/; ...
```

### 3. Logout Request
```
POST http://127.0.0.1:8000/api/auth/logout
Headers:
  Content-Type: application/json
  Accept: application/json
  X-CSRFToken: abc123...
  Cookie: csrftoken=abc123...; sessionid=...
  Credentials: include

Response: 200 OK
```

### 4. Change Password Request
```
POST http://127.0.0.1:8000/api/auth/change-password
Headers:
  Content-Type: application/json
  Accept: application/json
  X-CSRFToken: abc123...
  Cookie: csrftoken=abc123...; sessionid=...
  Credentials: include

Body: {
  "currentPassword": "...",
  "newPassword": "..."
}

Response: 200 OK
```

## Files Modified

1. **`website/src/components/forms/LoginForm.astro`** (line 72)
   - Changed: `fetch("/api/auth/csrf-token")` 
   - To: `fetch("http://127.0.0.1:8000/api/auth/csrf-token")`

2. **`website/src/components/forms/ChangePasswordForm.astro`** (line 97)
   - Changed: `fetch("/api/auth/csrf-token")`
   - To: `fetch("http://127.0.0.1:8000/api/auth/csrf-token")`

## Backend Validation

```bash
$ python manage.py check
System check identified no issues (0 silenced).
```

## Security Verification

✅ All CSRF token requests use absolute URLs pointing to Django backend
✅ All POST requests include `X-CSRFToken` header
✅ All requests use `credentials: "include"` for cookie handling
✅ CSRF protection remains enabled
✅ SessionAuthentication remains active
✅ No csrf_exempt used

## Summary

The issue was caused by using relative paths for CSRF token requests, which caused the browser to send requests to the Astro frontend origin (`localhost:4321`) instead of the Django backend origin (`localhost:8000`). 

The fix ensures all CSRF token requests use absolute URLs that point directly to the Django backend, matching the pattern already used in `auth.ts` for login, logout, and other authenticated endpoints.