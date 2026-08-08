# A1 CSRF Trace Audit

## Audit Date
2026-01-02

## Objective
Trace the complete CSRF token flow for the login endpoint to identify why CSRF validation is failing.

## Code Evidence

### 1. Backend CSRF Token Endpoint

**File:** `backend/backend/apps/accounts/views.py` (lines 150-163)

```python
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    """GET /api/auth/csrf-token — return the CSRF token for cross-origin frontend."""
    return Response(
        {'csrfToken': get_token(request)},
        status=status.HTTP_200_OK,
    )
```

**Expected behavior:**
- URL: `http://localhost:4321/api/auth/csrf-token` (via proxy) or `http://127.0.0.1:8000/api/auth/csrf-token`
- Response body: `{"csrfToken": "<token_value>"}`
- Response sets `csrftoken` cookie via `get_token()`

### 2. Frontend Auth Helper (CORRECT)

**File:** `website/src/lib/auth.ts` (lines 79-104)

```typescript
export async function login(
  email: string,
  password: string,
): Promise<{ user: AuthUser } | { error: string }> {
  try {
    const csrfToken = await getCsrfToken();  // ← FETCHES CSRF TOKEN
    const res = await fetch(AUTH_ENDPOINTS.login, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),  // ← SENDS X-CSRFToken HEADER
      },
      body: JSON.stringify({
        email: email.toLowerCase().trim(),
        password,
      }),
    });
    // ...
  }
}
```

**This implementation is CORRECT** - it fetches CSRF token and includes it in the header.

### 3. Frontend Login Form (BUGGY)

**File:** `website/src/components/forms/LoginForm.astro` (lines 71-79)

```typescript
const res = await fetch(form.dataset.endpoint!, {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },  // ← NO X-CSRFToken HEADER
  body: JSON.stringify({
    email: String(data.email).toLowerCase().trim(),
    password: data.password,
  }),
});
```

**This implementation is BUGGY** - it does NOT fetch CSRF token and does NOT send `X-CSRFToken` header.

## Root Cause Identified

### The CSRF Chain Breaks Here:

**Location:** `website/src/components/forms/LoginForm.astro` (lines 71-79)

**Problem:** The LoginForm component makes a direct `fetch()` call to the login endpoint WITHOUT:
1. Fetching the CSRF token from `/api/auth/csrf-token` first
2. Including the `X-CSRFToken` header in the POST request

**Impact:** Django's `CsrfViewMiddleware` rejects the POST request with:
```
CSRF Failed: CSRF token missing.
```

## Request Sequence Analysis

### Expected Flow (auth.ts implementation - CORRECT)
1. GET `/api/auth/csrf-token` → fetch CSRF token
2. Response: `{"csrfToken": "abc123..."}` + `csrftoken` cookie
3. POST `/api/auth/login` with header `X-CSRFToken: abc123...`
4. Django validates token → Success

### Actual Flow (LoginForm.astro - BUGGY)
1. **SKIPPED** - No CSRF token fetch
2. **SKIPPED** - No `X-CSRFToken` header
3. POST `/api/auth/login` WITHOUT CSRF token
4. Django rejects with `CSRF Failed: CSRF token missing.`

## Evidence Summary

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| CSRF endpoint called before login | YES | NO | ❌ FAIL |
| csrftoken cookie set | YES | NO | ❌ FAIL |
| X-CSRFToken header present | YES | NO | ❌ FAIL |
| CSRF token value matches cookie | YES | N/A | ❌ FAIL |

## Exact Point of Failure

**File:** `website/src/components/forms/LoginForm.astro`
**Line:** 71-79
**Function:** Form submit event handler
**Issue:** Direct fetch call without CSRF token acquisition

The login form bypasses the `login()` helper function in `auth.ts` which correctly implements CSRF token handling.

## Required Fix

The LoginForm.astro component must be updated to:
1. Call `getCsrfToken()` before making the login POST request
2. Include the `X-CSRFToken` header in the POST request
3. Use `credentials: "include"` (already present)

This will align the login form with the pattern already implemented in:
- `auth.ts` `login()` function (CORRECT)
- `auth.ts` `logout()` function (CORRECT)
- `ChangePasswordForm.astro` (already fixed)

## Security Implications

- **CSRF Protection Status:** Enabled but bypassed due to missing token
- **Risk:** High - Login endpoint is vulnerable to CSRF attacks
- **Impact:** Any malicious site can submit login forms on behalf of authenticated users

## Recommendation

Update `LoginForm.astro` to fetch and include CSRF token before POST request, matching the pattern in `auth.ts`.