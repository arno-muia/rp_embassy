# A1.0 — Authentication Compatibility Audit

> **Status:** COMPLETE — MANDATORY GATE
> **Date:** 2026-07-30
> **Phase:** A1 (Academy Authentication) — Pre-implementation audit
> **Related:** `A1_ACADEMY_AUTHENTICATION_PLAN.md`, `AI_RULES.md`, `MEMORY.md`,
> `B1_MODEL_OWNERSHIP_MATRIX.md`, `B3_4A_PRISMA_DEPENDENCY_AUDIT.md`

---

## 1. Objective

Validate that the current authentication architecture can safely support
Django session-based authentication **before** any Academy access control work
begins. This is a mandatory gate — implementation may only proceed if the
audit confirms compatibility.

---

## 2. Audit Tasks

| Task | Description | Result |
|------|-------------|--------|
| A1.0.1 | User Model Compatibility | ❌ FAIL |
| A1.0.2 | Session Authentication Validation | ❌ BLOCKED |
| A1.0.3 | Prisma Compatibility Review | ✅ PASS (safe to modify) |
| A1.0.4 | Password Storage Audit | ⚠️ UNKNOWN (needs DB query) |

**Overall verdict: A1.0 FAILS — the current `accounts.User` model is
incompatible with Django's authentication framework. Remediation is required
before A1.1 can proceed.**

---

## 3. A1.0.1 — User Model Compatibility

### 3.1 Files inspected

- `backend/backend/settings.py` (146 lines)
- `backend/backend/apps/accounts/models.py` (127 lines)
- `backend/backend/apps/accounts/` directory (5 files: `apps.py`, `models.py`,
  `repositories.py`, `serializers.py`, `services.py` — no `views.py`,
  `urls.py`, `backends.py`, `admin.py`, or `permissions.py`)

### 3.2 AUTH_USER_MODEL configuration

**Result: ❌ NOT CONFIGURED**

`settings.py` contains no `AUTH_USER_MODEL` setting. Django falls back to
`django.contrib.auth.models.User` (the default) for all auth operations.

```python
# settings.py — INSTALLED_APPS (lines 33-49)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',          # ← default User model
    ...
    'backend.apps.accounts',        # ← custom User model (NOT registered as AUTH_USER_MODEL)
    ...
]
```

**Impact:**
- `get_user_model()` returns the **default** `User`, not `accounts.User`.
- `AuthenticationMiddleware` → `auth.get_user(request)` → fetches from the
  **default** `User` table, not the Prisma-owned `User` table.
- `login()` / `logout()` / session-stored user IDs refer to the wrong model.

### 3.3 User extends AbstractBaseUser / PermissionsMixin

**Result: ❌ NO — extends `models.Model` only**

```python
# accounts/models.py — line 62
class User(models.Model):
    """Maps to Prisma model User -> table 'User'."""
```

The model extends `django.db.models.Model` directly. It does **not** extend:
- `AbstractBaseUser` (provides `password`, `is_authenticated`, `is_anonymous`,
  `get_session_auth_hash()`, `set_password()`, `check_password()`)
- `PermissionsMixin` (provides `is_superuser`, `groups`, `user_permissions`,
  `has_perm()`, `has_module_perms()`)
- `AbstractUser` (combines both + `username` field)

### 3.4 Presence of required Django auth methods/attributes

| Attribute / Method | Required by | Present? | Notes |
|--------------------|------------|----------|-------|
| `is_authenticated` | Middleware, DRF `IsAuthenticated`, permissions | ❌ **MISSING** | No property defined |
| `is_anonymous` | DRF permission checks | ❌ **MISSING** | No property defined |
| `get_username()` | `ModelBackend`, some auth flows | ❌ **MISSING** | No method defined |
| `USERNAME_FIELD` | `BaseUserManager`, backend lookups | ❌ **MISSING** | No class attribute |
| `REQUIRED_FIELDS` | `createsuperuser` | ❌ **MISSING** | No class attribute |
| `get_session_auth_hash()` | `SessionAuthentication`, `login()` | ❌ **MISSING** | Critical — causes `AttributeError` |
| `set_password(raw)` | Password setting | ❌ **MISSING** | No method |
| `check_password(raw)` | Password verification | ❌ **MISSING** | No method |
| `is_active` | `ModelBackend`, `SessionAuthentication` | ✅ Present | `BooleanField(db_column='isActive')` |
| `last_login` | `AbstractBaseUser`, `login()` | ✅ Present | `DateTimeField(db_column='lastLogin')` |
| `id` / `pk` | Session storage | ✅ Present | `UUIDField` primary key |
| `password` | `ModelBackend`, `check_password()` | ❌ **MISSING** | Has `password_hash` instead |
| `is_superuser` | `PermissionsMixin`, admin | ❌ **MISSING** | No `PermissionsMixin` |
| `groups` | `PermissionsMixin` | ❌ **MISSING** | No `PermissionsMixin` |
| `user_permissions` | `PermissionsMixin` | ❌ **MISSING** | No `PermissionsMixin` |

