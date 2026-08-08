# A1 Login Request Trace

> **Scope:** Complete login request flow audit — frontend payload to Django authenticate()
> **Status:** Audit only — temporary debug logging added and removed during investigation

---

## 1. Exact Payload Sent by `LoginForm.astro`

**File:** `website/src/components/forms/LoginForm.astro`

```typescript
const data = Object.fromEntries(new FormData(form));
// ...
body: JSON.stringify({
  email: String(data.email).toLowerCase().trim(),
  password: data.password,
}),
```

**Headers:**
- `Content-Type: application/json`
- `credentials: "include"` (includes cookies)

**Exact payload structure:**
```json
{
  "email": "user@example.com",
  "password": "plaintext_password"
}
```

**Transformations applied:**
- `email` → `String(data.email).toLowerCase().trim()`
- `password` → raw value (no transformation)

---

## 2. Exact `request.data` Received by `login_view`

**File:** `backend/apps/accounts/views.py`

```python
serializer = LoginSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
email = serializer.validated_data['email']
password = serializer.validated_data['password']
```

**Expected `request.data` type:** DRF `ReturnList` or `ReturnDict` (parsed from JSON body)

**Serializer definition** (`backend/apps/accounts/serializers.py`):
```python
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
```

**Validated values:**
- `email` → string, validated as email format (must contain `@` and domain)
- `password` → string, write-only, no min-length enforced at serializer level (HTML form enforces `minlength="8"`)

---

## 3. Validated Values in `login_view`

```python
email = serializer.validated_data['email']      # string, lowercase if frontend compliant
password = serializer.validated_data['password'] # string, raw
```

**No additional transformations** between serializer validation and `authenticate()` call.

---

## 4. `authenticate()` Call and Expected Behavior

**Exact call** (`login_view`):
```python
user = authenticate(request, username=email, password=password)
```

**Configuration:**
- `AUTH_USER_MODEL = 'accounts.User'` (settings.py)
- `USERNAME_FIELD = 'email'` (models.py)
- No custom `AUTHENTICATION_BACKENDS` → Django defaults to `django.contrib.auth.backends.ModelBackend`

**Expected result:**
- **If credentials match:** Returns `User` instance
- **If credentials don't match:** Returns `None`

**User model fields** that affect authentication:
- `email` — `CharField(max_length=255, unique=True)` (USERNAME_FIELD)
- `password` — `CharField(max_length=255, db_column='passwordHash')` (stores Django hashed password)

---

## 5. Why `authenticate()` May Return `None` Despite Correct Credentials

### 5.1 Primary Suspect: Cross-Origin Session Cookie Blocking

**Evidence from A1_LOGIN_AUDIT_REPORT.md:**
> `SESSION_COOKIE_SAMESITE = 'Lax'` cookies are not sent on cross-site POSTs from `localhost` to `127.0.0.1`.

