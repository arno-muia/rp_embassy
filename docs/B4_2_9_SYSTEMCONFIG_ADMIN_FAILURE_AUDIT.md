# B4.2.9 — SystemConfig Admin Failure Audit

**Date:** 2026-07-24  
**Phase:** Investigation Only  
**Status:** ROOT CAUSE IDENTIFIED (no fix implemented)

---

## Executive Summary

Opening a SystemConfig record in Django Admin fails with:

```
column User.password_hash does not exist
HINT:  Perhaps you meant to reference the column "User.passwordHash".
```

**Root Cause:** The `accounts.User` model field `password_hash` is missing its `db_column` mapping. The Django field is named `password_hash` (snake_case), but the actual PostgreSQL column is `passwordHash` (camelCase). All other camelCase fields in the User model have explicit `db_column` overrides — `password_hash` is the only one that does not.

**Offending Model:** `backend/apps/accounts/models.py` — `User` class  
**Offending Field:** `password_hash` (line 67)  
**Offending SQL:** `SELECT "User"."id", "User"."email", "User"."password_hash", ... FROM "User" LIMIT 1`  
**Required Fix:** Add `db_column='passwordHash'` to the `password_hash` field definition.

---

## 1. User Model Inspection

### File: `backend/apps/accounts/models.py`

```python
class User(models.Model):
    """Maps to Prisma model User -> table 'User'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)          # <-- MISSING db_column!
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.MEMBER)
    is_active = models.BooleanField(default=True, db_column='isActive')
    must_change_password = models.BooleanField(default=True, db_column='mustChangePassword')
    failed_login_attempts = models.IntegerField(default=0, db_column='failedLoginAttempts')
    locked_until = models.DateTimeField(null=True, blank=True, db_column='lockedUntil')
    last_login = models.DateTimeField(null=True, blank=True, db_column='lastLogin')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')

    class Meta:
        managed = False
        db_table = 'User'
```

### Finding: `db_column` Missing

| Field Name | `db_column` | PostgreSQL Column | Status |
|---|---|---|---|
| `id` | `None` | `id` | OK (same name) |
| `email` | `None` | `email` | OK (same name) |
| **`password_hash`** | **`None`** | **`passwordHash`** | **MISMATCH** |
| `name` | `None` | `name` | OK (same name) |
| `role` | `None` | `role` | OK (same name) |
| `is_active` | `isActive` | `isActive` | OK |
| `must_change_password` | `mustChangePassword` | `mustChangePassword` | OK |
| `failed_login_attempts` | `failedLoginAttempts` | `failedLoginAttempts` | OK |
| `locked_until` | `lockedUntil` | `lockedUntil` | OK |
| `last_login` | `lastLogin` | `lastLogin` | OK |
| `created_at` | `createdAt` | `createdAt` | OK |
| `updated_at` | `updatedAt` | `updatedAt` | OK |

Every other camelCase column in the User model has an explicit `db_column` override. Only `password_hash` is missing it.

---

## 2. SystemConfig Model Inspection

### File: `backend/apps/content/models.py`

```python
class SystemConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField()
    description = models.CharField(max_length=2000, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
    updated_by = models.ForeignKey(
        'accounts.User',
        null=True, blank=True,
        on_delete=models.DO_NOTHING,
        db_column='updatedById',
        db_constraint=False,
        related_name='system_configs',
    )
```

### Finding: SystemConfig FK to User

SystemConfig has a single FK to User: `updated_by` with `db_column='updatedById'`. This FK is exposed in the admin interface (see Section 3), which causes Django Admin to load User records. Loading User records triggers the failing query because the User model's `password_hash` field has no `db_column` mapping.

---

## 3. SystemConfig Admin Inspection

### File: `backend/apps/content/admin.py`

```python
@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'updated_by', 'updated_at')
    search_fields = ('key', 'description', 'value')
    list_filter = ('updated_at',)
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'description')
        }),
        ('Audit', {
            'fields': ('updated_by', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    ordering = ('key',)
```

### Finding: `updated_by` in Admin

The `updated_by` FK field appears in:
- `list_display` — causes User query on changelist page
- `fieldsets` — causes User query on change form page

When Django Admin renders either the changelist or the change form, it must load the User model to display the FK value. This triggers `User.objects.all()` (or similar), which generates a `SELECT` on the `User` table that includes all fields — including `password_hash`. Since `password_hash` has no `db_column`, Django generates `"User"."password_hash"` which does not exist in PostgreSQL.

