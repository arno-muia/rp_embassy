# B2.2 Remediation Plan

**Phase:** B2.2 — Schema Drift Resolution  
**Date:** 2026-07-20  
**Status:** Pending Approval  
**Related:** `RP/docs/B2_2_SCHEMA_DRIFT_AUDIT.md`, `RP/docs/B1_MODEL_OWNERSHIP_MATRIX.md`

---

## Source of Truth

Per the approved B1 architecture (`B1_MODEL_OWNERSHIP_MATRIX.md`):

- **Prisma schema** is authoritative for all legacy content models.
- Django acts as a **read/write client** only.
- **No Django migrations** may touch `managed = False` tables.
- Ownership conversion to Django is deferred post-B7.

Therefore, the Django model must be corrected to match the Prisma schema exactly.

---

## Remediation Steps

### 1. Remove unsupported field from Django model

**File:** `RP/backend/backend/apps/content/models.py`

**Change:** Remove the `is_archived` field from `WebsiteLeader` which does not exist in the database or Prisma schema.

**Before:**
```python
class WebsiteLeader(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    bio = models.TextField()
    photo_url = models.CharField(max_length=512, db_column='photoUrl')
    sort_order = models.IntegerField(default=0, db_column='sortOrder')
    social = models.JSONField(null=True, blank=True)
    is_published = models.BooleanField(default=True, db_column='isPublished')
    is_archived = models.BooleanField(default=False, db_column='isArchived')  # REMOVE
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
```

**After:**
```python
class WebsiteLeader(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    bio = models.TextField()
    photo_url = models.CharField(max_length=512, db_column='photoUrl')
    sort_order = models.IntegerField(default=0, db_column='sortOrder')
    social = models.JSONField(null=True, blank=True)
    is_published = models.BooleanField(default=True, db_column='isPublished')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
```

### 2. Verify no other code references `is_archived` on WebsiteLeader

Search for any usage of `is_archived` in serializers, views, services, or frontend code. If found, remove or replace with `is_published` semantics.

**Command:**
```bash
grep -r "is_archived" rpwebsite/RP/backend/ rpwebsite/RP/website/src/
```

If the grep returns results, update each reference. If no results, proceed.

### 3. Validate Django model loads without error

Run a Django shell check to confirm the model can be imported and queried:

```bash
cd rpwebsite/RP/backend
python manage.py shell -c "from apps.content.models import WebsiteLeader; print(WebsiteLeader._meta.get_fields())"
```

Expected: No `UndefinedColumn` error. Field list should not include `is_archived`.

### 4. Confirm API endpoint recovers

```bash
curl -s http://localhost:8000/api/leaders/ | head -c 200
```

Expected: JSON array response, HTTP 200.

---

## Constraints

- **Do NOT create a Django migration** for this change. The table schema is Prisma-owned.
- **Do NOT convert ownership** of `WebsiteLeader` to Django. Remain `managed = False`.
- **Do NOT add the missing column** to the database. That would bypass Prisma ownership and create drift in the opposite direction.

---

## Rollback

If any issue arises after removal:

1. Re-add `is_archived = models.BooleanField(default=False, db_column='isArchived')` to `WebsiteLeader`.
2. The field will again cause query errors until the database column is added via Prisma migration.
3. Coordinate with Prisma migration to add `isArchived` column if the feature is genuinely required.

---

## Post-Remediation Audit

After applying the fix, re-run the schema inspection script to confirm:

- All 8 legacy tables have matching Django model fields.
- No extra fields remain in Django models that do not exist in PostgreSQL.