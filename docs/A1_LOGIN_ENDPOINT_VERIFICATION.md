# A1 Login Endpoint Verification

> **Scope:** Determine if login failure is caused by frontend calling the wrong backend/API origin
> **Status:** Audit only — no code changes made

---

## 1. Exact URL Used by `LoginForm.astro`

**File:** `website/src/components/forms/LoginForm.astro` (line 8)

```typescript
<form id="login-form" class="space-y-5" data-endpoint={API_ENDPOINTS.login}>
```

**POST request** (lines 71-78):
```typescript
const res = await fetch(form.dataset.endpoint!, {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: String(data.email).toLowerCase().trim(),
    password: data.password,
  }),
});
```

**Endpoint source:** `API_ENDPOINTS.login` from `website/src/lib/api.ts`

---

## 2. Exact Value of Frontend API Base URL

**File:** `website/src/lib/api.ts` (lines 20-22)

```typescript
const API_BASE_URL =
  import.meta.env.PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";
```

**File:** `website/.env` (line 1)

```
PUBLIC_API_URL=http://127.0.0.1:8000
```

**Resolved `API_BASE_URL`:** `http://127.0.0.1:8000`

**Login endpoint:** `http://127.0.0.1:8000/api/auth/login`

---

## 3. Frontend Target Address

**Frontend is posting to:** `http://127.0.0.1:8000`

**NOT posting to:**
- `http://localhost:8000`
- Any other address

**Exact URL:** `http://127.0.0.1:8000/api/auth/login`

---

## 4. Origin Mismatch Analysis

| Component | Address | Port |
|-----------|---------|------|
| Astro dev server (frontend) | `localhost` | 4321 |
| Django dev server (backend) | `127.0.0.1` | 8000 |
| Frontend API target | `127.0.0.1` | 8000 |

**Critical finding:** The frontend is hosted on `localhost:4321` but posts to `127.0.0.1:8000`.

These are **different origins** in browser security terms:
- `http://localhost:4321` ≠ `http://127.0.0.1:8000`
- Even though they resolve to the same machine, browsers treat them as cross-origin

---

## 5. CORS Configuration

**File:** `backend/backend/settings.py` (lines 63-68)

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:4321',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:4321',
]
```

**CORS allows:** `http://localhost:4321` (frontend origin)

