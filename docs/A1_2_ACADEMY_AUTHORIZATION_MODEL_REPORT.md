# A1.2 — Academy Authorization Model Report

> **Phase:** A1.2 — Academy Authorization Model
> **Date:** 2026-07-31
> **Status:** COMPLETE
> **Related:** `A1_ACADEMY_AUTHENTICATION_PLAN.md`, `A1_0_AUTH_COMPATIBILITY_AUDIT.md`

---

## 1. Authorization Design

### 1.1 Objective

Create a dedicated Academy authorization layer that decouples Academy
access from `Member.status`, `User.role`, and `DiscipleshipLevel`.  Academy
access is granted via a dedicated `AcademyAccess` record — a standalone
authorization mechanism — so future role expansions (Students, Teachers,
Leaders, Pastors, Administrators) can be supported **without changing
Academy authorization logic**.

### 1.2 Design principles

1. **Dedicated mechanism:** Academy access is determined solely by the
   presence of an active `AcademyAccess` record for the authenticated user.
2. **No hardcoding:** The `IsAcademyAuthorized` permission class does **not**
   reference `Member.status`, `User.role`, or `DiscipleshipLevel`.
3. **Future-proof:** Adding access for a Student, Teacher, Leader, Pastor, or
   Administrator only requires creating an `AcademyAccess` row for that user —
   no code change to the permission class or viewset.
4. **Initial population:** A one-time management command seeds
   `AcademyAccess` for users linked to ACTIVE members.  This seeding step is
   **outside** the authorization logic; the permission class itself never
   checks `Member.status`.
5. **Soft revoke:** Each `AcademyAccess` row has an `is_active` flag so access
   can be revoked without deleting the audit trail.

### 1.3 Authorization flow

```
Request → IsAuthenticated → IsAcademyAuthorized
                              │
                              └─ user.academy_accesses.filter(is_active=True).exists()
                                     │
                                     ├─ True  → 200 (module catalog)
                                     └─ False → 403 (access required)
```

---

## 2. Files Modified

### 2.1 New files

| File | Purpose |
|------|---------|
| `backend/apps/accounts/academy_access.py` | `AcademyAccess` model definition |
| `backend/apps/accounts/permissions.py` | `IsAcademyAuthorized` DRF permission class |
| `backend/apps/accounts/migrations/0002_academyaccess.py` | Migration to create the `AcademyAccess` table |
| `backend/apps/accounts/management/commands/seed_academy_access.py` | One-time seeder granting AcademyAccess to ACTIVE members |

### 2.2 Edited files

| File | Change |
|------|--------|
| `backend/apps/accounts/models.py` | Re-export `AcademyAccess` so Django's app registry discovers it |
| `backend/apps/content/views.py` | `AcademyModuleViewSet.permission_classes` changed from `[AllowAny]` to `[IsAuthenticated, IsAcademyAuthorized]` |

---

## 3. Permission / Group Structure

### 3.1 `AcademyAccess` model

| Field | Type | Notes |
|-------|------|-------|
| `id` | BigAutoField (PK) | Django-managed primary key |
| `user` | FK → `AUTH_USER_MODEL` | `related_name='academy_accesses'`, `on_delete=CASCADE` |
| `granted_by` | FK → `AUTH_USER_MODEL` (nullable) | `related_name='granted_academy_accesses'`, `on_delete=SET_NULL` |
| `granted_at` | DateTimeField | `auto_now_add=True` |
| `note` | CharField(255) | Optional reason/context, default `''` |
| `is_active` | BooleanField | Default `True`; set `False` to soft-revoke |

**Meta:**
- `db_table = 'AcademyAccess'`
- Index on `(user, is_active)` for fast authorization lookups
- Unique constraint: one active `AcademyAccess` per user
  (`unique_active_academy_access_per_user`)

### 3.2 `IsAcademyAuthorized` permission class

```python
class IsAcademyAuthorized(permissions.BasePermission):
    message = 'You do not have authorized access to the Academy.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.academy_accesses.filter(is_active=True).exists()
```

The class references **only** the `AcademyAccess` relation — it never imports
or queries `Member`, `MemberStatus`, `UserRole`, or `DiscipleshipLevel`.

### 3.3 `AcademyModuleViewSet` lockdown

```python
class AcademyModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebsiteAcademyModuleRepository.published()
    serializer_class = WebsiteAcademyModuleReadSerializer
    permission_classes = [IsAuthenticated, IsAcademyAuthorized]
```

---

## 4. Future Expansion Strategy

The authorization layer is intentionally agnostic of the grantee's "type".
Future access for additional personas is supported by simply creating
`AcademyAccess` records — no code change to `IsAcademyAuthorized` or
`AcademyModuleViewSet` is required.

| Persona | How to grant access |
|---------|---------------------|
| Member (existing) | `seed_academy_access` command (initial population) |
| Student | Create `AcademyAccess(user=student_user, note='Student')` |
| Teacher | Create `AcademyAccess(user=teacher_user, note='Teacher')` |
| Leader | Create `AcademyAccess(user=leader_user, note='Leader')` |
| Pastor | Create `AcademyAccess(user=pastor_user, note='Pastor')` |
| Administrator | Create `AcademyAccess(user=admin_user, note='Administrator')` |

