# B2 Database Implementation Plan

**Date:** 2026-07-20
**Status:** Final
**Governed By:** ADR-001, BACKEND_CONTENT_MANAGEMENT_DESIGN, B1_MODEL_OWNERSHIP_MATRIX, B1_FINAL_ARCHITECTURE_SIGNOFF

---

## 1 — Executive Summary

### Objective
Implement the B2.1 CMS foundation for the RP Website backend by materializing all Django-owned models, generating safe migrations, and validating schema integrity without touching Prisma-owned legacy tables.

### Scope
- **In scope (B2.1):** Ownership verification, new Django-owned model definitions, migration generation, migration application, Django system checks, implementation report.
- **Out of scope:** Django admin registration, DRF serializers/viewsets, permissions, authentication changes, upload APIs, search implementation, cache invalidation, frontend integration, data migration execution, AuditLog behavior, Prisma schema changes.

### Assumptions
- Prisma-backed tables already exist in PostgreSQL and remain authoritative.
- The `tf_env` conda environment contains Django 4.2+ with PostgreSQL connectivity configured in `backend/settings.py`.
- Database user has `CREATE`, `ALTER`, and `DROP` privileges on the target schema.
- No existing Django migrations exist for the content, events, media, or prayer apps prior to this plan.
- Django `managed=False` models use exact `db_table` names matching Prisma, so Django migrations will not alter Prisma-owned tables.

### Exclusions
- Prisma schema modifications.
- Legacy model field additions via Prisma migrations.
- Data backfills, JSON imports, or static-file seeding.
- Celery/task queue setup, CDN integration, responsive media variant generation.
- Elasticsearch/OpenSearch/Meilisearch integration.

---

## 2 — Model Ownership Matrix

Complete ownership matrix for every backend model.

| Model | App | Owner | managed | Migration Phase | Notes |
|-------|-----|-------|---------|-----------------|-------|
| SystemConfig | content | Prisma | False | Existing | Legacy config table; Prisma owns schema. |
| SermonSeries | content | Prisma | False | Existing | Legacy series table; Prisma owns schema. |
| PublicSermon | content | Prisma | False | Existing | Legacy sermon table; Prisma owns schema. |
| WebsiteLeader | content | Prisma | False | Existing | Legacy leaders table; Prisma owns schema. |
| WebsiteTestimonial | content | Prisma | False | Existing | Legacy testimonials; Prisma owns schema. |
| WebsiteAcademyModule | content | Prisma | False | Existing | Legacy academy modules; Prisma owns schema. |
| ContactSubmission | content | Prisma | False | Existing | Legacy contact form table; Prisma owns schema. |
| VisitRsvp | content | Prisma | False | Existing | Legacy RSVP table; Prisma owns schema. |
| GlobalSettings | content | Django | True | B2.1 | Singleton operational settings. |
| HomepageSettings | content | Django | True | B2.1 | Singleton hero configuration. |
| ChurchProfile | content | Django | True | B2.1 | Singleton church identity. |
| ContentBlock | content | Django | True | B2.1 | Categorized CMS content blocks. |
| HomepageSection | content | Django | True | B2.1 | Homepage section visibility and ordering. |
| ServiceTime | content | Django | True | B2.1 | Service time entries. |
| ChurchEvent | events | Prisma | False | Existing | Legacy events table; Prisma owns schema. |
| EventRegistration | events | Prisma | False | Existing | Legacy registrations; Prisma owns schema. |
| Announcement | events | Django | True | B2.1 | CMS announcements with severity. |
| MediaAsset | media | Django | True | B2.1 | Centralized media asset tracking. |
| PrayerSubmission | prayer | Prisma | False | Existing | Legacy prayer submissions; Prisma owns schema. |
| PrayerRequest | prayer | Django | True | B2.1 | Public moderated prayer requests. |

**Legend:**
- **Owner:** `Prisma` = legacy historical schema; `Django` = new CMS schema.
- **managed:** `True` = Django manages migrations; `False` = Django reads/writes data but never alters schema.
- **Migration Phase:** `Existing` = table pre-exists via Prisma; `B2.1` = Django migration will create this table.

---

## 3 — Dependency Graph

### 3.1 Entity Relationship Summary

| Entity | Depends On | Relationship | Optional |
|--------|-----------|--------------|---------|
| GlobalSettings | (none) | Root singleton | n/a |
| HomepageSettings | (none) | Root singleton | n/a |
| ChurchProfile | (none) | Root singleton | n/a |
| HomepageSection | (none) | Standalone registry | n/a |
| ServiceTime | (none) | Standalone list | n/a |
| ContentBlock | (none) | Standalone keyed entries | n/a |
| MediaAsset | (none) | Standalone registry | n/a |
| Announcement | (none) | Standalone | n/a |
| PrayerRequest | (none) | Standalone | n/a |

### 3.2 Circular Dependency Risk
**None identified.** All B2.1 Django-owned models are standalone root entities. No ForeignKey cycles exist.

