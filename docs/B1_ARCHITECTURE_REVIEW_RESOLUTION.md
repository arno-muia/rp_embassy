# B1 Architecture Review Resolution

**Date:** 2026-07-20
**Status:** Complete — All Required Revisions Implemented
**ADR:** ADR-001-CONTENT-MANAGEMENT-ARCHITECTURE.md
**Design Doc:** BACKEND_CONTENT_MANAGEMENT_DESIGN.md

---

## 1. Summary of Approved Architecture

The B1 architecture establishes a **dual-ownership schema strategy** for the RP Website backend:

- **Prisma remains historical schema owner** for legacy public content tables (SermonSeries, PublicSermon, WebsiteLeader, WebsiteTestimonial, WebsiteAcademyModule, ChurchEvent, EventRegistration, PrayerSubmission, ContactSubmission, VisitRsvp, SystemConfig). These remain `managed=False` in Django with exact `db_table` names.
- **Django owns newly introduced CMS infrastructure** (GlobalSettings, HomepageSettings, ChurchProfile, ContentBlock, HomepageSection, ServiceTime, Announcement, MediaAsset, PrayerRequest). These are `managed=True`.

This reduces migration risk and defers future full Django ownership.

### Key Architectural Pillars

| Pillar | Decision |
|--------|----------|
| Schema Ownership | Dual: Prisma for legacy, Django for new CMS |
| Content Management | ContentBlock pattern replaces per-topic models for low-frequency content |
| Configuration | Split: GlobalSettings + HomepageSettings + ChurchProfile (replaces monolithic SiteSettings) |
| Media Strategy | Centralized MediaAsset with governance fields (file_size, checksum, focal_point, is_public, usage_count) |
| Workflow | Draft → In Review → Approved → Published → Archived (5-state) |
| Search | PostgreSQL Full Text Search in B2/B3 (no Elasticsearch/OpenSearch/Meilisearch at this stage) |
| Homepage | Managed via HomepageSection + HomepagePastorSection + ContentBlock (no hardcoded content) |
| Cache | post_save/post_delete hooks with cache key invalidation documented |
| Audit | AuditLog with old_value, new_value, ip_address, user_agent fields deferred to B3 |

---

## 2. List of Revisions Made

### Revision 1: Schema Ownership Strategy
- **Added** "Schema Ownership Strategy" section to ADR-001
- **Updated** BACKEND_CONTENT_MANAGEMENT_DESIGN.md to document dual ownership
- **Confirmed** all Prisma-backed models remain `managed=False`
- **Confirmed** all new CMS models use `managed=True`

### Revision 2: Split SiteConfig (SiteSettings → GlobalSettings + HomepageSettings + ChurchProfile)
- **Documented** GlobalSettings (church_name, contact, address, social links, giving, academy)
- **Documented** HomepageSettings (hero text, scripture, tagline, CTA)
- **Documented** ChurchProfile (mission, vision, welcome, history)
- **Updated** all references in both documents

### Revision 3: Reduce Over-Modeling (ContentBlock)
- **Added** ContentType choices enum (BELIEF, VALUE, FAQ, EXPECTATION, PAGE_SECTION, THEME)
- **Enhanced** ContentBlock with content_type, display_order, is_active
- **Documented** that dedicated models may be introduced later if needed
- **Updated** inventory sections in both documents

### Revision 4: Formal Content Workflow
- **Expanded** workflow from Draft → Published to: Draft → In Review → Approved → Published → Archived
- **Documented** role permissions per state:
  - Content Editor: create/edit drafts
  - Pastor: approve
  - Administrator: publish
  - Super Admin: all transitions
- **Applied** to: Sermons, Events, Testimonials, Announcements, Beliefs, Values

### Revision 5: Expand Media Strategy
- **Added** MediaAsset fields: file_size, checksum, focal_point_x, focal_point_y, is_public, usage_count
- **Documented** purpose: duplicate detection, responsive cropping, cleanup jobs, media governance, future CDN optimization
- **Added** indexes on checksum and is_public

### Revision 6: Cache Invalidation Architecture
- **Created** "Cache Invalidation Strategy" section in ADR-001
- **Documented** cache invalidation rules:
  - Sermon changes → invalidate sermon cache
  - Event changes → invalidate event cache
  - Homepage changes → invalidate homepage cache
  - Announcement changes → invalidate active announcement cache
- **Documented** intended use of post_save hooks, post_delete hooks, and cache key invalidation

### Revision 7: Search Strategy
- **Created** "Search Architecture" section in ADR-001
- **Specified** PostgreSQL Full Text Search in B2/B3
- **Documented** components: SearchVector, SearchRank, GIN indexes
- **Documented** no Elasticsearch/OpenSearch/Meilisearch at this stage
- **Documented** reason: unnecessary operational complexity

