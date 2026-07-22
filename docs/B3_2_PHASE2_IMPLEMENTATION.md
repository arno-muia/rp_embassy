# B3.2 Phase 2 — Ownership Conversion Implementation

**Phase:** B3.2 — Ownership Conversion Implementation (Phase 2 / Group A)  
**Date:** 2026-07-21  
**Status:** Complete  
**Related:** `RP/docs/B3_1_*`, `RP/docs/B3_2_PHASE1_IMPLEMENTATION.md`, `RP/docs/B3_2_PHASE1_VALIDATION.md`

---

## Executive Summary

Phase 2 of the Prisma → Django ownership conversion has been completed. Three medium-risk models with FK dependencies were converted from `managed=False` to `managed=True`.

### Converted Models

| # | Model | Table | App | Risk Level | Notes |
|---|-------|-------|-----|------------|-------|
| 1 | PublicSermon | PublicSermon | content | MEDIUM | Has FK to SermonSeries (now Django-owned), GIN search indexes |
| 2 | SystemConfig | SystemConfig | content | MEDIUM | Has FK to User (still Prisma-owned, kept db_constraint=False) |
| 3 | ChurchEvent | ChurchEvent | events | MEDIUM | Has FK to User (still Prisma-owned, kept db_constraint=False), GIN search indexes |

### Total Combined Progress (Phase 1 + Phase 2)

| Phase | Models Converted | Tables |
|-------|-----------------|--------|
| Phase 1 | 6 | WebsiteTestimonial, WebsiteAcademyModule, ContactSubmission, VisitRsvp, PrayerSubmission, SermonSeries |
| Phase 2 | 3 | PublicSermon, SystemConfig, ChurchEvent |
| **Total** | **9** | **9 tables now Django-owned** |

---

## Conversion Steps Performed

### Step 1: Model Changes

For each model, `managed = False` → `managed = True` while preserving:

- ✅ `db_table` values: `PublicSermon`, `SystemConfig`, `ChurchEvent`
- ✅ UUID primary keys with `default=uuid.uuid4`
- ✅ All field definitions with `db_column` mappings
- ✅ All existing indexes including GIN search indexes
- ✅ `db_constraint=False` on FK fields (SystemConfig → User, ChurchEvent → User)
- ✅ No changes to field types, nullability, or defaults

**Files modified:**
1. `backend/backend/apps/content/models.py` — PublicSermon, SystemConfig (lines 21-38, 76-117)
2. `backend/backend/apps/events/models.py` — ChurchEvent (lines 47-88)

### Step 2: Migration Generation

Three migration files were generated across two apps:

#### Migration 1: `content/migrations/0004_alter_publicsermon_options_and_more.py`
```python
operations = [
    migrations.AlterModelOptions(name='publicsermon', options={'managed': True}),
    migrations.AlterModelOptions(name='systemconfig', options={'managed': True}),
    # Re-claim existing Prisma indexes with IF NOT EXISTS
    migrations.RunSQL('CREATE INDEX IF NOT EXISTS ... ON "ContactSubmission" ...'),
    migrations.RunSQL('CREATE INDEX IF NOT EXISTS ... ON "SermonSeries" ...'),
    migrations.RunSQL('CREATE INDEX IF NOT EXISTS ... ON "VisitRsvp" ...'),
    migrations.RunSQL('CREATE INDEX IF NOT EXISTS ... ON "WebsiteAcademyModule" ...'),
    migrations.RunSQL('CREATE INDEX IF NOT EXISTS ... ON "WebsiteTestimonial" ...'),
]
```

#### Migration 2: `events/migrations/0003_alter_churchevent_options.py`
```python
operations = [
    migrations.AlterModelOptions(name='churchevent', options={'managed': True}),
]
```

### Step 3: SQL Review

#### Content app (0004):

