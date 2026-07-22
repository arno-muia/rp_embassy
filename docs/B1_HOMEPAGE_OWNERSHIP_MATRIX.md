# B1 Homepage Ownership Matrix

**Phase:** B1.5 — Final Architecture Validation
**Date:** 2026-07-20
**Status:** Approved
**Related:** `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md`

---

## Purpose

This document audits the current Astro homepage and defines ownership for every section. It eliminates ambiguity about what is managed via code vs. managed via the Django CMS, and documents the data flow for each section.

---

## Homepage Sections Audit

### Current Homepage Structure

File: `rpwebsite/RP/website/src/pages/index.astro`

Sections (in order):
1. Hero Section
2. Service Times
3. Events Carousel
4. What To Expect
5. Latest Sermon
6. Testimonials
7. Pastor Section
8. CTA Banner
9. Announcement Banner
10. Footer CTA

---

## Section Ownership Matrix

| Section | Data Source | Model | Editable | Owner | Notes |
|---------|-------------|-------|----------|-------|-------|
| Hero Section | `HomepageSettings` | `HomepageSettings` | YES | Content Editor (draft) → Pastor (approve) → Administrator (publish) | Fields: hero_title, hero_subtitle, cta_text, cta_link_url. Singleton. |
| Service Times | `ServiceTime` or `ContentBlock (PAGE_SECTION)` | `ServiceTime` or `ContentBlock` | YES | Church Administrator | Ordered by `display_order`. Optional poster image. |
| Events Carousel | `ChurchEvent` (upcoming, featured) | `ChurchEvent` (legacy, managed=False) | YES | Content Editor (draft) → Pastor (approve) → Administrator (publish) | Filtered by status=published, start_date >= today, featured first. |
| What To Expect | `ContentBlock (EXPECTATION)` | `ContentBlock` | YES | Content Editor (draft) → Pastor (approve) → Administrator (publish) | Ordered by `display_order`. Icon/text items. |
| Latest Sermon | `PublicSermon` (most recent published) | `PublicSermon` (legacy, managed=False) | YES | Media Team (create) → Pastor (approve) | Auto-selected by date desc. No manual selection. |
| Testimonials | `WebsiteTestimonial` (featured, published, not expired) | `WebsiteTestimonial` (legacy, managed=False) | YES | Content Editor (draft) → Pastor (approve) → Administrator (publish) | Filtered by is_featured, is_archived=false, expiration_date >= today. |
| Pastor Section | `ChurchProfile` (pastor_bio_*) | `ChurchProfile` | YES | Content Editor (draft) → Pastor (approve) → Administrator (publish) | Singleton. Image via pastor_image FK to MediaAsset. |
| CTA Banner | `HomepageSettings` (cta_text, cta_link_url) | `HomepageSettings` | YES | Content Editor (draft) → Pastor (approve) → Administrator (publish) | Part of singleton. |
| Announcement Banner | `Announcement` (active, display window) | `Announcement` (new, managed=True) | YES | Content Editor (draft) → Pastor/Administrator (publish) | Severity-driven styling. Auto-expires by display_until. |
| Footer CTA | `GlobalSettings` or `HomepageSettings` | `GlobalSettings` / `HomepageSettings` | YES | Church Administrator (GlobalSettings) / Content Editor (HomepageSettings) | Typically static; can be managed. |

---

## Section Ordering

### Static Ordering (Hardcoded)
- None. Order is defined by the `index.astro` template.

### Admin-Controlled Ordering (Managed)
- **Service Times**: `ServiceTime.display_order` or `ContentBlock.display_order`.
- **What To Expect**: `ContentBlock.display_order`.
- **Events Carousel**: Server-side ordering by `start_date_time` (upcoming first, then featured).
- **Testimonials**: Server-side ordering by `is_featured` desc, then `publish_date` desc.
- **Latest Sermon**: Server-side ordering by `date` desc (always latest).

### Future Admin-Controlled Ordering
- **HomepageSection** model (future B3+):
  - `section_name` (hero, events, testimonials, etc.)
  - `enabled` (visibility toggle)
  - `display_order` (section ordering)
  - Allows admin to reorder homepage sections without frontend deploy.

---

## Data Flow per Section

### 1. Hero Section
- **Frontend calls:** `GET /api/site-config` → `homepage_settings`
- **Cache:** 5 min
- **Invalidation:** On HomepageSettings save/delete
- **Fallback:** `src/lib/site.ts` hero values

### 2. Service Times
- **Frontend calls:** `GET /api/site-config` → `service_times`
- **Cache:** 5 min
- **Invalidation:** On ServiceTime save/delete
- **Fallback:** Hardcoded in `ServiceTimesCarousel.astro` or `site.ts`

### 3. Events Carousel
- **Frontend calls:** `GET /api/events?status=published&featured=true&start_after=today&page_size=3`
- **Cache:** 5 min
- **Invalidation:** On ChurchEvent save/delete
- **Fallback:** None (empty state shown)

### 4. What To Expect
- **Frontend calls:** `GET /api/site-config` → `content_blocks[category=EXPECTATION]`
- **Cache:** 5 min
- **Invalidation:** On ContentBlock save/delete with category EXPECTATION
- **Fallback:** Hardcoded in `WhatToExpectSection.astro`

