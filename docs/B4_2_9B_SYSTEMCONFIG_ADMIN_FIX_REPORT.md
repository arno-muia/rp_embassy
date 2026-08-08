# B4.2.9B — SystemConfig Admin Fix Report

**Date:** 2026-07-24  
**Phase:** Implementation  
**Status:** FIX APPLIED AND VALIDATED

---

## 1. File Modified

**File:** `backend/apps/accounts/models.py`  
**Model:** `User`  
**Field:** `password_hash`

### Change

**Before:**
```python
password_hash = models.CharField(max_length=255)
```

**After:**
```python
password_hash = models.CharField(
    max_length=255,
    db_column='passwordHash',
)
```

### Rationale

The PostgreSQL column is `passwordHash` (camelCase), but the Django field `password_hash` (snake_case) had no `db_column` override. Django was generating `"User"."password_hash"` which does not exist. All other camelCase columns in the User model already had explicit `db_column` overrides — `password_hash` was the only one missing it.

---

## 2. Validation Results

### 2.1 User.objects.first() — PASS

```
QuerySet returned 1 row(s)
```

The ORM query executed successfully without error.

### 2.2 Generated SQL — PASS

```sql
SELECT "User"."id", "User"."email", "User"."passwordHash", "User"."name",
       "User"."role", "User"."isActive", "User"."mustChangePassword",
       "User"."failedLoginAttempts", "User"."lockedUntil", "User"."lastLogin",
       "User"."createdAt", "User"."updatedAt"
FROM "User" LIMIT 1
```

Django now correctly generates `"User"."passwordHash"` instead of `"User"."password_hash"`.

### 2.3 No SQL references to `password_hash` — PASS

```
No captured query references 'password_hash'.
```

Zero queries contain the incorrect column name.

### 2.4 db_column mapping — PASS

```
password_hash|passwordHash|False
```

The field `password_hash` now correctly maps to `passwordHash` in PostgreSQL.

---

## 3. Constraints Compliance

| Constraint | Status |
|---|---|
| No migrations created | PASS — `managed = False`, no migration needed |
| No database schema altered | PASS — PostgreSQL unchanged |
| No database columns renamed | PASS |
| No PostgreSQL direct modification | PASS |
| SystemConfig model unchanged | PASS |
| SystemConfig admin unchanged | PASS |
| No serializers changed | PASS |
| No API endpoints changed | PASS |

---

## 4. Summary

A single `db_column='passwordHash'` parameter was added to the `User.password_hash` field in `backend/apps/accounts/models.py`. This is a minimal, zero-risk fix that restores Django Admin access to SystemConfig records by correcting the ORM column mapping. No migration, schema change, or additional refactoring was performed.