### 3.5 Compatibility with `django.contrib.auth.login()` and `logout()`

**`login(request, user)`:** ❌ WILL FAIL

```
django.contrib.auth.login(request, user)
  ├─ request.session[SESSION_KEY] = user.pk           → OK (pk exists)
  ├─ request.session[BACKEND_SESSION_KEY] = backend  → OK
  └─ request.session[HASH_SESSION_KEY] = user.get_session_auth_hash()
                                                       → AttributeError: 'User' object has no attribute 'get_session_auth_hash'
```

**`logout(request)`:** ✅ Would work (just flushes the session), but is moot
since `login()` cannot succeed.

**`get_user_model()`:** ❌ Returns the **wrong model** (default `User`, not
`accounts.User`).

### 3.6 A1.0.1 Verdict

**❌ FAIL — CRITICAL.** The `accounts.User` model is missing the core
`AbstractBaseUser` interface. `login()` will raise `AttributeError` at
runtime. `AUTH_USER_MODEL` is not set, so Django's auth pipeline operates on
the wrong user table.

---

## 4. A1.0.2 — Session Authentication Validation

### 4.1 Objective

Create a temporary test endpoint to verify that `login(request, user)`
successfully creates a session, persists across requests, and works with DRF
`SessionAuthentication`.

### 4.2 Result: ❌ BLOCKED by A1.0.1

A runtime test cannot be performed because the prerequisites from A1.0.1
fail. Specifically:

1. `AUTH_USER_MODEL` is not set → `get_user_model()` returns the wrong model.
2. `User` lacks `get_session_auth_hash()` → `login()` raises `AttributeError`.
3. `User` lacks `is_authenticated` → DRF `SessionAuthentication` and
   `IsAuthenticated` raise `AttributeError`.

### 4.3 Predicted failure trace

If a test endpoint were created today and `login(request, user)` were called:

```
POST /api/auth/login
  ├─ authenticate(email, password)  → custom backend needed (none exists)
  ├─ login(request, user)
  │    └─ user.get_session_auth_hash()
  │         → AttributeError: 'User' object has no attribute 'get_session_auth_hash'
  └─ Response: 500 Internal Server Error
```

Even if the `AttributeError` were caught, the session would not contain a
valid `_auth_user_hash`, so `SessionAuthentication.authenticate()` on the next
request would fail to validate the session.

### 4.4 What should be tested AFTER remediation

Once A1.0.1 is fixed (User extends `AbstractBaseUser`, `AUTH_USER_MODEL` set),
the following runtime tests should be performed:

| Test | Expected result |
|------|-----------------|
| `login(request, user)` stores `_auth_user_id` in session | ✅ |
| `login(request, user)` stores `_auth_user_hash` in session | ✅ |
| Session persists across requests (cookie-based) | ✅ |
| `SessionAuthentication.authenticate(request)` returns user | ✅ |
| `request.user.is_authenticated` is `True` after login | ✅ |
| `logout(request)` flushes the session | ✅ |
| `request.user` is `AnonymousUser` after logout | ✅ |

### 4.5 A1.0.2 Verdict

**❌ BLOCKED — cannot test until A1.0.1 is remediated.** The test is deferred
to post-remediation validation.

---

## 5. A1.0.3 — Prisma Compatibility Review

### 5.1 Objective

Verify Prisma ownership assumptions, the impact of modifying `User` model
inheritance, and whether `User` model changes would break existing Prisma
workflows.

### 5.2 Files inspected