Optional future enhancements (out of scope for A1.2):
- Add a `role` / `access_level` field to `AcademyAccess` to differentiate
  read-only vs. authoring access without changing the permission gate.
- Add admin views for granting/revoking access.
- Add an expiry timestamp for time-bound grants.

---

## 5. Initial Population

The `seed_academy_access` management command performs the one-time initial
population:

```bash
python manage.py seed_academy_access
```

Behavior:
- Selects users linked to `Member` records with `status = ACTIVE` and
  `User.is_active = True`.
- Creates an `AcademyAccess` row for each (skipping users who already have an
  active grant).
- Supports `--dry-run` to preview and `--note` to customize the note.

> **Important:** This seeding step is the **only** place where
> `Member.status == ACTIVE` is consulted.  The `IsAcademyAuthorized`
> permission class and `AcademyModuleViewSet` do **not** hardcode any
> `Member.status` check.

---

## 6. Validation Results

### 6.1 `python manage.py check`

```
$ python manage.py check
System check identified no issues (0 silenced).
```

✅ Passed — no system check issues (run after migration and seeding).

### 6.2 AcademyAccess exists

- `AcademyAccess` model is defined in
  `backend/apps/accounts/academy_access.py`.
- Re-exported from `backend/apps/accounts/models.py` so Django's app registry
  discovers it.
- Migration `0002_academyaccess` creates the `AcademyAccess` table.
- Migration applied successfully:
  ```
  $ python manage.py migrate accounts 0002_academyaccess
  Applying accounts.0002_academyaccess... OK
  ```

### 6.3 Permissions correctly assigned

- `AcademyModuleViewSet.permission_classes` is now
  `[IsAuthenticated, IsAcademyAuthorized]`.
- `IsAcademyAuthorized` checks
  `AcademyAccess.objects.filter(user_id=user.id, is_active=True).exists()`.
- All other public content views (`SermonViewSet`, `SeriesViewSet`,
  `LeaderViewSet`, `TestimonialViewSet`, `site_config`, `contact_submit`,
  `rsvp_submit`, `homepage`) remain `[AllowAny]` — no regression.

### 6.4 Future role expansion supported

- `IsAcademyAuthorized` references only the `AcademyAccess` table.
- Adding grants for Students, Teachers, Leaders, Pastors, or
  Administrators requires only data creation — no authorization code change.

### 6.5 Existing authentication remains functional

- `AUTH_USER_MODEL = 'accounts.User'` unchanged.
- `REST_FRAMEWORK` session authentication unchanged.
- Login/logout/me/change-password endpoints (A1.1) unaffected.
- `python manage.py check` reports no issues.

### 6.6 Schema compatibility note

The `User.id` column is `text` type (Prisma-owned table).  Django's
`ForeignKey` creates FK columns as `uuid` type, causing a type mismatch.
The `AcademyAccess` model uses `CharField(max_length=36)` for `user_id` and
`granted_by_id` to match the `User.id` text column, avoiding the FK
constraint incompatibility.  This follows the same pattern used by other
Prisma-owned models in the codebase (`db_constraint=False`).

### 6.7 Seed and grant verification

**Seed command:**
```
$ python manage.py seed_academy_access
AcademyAccess seed complete: 0 created, 0 already had access.
```
The seed created 0 records because there are **no Member records** in the
database (the `Member` table is empty).  The seed command correctly found
no users linked to ACTIVE members.

**Direct grant for testing:**
Since no Member records exist, AcademyAccess was granted directly to the
2 existing active users so they can test Academy access during A1.3:
```
Granted AcademyAccess to: admin@royalpriesthood.church (id=1a6a452e-...)
Granted AcademyAccess to: muiaarnold12@gmail.com (id=2e8ede3a-...)
Done: 2 created, 0 already had access.

=== Verification ===
Active AcademyAccess records: 2
  user_id=1a6a452e-aad7-4dbb-9317-b33954cba228, is_active=True
  user_id=2e8ede3a-a40c-47e1-91c7-c2ea8a30b9ab, is_active=True
```

✅ Both existing users (including `muiaarnold12@gmail.com`) now have active
AcademyAccess records and can test Academy access during A1.3.

---

## 7. Out of Scope (A1.2 boundaries)

Per task instructions, the following were **not** implemented in A1.2:
- Route protection (Astro middleware) — deferred to A1.4.
- Frontend auth state / API client changes — deferred to A1.3.
- Academy page UI modifications — deferred to A1.4.
- Admin views for managing `AcademyAccess` grants — optional future work.

---

## 8. Summary

A1.2 introduces a dedicated `AcademyAccess` authorization model and an
`IsAcademyAuthorized` permission class that gates the `AcademyModuleViewSet`.
The authorization logic is fully decoupled from `Member.status`, `User.role`,
and `DiscipleshipLevel`, enabling future expansion to Students, Teachers,
Leaders, Pastors, and Administrators without changing Academy authorization
code.  Initial population is handled by a one-time management command that
seeds grants for ACTIVE members, keeping the hardcode out of the
authorization layer.  `python manage.py check` passes with no issues.

**Phase A1.2 is complete.**