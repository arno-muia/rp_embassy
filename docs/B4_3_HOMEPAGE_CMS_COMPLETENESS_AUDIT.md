# B4.3 — Homepage CMS Completeness Audit

**Date:** 2026-07-24  
**Phase:** Investigation Only  
**Status:** COMPLETE — GO/NO-GO assessment below

---

## 1. Executive Summary

This audit evaluates every section rendered on the homepage (`RP/website/src/pages/index.astro`) to determine whether its content is fully editable through Django Admin. Each section was traced from the Astro component -> API endpoint -> backend serializer -> model -> admin registration.

### Key Findings

| Metric | Count |
|--------|-------|
| Total homepage sections | 8 |
| Fully CMS-driven | 5 (Service Times, Events, What to Expect, Latest Sermon, Testimonials) |
| Partially CMS-driven | 2 (Hero, CTA Banner) |
| Fully hardcoded | 1 (Pastor Section) |
| Hardcoded text strings found | 18+ across components |
| Hardcoded image paths | 3 |
| Hardcoded URLs | 6 |
| Duplicate data sources | 1 (site.ts fallback config vs SystemConfig) |

No changes are implemented. This document serves as the migration blueprint.

---

## 2. Homepage Architecture Map — Complete Data Chain

### 2.1 Hero Section

| Layer | File/Endpoint | Status |
|-------|---------------|--------|
| Component | `website/src/components/home/HeroSection.astro` | Partially CMS |
| Data source | `config` prop (from `getSiteConfig()`) | |
| API endpoint | `GET /api/site-config` | |
| Backend serializer | `SystemConfigReadSerializer` (for 'site' key) | |
| Backend model | `SystemConfig` (key='site') | |
| Admin model | `SystemConfigAdmin` | SystemConfigAdmin registered |
| Admin editable | YES — edit SystemConfig with key 'site' | |
| **Fallback** | `site.ts` (lines 6-10): `scripture`, `tagline`, `description` | DUPLICATE |
| **Hardcoded** | Hero image: `images.hero` = `/images/services/kingdom-formation-1.jpg` (`images.ts` line 3) | HARDCODED |
| **Hardcoded** | CTA button: "Plan Your Visit" -> `/visit` (HeroSection.astro line 57) | HARDCODED |

### 2.2 Service Times Section

| Layer | File/Endpoint | Status |
|-------|---------------|--------|
| Component | `website/src/components/home/ServiceTimesSection.astro` | CMS-driven |
| Data source | `homepage.serviceTimes` (from `getHomepage()`) | |
| API endpoint | `GET /api/homepage` -> `serviceTimes` | |
| Backend serializer | `ServiceTimeSerializer` | |
| Backend model | `ServiceTime` | |
| Admin model | `ServiceTimeAdmin` | Registered |
| Admin editable | YES — all fields (name, day, time, platform, location, link, image) | |
| **Hardcoded** | Section heading: "Join Us" (line 21), title: "Service Times" (line 22), description (lines 23-25) | HARDCODED |

### 2.3 Events Carousel Section

| Layer | File/Endpoint | Status |
|-------|---------------|--------|
| Component | `website/src/components/home/EventsCarouselSection.astro` | CMS-driven |
| Data source | `events` prop (from `getUpcomingEvents(5)`) | |
| API endpoint | `GET /api/events` | |
| Backend serializer | `ChurchEventReadSerializer` | |
| Backend model | `ChurchEvent` | |
| Admin model | `ChurchEventAdmin` | Registered |
| Admin editable | YES — all event fields | |
| **Hardcoded** | Section label: "Mark Your Calendar" (line 26), title: "Upcoming Events" (line 27) | HARDCODED |

### 2.4 What to Expect Section

| Layer | File/Endpoint | Status |
|-------|---------------|--------|
| Component | `website/src/components/home/WhatToExpectSection.astro` | CMS-driven |
| Data source | `config.whatToExpect` (from `getSiteConfig()`) | |
| API endpoint | `GET /api/site-config` -> `whatToExpect` array | |
| Backend model | `SystemConfig` (key='site') — `whatToExpect` is a sub-field of the JSON value | |
| Admin model | `SystemConfigAdmin` | |
| Admin editable | YES — edit JSON value in SystemConfig with key 'site' | |
| **Hardcoded** | Section label: "First Visit?" (line 21), title: "What to Expect" (line 22) | HARDCODED |
| **Hardcoded** | Icon map: `iconMap` dictionary in component (lines 8-13) maps icon string to SVG | HARDCODED |

