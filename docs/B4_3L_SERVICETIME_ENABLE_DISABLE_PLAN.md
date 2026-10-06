# B4.3L — ServiceTime Enable/Disable on Homepage (Implementation Plan)

**Status:** ✅ Implemented (2026-09-22) — Approved as **Option A**; Step 4 skipped by decision
**Date:** 2026-09-22
**Scope:** Admin-controlled visibility of individual Service Time entries

---

## 1. Requirement

The admin must be able to disable a specific service (e.g. "Cell Group Meetings") from
the homepage **Service Times** section without deleting it. A disabled service (and all
content under it — day, time, location, link, description, image) must remain intact in
the database and in the admin list; it simply must not be rendered on the public site.

---

## 2. Current State (Audit Findings)

| # | Finding | Location |
|---|---------|----------|
| 1 | `ServiceTime` model **already has** `is_published = models.BooleanField(default=True)` plus index `servicetime_published_idx` | `RP/backend/backend/apps/content/models.py:498` |
| 2 | Schema already shipped in migration `0011_servicetime_expand_fields` — **no new migration needed** | `RP/backend/backend/apps/content/migrations/0011_servicetime_expand_fields.py` |
| 3 | `ServiceTimeAdmin` **already exposes** the toggle: `list_display`, `list_filter`, `list_editable` (inline checkbox in the changelist), and the "Ordering & Visibility" fieldset | `RP/backend/backend/apps/content/admin.py:178-206` |
| 4 | `ServiceTimeSerializer` already sends `is_published` to the client | `RP/backend/backend/apps/content/serializers.py:206` |
| 5 | **THE GAP:** `ServiceTimeRepository.all_ordered()` returns `ServiceTime.objects.all()` with **no `is_published` filter**, and the homepage view uses it directly — so toggling the checkbox currently has **zero effect** on the site | `RP/backend/backend/apps/content/repositories.py:154-156`, `RP/backend/backend/apps/content/views.py:154` |
| 6 | Every other content repository follows the convention of a `published()` classmethod filtering `is_published=True` (`SermonRepository`, `SermonSeriesRepository`, `WebsiteLeaderRepository`, `WebsiteTestimonialRepository`, `WebsiteAcademyModuleRepository`) — `ServiceTimeRepository` is the only one missing it | `RP/backend/backend/apps/content/repositories.py` |
| 7 | Frontend consumers of `homepage.serviceTimes`: homepage tabs section, visit page carousel, CTA banner (`serviceTimes[0]`) | `website/src/pages/index.astro:67-68,94`, `website/src/pages/visit.astro:44-55`, `website/src/components/home/CtaBannerSection.astro:21` |
| 8 | All three consumers already guard against an empty array (`length > 0` / `firstService && …`), so an all-disabled state hides the section cleanly with no runtime errors | as above |
| 9 | Astro runs with `output: 'server'` (node adapter) — pages fetch the API per request, so the toggle takes effect on refresh, no rebuild required | `website/astro.config.mjs` |

**Conclusion:** This is not a new feature build. It is a one-line enforcement gap plus
optional polish. The admin UI work is already done.

---

## 3. Design Decision (requires confirmation)

The homepage and the **visit page** share the same `/api/homepage` endpoint. Two options:

| Option | Behavior | Recommendation |
|--------|----------|----------------|
| **A — Unpublish everywhere (recommended)** | Filter in the repository/API: a disabled service disappears from homepage, visit page, and CTA banner alike. Semantics match every other `is_published` flag in the codebase (sermons, leaders, testimonials). | ✅ Default |
| **B — Homepage only** | Send all entries and filter only in `index.astro`. Visit page keeps showing the disabled service. Requires frontend filtering + type change, and splits source-of-truth behavior. | ❌ Not recommended |


---

## 4. Implementation Steps (Option A)

### Step 1 — `RP/backend/backend/apps/content/repositories.py`

Add a `published()` classmethod to `ServiceTimeRepository`, following the existing
convention used by every other repository (keep `all_ordered()` untouched for
internal/admin use):

```python
class ServiceTimeRepository:
    """Repository for ServiceTime entries."""
    model = ServiceTime

    @classmethod
    def all_ordered(cls):
        """Get all service times ordered by display_order."""
        return ServiceTime.objects.all().order_by('display_order', 'day')

    @classmethod
    def published(cls):
        """Get published service times ordered for public display."""
        return cls.model.objects.filter(
            is_published=True
        ).order_by('display_order', 'day')
```

