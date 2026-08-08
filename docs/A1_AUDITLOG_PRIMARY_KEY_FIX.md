# A1 AuditLog Primary Key Fix

## Root Cause

The `AuditLog` model in `rpwebsite/RP/backend/backend/apps/accounts/models.py` defines `id` as a `CharField(max_length=255, primary_key=True)`. The database table `AuditLog` (Prisma-owned, `managed=False`) expects a non-empty string primary key. However, the `_write_audit()` helper in `views.py` called `AuditLog.objects.create(...)` without supplying an `id`, causing Django to attempt an insert with an empty primary key. PostgreSQL rejected this with:

```
IntegrityError: duplicate key value violates unique constraint "AuditLog_pkey"
Key (id)=() already exists
```

## Files Modified

- `rpwebsite/RP/backend/backend/apps/accounts/views.py`

## Schema Findings

- `AuditLog` is marked `managed = False` and maps to the existing Prisma-owned table.
- The `id` column is a `CharField` (not an auto-incrementing integer or UUID).
- No default value is defined in the Django model for `id`, so omitting it results in an empty string being sent to the database.
- Other models in the project use either `CharField` IDs (e.g., `User.id`) or UUIDs, but `AuditLog` is unique in that it is unmanaged and requires explicit ID assignment.

## Fix Applied

Updated `_write_audit()` in `views.py` to generate a UUID string for every new `AuditLog` entry:

```python
import uuid

def _write_audit(user, action, request):
    AuditLog.objects.create(
        id=str(uuid.uuid4()),
        user=user,
        action=action,
        entity_type='User',
        entity_id=str(user.id) if user else None,
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        timestamp=timezone.now(),
    )
```

## Validation Results

- `python manage.py check` passes with no issues.
- Login succeeds and returns a valid session.
- `AuditLog` records are created with unique UUID primary keys.
- Session creation and `/academy` access remain functional.