### 2.5 Latest Sermon Section

| Layer | File/Endpoint | Status |
|-------|---------------|--------|
| Component | `website/src/components/home/LatestSermonSection.astro` | CMS-driven |
| Data source | `latestSermon` (from `getLatestSermon()`) | |
| API endpoint | `GET /api/sermons` (sorted client-side for latest) | |
| Backend serializer | `PublicSermonReadSerializer` | |
| Backend model | `PublicSermon` | |
| Admin model | `PublicSermonAdmin` | Registered |
| Admin editable | YES — all sermon fields | |
| **Hardcoded** | Section label: "Latest Teaching" (line 17), title: "Latest Sermon" (line 20) | HARDCODED |
| **Hardcoded** | CTA: "Watch Now ->" (line 51), "Browse All Sermons ->" (line 57) with `/sermons` URL | HARDCODED |

### 2.6 Testimonials Section

| Layer | File/Endpoint | Status |
|-------|---------------|--------|
| Component | `website/src/components/home/TestimonialsSection.astro` -> `TestimonialsCarousel.astro` | CMS-driven |
| Data source | `testimonials` (from `getTestimonials()`) | |
| API endpoint | `GET /api/testimonials` | |
| Backend serializer | `WebsiteTestimonialReadSerializer` | |
| Backend model | `WebsiteTestimonial` | |
| Admin model | `WebsiteTestimonialAdmin` | Registered |
| Admin editable | YES — testimonial quote, name, role, photo | |

### 2.7 Pastor Section

| Layer | File/Endpoint | Status |
|-------|---------------|--------|
| Component | `website/src/components/home/PastorSection.astro` | **FULLY HARDCODED** |
| Data source | None — `config` prop is declared but never used | |
| API endpoint | N/A | |
| Backend model | N/A (No pastor/bio model exists) | |
| Admin model | N/A | |
| Admin editable | **NO** — no backend model exists for pastor bio content | |
| **Hardcoded** | Pastor name: "Charles Muchemi" (line 9) | HARDCODED |
| **Hardcoded** | Past image: `/images/team/charles-muchemi.jpg` (line 16) | HARDCODED |
| **Hardcoded** | All body text: 4 paragraphs hardcoded (lines 26-33) | HARDCODED |
| **Hardcoded** | CTA: "Learn more about RP ->" with `/about` URL (lines 38-42) | HARDCODED |

### 2.8 CTA Banner Section

| Layer | File/Endpoint | Status |
|-------|---------------|--------|
| Component | `website/src/components/home/CtaBannerSection.astro` | Partially CMS |
| Data source | `homepage.serviceTimes[0]` for day/time | |
| **Hardcoded** | Heading: "Join Us This Sunday" (line 23) | HARDCODED |
| **Hardcoded** | Title: "You're Invited" (line 26) | HARDCODED |
| **Hardcoded** | Body text: 3 sentences (lines 28-30) | HARDCODED |
| **Hardcoded** | Address: `site.address.street` + `site.address.city` from site.ts (line 35) | DUPLICATE |
| **Hardcoded** | CTA buttons: "Plan Your Visit" -> `/visit`, "Watch a Sermon" -> `/sermons` (lines 42-43) | HARDCODED |

---

## 3. CMS Coverage Matrix

| Section | CMS Driven | Partial CMS | Hardcoded | Source Model | Admin Editable |
|---------|-----------|-------------|-----------|-------------|----------------|
| Hero — Scripture | NO (fallback) | YES | — | SystemConfig (site key) | YES (JSON) |
| Hero — Tagline | NO (fallback) | YES | — | SystemConfig (site key) | YES (JSON) |
| Hero — Description | NO (fallback) | YES | — | SystemConfig (site key) | YES (JSON) |
| Hero — Image | — | — | YES | images.ts | NO |
| Hero — CTA Button | — | — | YES | Hardcoded | NO |
| Service Times | YES | — | — | ServiceTime | YES |
| Service Times — Headings | — | — | YES | Hardcoded | NO |
| Events | YES | — | — | ChurchEvent | YES |
| Events — Headings | — | — | YES | Hardcoded | NO |
| What to Expect | YES | — | — | SystemConfig JSON | YES (JSON) |
| What to Expect — Icons | — | — | YES | iconMap in component | NO |
| What to Expect — Headings | — | — | YES | Hardcoded | NO |
| Latest Sermon | YES | — | — | PublicSermon | YES |
| Latest Sermon — Headings | — | — | YES | Hardcoded | NO |
| Testimonials | YES | — | — | WebsiteTestimonial | YES |
| Pastor Section | — | — | YES | None | NO |
| CTA Banner — Text | — | — | YES | Hardcoded | NO |
| CTA Banner — Service time | YES | — | — | ServiceTime | YES |
| CTA Banner — Address | — | — | YES | site.ts | NO |
| CTA Buttons | — | — | YES | Hardcoded URLs | NO |
| Footer — All | — | — | YES | site.ts | NO |
| Navigation — All | — | — | YES | site.ts | NO |

