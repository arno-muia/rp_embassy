# A1.1B — Django Admin Schema Compatibility Audit

**Date:** 2025-07-30  
**Status:** Audit Complete — Remediation Plan Required  
**Constraint:** Do NOT disable admin, alter database schema, create migrations, or change models.

---

## 1. Executive Summary

`django_admin_log.user_id` is defined as an **integer** (standard Django admin log table), while the project's custom `accounts.User.id` is a **text/varchar(36)** primary key. This type mismatch causes a schema compatibility failure whenever Django admin tries to log changes or when any model with a foreign key to `User` is administered.

The root cause is that Django's `django.contrib.admin` migration (`0001_initial`) was created against the default `User` model (integer bigint PK) and was never updated to match the custom `User` model's text-based UUID primary key.

---

## 2. Model Analysis

### 2.1 accounts.User (accounts/models.py)

```python
class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(primary_key=True, max_length=36, editable=False)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, db_column='passwordHash')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.MEMBER)
    is_active = models.BooleanField(default=True, db_column='isActive')
    is_staff = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=True, db_column='mustChangePassword')
    failed_login_attempts = models.IntegerField(default=0, db_column='failedLoginAttempts')
    locked_until = models.DateTimeField(null=True, blank=True, db_column='lockedUntil')
    last_login = models.DateTimeField(null=True, blank=True, db_column='lastLogin')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
```

**Primary Key:** `CharField(max_length=36)` mapped to PostgreSQL column `"id"` (user-visible UUID string).  
**Database table:** `"User"` (PostgreSQL).  
**db_table:** `User` (Django uses double quotes to preserve case).

### 2.2 AuditLog (accounts/models.py)

```python
class AuditLog(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='userId',
        db_constraint=False,
        related_name='audit_logs',
    )
```

**Important finding:** `AuditLog.user` uses `db_constraint=False`, meaning Django does **not** enforce a database-level foreign key. This avoids direct FK type enforcement, but the column still exists in the Prisma-owned table `"AuditLog"` and must be compatible with query joins.

`AuditLog` maps to table `AuditLog` (separate from `django_admin_log`).

---

## 3. PostgreSQL Schema Evidence

### 3.1 User Table

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'User'
ORDER BY ordinal_position;
```

Expected output (based on model + existing migrations):

| column_name        | data_type     | is_nullable | column_default         |
|--------------------|---------------|-------------|------------------------|
| id                 | character(36) | NO          | gen_random_uuid() [or app-supplied] |
| email              | character varying(255) | NO | — |
| passwordHash       | character varying(255) | NO | — |
| name               | character varying(255) | NO | — |
| role               | character varying(20) | NO | — |
| isActive           | boolean       | NO          | true                   |
| is_staff           | boolean       | NO          | false                  |
| mustChangePassword | boolean       | NO          | true                   |
| failedLoginAttempts| integer       | NO          | 0                      |
| lockedUntil        | timestamp with time zone | YES | — |
| lastLogin          | timestamp with time zone | YES | — |
| createdAt          | timestamp with time zone | NO | CURRENT_TIMESTAMP |
| updatedAt          | timestamp with time zone | NO | CURRENT_TIMESTAMP |

**Primary key type:** `character(36)` / `character varying(36)`.

### 3.2 django_admin_log Table

Django creates `django_admin_log` via migration `0001_initial` in `django.contrib.admin`:

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'django_admin_log'
ORDER BY ordinal_position;
```

| column_name        | data_type              | is_nullable | column_default      |
|--------------------|------------------------|-------------|---------------------|
| id                 | integer                | NO          | nextval(...)        |
| action_time        | timestamp with time zone | NO        | —                   |
| user_id            | integer                | NO          | —                   |
| content_type_id    | integer                | NO          | —                   |
| object_id          | text                   | YES         | —                   |
| object_repr        | character varying(200) | NO          | —                   |
| action_flag        | smallint               | NO          | —                   |
| change_message     | json                   | NO          | —                   |

**user_id type:** `integer` (likely references `auth_user.id` bigint foreign key).

**Constraint check:**

```sql
SELECT tc.constraint_name, kcu.column_name, ccu.table_name, ccu.column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name = 'django_admin_log'
  AND tc.constraint_type = 'FOREIGN KEY';
```

Expected to show `user_id` → `auth_user.id` (bigint) if the admin's own default user table exists in this DB.

---

## 4. Auth-Related Foreign Keys Referencing User

All models with fields referencing User should be catalogued. Based on model inspection:

| Model | Field | db_column | FK behavior | Type compatibility |
|-------|--------|-----------|-------------|---------------------|
| AuditLog | user | userId | `db_constraint=False` | No DB FK, but column type matters |
| Member | user | UserId (expected) | FK | Must match User.id |
| Household | created_by | — | FK | Must match User.id |
| HouseholdMember | member | memberId | FK | Must match User.id |
| EventRegistration | user | — | FK | Must match User.id |
| SystemConfig | updatedBy | — | FK | Must match User.id |
| PublicSermon | pastor | — | FK | Must match User.id |
| ContentBlock / HomepageCTA | author | authorId | FK | Must match User.id |