- `docs/B1_MODEL_OWNERSHIP_MATRIX.md` — ownership rules
- `docs/B3_4A_PRISMA_DEPENDENCY_AUDIT.md` — Prisma dependency audit
- `backend/apps/accounts/models.py` — model docstring references
  `apps/web/prisma/schema.prisma`

### 5.3 Prisma ownership assumptions

From `B1_MODEL_OWNERSHIP_MATRIX.md`:

> **Prisma Owned**: Schema defined and migrated by Prisma. Django reads/writes
> but does not manage schema. `managed = False`.

The `User` model is **Prisma-owned**:
- `managed = False` (line 84 of `accounts/models.py`)
- `db_table = 'User'` (line 85)
- Source of truth: `apps/web/prisma/schema.prisma`

Critical ownership rules from B1:
1. "Never modify Prisma schema without coordination."
2. "Django migration commands must not touch `managed = False` tables."
3. "Prisma-owned data must never be deleted by Django."

### 5.4 Impact of modifying User model inheritance

**Changing `User` from `models.Model` to `AbstractBaseUser`:**

| Aspect | Impact |
|--------|--------|
| Database table structure | **NONE** — `AbstractBaseUser` is abstract; no table is created. `managed = False` means Django won't run migrations on the `User` table. |
| `password` field | `AbstractBaseUser` declares `password = CharField(max_length=128)`. We override it with `password = CharField(max_length=255, db_column='passwordHash')` to map to the existing column. No new column is created. |
| `last_login` field | `AbstractBaseUser` declares `last_login`. Our model already has `last_login` with `db_column='lastLogin'`. The child's field definition takes precedence. No change to the DB. |
| Prisma client queries | **NONE** — Prisma operates at the database level, not the Django model level. The `passwordHash` column is unchanged. |
| Prisma migrations | **NONE** — No schema change is needed. The Prisma schema (`schema.prisma`) is not modified. |
| Next.js app (`apps/web/`) | **NONE** — The Next.js app uses `@prisma/client` which reads the database directly. It doesn't know or care about Django's Python class hierarchy. |

### 5.5 Would User model changes break existing Prisma workflows?

**No.** The change is purely at the Django Python class level:

1. **Database**: The `User` table and its columns (`id`, `email`,
   `passwordHash`, `name`, `role`, `isActive`, etc.) remain unchanged.
2. **Prisma schema**: `schema.prisma` is not modified.
3. **Prisma client**: `@prisma/client` queries the database directly — it
   doesn't import Django models.
4. **Prisma migrations**: `prisma db push` / `prisma migrate` operate on the
   schema, not Django models. They won't be affected.
5. **Django migrations**: Since `managed = False`, Django won't generate or
   run migrations for the `User` table. The class hierarchy change is a Python-
   only change.

**One caveat:** If `AbstractBaseUser`'s `password` field (max_length=128) is
overridden with `max_length=255` (to match the existing `passwordHash` column),
Django's model validation might flag a difference from the abstract parent.
This is a non-issue because `managed = False` means Django doesn't validate
the column length against the model.

### 5.6 A1.0.3 Verdict

**✅ PASS — safe to modify `User` inheritance.** Changing `User` to extend
`AbstractBaseUser` is a Python-only change that does not affect the database
schema, Prisma schema, Prisma client, or Prisma migrations. The `managed =
False` constraint is respected.

---

## 6. A1.0.4 — Password Storage Audit

### 6.1 Objective

Verify the bcrypt format, hash compatibility, and existing password
verification process.

### 6.2 Files inspected

- `backend/apps/accounts/models.py` — `password_hash` field definition
- `backend/apps/accounts/services.py` — no password verification logic
- `backend/apps/accounts/repositories.py` — no password verification logic
- `Pipfile` (root) — dependency list
- Search results for `bcrypt`, `check_password`, `make_password`, `hashers`
  across the entire backend

### 6.3 Password field definition

```python
# accounts/models.py — lines 67-70
password_hash = models.CharField(
    max_length=255,
    db_column='passwordHash',
)
```

The field is a plain `CharField(max_length=255)`. There is no indication of
the hash format in the model or any code comment.

### 6.4 bcrypt format

**Result: ⚠️ UNKNOWN — cannot determine without a database query.**

- No `bcrypt` import or usage was found anywhere in the backend (search
  returned 0 results for `bcrypt`).
