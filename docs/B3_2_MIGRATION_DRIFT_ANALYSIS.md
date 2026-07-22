# B3.2 Migration Drift Investigation — content.0005

**Date**: 2026-07-21  
**Project**: RP Website (Django-MVC)  
**Migration**: `content.0005_publicsermon_series_systemconfig_updated_by_and_more`  
**Objective**: Determine whether `content.0005` can safely be marked as applied using `python manage.py migrate content 0005 --fake`

---

## 1. Migration Operations Inventory

Migration `0005` contains **2 AddField operations** and **9 AddIndex operations**:

### AddField
1. `PublicSermon.series` — ForeignKey to `SermonSeries`, `db_column='seriesId'`, `db_constraint=False`, `null=True`, `blank=True`
2. `SystemConfig.updated_by` — ForeignKey to `User`, `db_column='updatedById'`, `db_constraint=False`, `null=True`, `blank=True`

### AddIndex
3. `ContactSubmission.created_at` → index name: `contactsub_creat_idx`
4. `PublicSermon.series_slug` → index name: `sermon_serislug_idx`
5. `PublicSermon.is_published` → index name: `sermon_ispub_idx`
6. `PublicSermon.date` → index name: `sermon_date_idx`
7. `SermonSeries.is_published` → index name: `series_ispub_idx`
8. `SermonSeries.sort_order` → index name: `series_sort_idx`
9. `SystemConfig.key` → index name: `syscfg_key_idx`
10. `VisitRsvp.created_at` → index name: `rsvp_created_idx`
11. `VisitRsvp.status` → index name: `rsvp_status_idx`
12. `WebsiteAcademyModule.sort_order` → index name: `academy_sort_idx`
13. `WebsiteTestimonial.sort_order` → index name: `testi_sort_idx`

*Note: Django auto-generates 2 additional indexes for ForeignKey fields: `PublicSermon_seriesId_959d1c5b` and `SystemConfig_updatedById_b94f0d76`.*

---

## 2. SQL Output Summary

Generated via:
```bash
C:\ProgramData\Anaconda3\envs\tf_env\python.exe rpwebsite/RP/backend/manage.py sqlmigrate content 0005
```

```sql
BEGIN;
ALTER TABLE "PublicSermon" ADD COLUMN "seriesId" uuid NULL;
ALTER TABLE "SystemConfig" ADD COLUMN "updatedById" uuid NULL;
CREATE INDEX "contactsub_creat_idx" ON "ContactSubmission" ("createdAt");
CREATE INDEX "sermon_serislug_idx" ON "PublicSermon" ("seriesSlug");
CREATE INDEX "sermon_ispub_idx" ON "PublicSermon" ("isPublished");
CREATE INDEX "sermon_date_idx" ON "PublicSermon" ("date");
CREATE INDEX "series_ispub_idx" ON "SermonSeries" ("isPublished");
CREATE INDEX "series_sort_idx" ON "SermonSeries" ("sortOrder");
CREATE INDEX "syscfg_key_idx" ON "SystemConfig" ("key");
CREATE INDEX "rsvp_created_idx" ON "VisitRsvp" ("createdAt");
CREATE INDEX "rsvp_status_idx" ON "VisitRsvp" ("status");
CREATE INDEX "academy_sort_idx" ON "WebsiteAcademyModule" ("sortOrder");
CREATE INDEX "testi_sort_idx" ON "WebsiteTestimonial" ("sortOrder");
CREATE INDEX "PublicSermon_seriesId_959d1c5b" ON "PublicSermon" ("seriesId");
CREATE INDEX "SystemConfig_updatedById_b94f0d76" ON "SystemConfig" ("updatedById");
COMMIT;
```

---

## 3. Database Verification Results

Verified via direct psycopg2 queries against PostgreSQL database `RP`.

### Column Verification

| Table | Column | Expected | Exists in DB |
|-------|--------|----------|--------------|
| PublicSermon | seriesId | Yes | Yes |
| SystemConfig | updatedById | Yes | Yes |

**Conclusion**: Both FK columns were added outside of Django migrations (drift confirmed).

### Index Verification

The database contains **auto-generated Django index names** rather than the **custom names** specified in migration 0005.

