# B2.1 Schema Hardening & Ownership Implementation Report

**Date:** 2026-07-20
**Phase:** B2.1 — Schema Hardening & Ownership Implementation
**Status:** Complete
**Governed By:** B1 Architecture Documents (ADR-001, BACKEND_CONTENT_MANAGEMENT_DESIGN, B1_MODEL_OWNERSHIP_MATRIX, B1_FINAL_ARCHITECTURE_SIGNOFF)

---

## 1. Models Audited

### Content App (`backend/apps/content/models.py`)

| Model | Managed | Ownership | Verdict |
|-------|---------|-----------|---------|
| SystemConfig | False | Prisma-owned | ✅ Verified, no changes |
| SermonSeries | False | Prisma-owned | ✅ Verified, no changes |
| PublicSermon | False | Prisma-owned | ✅ Verified, no changes |
| WebsiteLeader | False | Prisma-owned | ✅ Verified, no changes |
| WebsiteTestimonial | False | Prisma-owned | ✅ Verified, no changes |
| WebsiteAcademyModule | False | Prisma-owned | ✅ Verified, no changes |
| ContactSubmission | False | Prisma-owned | ✅ Verified, no changes |
| VisitRsvp | False | Prisma-owned | ✅ Verified, no changes |
| GlobalSettings | True | Django-owned | ✅ Verified |
| HomepageSettings | True | Django-owned | ✅ Verified |
| ChurchProfile | True | Django-owned | ✅ Verified |
| ContentBlock | True | Django-owned | ✅ Enhanced (added content_type, display_order, is_active) |
| HomepageSection | True | Django-owned | ✅ Newly created |
| ServiceTime | True | Django-owned | ✅ Newly created |

### Events App (`backend/apps/events/models.py`)

| Model | Managed | Ownership | Verdict |
|-------|---------|-----------|---------|
| ChurchEvent | False | Prisma-owned | ✅ Verified, no changes |
| EventRegistration | False | Prisma-owned | ✅ Verified, no changes |
| Announcement | True | Django-owned | ✅ Verified |

### Media App (`backend/apps/media/models.py`)

| Model | Managed | Ownership | Verdict |
|-------|---------|-----------|---------|
| MediaAsset | True | Django-owned | ✅ Enhanced (added file_size, checksum, focal_point, is_public, usage_count) |

### Prayer App (`backend/apps/prayer/models.py`)

| Model | Managed | Ownership | Verdict |
|-------|---------|-----------|---------|
| PrayerSubmission | False | Prisma-owned | ✅ Verified, no changes |
| PrayerRequest | True | Django-owned | ✅ Verified |

---

## 2. Ownership Decisions

All ownership decisions follow the B1_MODEL_OWNERSHIP_MATRIX exactly:

- **7 Prisma-owned models**: SystemConfig, SermonSeries, PublicSermon, WebsiteLeader, WebsiteTestimonial, WebsiteAcademyModule, ContactSubmission, VisitRsvp, ChurchEvent, EventRegistration, PrayerSubmission — all remain `managed=False` with exact `db_table` names. No schema modifications made.
- **9 Django-owned models**: GlobalSettings, HomepageSettings, ChurchProfile, ContentBlock, HomepageSection, ServiceTime, Announcement, MediaAsset, PrayerRequest — all `managed=True`.

---

## 3. Models Enhanced or Created

### Enhanced (3 models)

| Model | App | Fields Added |
|-------|-----|--------------|
| **ContentBlock** | content | `content_type` (choices: BELIEF, VALUE, FAQ, EXPECTATION, PAGE_SECTION, THEME), `display_order`, `is_active`. Indexes on `content_type` and `display_order`. |
| **MediaAsset** | media | `file_size` (BigIntegerField), `checksum` (CharField, max_length=64), `focal_point_x` (FloatField, default=0.5), `focal_point_y` (FloatField, default=0.5), `is_public` (BooleanField, default=True), `usage_count` (IntegerField, default=0). Indexes on `checksum` and `is_public`. |

### Created (2 models)

