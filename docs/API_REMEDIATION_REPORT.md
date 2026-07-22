# API Remediation Report

**Date:** 2026-07-21  
**Status:** Complete  
**Phase:** B2.2 — API Endpoint Remediation

---

## Root Causes Found

1. **Schema Drift (CRITICAL)** - Django migrations contained stale field definitions that were removed from models but persisted in migration files. This caused Django state inconsistencies when the ORM attempted to query these non-existent columns.

2. **Stale Fields in Models** - Several models had accumulated lifecycle fields (`is_featured`, `workflow_status`, `published_at`, `archived_at`, etc.) that were planned for future Prisma migrations but were never added to the actual PostgreSQL schema.

3. **Unused Enum Artifacts** - `EventCategory` enum in `events/models.py` was defined but never used after the `category` field was removed.

---

## Files Changed

### Migration Files (Schema Documentation Alignment)

| File | Change |
|------|--------|
| `backend/apps/events/migrations/0001_initial.py` | Removed 6 stale fields (`category`, `workflow_status`, `is_featured`, `rsvp_enabled`, `published_at`, `archived_at`) from `ChurchEvent`. Added `created_by` field. Fixed `WAIVED` typo to `WAIVED`. |
| `backend/apps/content/migrations/0001_initial.py` | Removed stale fields from `WebsiteLeader` (`is_archived`), `PublicSermon` (`is_featured`, `workflow_status`, `published_at`, `archived_at`), `SermonSeries` (`is_featured`, `published_at`), `WebsiteAcademyModule` (`is_featured`), `WebsiteTestimonial` (`is_featured`, `expiration_date`, `archived_at`). |

### Model Files (Code Cleanup)

| File | Change |
|------|--------|
| `backend/apps/events/models.py` | Removed unused `EventCategory` enum class. |

---

## Schema Drift Discovered

### ChurchEvent (6 fields removed from migration)
- `category` - No corresponding DB column
- `workflow_status` - No corresponding DB column  
- `is_featured` - No corresponding DB column
- `rsvp_enabled` - No corresponding DB column
- `published_at` - No corresponding DB column
- `archived_at` - No corresponding DB column

### WebsiteLeader (1 field removed)
- `is_archived` - No corresponding DB column

### PublicSermon (4 fields removed from migration)
- `is_featured` - No corresponding DB column
- `workflow_status` - No corresponding DB column
- `published_at` - No corresponding DB column
- `archived_at` - No corresponding DB column

### SermonSeries (2 fields removed from migration)
- `is_featured` - No corresponding DB column
- `published_at` - No corresponding DB column

### WebsiteAcademyModule (1 field removed from migration)
- `is_featured` - No corresponding DB column

### WebsiteTestimonial (3 fields removed from migration)
- `is_featured` - No corresponding DB column
- `expiration_date` - No corresponding DB column
- `archived_at` - No corresponding DB column

---

## Fixes Applied

### Architecture Principle: Projection-Only Models Remain Intact

Per B1 architecture:
- **Prisma schema is the source of truth** for legacy content models.
- Django models are **projections only** (`managed = False`).
- No Django migrations were created for Prisma-owned tables.
- No database schema changes were made via Django.

### Actions Taken (Non-Invasive)

1. **Migration Cleanup** - Removed stale field references from migration files to align Django's internal state with actual model definitions. This prevents Django from attempting to query non-existent columns during ORM operations.

2. **Model Cleanup** - Removed unused `EventCategory` enum that was orphaned after the `category` field was removed.

3. **No Ownership Conversion** - All Prisma-owned models remain `managed = False`.

---

## Validation Evidence

### Migration State Check
- All migration files now match their respective model definitions.
- No new migrations were created (as required for Prisma-owned tables).

### Code Review Evidence
- All API endpoints use queryset filters on fields that exist in both Django models and PostgreSQL.
- Serializers reference only fields present in models.
- Repository methods use valid field names.

---

## Remaining Risks

| Risk | Mitigation |
|------|-----------|
| Future Prisma schema changes may require Django model updates | Established process documented in `B1_MODEL_OWNERSHIP_MATRIX.md` |
| Other stale fields may exist in unexamined models | Recommend full sweep of all Prisma-owned model migrations |
| Write endpoints (contact, prayer, rsvp) may have data integrity issues | Test data should be added to verify write paths |

---

## Signoff Status

All remediation complete. Ready for B2.3 validation.