| Table | Expected Index Name (Migration) | Actual Index Name (DB) | Status |
|-------|--------------------------------|------------------------|--------|
| ContactSubmission | contactsub_creat_idx | contactsub_creat_idx | Present |
| PublicSermon | sermon_serislug_idx | PublicSermon_seriesSlug_idx | **MISSING** |
| PublicSermon | sermon_ispub_idx | PublicSermon_isPublished_idx | **MISSING** |
| PublicSermon | sermon_date_idx | PublicSermon_date_idx | **MISSING** |
| SermonSeries | series_ispub_idx | series_ispub_idx + SermonSeries_isPublished_idx | Duplicate present |
| SermonSeries | series_sort_idx | series_sort_idx + SermonSeries_sortOrder_idx | Duplicate present |
| SystemConfig | syscfg_key_idx | SystemConfig_key_idx | **MISSING** |
| VisitRsvp | rsvp_created_idx | rsvp_created_idx + VisitRsvp_createdAt_idx | Duplicate present |
| VisitRsvp | rsvp_status_idx | rsvp_status_idx + VisitRsvp_status_idx | Duplicate present |
| WebsiteAcademyModule | academy_sort_idx | academy_sort_idx + WebsiteAcademyModule_sortOrder_idx | Duplicate present |
| WebsiteTestimonial | testi_sort_idx | testi_sort_idx + WebsiteTestimonial_sortOrder_idx | Duplicate present |
| PublicSermon | PublicSermon_seriesId_959d1c5b | **NOT FOUND** | **MISSING** |
| SystemConfig | SystemConfig_updatedById_b94f0d76 | **NOT FOUND** | **MISSING** |

---

## 4. Migration History Review

```bash
C:\ProgramData\Anaconda3\envs\tf_env\python.exe rpwebsite/RP/backend/manage.py showmigrations content
```

```
content
 [X] 0001_initial
 [X] 0002_gin_search_indexes
 [X] 0003_alter_contactsubmission_options_and_more
 [X] 0004_alter_publicsermon_options_and_more
 [ ] 0005_publicsermon_series_systemconfig_updated_by_and_more
 [ ] 0006_alter_websiteleader_options
```

**Status**: `0005` is **NOT** marked as applied. `0006` is also NOT applied.

---

## 5. Verification Matrix

| Migration Operation | Exists In DB | Safe To Fake |
|---------------------|--------------|--------------|
| AddField PublicSermon.series (seriesId) | Yes | Yes |
| AddField SystemConfig.updated_by (updatedById) | Yes | Yes |
| AddIndex ContactSubmission.created_at (contactsub_creat_idx) | Yes | Yes |
| AddIndex PublicSermon.series_slug (sermon_serislug_idx) | **No** (PublicSermon_seriesSlug_idx exists) | **No** |
| AddIndex PublicSermon.is_published (sermon_ispub_idx) | **No** (PublicSermon_isPublished_idx exists) | **No** |
| AddIndex PublicSermon.date (sermon_date_idx) | **No** (PublicSermon_date_idx exists) | **No** |
| AddIndex SermonSeries.is_published (series_ispub_idx) | Partial (duplicate exists) | **No** |
| AddIndex SermonSeries.sort_order (series_sort_idx) | Partial (duplicate exists) | **No** |
| AddIndex SystemConfig.key (syscfg_key_idx) | **No** (SystemConfig_key_idx exists) | **No** |
| AddIndex VisitRsvp.created_at (rsvp_created_idx) | Partial (duplicate exists) | **No** |
| AddIndex VisitRsvp.status (rsvp_status_idx) | Partial (duplicate exists) | **No** |
| AddIndex WebsiteAcademyModule.sort_order (academy_sort_idx) | Partial (duplicate exists) | **No** |
| AddIndex WebsiteTestimonial.sort_order (testi_sort_idx) | Partial (duplicate exists) | **No** |
| Auto-index PublicSermon_seriesId_959d1c5b | **No** | **No** |
| Auto-index SystemConfig_updatedById_b94f0d76 | **No** | **No** |

---

## 6. Risk Assessment