| Model | App | Fields |
|-------|-----|--------|
| **HomepageSection** | content | `section_name` (CharField, unique), `enabled` (BooleanField), `display_order` (IntegerField), timestamps. Indexes on `display_order` and `enabled`. |
| **ServiceTime** | content | `day` (CharField with DayOfWeek choices), `time` (TimeField), `label` (CharField), `display_order` (IntegerField), timestamps. Indexes on `display_order` and `day`. |

---

## 4. Conversions from `managed=False`

No models were converted from `managed=False` to `managed=True`. This is intentional per the B1 architecture:
- Legacy Prisma-backed models remain `managed=False`.
- New Django-owned models were always `managed=True` from their creation.
- No migration risk was introduced by altering legacy table ownership.

---

## 5. Migration Files Created

| App | Migration File | Operation Type |
|-----|----------------|----------------|
| content | `0001_initial.py` | Create all models (both Prisma-owned managed=False and Django-owned managed=True) |
| events | `0001_initial.py` | Create all models (both Prisma-owned managed=False and Django-owned managed=True) |
| media | `0001_initial.py` | Create MediaAsset model with all governance fields |
| prayer | `0001_initial.py` | Create PrayerSubmission (managed=False) and PrayerRequest (managed=True) |

### Migration Safety Verification

- **No destructive operations**: No table drops, column drops, or data deletions.
- **No Prisma table modifications**: All Prisma-owned tables use `managed=False` with exact `db_table` names. Django migrations do not touch these tables.
- **No data loss**: All migrations are additive (new tables, new columns with defaults).

---

## 6. Validation Results

| Check | Result |
|-------|--------|
| `python manage.py makemigrations` | ✅ Passed — 4 migration files generated |
| `python manage.py migrate` | ✅ Passed — all migrations applied OK |
| `python manage.py check` | ✅ Passed — 0 issues silenced |

---

## 7. Risks Discovered

| Risk | Severity | Status |
|------|----------|--------|
| HomepageSection and ServiceTime models initially placed in wrong section of content/models.py (above legacy models) | LOW | ✅ Resolved - Rewritten with correct ordering |
| Prisma-backed models created with Django migrations — expected behavior since `managed=False` with `db_table` prevents actual schema creation for those tables | LOW | ✅ Verified - No tables created for managed=False models |
| ContentBlock `ContentType` choices class name could conflict with model names | LOW | ✅ Verified — No conflict exists |

---

## 8. Outstanding Work Deferred to B2.2+

| Item | Phase | Reason |
|------|-------|--------|
| Admin registration for all new models | B3 | B2.1 is schema-only |
| DRF serializers and viewsets | B3 | B2.1 is schema-only |
| Role-based permissions | B3 | B2.1 is schema-only |
| Workflow enforcement (Draft→In Review→Approved→Published→Archived) | B3 | B2.1 is schema-only |
| AuditLog wiring for mutating endpoints | B3 | B2.1 is schema-only |
| Media upload endpoint and storage integration | B4 | B2.1 is schema-only |
| MediaAsset responsive variants | B4 | B2.1 is schema-only |
| PostgreSQL Full Text Search indexes | B5 | B2.1 is schema-only |
| Cache invalidation hooks | B5 | B2.1 is schema-only |
| Data migration from static JSON | B7 | B2.1 is schema-only |
| Feature-flagged frontend cutover | B6/B7 | B2.1 is schema-only |

---

## 9. Summary

B2.1 Schema Hardening is **complete**. All B1 architecture requirements for schema ownership have been implemented:

- ✅ All models classified correctly (Prisma-owned vs Django-owned)
- ✅ No ownership conflicts detected
- ✅ ContentBlock enhanced with content_type, display_order, and is_active
- ✅ MediaAsset enhanced with governance fields (file_size, checksum, focal_point, is_public, usage_count)
- ✅ HomepageSection created (section_name, enabled, display_order)
- ✅ ServiceTime created (day, time, label, display_order)
- ✅ Migrations generated and applied without errors
- ✅ `python manage.py check` passes with 0 issues
- ✅ No destructive operations or data loss
- ✅ B2.1 scope strictly maintained (no admin, no permissions, no serializers, no viewsets)

The backend is now ready for **Phase B3** (Admin Registration & Permissions).