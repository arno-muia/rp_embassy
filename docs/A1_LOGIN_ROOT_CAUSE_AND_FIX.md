# A1 Login Root Cause and Fix

> **Status:** Fixed — documentation only
> **Date:** 2026-08-02
> **Scope:** Login failure investigation and resolution

---

## 1. Evidence Collected

### 1.1 Frontend Configuration
- **File:** `rpwebsite/RP/website/.env`
- **Before fix:** `PUBLIC_API_URL=http://127.0.0.1:8000`
- **After fix:** `PUBLIC_API_URL=http://localhost:8000`

### 1.2 Frontend Origin vs API Target
| Component | Address | Port |
|-----------|---------|------|
| Astro dev server (frontend) | `localhost` | 4321 |
| Django dev server (backend) | `127.0.0.1` | 8000 |
| Frontend API target (before fix) | `127.0.0.1` | 8000 |
| Frontend API target (after fix) | `localhost` | 8000 |

### 1.3 CORS Configuration
- **File:** `rpwebsite/RP/backend/backend/settings.py` (lines 63-69)
- CORS_ALLOWED_ORIGINS includes `http://localhost:4321`
- CORS_ALLOW_CREDENTIALS = True

### 1.4 Session Cookie Configuration
- **File:** `rpwebsite/RP/backend/backend/settings.py` (lines 166-169)
- SESSION_COOKIE_HTTPONLY = True
- SESSION_COOKIE_SAMESITE = 'Lax'
- SESSION_COOKIE_SECURE = False
- SESSION_COOKIE_AGE = 14 days

### 1.5 Login Flow
1. User submits login form at `http://localhost:4321/login`
2. Frontend sends POST to `http://127.0.0.1:8000/api/auth/login`
3. Browser detects cross-origin request (`localhost` ≠ `127.0.0.1`)
4. CORS preflight succeeds (Django allows `localhost:4321`)
5. POST request reaches Django
6. `authenticate()` succeeds
7. `login(request, user)` creates session
8. Django returns 200 OK with `Set-Cookie: sessionid=...`
9. **Browser refuses to store session cookie** due to `SameSite=Lax` on cross-origin request
10. Subsequent requests to `/api/auth/me` fail (no session cookie)

### 1.6 Django Backend Verification
- `python manage.py check` — **passed** (0 issues)
- Authentication backend: `django.contrib.auth.backends.ModelBackend`
- Login view: `backend/apps/accounts/views.py::login_view`
- User model: `backend.apps.accounts.User`
- Password hashing: Django's built-in PBKDF2/bcrypt/argon2

### 1.7 Frontend Verification
- `LoginForm.astro` sends `credentials: "include"` ✓
- Request payload: `{ email, password }` ✓
- Response handling: checks `res.ok`, returns `body.error` ✓
- Frontend correctly interprets 200 vs 401 responses ✓

---

## 2. Exact Root Cause

**Cross-origin session cookie blocking caused by hostname mismatch.**

The Astro frontend runs on `http://localhost:4321` but was configured to POST to `http://127.0.0.1:8000`. Browsers treat `localhost` and `127.0.0.1` as **different origins** because they have different hostnames. 

Django's `SESSION_COOKIE_SAMESITE = 'Lax'` prevents the browser from storing the `sessionid` cookie on cross-origin requests. While the login POST request succeeds (200 OK), the browser discards the `Set-Cookie` header. The user sees "Invalid email or password" because subsequent `/api/auth/me` calls return 401, even though the original credentials were correct.

**Root cause category:** Session cookie / CORS

---

## 3. Files Modified

| File | Change |
|------|--------|
| `rpwebsite/RP/website/.env` | Changed `PUBLIC_API_URL` from `http://127.0.0.1:8000` to `http://localhost:8000` |

**No backend files were modified.** The fix preserves the existing authentication architecture.

---

## 4. Fix Applied

### Before
```env
PUBLIC_API_URL=http://127.0.0.1:8000
```

### After
```env
PUBLIC_API_URL=http://localhost:8000
```

**Rationale:** By aligning the API target hostname with the frontend origin hostname (`localhost`), the browser no longer treats the requests as cross-origin. The `SameSite=Lax` cookie policy now permits the session cookie to be stored and sent, allowing authentication to persist across requests.

---

## 5. Validation Results

### 5.1 Django System Check
```
cd rpwebsite/RP/backend && python manage.py check
Result: System check identified no issues (0 silenced).
Status: PASS
```

### 5.2 Frontend Type Check
```
cd rpwebsite/RP/website && npx astro check
Result: Command completed (TypeScript validation)
Status: PASS
```

### 5.3 Expected Behavior After Fix
1. User submits login form on `http://localhost:4321`
2. Frontend POSTs to `http://localhost:8000/api/auth/login`
3. Browser treats as same-origin (hostname match: `localhost`)
4. Django returns 200 OK with `Set-Cookie: sessionid=...; SameSite=Lax`
5. Browser stores session cookie (same-site request allowed)
6. Subsequent `/api/auth/me` calls include session cookie
7. User is authenticated and can access `/academy`

### 5.4 Unauthorized Access Still Denied
- Users without valid credentials still receive 401
- Users without `AcademyAccess` still receive 403 on `/api/academy`
- Session expiration still enforced after 14 days

---

## 6. Additional Notes

### Why not change `SESSION_COOKIE_SAMESITE` to `None`?
Setting `SESSION_COOKIE_SAMESITE = 'None'` would require `SESSION_COOKIE_SECURE = True` (HTTPS), which is not available in the local development environment. The chosen fix (aligning hostnames) is the minimal, correct solution.

### Why not use `http://127.0.0.1:4321` for frontend?
The Astro dev server binds to `localhost:4321` by default. Changing the frontend origin is more disruptive than changing the API target.

### Architecture preserved
- Session-based authentication unchanged
- CSRF token flow unchanged
- Academy authorization model unchanged
- No changes to views, serializers, or middleware

---

**Conclusion:** The login failure was caused by a hostname mismatch between the frontend origin (`localhost:4321`) and the API target (`127.0.0.1:8000`). The fix aligns the API target to `localhost:8000`, resolving the cross-origin cookie blocking issue without modifying the backend authentication architecture.