---

## 4. PostgreSQL Schema Verification

### Actual columns on `User` table:

```
COLUMN_NAME|DATA_TYPE|IS_NULLABLE|COLUMN_DEFAULT
-----------|----------|-----------|-------------
id|text|NO|None
email|text|NO|None
passwordHash|text|NO|None          <-- camelCase
name|text|NO|None
role|USER-DEFINED|NO|'MEMBER'::"UserRole"
isActive|boolean|NO|true
mustChangePassword|boolean|NO|true
failedLoginAttempts|integer|NO|0
lockedUntil|timestamp without time zone|YES|None
lastLogin|timestamp without time zone|YES|None
createdAt|timestamp without time zone|NO|CURRENT_TIMESTAMP
updatedAt|timestamp without time zone|NO|None
```

The PostgreSQL column is `passwordHash` (camelCase), not `password_hash` (snake_case).

---

## 5. Reproduced Failing SQL

### Exact SQL generated by Django:

```sql
SELECT "User"."id", "User"."email", "User"."password_hash", "User"."name",
       "User"."role", "User"."isActive", "User"."mustChangePassword",
       "User"."failedLoginAttempts", "User"."lockedUntil", "User"."lastLogin",
       "User"."createdAt", "User"."updatedAt"
FROM "User" LIMIT 1
```

### Error:

```
django.db.utils.ProgrammingError: column User.password_hash does not exist
LINE 1: SELECT "User"."id", "User"."email", "User"."password_hash", ...
                                            ^
HINT:  Perhaps you meant to reference the column "User.passwordHash".
```

---

## 6. Root Cause Analysis

### Mismatch Classification: **B. db_column is missing**

The model was generated from a Prisma schema where the column is `passwordHash` (camelCase). The Django model field was named `password_hash` (following Python/Django snake_case convention), but the `db_column` parameter was omitted. Django therefore assumes the column name matches the field name (`password_hash`), which does not exist in PostgreSQL.

All other camelCase columns in the User model have explicit `db_column` overrides. This was an oversight when the model was initially created.

### Chain of Failure:

1. User visits `/admin/content/systemconfig/<uuid>/change/`
2. Django Admin renders the SystemConfig change form
3. The form includes `updated_by` ForeignKey field
4. Django Admin creates a `ModelChoiceField` with `queryset = User.objects.all()`
5. Django generates `SELECT ... FROM "User"` including all fields
6. Django uses field name `password_hash` as column name (no `db_column`)
7. PostgreSQL rejects `"User"."password_hash"` — column does not exist
8. `ProgrammingError` is raised, admin page crashes

---

## 7. Required Fix

### File: `backend/apps/accounts/models.py`, line 67

**Current:**
```python
password_hash = models.CharField(max_length=255)
```

**Required:**
```python
password_hash = models.CharField(max_length=255, db_column='passwordHash')
```

### Impact:

- **No migration needed** — the model uses `managed = False`, so Django does not manage the schema. Adding `db_column` only changes how Django maps the field to the existing column.
- **No data loss** — the column already exists in PostgreSQL with the correct name.
- **No schema change** — the PostgreSQL table is unchanged.
- **Fixes the admin** — Django will now generate `"User"."passwordHash"` instead of `"User"."password_hash"`.

---

## 8. Risk Assessment

| Risk Category | Level | Notes |
|---|---|---|
| Code change risk | LOW | Single field parameter addition |
| Regression risk | LOW | All other fields already use `db_column` pattern |
| Data integrity risk | NONE | No schema or data changes |
| Admin availability risk | HIGH (currently broken) | Fix restores admin functionality |
| Migration risk | NONE | `managed = False` — no migration needed |

---

## 9. GO/NO-GO Assessment

**GO** for implementation phase B4.2.9B.

The root cause is clearly identified, the fix is minimal and low-risk, and the impact of not fixing is that SystemConfig admin (and any other admin page that loads User records) remains broken.

---

## Appendix: Diagnostic Script

See `rpwebsite/RP/backend/audit_b429.py` for the complete diagnostic routine used to:
1. Query PostgreSQL `information_schema.columns` for the User table
2. Inspect Django model field-to-column mappings
3. Reproduce the failing SQL via Django ORM
4. Capture and display the exact generated SQL
5. Inspect SystemConfig FK and admin configuration