**But NOT:** `http://127.0.0.1:8000` (API target origin — this is the backend itself, so CORS doesn't apply)

**CORS impact:** The frontend origin (`http://localhost:4321`) IS in the allowed list. CORS preflight should succeed.

---

## 6. Session Cookie Configuration

**File:** `backend/backend/settings.py` (lines 166-169)

```python
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 days
```

**Critical issue:** `SESSION_COOKIE_SAMESITE = 'Lax'`

With `Lax` cookies:
- Cookies ARE sent on same-site requests
- Cookies are NOT sent on cross-site POST requests
- **`localhost:4321` → `127.0.0.1:8000` is cross-site** (different hostnames)

**Result:** The session cookie set by Django's `login()` will NOT be stored by the browser for subsequent cross-origin requests.

---

## 7. Request Flow and Failure Point

```
1. User clicks "Sign In" on http://localhost:4321/login
   ↓
2. LoginForm.astro sends POST to http://127.0.0.1:8000/api/auth/login
   ↓
3. Browser detects cross-origin request (localhost → 127.0.0.1)
   ↓
4. CORS preflight OPTIONS request sent to http://127.0.0.1:8000/api/auth/login
   ↓
5. Django CORS middleware allows http://localhost:4321 ✓
   ↓
6. POST request proceeds with credentials: "include"
   ↓
7. Django receives the POST request
   ↓
8. login_view executes (if URL is correct)
   ↓
9. authenticate() runs
   ↓
10. If successful, login() creates session
   ↓
11. Response sent back with Set-Cookie header
   ↓
12. Browser REFUSES to store session cookie (Lax + cross-origin)
   ↓
13. Frontend receives 200 OK but no cookie stored
   ↓
14. Subsequent requests to /api/auth/me fail (no session cookie)
```

---

## 8. Can Django Receive the Request?

**Yes, Django can receive the request** if:
1. Django is running on `127.0.0.1:8000`
2. CORS middleware is configured correctly (it is)
3. URL routing is correct

**The request should reach `login_view`** because:
- CORS allows `http://localhost:4321`
- The URL `http://127.0.0.1:8000/api/auth/login` matches the URL pattern
- No CSRF required for this endpoint (`AllowAny` permission)

**However:** The browser will block the response cookies from being stored.

---

## 9. Verification Steps

To verify the exact failure point, check:

### 9.1 Browser Developer Tools
1. Open DevTools → Network tab
2. Submit login form
3. Check the request:
   - **Request URL:** Should be `http://127.0.0.1:8000/api/auth/login`
   - **Request Method:** POST
   - **Status Code:** Check if 200 or 401
   - **Response Body:** Check error message
   - **Set-Cookie header:** Check if present in response

### 9.2 Django Server Logs
Check if Django logs show:
```
POST /api/auth/login 200/401
```

If no log entry appears, the request is not reaching Django.

### 9.3 CORS Preflight
Check for OPTIONS request in browser Network tab:
- Should show `Access-Control-Allow-Origin: http://localhost:4321`

---

## 10. Root Cause Determination

### Primary Root Cause: Cross-Origin Session Cookie Blocking

**Evidence:**
1. Frontend origin: `http://localhost:4321`
2. API target: `http://127.0.0.1:8000`
3. These are different origins (hostname mismatch)
4. `SESSION_COOKIE_SAMESITE = 'Lax'` blocks cross-origin cookies
5. Frontend uses `credentials: "include"` but browser refuses to store session cookie

**Impact:**
- Login may succeed (200 response) but session is not persisted
- Subsequent authenticated requests fail because no session cookie is sent
- User appears to be logged out immediately after login

### Secondary Issue: Potential URL Mismatch

If Django is actually running on `http://localhost:8000` instead of `http://127.0.0.1:8000`, the request will fail with a network error (connection refused).

**Verification:** Check what address Django is bound to:
```bash
# In Django runserver output, look for:
# "Starting development server at http://127.0.0.1:8000/"
# or
# "Starting development server at http://localhost:8000/"
```

---

## 11. Evidence Summary

| Evidence | Finding |
|----------|---------|
| Frontend `.env` | `PUBLIC_API_URL=http://127.0.0.1:8000` |
| Frontend API base URL | `http://127.0.0.1:8000` |
| Frontend origin | `http://localhost:4321` |
| Django CORS allows | `http://localhost:4321` ✓ |
| Django SESSION_COOKIE_SAMESITE | `Lax` |
| Cross-origin? | Yes (`localhost` ≠ `127.0.0.1`) |
| Cookies stored? | **No** (blocked by Lax + cross-origin) |
| Login endpoint reachable? | Yes, if Django is on 127.0.0.1:8000 |
| Session persisted? | **No** |
| Root cause | Cross-origin session cookie blocking |

---

## 12. Recommended Verification Commands

```bash
# 1. Check if Django is running and on which address
curl http://127.0.0.1:8000/api/health/

# 2. Check if frontend can reach backend
curl http://127.0.0.1:8000/api/auth/csrf-token

# 3. Test login from command line (bypass CORS/cookies)
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"muiaarnold12@gmail.com","password":"RP@2026!"}' \
  -c cookies.txt \
  -v

# 4. Check browser Network tab for:
#    - Request URL
#    - Status code
#    - Set-Cookie headers
#    - CORS headers
```

---

**Conclusion:** The frontend is posting to `http://127.0.0.1:8000` from `http://localhost:4321`. This is a cross-origin request. While CORS allows the request and Django receives it, the session cookie is not stored due to `SESSION_COOKIE_SAMESITE = 'Lax'`. This causes login to appear to fail from the user's perspective, even if `authenticate()` succeeds.

**No code changes were made — this is an audit-only document.**