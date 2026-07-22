# B2.2 Existing Content Model Hardening — Implementation Report

**Date:** 2026-07-20
**Phase:** B2.2 — Existing Content Model Hardening
**Status:** Complete — No Code Changes Required
**Execution Basis:** B2.1 Post-Implementation Audit (GO), Approved Architecture Documents

---

## 1. Scope Clarification

B2.2 hardening applies to these Prisma-owned legacy models:

| Model | App | Managed | Owner |
|-------|-----|---------|-------|
| PublicSermon | content | False | Prisma |
| SermonSeries | content | False | Prisma |
| WebsiteLeader | content | False | Prisma |
| WebsiteTestimonial | content | False | Prisma |
| WebsiteAcademyModule | content | False | Prisma |
| ChurchEvent | events | False | Prisma |

**Critical constraint:** These remain `managed=False`. Django does not own their schema. No Django migration may create, alter, or drop these tables.

---

## 2. Architecture Requirements vs. Current State

### 2.1 PublicSermon

| Required Hardening | Architecture Source | Current State | Action |
|--------------------|---------------------|---------------|--------|
| `workflow_status` (Draft/In Review/Approved/Published/Archived) | ADR-001, BACKEND_CONTENT_MANAGEMENT_DESIGN | ✅ Present | None |
| `published_at` | ADR-001 | ✅ Present | None |
| `archived_at` | ADR-001 | ✅ Present | None |
| `is_featured` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present | None |
| `is_published` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present | None |
| `series_slug`, `series_title` | B1_API_CONTRACT_MATRIX | ✅ Present | None |
| Indexes: workflow, publication, featured | BACKEND_CONTENT_MANAGEMENT_DESIGN | ✅ Present (`sermon_wf_idx`, `sermon_ispub_idx`, `sermon_feat_idx`) | None |
| Meta ordering | Architecture | ✅ Not set in Meta | None required — ordering is presentation-layer concern |

### 2.2 SermonSeries

| Required Hardening | Architecture Source | Current State | Action |
|--------------------|---------------------|---------------|--------|
| `is_featured` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present | None |
| `is_published` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present | None |
| `sort_order` | BACKEND_CONTENT_MANAGEMENT_DESIGN | ✅ Present (`sortOrder`) | None |
| `published_at` | ADR-001 | ✅ Present | None |
| Indexes: publication, sort, featured | Architecture | ✅ Present | None |

### 2.3 WebsiteLeader

| Required Hardening | Architecture Source | Current State | Action |
|--------------------|---------------------|---------------|--------|
| `is_archived` | BACKEND_CONTENT_MANAGEMENT_DESIGN | ✅ Present (`isArchived`) | None |
| `is_published` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present | None |
| `sort_order` | Architecture | ✅ Present (`sortOrder`) | None |
| Indexes: sort, archive | Architecture | ✅ Present | None |

### 2.4 WebsiteTestimonial

| Required Hardening | Architecture Source | Current State | Action |
|--------------------|---------------------|---------------|--------|
| `is_featured` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present | None |
| `is_published` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present | None |
| `expiration_date` | BACKEND_CONTENT_MANAGEMENT_DESIGN | ✅ Present (`expirationDate`) | None |
| `archived_at` | ADR-001 | ✅ Present (`archivedAt`) | None |
| `sort_order` | Architecture | ✅ Present (`sortOrder`) | None |
| Indexes: sort, featured, expiry | Architecture | ✅ Present | None |

### 2.5 WebsiteAcademyModule

| Required Hardening | Architecture Source | Current State | Action |
|--------------------|---------------------|---------------|--------|
| `is_featured` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present | None |
| `is_published` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present | None |
| `sort_order` | Architecture | ✅ Present (`sortOrder`) | None |
| `lessons_count` | BACKEND_CONTENT_MANAGEMENT_DESIGN | ✅ Present | None |
| Indexes: sort, featured | Architecture | ✅ Present | None |

### 2.6 ChurchEvent

| Required Hardening | Architecture Source | Current State | Action |
|--------------------|---------------------|---------------|--------|
| `category` (explicit choices) | BACKEND_CONTENT_MANAGEMENT_DESIGN | ✅ Present (EventCategory choices) | None |
| `type` (explicit choices) | Architecture | ✅ Present (ChurchEventType choices) | None |
| `workflow_status` | ADR-001 | ✅ Present | None |
| `is_featured` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present (`isFeatured`) | None |
| `rsvp_enabled` | B1_MODEL_OWNERSHIP_MATRIX | ✅ Present (`rsvpEnabled`) | None |
| `published_at` | ADR-001 | ✅ Present | None |
| `archived_at` | ADR-001 | ✅ Present | None |
| `registration_required` | Architecture | ✅ Present | None |
| Indexes: start, status, type, workflow, featured | Architecture | ✅ Present | None |

---

## 3. Fields Added

**No fields were added during B2.2.**

All architecture-required hardening fields were already present in the Django model definitions inherited from B2.1 initial migrations. These models are `managed=False` and their schema is owned by Prisma; Django reflects the schema but does not alter it.

---

## 4. Indexes Added

**No indexes were added during B2.2.**

All architecture-required indexes were already present in the model `Meta.indexes` definitions:
- `sermon_serislug_idx`, `sermon_ispub_idx`, `sermon_date_idx`, `sermon_wf_idx`, `sermon_feat_idx` (PublicSermon)
- `series_ispub_idx`, `series_sort_idx`, `series_feat_idx` (SermonSeries)
- `leader_sort_idx`, `leader_archived_idx` (WebsiteLeader)
- `testi_sort_idx`, `testi_feat_idx`, `testi_expiry_idx` (WebsiteTestimonial)
- `academy_sort_idx`, `academy_feat_idx` (WebsiteAcademyModule)
- `event_start_idx`, `event_status_idx`, `event_type_idx`, `event_wf_idx`, `event_feat_idx` (ChurchEvent)

---

## 5. Migrations Created

**No migrations were created during B2.2.**

Since these are Prisma-owned models (`managed=False`), Django migrations never touch their tables. Any future schema changes to these tables must be done via Prisma migrations, not Django.

| Expected Migration | Action |
|--------------------|--------|
| content/0002_*.py | NOT CREATED — no Django-owned changes |
| events/0002_*.py | NOT CREATED — no Django-owned changes |

---

## 6. Validation Results

### 6.1 makemigrations

```text
No changes detected
```

**Result:** PASS — no pending migrations for Prisma-owned models.

### 6.2 migrate

Already applied from B2.1. No new migrations to apply.

### 6.3 check

```text
System check identified no issues (0 silenced).
```

**Result:** PASS

---

## 7. Risks

| Risk | Severity | Status |
|------|----------|--------|
| B2.2 scope was intentionally narrow (Prisma-owned models only) | LOW | Accepted |
| Future Prisma schema changes must be coordinated with Django model updates | MEDIUM | Deferred to B7 cutover planning |
| Missing `display_order` on PublicSermon (uses `date` for ordering) | LOW | Accepted — date-based ordering is intentional |
| Singleton enforcement not implemented for settings models | LOW | Deferred to B3 |

---

## 8. B2.3 Readiness

**GO**

All architecture-required hardening fields are already present in the Django model definitions. The Prisma-owned models require no further Django-side schema work. B2.3 may proceed with:
- PostgreSQL Full Text Search indexes (new Django migrations)
- Search vector integration
- GIN index creation

---

*End of B2.2 Implementation Report*