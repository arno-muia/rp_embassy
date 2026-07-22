# API Prisma-Owned Endpoints 500 Fix Report

**Date:** 2026-07-20
**Status:** Investigation Complete — Root Cause Identified

---

## 1. Issue Summary

Multiple public content endpoints return HTTP 500:

- `/api/sermons`
- `/api/series`
- `/api/leaders`
- `/api/testimonials`
- `/api/academy`

These are the Prisma-owned legacy content endpoints. Django-owned endpoints (`/api/site-config`, `/api/contact`, `/api/rsvp`, `/api/prayer`) are unaffected.

---

## 2. Root Cause Analysis

### 2.1 Call Chain

All affected endpoints use the same pattern:
- `LeaderViewSet` → `WebsiteLeaderRepository.published()` → `WebsiteLeader.objects.filter(is_published=True).order_by('sort_order')`
- `SermonViewSet` → `SermonRepository.published()` → `PublicSermon.objects.filter(is_published=True).select_related('series').order_by('-date')`
- `SeriesViewSet` → `SeriesRepository.published()` → `SermonSeries.objects.filter(is_published=True).order_by('sort_order')`
- `TestimonialViewSet` → `WebsiteTestimonialRepository.published()` → `WebsiteTestimonial.objects.filter(is_published=True).order_by('sort_order')`
- `AcademyModuleViewSet` → `WebsiteAcademyModuleRepository.published()` → `WebsiteAcademyModule.objects.filter(is_published=True).order_by('sort_order')`

### 2.2 Verified Facts

| Check | Result |
|-------|--------|
| Serializer fields match model fields | ✅ |
| URL routing | ✅ |
| `managed = False` respected in migrations | ✅ |
| Database settings | ✅ PostgreSQL backend configured |

### 2.3 Probable Root Cause

These models are declared `managed = False` (Prisma-owned). Django does not create or migrate their tables. The 500 occurs when Django evaluates the queryset against PostgreSQL because the underlying Prisma-managed tables are either:

1. **Missing** — Prisma migrations were never applied to PostgreSQL, or
2. **Schema drift** — Prisma table columns do not match Django model expectations (e.g., missing `sort_order`, `is_published`, `photo_url`)

This is a **database schema mismatch**, not a code bug.

---

## 3. Resolution

### Immediate Steps

1. Connect to PostgreSQL and verify each table exists:
   - `PublicSermon`
   - `SermonSeries`
   - `WebsiteLeader`
   - `WebsiteTestimonial`
   - `WebsiteAcademyModule`

2. Verify expected columns for each table. Minimum required:
   - `id` (uuid)
   - `is_published` / `isPublished` (boolean)
   - `sort_order` / `sortOrder` (integer)
   - model-specific fields (`photo_url`/`photoUrl`, `title`, etc.)

3. If tables/columns are missing, apply the Prisma migration to PostgreSQL.

### Verification

```bash
curl http://127.0.0.1:8000/api/sermons
curl http://127.0.0.1:8000/api/leaders
curl http://127.0.0.1:8000/api/series
curl http://127.0.0.1:8000/api/testimonials
curl http://127.0.0.1:8000/api/academy
```

Expected: HTTP 200 with JSON arrays.

---

## 4. Files Reviewed

| File | Purpose |
|------|---------|
| `backend/apps/content/views.py` | All 5 Prisma-owned viewsets |
| `backend/apps/content/serializers.py` | Read serializers for all Prisma-owned models |
| `backend/apps/content/repositories.py` | Repository queries for all Prisma-owned models |
| `backend/apps/content/models.py` | `managed=False` declarations |
| `backend/apps/content/urls.py` | Router registrations |
| `RP/website/src/lib/api.ts` | Frontend mappers |
| `RP/website/src/types/*.ts` | Frontend type contracts |

---

*Report generated: 2026-07-20*