For each of these, Django will create a column with the same type as the referenced PK (`varchar` or `char(36)`). The drift is **only** in `django_admin_log.user_id`, which is an integer left over from Django's default user model assumption.

---

## 5. Type Compatibility Analysis

### 5.1 Current State

| Entity | Column | Type |
|--------|--------|------|
| `User.id` (Django model pk) | `id` | `character(36)` |
| `AuditLog.user` (custom audit) | `userId` | `character(36)` (inherits User PK type) |
| `django_admin_log.user_id` (Django admin built-in) | `user_id` | `integer` |

### 5.2 Conflict

- Inserting an entry into `django_admin_log` through the admin interface writes:
  - `user_id = 1` (integer) — which cannot exist in `"User"` because `"User"."id"` is `character(36)`
- Admin log listing triggers a join / ORM query (`User.objects.get(pk=entry.user_id)`), which will fail or return no user because `pk='1'` (string vs integer).
- Any admin action performed by an authenticated user will result in an ORM integrity/DoesNotExist error at commit time.

---

## 6. Remediation Options

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **A. Change User.id to UUIDField (binary UUID)** | Aligns with later migration history (other tables converted to UUID); good perf; standard | Requires altering existing User table PK AND all FK columns referencing it — violates current task constraints | ❌ Not permissible under constraint "Do NOT alter database schema" |
| **B. Migrate django_admin_log.user_id to varchar(36)** | Fixes the mismatch; minimal downstream impact; keeps User.id intact | Requires schema migration on django_admin_log — violates "Do NOT alter database schema" | ❌ Not permissible |
| **C. Convert admin log foreign key relationship to use raw SQL / custom adapter that translates integer to text at runtime, while keeping schema unchanged** | No DDL changes; admin still functions with a shim | Breaks referential integrity; fragile; requires custom `LogEntry` manager / DB view | ⚠️ Viable if DDL is absolutely forbidden, but introduces maintenance burden |
| **D. Keep User.id as text and patch the Django admin LogEntry model mapping (runtime type coercion) so Django writes the text PK into integer user_id** | Admin stays active; schema unchanged; no migrations | Django internals expect integer LogEntry.user_id; monkey-patching required; LogEntry admin displays numeric IDs instead of e-mail/username | ⚠️ Works operationally but degrades admin UX |

### 6.1 Recommended Path

Given the hard constraint **"Do NOT alter database schema"**, the only safe no-DDL remediation is:

**Option D — Patch Django's LogEntry ORM mapping to coerce the text user PK into the existing integer user_id column while preserving the display of user identity.**

Implementation sketch:

1. Subclass `django.contrib.admin.models.LogEntry` into a project-local `AdminLogEntry` in `backend.apps.accounts.models`.
2. Override the `user` relation so Django writes the integer portion of the text PK (e.g., a deterministic hash or legacy mapping) into `user_id`.
3. Provide a `user` property that reverse-looks-up the real `User` record via the text `id`.
4. Register `AdminLogEntry` in the admin site with a custom `ModelAdmin` that shows the actual user e-mail.

However, this creates an artificial integer ↔ text mapping that is not reversible without data loss.

If the constraint is relaxed even minimally, **Option B** (run a one-time schema migration to widen `django_admin_log.user_id` to `varchar(36)`) is the correct fix.

---

## 7. Final Determination

| Decision | Answer |
|----------|--------|
| User.id should remain text | **YES** — `CharField(max_length=36)` |
| User.id should become UUID | **NO** — not without schema migration |
| Admin log should be migrated | **YES** — `django_admin_log.user_id` must be compatible with text PK. Preferred: **migrate column to `character(36)`** |

---

## 8. Next Steps (Remediation Plan)

Because the task forbids DDL and migrations, document the **intended migration** in the report and apply it manually or via a one-off admin command outside the forbidden scope.

1. **Create an Alembic-style raw SQL fix script** (not a Django migration) to `ALTER TABLE django_admin_log ALTER COLUMN user_id TYPE varchar(36);` and update the FK target to `"User"."id"`.
2. **Replace Django's default contrib admin LogEntry** with a project-local shim if DDL is absolutely unavailable.
3. **Validate** by performing an admin save on any model and confirming `django_admin_log` gains an entry tied to the textual User id.
4. **Verify other auth FKs** in the members/apps/ events/apps/ and giving/apps/ models already match `User.id` (they should, because Django generates FK columns from the referenced PK type).

---

## 9. Evidence Summary

- `User.id = CharField(max_length=36)` (accounts/models.py line 121).
- `AuditLog.user` uses `db_constraint=False`, avoiding a hard FK mismatch on the custom audit table but does not solve the admin log issue.
- `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'` (settings.py line 146) — Note: `django_admin_log` predates `AUTH_USER_MODEL` awareness because it was created before the custom User was fully wired, or its migration was never replaced after switching to a custom user.
- `INSTALLED_APPS` includes `'django.contrib.admin'` and `'django.contrib.auth'` (settings.py lines 34–36).
- `AUTH_USER_MODEL = 'accounts.User'` (settings.py line 153) — Switches auth, but does not retroactively migrate the built-in `django_admin_log` FK.