### 5. Latest Sermon
- **Frontend calls:** `GET /api/sermons?page_size=1&sort=-date`
- **Cache:** 5 min
- **Invalidation:** On PublicSermon save/delete
- **Fallback:** None (empty state)

### 6. Testimonials
- **Frontend calls:** `GET /api/testimonials?featured=true`
- **Cache:** 5 min
- **Invalidation:** On WebsiteTestimonial save/delete
- **Fallback:** Hardcoded in `TestimonialsCarousel.astro`

### 7. Pastor Section
- **Frontend calls:** `GET /api/site-config` → `church_profile`
- **Cache:** 5 min
- **Invalidation:** On ChurchProfile save/delete
- **Fallback:** Hardcoded in `PastorSection.astro` (current) → remove after B7 cutover

### 8. CTA Banner
- **Frontend calls:** `GET /api/site-config` → `homepage_settings.cta_*`
- **Cache:** 5 min
- **Invalidation:** On HomepageSettings save/delete
- **Fallback:** Hardcoded in `CtaBannerSection.astro`

### 9. Announcement Banner
- **Frontend calls:** `GET /api/announcements/active`
- **Cache:** 1 min
- **Invalidation:** On Announcement save/delete
- **Fallback:** None (hidden if no active announcements)

### 10. Footer CTA
- **Frontend calls:** `GET /api/site-config` → `global_settings` or `homepage_settings`
- **Cache:** 5 min
- **Invalidation:** On settings save
- **Fallback:** Hardcoded in `SiteFooter.astro`

---

## Content Ownership by Homepage Section

| Section | Who Can Edit? | Who Can Publish? | Approval Required? |
|---------|---------------|------------------|-------------------|
| Hero | Content Editor | Administrator | Yes (Pastor approves) |
| Service Times | Church Administrator | N/A (always live) | No |
| Events Carousel | Content Editor | Administrator | Yes (Pastor approves events) |
| What To Expect | Content Editor | Administrator | Yes (Pastor approves) |
| Latest Sermon | Media Team | N/A (auto-published on publish) | Yes (Pastor approves sermon) |
| Testimonials | Content Editor | Administrator | Yes (Pastor approves) |
| Pastor Section | Content Editor | Administrator | Yes (Pastor approves) |
| CTA Banner | Content Editor | Administrator | Yes (Pastor approves) |
| Announcement Banner | Content Editor | Administrator | No (Pastor optional for operational) |
| Footer CTA | Church Administrator / Content Editor | N/A (always live) | No |

---

## Caching Strategy Summary

| Section | Cache Key Pattern | TTL | Invalidation Trigger |
|---------|-------------------|-----|---------------------|
| Hero | `homepage_settings` | 5 min | HomepageSettings save |
| Service Times | `service_times` | 5 min | ServiceTime save/delete |
| Events | `events:{filter_hash}` | 5 min | ChurchEvent save/delete |
| What To Expect | `content_blocks:EXPECTATION` | 5 min | ContentBlock save/delete (category=EXPECTATION) |
| Latest Sermon | `sermons:latest` | 5 min | PublicSermon save/delete |
| Testimonials | `testimonials:featured` | 5 min | WebsiteTestimonial save/delete |
| Pastor Section | `church_profile` | 5 min | ChurchProfile save/delete |
| Announcements | `announcements:active` | 1 min | Announcement save/delete |
| Global Settings | `global_settings` | 5 min | GlobalSettings save/delete |

---

## Frontend Contract

### Current (Static)
- `src/lib/site.ts` contains hardcoded fallbacks for hero, service times, pastor bio, CTA.
- `PastorSection.astro` hardcodes pastor bio text.
- `ServiceTimesCarousel.astro` hardcodes service times.
- `WhatToExpectSection.astro` hardcodes what-to-expect items.
- `TestimonialsCarousel.astro` hardcodes testimonials.
- `CtaBannerSection.astro` hardcodes CTA text.

### Target (Managed)
- All sections consume from `/api/site-config` or dedicated endpoints.
- `site.ts` becomes pure fallback only.
- No hardcoded content in `.astro` files (except structural/layout).
- Announcement banner is new; no current Astro component.

---

## Migration Notes

- **Phase B7**: After cutover, remove hardcoded content from Astro components.
- **Feature flag**: `USE_MANAGED_CONTENT=true` enables managed endpoints; `false` uses hardcoded fallbacks.
- **Validation**: B7 must verify frontend renders identically with managed data before removing fallbacks.

---

## Open Questions

1. Should Service Times be a dedicated `ServiceTime` model or `ContentBlock` with category `PAGE_SECTION`?
   - Recommendation: Dedicated `ServiceTime` for clearer ordering and optional poster image.
2. Should the Announcement banner be a separate Astro component or integrated into existing hero?
   - Recommendation: Separate component; severity-driven styling.
3. Should homepage section ordering be static (code) or admin-controlled in B2?
   - Recommendation: Static in B2; `HomepageSection` model in B3+.