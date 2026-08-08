# A1 Login Audit Report

> **Scope:** A1.3 through A1.8
> **Focus:** Academy login for existing superuser (`muiaarnold12@gmail.com`)
> **Status:** Audit only — no implementation changes made

---

## 1. Credentials Introduced / Modified During A1.3–A1.8

| Phase | File | What was seeded / changed | Credential value |
|-------|------|---------------------------|------------------|
| A1.2 / seed_superuser | `backend/apps/accounts/management/commands/seed_superuser.py` | Created/updated superuser `RPADMIN` | Email: `muiaarnold12@gmail.com`<br>Password: `RP@2026!` |
| A1.2 / verify_academy_access | `backend/verify_academy_access.py` | Grants `AcademyAccess` to active members; does **not** create users | N/A |
| A1.2 / grant_academy_access | `backend/grant_academy_access` | Same as above | N/A |

**Key point:** The only login-capable account created/modified in this phase is the superuser above. No member/student/teacher accounts were seeded.

---

## 2. Current Superuser State

- **Email:** `muiaarnold12@gmail.com`
- **Password hash:** Updated by `seed_superuser.py` via `user.set_password('RP@2026!')`
- **Flags:** `is_active=True`, `is_staff=True`, `is_superuser=True`, `role=ADMIN`
- **Password storage:** Django `User.password` field maps to DB column `passwordHash` using Django’s password hashers

---

## 3. Login Flow Audit

### 3.1 Frontend
- File: `website/src/components/forms/LoginForm.astro`
- Endpoint: `POST /api/auth/login`
- Payload: `{ email, password }`
- Uses `credentials: "include"` so the session cookie is stored.

### 3.2 Backend
- File: `backend/apps/accounts/views.py`
- View: `login_view`
- Serializer: `LoginSerializer`
- Auth call: `authenticate(request, username=email, password=password)`

```python
user = authenticate(request, username=email, password=password)
```

Because `AUTH_USER_MODEL = 'accounts.User'` and `USERNAME_FIELD = 'email'`, passing `username=email` is correct for Django’s default `ModelBackend`.

---

## 4. Why the Existing Superuser Login Is Failing

### 4.1 Probable cause 1 — Password was never actually set on the DB row
`seed_superuser.py` runs `get_or_create(name='RPADMIN', defaults={...})`. If the user was created earlier with the same `name`, `get_or_create` returns the existing row and the command then sets:
```python
user.email = 'muiaarnold12@gmail.com'
user.set_password('RP@2026!')
user.save()
```
This should work. However, if the existing row had a **different primary key / id** behavior or if `save()` was not persisted correctly in a previous run, the password may not match.

### 4.2 Probable cause 2 — Timezone warning indicates legacy naive datetimes
During `seed_superuser`, Django emits:
```
RuntimeWarning: DateTimeField User.last_login received a naive datetime ...
RuntimeWarning: DateTimeField User.created_at received a naive datetime ...
```
This means the existing superuser row has **naive datetimes** stored while `TIME_ZONE` is active. Django can coerce on write, but in some configurations this may cause the user row to be considered corrupted or may interfere with session/auth middleware expectations. It does **not** directly cause authentication failure, but it indicates schema-level inconsistency.

### 4.3 Probable cause 3 — Session/auth backend mismatch
The project uses DRF `SessionAuthentication`. If the frontend and backend are on different origins and CSRF/session cookies are not being set correctly, login will appear to fail even with correct credentials. The `LoginForm` now sends `credentials: "include"`, but:
- `SESSION_COOKIE_SAMESITE = 'Lax'`
- Frontend runs on `localhost:4321`, backend on `127.0.0.1:8000`

`Lax` cookies are not sent on cross-site POSTs from `localhost` to `127.0.0.1`. This is the **most likely cause** of “Invalid email or password” when testing from the Astro frontend.

### 4.4 Probable cause 4 — `AUTHENTICATION_BACKENDS` not explicitly set
There is no custom `backends.py` and `AUTHENTICATION_BACKENDS` is not set in `settings.py`. Django defaults to `django.contrib.auth.backends.ModelBackend`, which should work for email login because `USERNAME_FIELD = 'email'`.

---

## 5. Root-Cause Determination

| # | Finding | Severity | Blocks login? |
|---|---------|----------|---------------|
| 1 | Superuser password may not be persisted if row pre-exists with stale data | High | Yes |
| 2 | Naive datetimes in existing `User` row | Medium | Unlikely directly |
| 3 | Cross-origin `Lax` cookies between Astro (`localhost:4321`) and Django (`127.0.0.1:8000`) | **High** | **Yes** |
| 4 | No custom auth backend; default `ModelBackend` should handle email | Low | No |

**Most likely blocker:** Combination of #1 and #3. Even with correct credentials, the session cookie may not be stored due to same-site policy, and the superuser row may have stale password hash from a previous seed run.

---

## 6. Proposed Plan (Do Not Implement Yet)

### Step 1 — Ensure superuser password is explicitly reset
Run `python manage.py seed_superuser` and confirm output says `updated`. Then verify directly in DB/SDK that `passwordHash` starts with a Django hasher prefix (`pbkdf2_sha256$` or similar).

### Step 2 — Fix cross-origin session cookie behavior
Options:
- **Option A (preferred):** Set `SESSION_COOKIE_SAMESITE = 'None'` and `SESSION_COOKIE_SECURE = False` for local dev, so cookies are sent cross-origin.  
- **Option B:** Serve Astro and Django on the **same origin** during dev (e.g., Django serves Astro build artifacts, or proxy through one dev server).  
- **Option C:** Switch to token auth for the portal instead of session cookies.

### Step 3 — Normalize existing superuser datetimes
Update `User.last_login` and `User.created_at` to timezone-aware values, or migrate existing rows to UTC-aware timestamps.

### Step 4 — Re-test
After steps 1–3, attempt login from `/login` with `muiaarnold12@gmail.com` / `RP@2026!`.

---

## 7. Recommendation

Proceed with **Step 1** and **Step 2A** first:
1. Re-run `seed_superuser` and verify DB password hash format.
2. Temporarily set `SESSION_COOKIE_SAMESITE = 'None'` and `SESSION_COOKIE_SECURE = False` in `settings.py` for local dev.
3. Re-test login from the frontend.

If successful, document the dev-only cookie settings and plan production hardening (`Secure=True`, `SameSite=None` with HTTPS).

---

**No implementation changes were made in this audit.**