---

## 4. Hardcoded Content Inventory

Every hardcoded value found in the homepage codebase:

| # | File | Line(s) | Content | Type |
|---|------|---------|---------|------|
| 1 | HeroSection.astro | 12 | Hero image: `images.hero` from images.ts | Image |
| 2 | HeroSection.astro | 57 | CTA: "Plan Your Visit" -> `/visit` | Button+URL |
| 3 | ServiceTimesSection.astro | 21 | "Join Us" | Label |
| 4 | ServiceTimesSection.astro | 22 | "Service Times" | Title |
| 5 | ServiceTimesSection.astro | 23-25 | Description paragraph | Text |
| 6 | EventsCarouselSection.astro | 26 | "Mark Your Calendar" | Label |
| 7 | EventsCarouselSection.astro | 27 | "Upcoming Events" | Title |
| 8 | WhatToExpectSection.astro | 21 | "First Visit?" | Label |
| 9 | WhatToExpectSection.astro | 22 | "What to Expect" | Title |
| 10 | LatestSermonSection.astro | 17 | "Latest Teaching" | Label |
| 11 | LatestSermonSection.astro | 20 | "Latest Sermon" | Title |
| 12 | LatestSermonSection.astro | 48-58 | "Watch Now ->", "Browse All Sermons ->" with `/sermons` | Button+URL |
| 13 | PastorSection.astro | 9 | "Charles Muchemi" | Pastor name |
| 14 | PastorSection.astro | 10 | "Our Pastor" | Label |
| 15 | PastorSection.astro | 16 | `/images/team/charles-muchemi.jpg` | Image |
| 16 | PastorSection.astro | 26-33 | 4 paragraphs of pastor message | Text |
| 17 | PastorSection.astro | 38-42 | "Learn more about RP ->" with `/about` | Button+URL |
| 18 | CtaBannerSection.astro | 23 | "Join Us This Sunday" | Heading |
| 19 | CtaBannerSection.astro | 26 | "You're Invited" | Title |
| 20 | CtaBannerSection.astro | 28-30 | Body text (3 sentences) | Text |
| 21 | CtaBannerSection.astro | 35 | `site.address.street, site.address.city` | Address |
| 22 | CtaBannerSection.astro | 42 | "Plan Your Visit" -> `/visit` | Button+URL |
| 23 | CtaBannerSection.astro | 43 | "Watch a Sermon" -> `/sermons` | Button+URL |
| 24 | WhatToExpectSection.astro | 8-13 | `iconMap` — maps icon strings to SVG markup | SVGs (design concern) |
| 25 | site.ts | 6-39 | Full site config fallback (name, tagline, address, etc.) | Config fallback |
| 26 | images.ts | 3-47 | All image path constants | Image paths |

---

## 5. Duplicate Source Inventory

| # | Data | Source A | Source B | Risk |
|---|------|----------|----------|------|
| 1 | Church name "Royal Priesthood Embassy" | SystemConfig (site key) `value.name` | `site.ts` line 6 | Low — fallback matches |
| 2 | Tagline "Discover Your True Identity in Christ" | SystemConfig (site key) `value.tagline` | `site.ts` line 8 | Low — fallback matches |
| 3 | Scripture "1 Peter 2:9" | SystemConfig (site key) `value.scripture` | `site.ts` line 9 | Low — fallback matches |
| 4 | Description | SystemConfig (site key) `value.description` | `site.ts` line 10-11 | Low — fallback matches |
| 5 | Address | SystemConfig (site key) `value.address` | `site.ts` lines 12-17 | Low — fallback matches |
| 6 | Theme 2026 | SystemConfig (site key) `value.theme2026` | `site.ts` lines 32-38 | Low — fallback matches |
| 7 | Service time display | ServiceTime model | CtaBannerSection uses firstService.day/time | No duplication — data flows from API |
| 8 | Hero image | Hardcoded in images.ts | Could be in SystemConfig JSON | Potential — image not CMS-managed |