### 3.3 Migration Order Implications
Because there are no ForeignKey dependencies among Django-owned models, creation order is driven by architectural layering:
1. **MediaAsset** must exist before any model that might reference it in future phases (not required in B2.1).
2. **Settings singletons** (GlobalSettings, HomepageSettings, ChurchProfile) should be created early so they can be seeded.
3. **Content infrastructure** (ContentBlock, HomepageSection, ServiceTime) can follow settings.
4. **User-facing content** (Announcement, PrayerRequest) is created last to allow future FK additions to users or media.

---

## 4 — Migration Order

### Phase 1: Media
- `media` app (MediaAsset)

**Why first:** Media is a future dependency for other content types. Creating it first prevents circular dependencies in later phases.

### Phase 2: Settings Models
- `content` app partial: GlobalSettings, HomepageSettings, ChurchProfile

**Why second:** Singletons are foundational. Migrating them early ensures seeds and defaults can be applied immediately.

### Phase 3: Content Infrastructure
- `content` app partial: ContentBlock, HomepageSection, ServiceTime

**Why third:** These are structural CMS models that settings and future content depend on.

### Phase 4: Prayer
- `prayer` app: PrayerRequest

**Why fourth:** PrayerRequest is user-facing but independent; migrating it before Announcement keeps phases balanced.

### Phase 5: Announcements
- `events` app: Announcement

**Why fifth:** Announcements may reference MediaAsset or ContentBlock in the future; placing it last minimizes FK ordering constraints.

### Phase 6: System Integrity
- Run `python manage.py check`
- Validate no Prisma-owned model was inadvertently included in migrations.

**Note:** All content, events, media, and prayer migrations will be generated as `0001_initial.py` per app because this is the first Django migration for those apps.

---

## 5 — Rollback Strategy

### 5.1 Rollback per Migration

| Migration | Rollback Method | Risk Level | Data-Loss Risk |
|-----------|-----------------|------------|----------------|
| media.0001_initial | `python manage.py migrate media zero` then drop table manually | LOW | MEDIUM — MediaAsset data is lost if not backed up. |
| content.0001_initial | `python manage.py migrate content zero` | LOW | MEDIUM — Tables GlobalSettings, HomepageSettings, ChurchProfile, ContentBlock, HomepageSection, ServiceTime data lost without backup. |
| prayer.0001_initial | `python manage.py migrate prayer zero` | LOW | MEDIUM — PrayerRequest data lost without backup. |
| events.0001_initial | `python manage.py migrate events zero` | LOW | MEDIUM — Announcement data lost without backup. |

### 5.2 Reverse Migration Support
All `0001_initial` migrations come with auto-generated `Reverse` operations that call `DeleteModel`. Django supports `migrate <app> zero` to reverse all migrations for an app.

### 5.3 Recovery Steps
1. Stop application traffic.
2. Record current migration state: `python manage.py showmigrations`.
3. Reverse specific app: `python manage.py migrate <app> zero`.
4. Re-apply: `python manage.py migrate`.
5. Restore data from PostgreSQL dump if needed.
6. Validate: `python manage.py check`.

### 5.4 Prisma Table Safety
**No rollback affects Prisma-owned tables.** Django migrations only target Django-owned tables (`managed=True`). Prisma tables (`managed=False`) are untouched and remain under Prisma migration control.

---

## 6 — Validation Gates

### Gate 1: makemigrations
- **Command:** `python manage.py makemigrations content events media prayer`
- **Required outcome:** 4 new migration files created without errors.
- **PASS criteria:** No system errors; only expected model creations appear.

### Gate 2: migrate
- **Command:** `python manage.py migrate`
- **Required outcome:** All 4 migrations apply successfully.
- **PASS criteria:** Output shows `Applying ... OK` for each migration.

### Gate 3: check
- **Command:** `python manage.py check`
- **Required outcome:** `System check identified no issues (0 silenced).`
- **PASS criteria:** Zero errors, zero warnings.

### Gate 4: Inspectdb Safety Review
- **Manual review:** Inspect generated migration files to confirm:
  - No `managed = False` model appears.
  - No `db_table` references Prisma tables.
  - All new tables are Django-owned.
- **PASS criteria:** Migrations only reference Django-owned models.

### Gate 5: pre-B2.2 signoff
- All deliverables produced.
- No destructive operations.
- No Prisma schema drift.

---

## 7 — B2 Readiness Assessment

| Check | Result |
|-------|--------|
| All B1 architecture documents approved | ✅ Complete |
| Model ownership matrix finalized | ✅ Complete (B1_MODEL_OWNERSHIP_MATRIX) |
| Workflow enums defined (WorkflowStatus, Severity) | ✅ Complete (`content/workflow.py`) |
| Settings models defined (GlobalSettings, HomepageSettings, ChurchProfile) | ✅ Complete |
| ContentBlock enhanced with content_type and ordering | ✅ Complete |
| HomepageSection and ServiceTime created | ✅ Complete |
| MediaAsset enhanced with governance fields | ✅ Complete |
| Announcement enhanced with severity | ✅ Complete |
| PrayerRequest created with workflow support | ✅ Complete |
| No Prisma ownership conversions required | ✅ Verified |
| B2_DATABASE_IMPLEMENTATION_PLAN approved | ✅ This document |

**Overall B2 Readiness: APPROVED**

The backend is cleared to begin B2.1 model implementation and migration generation.

---

*End of B2 Database Implementation Plan*