```sql
BEGIN;
-- Change Meta options on publicsermon -- (no-op)
-- Change Meta options on systemconfig -- (no-op)
-- Create indexes with IF NOT EXISTS (safe)
CREATE INDEX IF NOT EXISTS "contactsub_creat_idx" ON "ContactSubmission" ("createdAt");
CREATE INDEX IF NOT EXISTS "series_ispub_idx" ON "SermonSeries" ("isPublished");
CREATE INDEX IF NOT EXISTS "series_sort_idx" ON "SermonSeries" ("sortOrder");
CREATE INDEX IF NOT EXISTS "rsvp_created_idx" ON "VisitRsvp" ("createdAt");
CREATE INDEX IF NOT EXISTS "rsvp_status_idx" ON "VisitRsvp" ("status");
CREATE INDEX IF NOT EXISTS "academy_sort_idx" ON "WebsiteAcademyModule" ("sortOrder");
CREATE INDEX IF NOT EXISTS "testi_sort_idx" ON "WebsiteTestimonial" ("sortOrder");
COMMIT;
```

**Safety analysis:**
- ❌ No table recreation
- ❌ No ALTER TABLE on data columns
- ❌ No DROP INDEX
- ✅ `CREATE INDEX IF NOT EXISTS` — idempotent, safe for existing indexes
- ✅ No data migration operations

#### Events app (0003):

```sql
BEGIN;
-- Change Meta options on churchevent -- (no-op)
COMMIT;
```
**Completely no-op.**

### Step 4: Migration Application

Both migrations applied successfully:

```
$ python manage.py migrate events
Applying events.0003_alter_churchevent_options... OK

$ python manage.py migrate content
Applying content.0004_alter_publicsermon_options_and_more... OK
```

---

## Migration Files Created

| File | Path | Lines |
|------|------|-------|
| `0004_alter_publicsermon_options_and_more.py` | `backend/backend/apps/content/migrations/` | 62 |
| `0003_alter_churchevent_options.py` | `backend/backend/apps/events/migrations/` | 16 |

---

## Risk Observations

### 1. Index Reclamation via RunSQL
**Observation:** The content migration 0004 includes `CREATE INDEX IF NOT EXISTS` statements for indexes that were previously defined in the model's `Meta.indexes` but existed only in PostgreSQL from Prisma schema.
**Resolution:** Modified the auto-generated migration to use `RunSQL` with `IF NOT EXISTS` clause, making it safe for indexes that already exist.

### 2. FK Constraints Remain Unchanged
**Observation:** Both SystemConfig and ChurchEvent have FK references to `accounts.User` which remains `managed=False` (Phase 3 scope). The `db_constraint=False` setting was preserved.
**Resolution:** No constraint enforcement change — FKs remain logical-only during transition.

### 3. GIN Search Index Integrity
**Observation:** The GIN search indexes created during B2.3 on `PublicSermon` and `ChurchEvent` were not affected by this migration. No ALTER operations touched these tables.

---

## Deviation from Expected Ownership-Only Migration

**Minor deviation:** The auto-generated content migration 0004 included `AddIndex` operations for 7 indexes on Phase 1 models. These were converted to `RunSQL` with `IF NOT EXISTS` to ensure idempotency. This is a safety enhancement, not a regression.

All other migrations (events 0003) were pure ownership-only migrations with no DDL.

---

## GO / NO-GO Recommendation

**STATUS: ✅ GO**

### Rationale

1. **Data preserved** — No destructive operations
2. **No schema changes** to table columns or PKs
3. **Indexes safe** — `IF NOT EXISTS` ensures idempotent index creation
4. **FK behavior unchanged** — `db_constraint=False` maintained
5. **GIN indexes intact** — No operations on PublicSermon or ChurchEvent columns
6. **No downtime** — Sub-second migrations
7. **Full rollback available** — `python manage.py migrate content 0003` and `python manage.py migrate events 0002`

### Next Steps (Phase 3)

Remaining models for Phase 3 (high risk, requires maintenance window):

| Model | App | Reason |
|-------|-----|--------|
| WebsiteLeader | content | Already schema-clean |
| User | accounts | Authentication critical |
| AuditLog | accounts | Auth-critical |
| Household | members | Complex FKs |
| Member | members | Complex FKs, PII |
| HouseholdMember | members | Bridge table |
| GivingTransaction | giving | Financial data |
| EventRegistration | events | Multi-FK |

**END OF DOCUMENT**