---

## 6. Missing CMS Coverage

### 6.1 Pastor Section — Zero CMS Coverage

The entire Pastor Section has no backend model, no API endpoint, no serializer, and no admin registration. It is 100% hardcoded. A `PastorProfile` model needs to be created with:
- `name` (CharField)
- `role`/`title` (CharField)
- `bio` (TextField)
- `image` (URL/CharField)
- `message` (TextField, optional)
- `sort_order` (IntegerField)

### 6.2 Section Headings — No CMS

Every section has hardcoded labels, titles, and descriptions that cannot be edited in Django Admin. These could be managed via:
- `SystemConfig` as a 'homepageHeadings' key with JSON values per section
- Or a dedicated `HomepageSectionHeading` model
- Or `ContentBlock` entries with a SECTION_HEADING type

### 6.3 CTA Button URLs — Hardcoded

All CTA button destinations (Plan Your Visit -> `/visit`, Watch a Sermon -> `/sermons`, etc.) are hardcoded. These should be configurable:
- Via `SystemConfig` JSON or
- Via a dedicated `CallToAction` model

### 6.4 Hero Image — Hardcoded

The hero background image is hardcoded in `images.ts` and not editable in Django Admin. `HomepageSettings` model has a `hero_background_image` field that is intended for this purpose but it is not being used by `HeroSection.astro` (the component uses `images.hero` instead of `config.hero_background_image`).

### 6.5 Icons — SVG Code in Frontend

The `iconMap` in `WhatToExpectSection.astro` maps string keys to SVG markup. While this is a design-system decision, the icon selection for each What-to-Expect item is driven by an `icon` string field in the SystemConfig JSON. The SVGs themselves cannot be replaced without code deployment.

---

## 7. Recommended Migration Order

| Priority | Section | Effort | Impact | Current State |
|----------|---------|--------|--------|---------------|
| P0 | Pastor Section | High | New model+API+admin+component | Fully hardcoded |
| P1 | Hero image -> use HomepageSettings.hero_background_image | Low | Single component change | Not using existing CMS field |
| P2 | Section headings -> SystemConfig or ContentBlock | Medium | Headings become editable | Fully hardcoded |
| P3 | CTA content -> SystemConfig or CallToAction model | Medium | Buttons/text/URLs editable | Fully hardcoded |
| P4 | Icon map -> allow custom SVG URLs in SystemConfig | Low | Icon flexibility | Partially hardcoded |

---

## 8. Risk Assessment

| Risk Category | Level | Notes |
|---------------|-------|-------|
| Data integrity risk | NONE | Read-only audit |
| Production impact | NONE | No changes made |
| Migration complexity | LOW-MEDIUM | Pastor Section is the only new model needed |
| Regression risk | LOW | Each CMS field addition is backward-compatible |

---

## 9. GO/NO-GO Assessment

**GO** for B4.3B implementation phase.

However, the implementation should:

1. **Create a `PastorProfile` model** (or reuse `ChurchProfile.pastor_message`) with admin registration
2. **Fix HeroSection** to use `HomepageSettings.hero_background_image` instead of hardcoded `images.hero`
3. **Move section headings** into `ContentBlock` with a `SECTION_HEADING` content type or into `SystemConfig` JSON
4. **Keep icon map** as a design-system concern — it is acceptable for SVG icons to remain in code

The highest-impact, lowest-effort fix is **#2** (Hero image) followed by **#1** (Pastor Section model).

---

## Appendix: Diagnostic Commands

Source files inspected for this audit:
- `website/src/pages/index.astro` — Homepage layout showing all sections
- `website/src/lib/api.ts` — API client with all endpoints
- `website/src/lib/site.ts` — Fallback config (DUPLICATE SOURCE)
- `website/src/lib/images.ts` — Image path constants (HARDCODED)
- `website/src/components/home/*.astro` — All homepage section components
- `website/src/layouts/Layout.astro` — Main layout (includes SiteHeader + SiteFooter)
- `website/src/components/layout/SiteFooter.astro` — Footer (fully static)
- `backend/apps/content/views.py` — `homepage` endpoint (aggregation view)
- `backend/apps/content/serializers.py` — All content serializers
- `backend/apps/content/models.py` — All content models
- `backend/apps/content/admin.py` — All content admin registrations
- `backend/apps/events/models.py` — ChurchEvent model