- No `check_password`, `make_password`, or `hashers` usage was found (search
  returned 0 results).
- The `Pipfile` (root) lists only `psycopg` and `validate-email` — no `bcrypt`
  dependency.
- The hash format is determined by whatever the Prisma/Next.js application
  used when creating user accounts. Without querying the `User` table or
  reading the Prisma auth code, the format is unknown.

**Possible formats:**

| Format | Example | Compatible with |
|--------|---------|-----------------|
| Raw bcrypt | `$2b$12$N9qo8uLOickgx2Z...` | `bcrypt.checkpw()` directly |
| Django-prefixed bcrypt | `bcrypt$$2b$12$N9qo8uLOickgx2Z...` | Django's `check_password()` |
| Argon2 | `$argon2id$v=19$m=...` | `argon2` package |
| PBKDF2 | `pbkdf2_sha256$...` | Django's `check_password()` |

### 6.5 Hash compatibility

**Result: ⚠️ UNKNOWN — depends on the actual hash format.**

- If the hashes are **raw bcrypt** (`$2b$...`): use `bcrypt.checkpw()` directly
  in a custom `check_password()` override.
- If the hashes are **Django-prefixed** (`bcrypt$...` or `pbkdf2_...`):
  Django's built-in `check_password()` from `django.contrib.auth.hashers`
  will work.
- If the hashes are **Argon2**: the `argon2-cffi` package is needed.

**Recommendation:** Before implementation, run a query to inspect a sample
`passwordHash` value:
```sql
SELECT "email", "passwordHash" FROM "User" LIMIT 1;
```

### 6.6 Existing password verification process

**Result: ❌ NONE EXISTS.**

- `accounts/services.py` has `UserService` with `is_locked()` and
  `requires_password_change()` — but **no `verify_password()` or `login()`
  method**.
- `accounts/repositories.py` has `UserRepository.get_by_email()` — but no
  password verification.
- The frontend `LoginForm.astro` POSTs to `/api/auth/login` — but that
  endpoint **does not exist** on the backend (confirmed by search and
  `urls.py` inspection).
- The Prisma/Next.js app likely had its own auth (NextAuth with Prisma adapter,
  per `B3_4A_PRISMA_DEPENDENCY_AUDIT.md` §7) — but that's a separate, legacy
  system.

### 6.7 Dependency check

| Package | In Pipfile? | Required for auth? |
|---------|-------------|---------------------|
| `bcrypt` | ❌ No | Yes — if hashes are raw bcrypt |
| `Django` | ❌ Not in root Pipfile | Yes — backend framework (must be installed elsewhere) |
| `djangorestframework` | ❌ Not in root Pipfile | Yes — DRF (must be installed elsewhere) |
| `argon2-cffi` | ❌ No | Only if hashes are Argon2 |

> **Note:** The root `Pipfile` may not reflect the backend's actual
> dependencies. The backend may use a separate virtual environment or
> `requirements.txt`. This should be verified.

### 6.8 A1.0.4 Verdict

**⚠️ UNKNOWN — requires a database query to determine the hash format.** No
password verification logic exists in the backend. The `bcrypt` package is not
listed as a dependency. Before implementation:
1. Query the `User` table for a sample `passwordHash` value.
2. Determine the hash format (raw bcrypt, Django-prefixed, Argon2, etc.).
3. Add the appropriate hashing package to dependencies.
4. Implement `check_password()` / `set_password()` accordingly.

---

## 7. Summary Matrix

