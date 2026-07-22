# B1 Implementation Risk Assessment

**Phase:** B1.5 — Final Architecture Validation
**Date:** 2026-07-20
**Status:** Approved
**Related:** `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md`

---

## Purpose

This document identifies implementation risks before B2 begins. It ensures the team understands what could go wrong, how to mitigate it, and where to focus attention.

---

## Risk Summary

| Risk Level | Count |
|------------|-------|
| HIGH | 3 |
| MEDIUM | 5 |
| LOW | 4 |

---

## High Risks

### H1 — Prisma Schema Extension Coordination

**Description:** B2 requires adding fields to Prisma-owned tables (`is_featured`, `category`, `status`, `thumbnail` FK, etc.). If Django teams and Prisma teams are not synchronized, Django models will reference columns that do not exist.

**Impact:** Migration failures; broken reads; deployment blocked.

**Mitigation:**
- Create a Prisma extension checklist (see Ownership Matrix).
- Require Prisma migration to be run before Django migration.
- Add integration tests that verify Django can read all expected columns.
- Block Django B2 deployment if Prisma migration pending.

---

### H2 — Frontend Contract Break During Cutover

**Description:** Switching from static JSON to managed API may introduce subtle differences (field names, data shapes, nullability) that break the Astro frontend.

**Impact:** Broken homepage, sermons, events pages in production.

**Mitigation:**
- Feature flag `USE_MANAGED_CONTENT` enables instant rollback.
- B7 validation script compares static JSON output vs API output field-by-field.
- Canary traffic (10% → 50% → 100%) before full cutover.
- Keep static JSON fallback for 7 days post-cutover.

---

### H3 — Media Backfill Data Loss

**Description:** Moving static images to `MediaAsset` and updating references risks broken image links if any step fails.

**Impact:** Missing images across site; broken user experience.

**Mitigation:**
- Idempotent backfill script; re-runnable without duplicates.
- Validation: every source image path must map to a `MediaAsset`.
- Rollback: Prisma URL fields can revert to old paths; Django `MediaAsset` rows can be deleted.
- Parallel run: both old paths and new URLs valid during transition.

---

## Medium Risks

### M1 — Cache Invalidation Missed Edge Cases

**Description:** Complex content relationships (e.g., sermon → series → featured flag) may cause stale caches if invalidation hooks miss indirect dependencies.

**Impact:** Users see outdated content; confusion between draft and published.

**Mitigation:**
- Document explicit invalidation table (see API Contract).
- Use short TTLs (5 min) as safety net.
- Add post_save/post_delete signals for all content models.
- Manual cache clear endpoint for emergency invalidation.

---

### M2 — Workflow State Machine Gaps

**Description:** Implementing Draft → In Review → Approved → Published → Archived requires careful state transition logic. Edge cases (reject, force-publish, concurrent edits) may be missed.

**Impact:** Content stuck in wrong state; unauthorized publishes.

**Mitigation:**
- State machine library or explicit transition matrix in code.
- AuditLog every transition with old/new state.
- Super Admin override clearly documented.
- Unit tests for every transition path.

---

### M3 — Permission Overlap and Conflict

**Description:** Users may hold multiple roles (e.g., Content Editor + Pastor). Permission resolution must be deterministic.

**Impact:** unauthorized edits or blocked legitimate actions.

**Mitigation:**
- Highest-role-wins rule documented in Permission Matrix.
- Object-level permission checks in DRF.
- Admin UI reflects effective permissions.

---

### M4 — Search Relevance Quality

**Description:** PostgreSQL FTS may return irrelevant results for short queries or proper names.

**Impact:** Poor search experience; users cannot find content.

**Mitigation:**
- Tune FTS configuration (english config, weights).
- Add search result validation in B5.
- Consider prefix matching for partial words.
- Fallback: no search = empty state message (acceptable for B2).

---

### M5 — AuditLog Table Growth

**Description:** Every mutating action writes to AuditLog. Without partitioning, the table grows unbounded and queries slow.

**Impact:** Admin audit page becomes slow; database bloat.

**Mitigation:**
- Partition by year (PostgreSQL range partition).
- Archive old partitions to cold storage after 1 year.
- Index on `performed_at`, `model_name`, `action`.

---

## Low Risks

### L1 — Singleton Race Conditions

**Description:** Concurrent requests to create `GlobalSettings` could create duplicates if not locked.

**Impact:** Multiple singletons; API returns wrong data.

**Mitigation:**
- Use `get_or_create()` with unique constraint.
- Database-level unique constraint on singleton key (e.g., `type='global'`).
- Django admin enforced single instance via `ModelAdmin`.

---

### L2 — ContentBlock Category Explosion

**Description:** Teams may request many categories, leading to an unmaintained category enum.

**Impact:** Admin confusion; inconsistent categorization.

**Mitigation:**
- Document allowed categories in Permission Matrix.
- Admin dropdown with explicit choices; no free-text category.
- New categories require architecture review (this doc).

---

### L3 — Migration Script Idempotency

**Description:** If B7 migration script is run twice, it may create duplicate records.

**Impact:** Duplicate content; data cleanup required.

**Mitigation:**
- Use `get_or_create()` with unique keys.
- Validation counts before and after.
- Idempotent design: running twice produces same result.

---

### L4 — Frontend Fallback Drift

**Description:** Hardcoded fallbacks in `site.ts` may diverge from managed content during transition.

**Impact:** Inconsistent UX depending on feature flag.

**Mitigation:**
- B7 validation ensures both paths return identical data.
- After cutover, remove fallbacks entirely (planned).
- Feature flag planned for removal after 30 days.

---

## Risk by Phase

| Phase | High | Medium | Low |
|-------|------|--------|-----|
| B2 (Models) | H1 | M2, M3 | L1, L2, L3 |
| B3 (Admin) | — | M2, M3, M5 | L1, L2 |
| B4 (Media) | H3 | M1 | L3, L4 |
| B5 (API/Cache) | H2 | M1, M4 | L4 |
| B6 (Frontend) | H2 | M4 | L4 |
| B7 (Migration) | H2, H3 | M1, M3 | L3, L4 |
| B8 (Governance) | — | M5 | — |

---

## Top Mitigation Priorities

1. **Lock Prisma migration schedule** — coordinate with B2 kickoff.
2. **Build feature flag infrastructure** before any frontend integration.
3. **Validate backfill idempotency** in staging before production.
4. **Write state machine unit tests** before implementing workflow.
5. **Plan AuditLog partitioning** early (B3 schema).

---

## Decision Reminders

- Do not change storage architecture after B4 (see `B1_STORAGE_ARCHITECTURE.md`).
- Do not introduce Elasticsearch/OpenSearch unless PostgreSQL FTS proves insufficient.
- Do not convert legacy tables to `managed=True` without explicit decision post-B7.