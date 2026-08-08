# B4.3I — Homepage CMS Architecture Implementation Report

**Date:** 2026-07-26  
**Status:** Complete  
**Phase:** B4.3I (Pre-Jazzmin Homepage Architecture)

---

## 1. Homepage Source Of Truth Matrix

| Section | Backend Model | Admin Registration | API Endpoint | Serializer | Frontend Component | Source Of Truth | Status |
|---------|--------------|-------------------|-------------|------------|-------------------|----------------|--------|
| Hero | `HomepageSettings` | ✅ `HomepageSettingsAdmin` | `/api/homepage` | `HomepageSettingsSerializer` | `HeroSection.astro` | `HomepageSettings` (single row) | ✅ Clean |
| Church Profile | `ChurchProfile` | ✅ `ChurchProfileAdmin` | `/api/homepage` | `ChurchProfileSerializer` | `WelcomeSection.astro` | `ChurchProfile` (single row) | ✅ Clean |
| Service Times | `ServiceTime` | ✅ `ServiceTimeAdmin` | `/api/homepage` | `ServiceTimeSerializer` | `ServiceTimesSection.astro` | `ServiceTime` (multiple rows) | ✅ Clean |
| Events | `Event` (events app) | ✅ `EventAdmin` (events app) | `/api/events` | `EventSerializer` | `EventsSection.astro` | `Event` (events app) | ✅ Clean |
| Teaching Events | `Event` (events app) | ✅ `EventAdmin` (events app) | `/api/events` | `EventSerializer` | `TeachingEventsSection.astro` | `Event` (events app) | ✅ Clean |
| Sermons | `PublicSermon` | ✅ `PublicSermonAdmin` | `/api/sermons` | `PublicSermonSerializer` | `SermonSection.astro` | `PublicSermon` | ✅ Clean |
| Testimonials | `WebsiteTestimonial` | ✅ `WebsiteTestimonialAdmin` | `/api/testimonials` | `WebsiteTestimonialSerializer` | `TestimonialsSection.astro` | `WebsiteTestimonial` | ✅ Clean |
| Pastor Section | `PastorProfile` | ✅ `PastorProfileAdmin` | `/api/homepage` | `PastorProfileSerializer` | `PastorSection.astro` | `PastorProfile` (single active) | ✅ Clean |
| CTA Banner | `HomepageSettings` | ✅ `HomepageSettingsAdmin` | `/api/homepage` | `HomepageSettingsSerializer` | `CtaBannerSection.astro` | `HomepageSettings` (single row) | ✅ Clean |
| What To Expect | `ContentBlock` (type=EXPECTATION) | ✅ `ContentBlockAdmin` | `/api/homepage` | `ContentBlockSerializer` | `WhatToExpectSection.astro` | `ContentBlock` (filtered) | ✅ Clean |
| Homepage Settings | `HomepageSettings` | ✅ `HomepageSettingsAdmin` | `/api/homepage` | `HomepageSettingsSerializer` | `index.astro` | `HomepageSettings` (single row) | ✅ Clean |

### Duplicate Sources Assessment

| Section | Duplicate Sources Found | Action Taken |
|---------|----------------------|-------------|
| Hero | None — single source `HomepageSettings` | No action needed |
| Service Times | Previously had `SystemConfig` fallback — already removed in B4.2.8 | Already resolved |
| CTA Banner | None — single source `HomepageSettings` | No action needed |
| All Others | None — single authoritative model per section | No action needed |

**Conclusion:** No duplicate sources remain. Every homepage section has exactly one source of truth.

---

## 2. Duplicate Sources Removed

No duplicate sources were found that required removal. All previous duplicate/fallback paths were eliminated in prior phases (B4.2.8 ServiceTime CMS migration, B4.2.9B SystemConfig admin fix).

---

## 3. Hero Improvements

### Fields Added
- `hero_secondary_cta_text` — Secondary CTA button text (CMS editable)
- `hero_secondary_cta_url` — Secondary CTA button URL (CMS editable)

### Hero Section Completeness Checklist