### Revision 8: Move Homepage Pastor Content into CMS
- **Created** HomepagePastorSection (managed content) in BACKEND_CONTENT_MANAGEMENT_DESIGN.md
- **Fields**: title, subtitle, biography, image, CTA text
- **Documented** reason: pastor changes should not require deployments
- **Updated** justification tables

### Revision 9: Homepage Configuration Architecture
- **Created** HomepageSection model in backend/apps/content/models.py
- **Fields**: section_name, enabled, display_order
- **Purpose**: visibility, ordering, feature toggles without page-builder
- **Documented** as future-ready architecture

### Revision 10: Enhance Announcement Model
- **Added** severity field to Announcement model
- **Choices**: INFO, SUCCESS, WARNING, URGENT
- **Documented** intended frontend usage

### Revision 11: Expand Audit Log Requirements
- **Documented** additional audit fields: old_value, new_value, ip_address, user_agent
- **Documented** purpose: traceability, rollback analysis, security investigations
- **Deferred** implementation to B3

### Revision 12: Data Migration Strategy
- **Created** `RP/docs/DATA_MIGRATION_STRATEGY.md`
- **Documented** source files: site.json, sermons.json, series.json, events.json, testimonials.json, leadership.json, academy-modules.json
- **For each source**: Source → Destination → Transformation Rules → Validation Steps → Rollback Strategy

---

## 3. Final Recommendations

### Immediate (Pre-B2)
1. ✅ **Complete** — B2.1 Schema Hardening implemented and validated
2. ✅ **Complete** — All 12 architecture revisions documented
3. ✅ **Complete** — DATA_MIGRATION_STRATEGY.md created
4. ✅ **Complete** — B1_ARCHITECTURE_REVIEW_RESOLUTION.md created

### Before B2 Implementation
1. Review B2_1_IMPLEMENTATION_PLAN.md and B2_1_SCHEMA_HARDENING_REPORT.md
2. Ensure all team members understand dual-ownership strategy
3. Prevent accidental `makemigrations` on Prisma-backed models in future
4. Establish convention: new models default to `managed=True` unless explicit Prisma mapping required

### B2 Scope
- Admin registration for all models
- DRF serializers and viewsets
- Role-based permissions
- Workflow enforcement
- PostgreSQL Full Text Search indexes

### B3+ Scope
- AuditLog wiring
- Cache invalidation hooks
- Media upload and CDN integration
- Data migration from static JSON

---

## 4. Readiness Assessment for B2

| Criterion | Status | Notes |
|-----------|--------|-------|
| All Prisma-backed models verified `managed=False` | ✅ Complete | Verified in content, events, prayer apps |
| All new CMS models created `managed=True` | ✅ Complete | ContentBlock, HomepageSection, ServiceTime added |
| ContentBlock enhanced with content_type | ✅ Complete | Added ContentType choices enum |
| MediaAsset enhanced with governance fields | ✅ Complete | file_size, checksum, focal_point, is_public, usage_count |
| HomepageSection created | ✅ Complete | section_name, enabled, display_order |
| ServiceTime created | ✅ Complete | day, time, label, display_order |
| Announcement enhanced with severity | ✅ Complete | INFO, SUCCESS, WARNING, URGENT |
| Migrations generated without errors | ✅ Complete | 4 initial migrations (content, events, media, prayer) |
| Migrations applied without errors | ✅ Complete | All 4 applied OK |
| Django system check passes | ✅ Complete | 0 issues silenced |
| No destructive operations in migrations | ✅ Complete | Additive only |
| No Prisma table modifications | ✅ Complete | managed=False respected |
| All 12 revisions documented | ✅ Complete | See Section 2 above |
| DATA_MIGRATION_STRATEGY.md created | ✅ Complete | Source/destination/validation/rollback for all JSON files |
| B1_ARCHITECTURE_REVIEW_RESOLUTION.md created | ✅ Complete | This document |

**Overall B2 Readiness: APPROVED**

The backend schema is hardened, ownership is clear, and all architecture review requirements are satisfied. The project is cleared to proceed to B2 implementation.

---

## 5. Document Index

| Document | Path | Status |
|----------|------|--------|
| ADR-001 | `RP/docs/adr/ADR-001-CONTENT-MANAGEMENT-ARCHITECTURE.md` | Updated |
| Backend Design | `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md` | Updated |
| Data Migration Strategy | `RP/docs/DATA_MIGRATION_STRATEGY.md` | Created |
| B1 Architecture Review Resolution | `RP/docs/B1_ARCHITECTURE_REVIEW_RESOLUTION.md` | Created (this document) |
| B2.1 Implementation Plan | `RP/docs/B2_1_IMPLEMENTATION_PLAN.md` | Created |
| B2.1 Schema Hardening Report | `RP/docs/B2_1_SCHEMA_HARDENING_REPORT.md` | Created |

---

*End of B1 Architecture Review Resolution*