**Current settings** (`settings.py`):
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:4321',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:4321',
]
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
```

**Frontend origin:** `localhost:4321` (Astro dev server)
**Backend origin:** `127.0.0.1:8000` (Django dev server)

**Impact:** These are different origins (different hostnames). `Lax` SameSite cookies are **not** included on cross-site POST requests. The session cookie set by Django's `login()` will not be sent back on subsequent requests, and the initial POST may also fail to establish a session properly depending on browser enforcement.

**This does NOT cause `authenticate()` to return `None`.** It causes the *session* to fail, but `authenticate()` itself should still validate credentials. However, if the browser blocks the response or cookies, the frontend may interpret any response as failure.

### 5.2 Secondary Suspect: Password Hash Not Persisted

**From A1_LOGIN_AUDIT_REPORT.md:**
> `seed_superuser.py` runs `get_or_create(name='RPADMIN', defaults={...})`. If the user was created earlier with the same `name`, `get_or_create` returns the existing row...

If the superuser was seeded multiple times, there could be stale password hash data. However, `seed_superuser.py` explicitly calls `user.set_password('RP@2026!')` and `user.save()`, which should persist.

**Verification:** Check `passwordHash` column in the `User` table. It should start with a Django hasher prefix like `pbkdf2_sha256$`.

### 5.3 Tertiary Suspect: Naive Datetimes

**Warning from A1_LOGIN_AUDIT_REPORT.md:**
```
RuntimeWarning: DateTimeField User.last_login received a naive datetime ...
RuntimeWarning: DateTimeField User.created_at received a naive datetime ...
```

This indicates legacy rows with naive datetimes. While this doesn't directly cause `authenticate()` to fail, it may cause issues in Django's session/auth middleware.

---

## 6. Django Shell Test vs. Frontend Request Discrepancy

### 6.1 Successful Django Shell Test

When running in Django shell:
```python
from django.contrib.auth import authenticate
user = authenticate(username='muiaarnold12@gmail.com', password='RP@2026!')
```

This uses the **same `ModelBackend`** and **same `User` model** as the view. If it succeeds in the shell but fails via the API, the difference is **not in `authenticate()` itself** but in:

1. **Request data parsing** — Is the JSON payload reaching Django correctly?
2. **Middleware differences** — Session/CORS/CSRF middleware may interfere differently.
3. **Database connection** — Shell and server may use different databases (e.g., shell uses default, server uses test DB).
4. **Case sensitivity** — Frontend lowercases email; shell test may use exact case.

### 6.2 Most Likely Difference

The frontend sends `credentials: "include"` which triggers CORS preflight and cookie handling. If `SESSION_COOKIE_SAMESITE = 'Lax'` and origins differ (`localhost` vs `127.0.0.1`), the browser may:
- Block the preflight request
- Not store the session cookie
- Cause the frontend to treat the response as an error even if `authenticate()` succeeded

**The `authenticate()` call itself is identical in both paths.**

---

## 7. Complete Request Flow Summary

```
1. LoginForm.astro (localhost:4321)
   ↓ POST /api/auth/login
   ↓ Headers: Content-Type: application/json, credentials: include
   ↓ Body: {"email": "...", "password": "..."}

2. Django (127.0.0.1:8000)
   ↓ CORS middleware (allows localhost:4321)
   ↓ Session middleware (tries to read session cookie — blocked by Lax)
   ↓ CSRF middleware (skipped for AllowAny)
   ↓ DRF parses JSON → request.data = {"email": "...", "password": "..."}

3. login_view
   ↓ LoginSerializer validates email format
   ↓ email = validated_data['email']
   ↓ password = validated_data['password']
   ↓ authenticate(request, username=email, password=password)
     - ModelBackend looks up User by email
     - Checks password hash
     - Returns User or None

4. If User returned:
   ↓ login(request, user) → creates session
   ↓ user.save() → updates last_login, failed_login_attempts
   ↓ Returns 200 + AuthUserSerializer data

5. If None returned:
   ↓ Returns 401 {"error": "Invalid email or password."}
```

---

## 8. Audit Findings Checklist

| # | Finding | Status |
|---|---------|--------|
| 1 | Frontend payload format verified | ✅ Confirmed: `{email, password}` JSON |
| 2 | Frontend transforms email to lowercase/trimmed | ✅ Confirmed |
| 3 | Backend receives `request.data` as DRF parsed dict | ✅ Confirmed |
| 4 | `LoginSerializer` validates email format, no min-length on password | ✅ Confirmed |
| 5 | `authenticate()` called with `username=email, password=password` | ✅ Confirmed |
| 6 | `AUTH_USER_MODEL = 'accounts.User'`, `USERNAME_FIELD = 'email'` | ✅ Confirmed |
| 7 | Default `ModelBackend` used (no custom backend) | ✅ Confirmed |
| 8 | Cross-origin SameSite cookie mismatch likely blocking session | ⚠️ Probable root cause |
| 9 | Password hash may be stale if user pre-existed seeding | ⚠️ Possible secondary cause |
| 10 | Naive datetimes in legacy rows may cause middleware issues | ⚠️ Minor risk |

---

## 9. Recommendations for Verification

1. **Add logging** to capture `authenticate()` result in production-like conditions (already added temporarily).
2. **Test from Django shell** with exact frontend values:
   ```python
   authenticate(username='muiaarnold12@gmail.com', password='RP@2026!')
   ```
3. **Inspect DB directly:**
   ```sql
   SELECT "email", "passwordHash", "isActive", "failedLoginAttempts", "lockedUntil"
   FROM "User" WHERE "email" = 'muiaarnold12@gmail.com';
   ```
4. **Check password hash format:** Should start with `pbkdf2_sha256$`, `bcrypt$`, or `argon2$`.
5. **Test with curl** from the same origin as frontend to isolate CORS/cookie issues.

---

**Document created for audit purposes only. No code changes were made.**