| Field | CMS Editable | API Exposed | Frontend Consumed | Status |
|-------|-------------|-------------|-------------------|--------|
| Hero title | ✅ | ✅ | ✅ | Complete |
| Hero scripture | ✅ | ✅ | ✅ | Complete |
| Hero description | ✅ | ✅ | ✅ | Complete |
| Hero image | ✅ | ✅ | ✅ | Complete |
| Primary CTA label | ✅ | ✅ | ✅ | Complete |
| Primary CTA URL | ✅ | ✅ | ✅ | Complete |
| Secondary CTA label | ✅ | ✅ | ✅ | Complete |
| Secondary CTA URL | ✅ | ✅ | ✅ | Complete |

**No hardcoded values remain.** All hero fields are CMS editable through `HomepageSettings`.

---

## 4. Admin Improvements

### Changes Applied

1. **HomepageSettingsAdmin fieldsets** — Added `description` to Hero Section and CTA Banner fieldsets for clarity
2. **Verbose names** — All homepage-related models already have `verbose_name` and `verbose_name_plural` set
3. **Help text** — All `HomepageSettings` fields have descriptive `help_text` for admin users
4. **Ordering** — All admin classes have sensible `ordering` defined
5. **Section grouping** — `HomepageContentAdmin` custom admin site exists for future dedicated dashboard

### Admin Readability

Homepage-related content is now immediately recognizable in the admin:
- **Homepage Settings** — Hero content, CTA banner, all CMS fields
- **Service Times** — Grouped with fieldsets for service details, location, content, ordering
- **Pastor Profiles** — Grouped with fieldsets for profile, CTA, ordering, status
- **Homepage Sections** — Visibility and ordering control

---

## 5. Files Modified

| File | Change |
|------|--------|
| `backend/backend/apps/content/models.py` | Added `hero_secondary_cta_text` and `hero_secondary_cta_url` fields with help_text |
| `backend/backend/apps/content/admin.py` | Added fieldset descriptions to HomepageSettingsAdmin |
| `backend/backend/apps/content/serializers.py` | Added `hero_secondary_cta_text` and `hero_secondary_cta_url` to serializer |
| `backend/backend/apps/content/migrations/0015_homepagesettings_hero_secondary_cta_text_and_more.py` | New migration for secondary CTA fields |
| `website/src/components/home/HeroSection.astro` | Already consuming secondary CTA fields (no change needed) |

---

## 6. Validation Results

### Django System Check
```
$ python manage.py check
System check identified no issues (0 silenced).
```

### Django System Check (Deploy)
```
$ python manage.py check --deploy
System check identified 7 issues (0 silenced).
```
All 7 warnings are standard deployment security warnings (HSTS, SSL, SECRET_KEY, etc.) — none related to homepage architecture.

### Migration Status
```
Applying content.0015_homepagesettings_hero_secondary_cta_text_and_more... OK
```

---

## 7. Remaining Work Before Jazzmin

| Item | Status | Notes |
|------|--------|-------|
| Homepage content has clearly defined source of truth | ✅ Complete | Matrix verified — one source per section |
| Duplicate homepage content paths removed or documented | ✅ Complete | No duplicates found |
| Hero section is fully CMS editable | ✅ Complete | All 8 hero fields editable via admin |
| Homepage-related admin content is easier to manage | ✅ Complete | Fieldsets, descriptions, help_text, ordering |
| Validation passes | ✅ Complete | `manage.py check` passes with 0 errors |
| Report created | ✅ Complete | This document |

### Items NOT in Scope (Future Phases)
- Jazzmin admin theme integration (B4.3J)
- B4.3B phase items
- Custom admin dashboard widgets
- Admin search/index improvements
- Permission/role configuration

---

## Summary

Phase B4.3I is **complete**. The homepage CMS architecture now has:

1. **One source of truth per section** — verified across all 11 homepage sections
2. **No duplicate content paths** — all previous fallbacks eliminated
3. **Fully CMS-editable Hero section** — all 8 fields editable, exposed via API, consumed by frontend
4. **Improved admin experience** — fieldsets with descriptions, help_text, proper ordering
5. **Clean validation** — zero errors, zero homepage-related warnings

Ready for Jazzmin integration (B4.3J) when scheduled.