### Primary Risk: Index Name Mismatch
The database was partially migrated using different index names (likely via Django auto-generation or manual SQL). Migration 0005 specifies custom index names that do **not exist**.

**Impact**:
- If `0005` is faked, Django will record those index names in `django_migrations`, but the actual indexes have different names.
- Future `migrate` operations or `sqlmigrate` calls will generate SQL that references non-existent index names if a reverse migration is attempted.
- `makemigrations` may not detect additional drift, leading to further divergence.
- The `DuplicateColumn: seriesId` error initially reported is now explained: the column exists, but the migration expects to add it in a specific order with specific index names that conflict with the current schema state.

### Secondary Risk: Missing FK Indexes
The auto-generated ForeignKey indexes (`PublicSermon_seriesId_959d1c5b`, `SystemConfig_updatedById_b94f0d76`) are **absent**, meaning FK join performance is degraded and referential integrity checks are unindexed.

### Tertiary Risk: Duplicate Indexes
Several tables have **both** the auto-generated Django index names AND the custom names from other migrations (e.g., `series_ispub_idx` and `SermonSeries_isPublished_idx`). This creates redundant indexes that waste disk space and slow down writes.

---

## 7. Follow-On Migration Review

### content.0006
`0006_alter_websiteleader_options` — only alters `Meta` options (ordering/verbose_name). It depends on `0005` being applied. **Safe to apply after 0005 is resolved.**

### events.0005
Not present in the project (no `events/migrations/0005_*` file). **No impact.**

---

## 8. Recommended Next Steps

**DO NOT run `python manage.py migrate content 0005 --fake`** until the following are corrected:

1. **Drop redundant duplicate indexes** on:
   - `SermonSeries`: keep `series_ispub_idx` and `series_sort_idx`, drop `SermonSeries_isPublished_idx` and `SermonSeries_sortOrder_idx`
   - `VisitRsvp`: keep `rsvp_created_idx` and `rsvp_status_idx`, drop `VisitRsvp_createdAt_idx` and `VisitRsvp_status_idx`
   - `WebsiteAcademyModule`: keep `academy_sort_idx`, drop `WebsiteAcademyModule_sortOrder_idx`
   - `WebsiteTestimonial`: keep `testi_sort_idx`, drop `WebsiteTestimonial_sortOrder_idx`

2. **Rename indexes** on `PublicSermon` and `SystemConfig` to match migration 0005:
   - `PublicSermon_seriesSlug_idx` → `sermon_serislug_idx`
   - `PublicSermon_isPublished_idx` → `sermon_ispub_idx`
   - `PublicSermon_date_idx` → `sermon_date_idx`
   - `SystemConfig_key_idx` → `syscfg_key_idx`

3. **Create missing FK indexes**:
   - `CREATE INDEX "PublicSermon_seriesId_959d1c5b" ON "PublicSermon" ("seriesId");`
   - `CREATE INDEX "SystemConfig_updatedById_b94f0d76" ON "SystemConfig" ("updatedById");`

4. **Re-run verification** to confirm all schema elements match migration 0005.

5. **Then** run: 
   ```bash
   python manage.py migrate content 0005 --fake
   ```

---

## Final Conclusion

```text
NOT SAFE TO FAKE content.0005
```

**Evidence**:
- Migration 0005 specifies custom index names (`sermon_serislug_idx`, `sermon_ispub_idx`, `sermon_date_idx`, `syscfg_key_idx`) that do **not exist** in PostgreSQL.
- Auto-generated Django index names (`PublicSermon_seriesSlug_idx`, `PublicSermon_isPublished_idx`, `PublicSermon_date_idx`, `SystemConfig_key_idx`) exist instead.
- The ForeignKey auto-indexes (`PublicSermon_seriesId_959d1c5b`, `SystemConfig_updatedById_b94f0d76`) are **missing**.
- Columns `seriesId` and `updatedById` were added outside of Django's migration system.
- Duplicate indexes exist on `SermonSeries`, `VisitRsvp`, `WebsiteAcademyModule`, and `WebsiteTestimonial`.

Faking `0005` would mark the migration as applied while leaving the database schema in a state that does not match what Django expects, creating latent risk for future migrations and schema introspection.