### Step 2 — `RP/backend/backend/apps/content/views.py` (line 154)

Switch the homepage aggregation to the published queryset:

```python
# BEFORE
service_times = ServiceTimeSerializer(ServiceTimeRepository.all_ordered(), many=True).data

# AFTER
service_times = ServiceTimeSerializer(ServiceTimeRepository.published(), many=True).data
```

### Step 3 — No frontend changes

`index.astro`, `visit.astro`, and `CtaBannerSection.astro` already:
- consume `homepage.serviceTimes` from the API (single source of truth), and
- guard against empty arrays.

Filtering server-side makes the disabled entry vanish from all of them automatically.
No TypeScript/type edits are required for the core feature.

### Step 4 (optional polish) — Admin label clarity

Rename the column header from the generic "Is published" to **"Visible on site"**
via `ServiceTimeAdmin` (a `formfield_for_dbfield` override or a display method with
`boolean=True, short_description='Visible on site'`), so admins immediately understand
the checkbox controls site visibility. Implemented purely in `admin.py` → no migration.

### Explicitly out of scope

- **No deletion** of any kind — rows, related content, or media.
- No schema change / no new migration (`makemigrations --check` must stay clean).
- No changes to `HomepageSection` (that model controls the whole section, not individual rows).
- No changes to seeding scripts (`seed_homepage_content.py` already sets `is_published=True`).

---

## 5. Edge Cases Covered

| Case | Result |
|------|--------|
| One service disabled | Its tab disappears; remaining tabs re-layout (`flex-1`); JS tab indices are data-driven, so no stale references |
| All services disabled | `serviceTimes = []` → homepage section hidden by existing `length > 0` guard; CTA banner falls back to defaults; visit carousel hidden |
| Re-enable later | Row is unchanged (`display_order`, content intact) → reappears in the same position |
| Admin list | Row always visible; filterable via existing `list_filter = (..., 'is_published')`; toggleable inline via `list_editable` |

---

## 6. Verification Plan

1. **Migration cleanliness:** `python manage.py makemigrations --check` → no pending migrations.
2. **API:** start backend → `GET /api/homepage` → count of `serviceTimes` matches published rows.
3. **Toggle flow:** uncheck "Cell Group Meetings" in admin changelist → refresh API → 4 entries, row still present in admin/DB (verify via shell: `ServiceTime.objects.count()` unchanged).
4. **Homepage:** run `npm run dev` → Service Times shows 4 tabs, no console errors.
5. **Visit page + CTA:** confirm the disabled service is absent from both (Option A).
6. **All-disabled test:** disable all 5 → homepage renders without the section, no errors → re-enable all.
7. **Regression:** `npm run check` (astro check) passes.
8. **Admin UX (if Step 4 adopted):** label reads "Visible on site", boolean icon renders correctly.

---

## 7. Approval Checklist

- [x] Proceed with Option A (unpublish everywhere) — approved 2026-09-22
- [x] Step 4 admin label polish — **skipped** (explicitly declined)
- [x] Approve implementation

---

## 8. Implementation & Validation Report (2026-09-22)

**Changes made (2 files):**
1. `RP/backend/backend/apps/content/repositories.py` — added `ServiceTimeRepository.published()` filtering `is_published=True`, ordered by `display_order`, `day`.
2. `RP/backend/backend/apps/content/views.py:154` — homepage endpoint now uses `ServiceTimeRepository.published()`.

No frontend changes. No migration. Admin untouched (Step 4 declined).

**Validation (Django env: `conda activate tf_env`):**
| Check | Result |
|-------|--------|
| `python manage.py check` | ✅ 0 issues |
| `python manage.py makemigrations --check` | ✅ `content` app clean (pre-existing drift only in `accounts`/`events`, unrelated) |
| Baseline `GET /api/homepage` | ✅ 200, 5 services (all 5 named services present) |
| Disable 1 service (in transaction) | ✅ API returned 4; disabled name absent; DB row count unchanged (5); row persisted with `is_published=False` |
| Disable ALL services (in transaction) | ✅ API returned `[]`, 200; DB rows intact |
| Rollback after both tests | ✅ DB restored to 5 published; API back to 5 |