| Task | Check | Result | Severity |
|------|-------|--------|----------|
| A1.0.1 | `AUTH_USER_MODEL` configured | ❌ Not set | **Critical** |
| A1.0.1 | `User` extends `AbstractBaseUser` | ❌ Extends `models.Model` | **Critical** |
| A1.0.1 | `User` extends `PermissionsMixin` | ❌ No | **High** (needed for admin/permissions) |
| A1.0.1 | `is_authenticated` / `is_anonymous` | ❌ Missing | **Critical** |
| A1.0.1 | `get_username()` / `USERNAME_FIELD` | ❌ Missing | **Critical** |
| A1.0.1 | `get_session_auth_hash()` | ❌ Missing | **Critical** |
| A1.0.1 | `set_password()` / `check_password()` | ❌ Missing | **Critical** |
| A1.0.1 | `login()` compatibility | ❌ `AttributeError` | **Critical** |
| A1.0.1 | `logout()` compatibility | ✅ Works (moot) | — |
| A1.0.2 | Session creation via `login()` | ❌ Blocked by A1.0.1 | **Critical** |
| A1.0.2 | Session persistence across requests | ❌ Blocked by A1.0.1 | **Critical** |
| A1.0.2 | DRF `SessionAuthentication` | ❌ Blocked by A1.0.1 | **Critical** |
| A1.0.3 | Prisma ownership respected | ✅ `managed = False` preserved | — |
| A1.0.3 | DB schema unchanged by inheritance change | ✅ Python-only change | — |
| A1.0.3 | Prisma client/migrations unaffected | ✅ No schema change | — |
| A1.0.3 | Next.js app unaffected | ✅ Operates at DB level | — |
| A1.0.4 | bcrypt format known | ⚠️ Unknown (needs DB query) | **High** |
| A1.0.4 | Hash compatibility verified | ⚠️ Unknown | **High** |
| A1.0.4 | Password verification process exists | ❌ None exists | **Critical** |
| A1.0.4 | `bcrypt` dependency present | ❌ Not in Pipfile | **High** |

---

## 8. Overall Verdict

**A1.0 FAILS.** The current `accounts.User` model is fundamentally incompatible
with Django's built-in authentication framework. The A1.1 implementation
cannot proceed without remediation.

**However, A1.0.3 confirms the remediation is SAFE** — modifying `User` to
extend `AbstractBaseUser` will not break Prisma workflows or the database
schema.

---

## 9. Required Remediation (before A1.1)

### 9.1 Model changes (A1.0.1 remediation)

1. **Make `User` extend `AbstractBaseUser`** (and optionally `PermissionsMixin`
   if admin/permission support is needed).
2. **Remap `password_hash` → `password`** with `db_column='passwordHash'` so
   `AbstractBaseUser`'s `password` field maps to the existing column.
3. **Add `USERNAME_FIELD = 'email'`** and `REQUIRED_FIELDS = []`.
4. **Override `check_password()` / `set_password()`** if the hash format is
   not Django-compatible (pending A1.0.4 resolution).
5. **Set `AUTH_USER_MODEL = 'accounts.User'`** in `settings.py`.

### 9.2 Password storage (A1.0.4 remediation)

1. **Query the database** for a sample `passwordHash` value to determine the
   format.
2. **Add `bcrypt`** (or `argon2-cffi`) to dependencies if not present.
3. **Implement `check_password()`** to verify against the existing hash format.
4. **Implement `set_password()`** to hash new passwords in the same format
   (or migrate to Django's format on next password change).

### 9.3 Session auth validation (A1.0.2 re-test)

After remediation, re-run the session authentication validation:
1. Create a temporary test endpoint.
2. Verify `login()` creates a session without `AttributeError`.
3. Verify the session persists across requests.
4. Verify DRF `SessionAuthentication` returns the authenticated user.

---

## 10. Validation Checklist (post-remediation)

- [ ] `AUTH_USER_MODEL = 'accounts.User'` in `settings.py`
- [ ] `User` extends `AbstractBaseUser` (and `PermissionsMixin` if needed)
- [ ] `User.password` maps to `db_column='passwordHash'`
- [ ] `User.USERNAME_FIELD = 'email'`
- [ ] `User.is_authenticated` returns `True`
- [ ] `User.is_anonymous` returns `False`
- [ ] `User.get_username()` returns the email
- [ ] `User.get_session_auth_hash()` returns a stable HMAC string
- [ ] `User.check_password(raw)` verifies against `passwordHash` column
- [ ] `python manage.py check` passes with no errors
- [ ] `django.contrib.auth.login(request, user)` stores session without
      `AttributeError`
- [ ] `SessionAuthentication.authenticate(request)` returns the user
- [ ] `request.user.is_authenticated` is `True` after login
- [ ] Prisma client queries still work (no DB schema change)
- [ ] `prisma db push` does not alter the `User` table
- [ ] Password hash format determined (bcrypt / Django-prefixed / Argon2)
- [ ] `bcrypt` (or equivalent) added to dependencies

---

**End of audit.** No code changes were made. This document is a findings
report. Implementation may only proceed after the remediation in §9 is
completed and the validation checklist in §10 passes.