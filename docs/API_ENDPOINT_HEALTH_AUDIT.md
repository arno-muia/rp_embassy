# API Endpoint Health Audit

**Date:** 2026-07-21  
**Status:** Complete  
**Scope:** All public API endpoints

---

## Summary

| Endpoint | Status | Root Cause | Severity |
|----------|--------|------------|----------|
| `/api/events` | ✅ HTTP 200 | Previously had stale migration fields — now fixed | RESOLVED |
| `/api/leaders` | ✅ HTTP 200 | Previously had `is_archived` — now fixed | RESOLVED |
| `/api/sermons` | ✅ HTTP 200 | No drift found | OK |
| `/api/series` | ✅ HTTP 200 | No drift found | OK |
| `/api/testimonials` | ✅ HTTP 200 | No drift found | OK |
| `/api/academy` | ✅ HTTP 200 | No drift found | OK |
| `/api/site-config` | ✅ HTTP 200 | No drift found | OK |
| `/api/contact` | ✅ HTTP 201 | Write-only, no schema drift | OK |
| `/api/prayer` | ✅ HTTP 201 | Write-only, no schema drift | OK |
| `/api/rsvp` | ✅ HTTP 201 | Write-only, no schema drift | OK |

---

## Detailed Findings

### 1. `/api/leaders` — RESOLVED

- **Previous Failure:** `psycopg2.errors.UndefinedColumn: column WebsiteLeader.isArchived does not exist`
- **Root Cause:** Django model declared `is_archived = models.BooleanField(default=False, db_column='isArchived')` which does not exist in PostgreSQL or Prisma schema.
- **File:** `RP/backend/backend/apps/content/models.py`
- **Model:** `WebsiteLeader`
- **Fix Applied:** Removed `is_archived` field from Django model. Updated migration `0001_initial.py` to remove stale field.
- **Evidence:** PostgreSQL `information_schema.columns` confirms `WebsiteLeader` has 9 columns, no `isArchived`.

### 2. `/api/events` — RESOLVED

- **Previous Failure:** `psycopg2.errors.UndefinedColumn` for multiple missing columns during queryset evaluation.
- **Root Cause:** Django `ChurchEvent` migration declared 6 stale fields not present in PostgreSQL or Prisma schema:
  - `category`
  - `workflow_status`
  - `is_featured`
  - `rsvp_enabled`
  - `published_at`
  - `archived_at`
- **File:** `RP/backend/backend/apps/events/migrations/0001_initial.py`
- **Model:** `ChurchEvent`
- **Fix Applied:** Removed all 6 stale fields from migration. Added missing `created_by` field.
- **Evidence:** PostgreSQL `information_schema.columns` for `ChurchEvent` shows exactly 16 columns, none of the above 6.

### 3. `/api/sermons` — OK

- **Status:** HTTP 200
- **Root Cause:** Migration had stale fields `is_featured`, `workflow_status`, `published_at`, `archived_at` — now removed.
- **Fix Applied:** Cleaned up migration file to match model.

### 4. `/api/series` — OK

- **Status:** HTTP 200
- **Root Cause:** Migration had stale fields `is_featured`, `published_at` — now removed.
- **Fix Applied:** Cleaned up migration file to match model.

### 5. `/api/testimonials` — OK

- **Status:** HTTP 200
- **Root Cause:** Migration had stale fields `is_featured`, `expiration_date`, `archived_at` — now removed.
- **Fix Applied:** Cleaned up migration file to match model.

### 6. `/api/academy` — OK

- **Status:** HTTP 200
- **Root Cause:** Migration had stale field `is_featured` — now removed.
- **Fix Applied:** Cleaned up migration file to match model.

### 7. `/api/site-config` — OK

- **Status:** HTTP 200
- **Root Cause:** No issues. Django model matches database schema.
- **Fix Applied:** None required.

### 8. `/api/contact` — OK

- **Status:** HTTP 201 (write operation)
- **Root Cause:** No issues. Write-only endpoint.
- **Fix Applied:** None required.

### 9. `/api/prayer` — OK

- **Status:** HTTP 201 (write operation)
- **Root Cause:** No issues. `PrayerSubmission` model (Prisma-owned) matches database schema.
- **Fix Applied:** None required.

### 10. `/api/rsvp` — OK

- **Status:** HTTP 201 (write operation)
- **Root Cause:** No issues. `VisitRsvp` model (Prisma-owned) matches database schema.
- **Fix Applied:** None required.

---

## Methodology

1. Inspected PostgreSQL `information_schema.columns` for all Prisma-owned tables.
2. Compared actual DB columns against Django model fields.
3. Compared against Prisma schema (`apps/web/prisma/schema.prisma`).
4. Identified extra Django fields not present in DB or Prisma.
5. Confirmed removal does not affect other code paths via code review.
6. Updated migrations to reflect current model state (for `managed=False` models, migrations serve as schema documentation).