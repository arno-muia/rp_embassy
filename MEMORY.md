# MEMORY.md — Persistent Project Memory

---

## Project State

Current architecture:
- Astro frontend
- Django backend
- PostgreSQL database
- CMS-driven church website
- Migrated from previous rpwebsite implementation

---

## Completed Work

### B4.2.7 — ServiceTime Source of Truth Migration

**Summary:**
Homepage and visit pages now consume serviceTimes from `/api/homepage`.

---

### B4.2.8 — ServiceTime CMS Migration

**Summary:**
ServiceTime expanded with:
- name
- platform
- location
- link
- description
- image
- is_published

**Removed:**
- Real-Time Drag-and-Drop Image Upload Widget implemented across Django Admin (`RealtimeImageUploadWidget`) backed by `/api/content/upload-image/` endpoint and Pillow optimization/orientation handling.
- Media handling configured with `MEDIA_ROOT` and `MEDIA_URL` with backward compatibility for static paths (`/images/...`) and new uploads (`/media/uploads/<folder>/...`).
- Frontend components (`TestimonialsCarousel.astro`, `LeaderCard.astro`, `PastorSection.astro`, etc.) support both local static fallbacks and uploaded media images seamlessly.

- frontend fallback source-of-truth behavior
- name matching reconstruction

**Result:**
Admin → ServiceTime → API → UI

---

### B4.2.9 — SystemConfig Admin Repair

**Summary:**
User.password_hash mapped to:
- db_column="passwordHash"

Admin crash resolved.

---

### B4.3L — ServiceTime Homepage Visibility Toggle

**Summary:**
Admin can now disable an individual Service Time from the public site (homepage,
visit page, CTA banner) without deleting it. Enforced the existing `is_published`
flag: `ServiceTimeRepository.published()` added and used by `/api/homepage`.
No migration, no frontend changes. Step 4 (admin label polish) declined.
Plan/Report: `docs/B4_3L_SERVICETIME_ENABLE_DISABLE_PLAN.md`

**Django env for this project:** `source /c/ProgramData/Anaconda3/etc/profile.d/conda.sh && conda activate tf_env`

---

### B5.1 — R1: Unified Section Visibility (admin enable/disable per section)

**Summary:**
Every admin-managed section on every public page can now be disabled from the
public site without deleting anything. New `SiteSection` model (page, key,
title, enabled) + `sections_registry.SECTION_REGISTRY` (28 keys across 9 pages)
seeds toggle rows idempotently. `GET /api/sections` serves `{page: {key: bool}}`;
Astro pages gate each block with `isEnabled(...)` — fail-open (missing = enabled,
API failure never blanks the site). Per-page admin proxies put each page's
toggles inside that page's admin group (9 admins); add/delete are disabled —
only enable/disable. A FUTURE section inherits with one registry line + one
frontend wrap (no migration, no admin code). Legacy `HomepageSection` kept
dormant (model + 5 rows, D1b) and removed from the admin registry.

**Decisions:** D1b keep-dormant · D2b include What-to-Expect + CTA · D3 per-page
groups · D4a all pages.

**Verified:** 28/28 enabled baseline; per-toggle live E2E (markers vanish /
restore exactly, siblings untouched); all-homepage-off → HTTP 200 with
header/footer intact; fail-open 6/6; zero new astro-check diagnostics.
Plan/Report: `docs/B5_1_R1_SECTION_VISIBILITY_PLAN.md` (§9.1 results).

**Known (pre-existing, out of scope):** with the backend fully down, SSR pages
awaiting ungated data helpers (`getUpcomingEvents`/`getLatestSermon`/
`getTestimonials`) return 500; R1's `getSections()` is fail-open. Whole-page
resilience is a separate hardening item.

**Deferred:** B5 R2 — admin media/image uploads (draft in
`docs/B5_UNIFIED_SECTION_VISIBILITY_AND_MEDIA_UPLOAD_PLAN.md` §4, awaiting
approval).

---

### B5.2 — "Give" → "Partner" Page Group + Partner Page Sections

**Summary:**
The admin's "Give" page group is now **"Partner"** (matching the public nav) and
its Sections list grew 1 → 4: **Page Hero, Why We Give, M-Pesa Giving, Where Your
Giving Goes** — each individually disable/enable-able; nothing deleted. The rename
is **display-layer only**: the stored page key stays `'give'` and **no migration
was created** (binding constraint from the approval). Mechanism: card name in
`PAGE_SECTION_GROUPS` + `GiveSections.get_page_display()` alias + a `page_label`
readonly method in `BaseSectionsAdmin` — needed because Django's readonly cell
renders static field choices, not the instance's `get_page_display()`.

**Decisions:** D1 titles as proposed · D2 keep key `'give'` · D3 keep proxy class
`GiveSections` · D4 keep Page Hero · **no migrations**.

**Verified:** `makemigrations content --check` → "No changes detected" (zero
drift); admin card "Partner" (no "Give"); 4 rows; breadcrumb "Partner - …";
readonly Page = "Partner"; other 8 groups unchanged, all 9 changelists 200; live
E2E on `/give` (disable → targeted markers vanish — the footer till card is
outside sections; restore → byte-exact baseline); all-off → HTTP 200 with
chrome intact; 31/31 keys enabled at rest.
Plan/Report: `docs/B5_2_PARTNER_RENAME_AND_GIVE_PAGE_SECTIONS_PLAN.md` (§6.1).

**Rule established:** page-group display names may differ from stored page keys —
rename at the display layer (proxy `get_page_display` + `page_label`), never via a
migration.

---

### B5.3 — Sermons & Contact Section Gaps (+ Prayer found in audit)

**Summary:**
Closed every remaining "ungated section" gap: **Sermons 1 → 3** (Page Hero,
Browse by Series, All Sermons), **Contact 1 → 2** (Page Hero, Contact Details &
Form), **Prayer 1 → 2** (Page Hero, Prayer Form — same class of gap discovered
during this audit and included by approval). Registry 31 → **35** keys. Also
fixed admin list order: `BaseSectionsAdmin.get_ordering` now displays rows in
**registry (page) order** via a Case expression (admin-level only — no Meta
change, no migration), so newly added sections appear at their page position
instead of being appended.

**Decisions:** D1 "Contact Details & Form" · D2 registry/page order · D3 Prayer
included · D4 "Page Hero" · no migrations.

**Verified:** `makemigrations content --check` → "No changes detected"; all 9
changelists 200 with `cl.result_list` order == registry order (sermons: Page Hero
→ Browse by Series → All Sermons); `/api/sections` 35 keys; live E2E per page
(disable → exact markers vanish, siblings intact, API flags false; restore →
baseline); all-off → HTTP 200 with chrome intact; 35/35 enabled at rest; astro
check unchanged.
Plan/Report: `docs/B5_3_SERMONS_CONTACT_SECTIONS_GAP_PLAN.md` (§6.1).

---

### B5.4 — Page Groups: Per-Section Content Components (About first) — v2 implemented (`content.0018`) → **SUPERSEDED by B5.5 (2026-09-28)**

**Summary:** v1 ("Option 3": WebsiteLeader-only) was implemented, then **fully REVERTED on
user instruction** ("NO. Not that way… study how sections were added under Homepage and
Prayer…"). Revert verified: `admin.py` byte-identical to pre-v1 (0 B5.4 markers), temp script
deleted, `check`/`makemigrations --check` clean; DB/API/frontend/live server never touched.
**Correct requirement:** each page SECTION + its components individually manageable from the
admin. Study findings — **Homepage** card = per-section entries via dedicated tables
(`ServiceTime`, `WebsiteTestimonial`, `PastorProfile`), proxies over existing tables
(`HeroSectionConfig`→SystemConfig 'site', `HomepageUpcomingEvent`→ChurchEvent,
`HomepageLatestSermon`→PublicSermon; proxy migration precedent 0016) + toggle LAST;
**Prayer** = `PrayerRequest`/`PrayerSubmission` rows + toggle last. **About** live sources:
`intro` hardcoded (SystemConfig 'site'.welcomeMessage exists+typed+unused; ChurchProfile
excluded per user), `values` = 'site'.values (live, 3 items), `leadership` = `WebsiteLeader`
(live, misfiled), `theme-2026` = 'site'.theme2026 (live dict).
**Proposed About card:** AboutIntroConfig + AboutValuesConfig + WebsiteLeader +
AboutThemeConfig → `Sections` (3 proxies over 'site' with per-subkey merge-on-save forms;
only frontend change = intro reads welcomeMessage with hardcoded fallback).
**Decisions pending:** D1 mechanism (proxy recommended vs ContentBlock vs new tables) ·
D2 intro wiring (A recommended) · D3 subfield vs whole-blob form · D4 accept state-only
migration `content.0018`.
Plan/Report: `docs/B5_4_ABOUT_GROUP_COMPONENTS_PLAN.md` — **do not implement without
user approval.**

---

### B5.5 — About Sections: Dedicated Models (admin-managed components) — ✅ Implemented 2026-09-28

**Summary:**
The About page's three remaining sections are now managed exactly like Website Leaders —
one admin entry per section holding *every* rendered component, no raw JSON:
`AboutWelcome` (eyebrow, title, vision label/text, mission label/text) ·
`AboutValuesSection` + inline `AboutValue` rows (heading, subtitle + card
title/description/order/published) · `AboutTheme` (eyebrow, title, scripture, scripture
text, image + admin preview, button label/URL). `WebsiteLeader` and the `Sections` toggle
are unchanged. Migrations: `content.0019` (4 new tables; 3 JSON proxies deleted) +
`content.0020` (seed from the live `SystemConfig 'site'` content plus the previously
hardcoded labels → zero visual change; reverse only deletes the seeded rows — SystemConfig
is never modified). New `GET /api/about` serves `{intro, values{heading,subtitle,items[]},
theme}`; `about.astro` reads it with the original copy as fallback and now renders the
2026 theme poster when set. The About card = Welcome, Vision & Mission → Our Values →
Website leaders → 2026 Theme → Sections.

**Decisions (approved):** D1 dedicated models (not JSON forms) · D2 theme image included
and rendered · D3 intro author omitted · D4 value cards keep title+description ·
D5 no add/delete restrictions — the API renders the most recently updated record ·
D6 live site scope only.

**Verified:** `manage.py check` clean; `migrate` applies 0019+0020; seeded copy == live
copy; About card entries + all admin pages 200; removed proxies 404; `/api/about` 200 with
the full component set; `/api/site-config` and `/api/sections` unchanged; `astro check` /
build clean.
Plan/Report: `docs/B5_5_ABOUT_SECTION_MODELS_PLAN.md`.

---

## Known Architecture Decisions

- ServiceTime ordering controlled by `display_order`.
- Homepage API is preferred for homepage content.
- CMS-first architecture.
- Avoid SystemConfig when dedicated models already exist.

---

## Current Phase

**B4.3 — Homepage CMS Completeness Migration**

**Pending items:**
- Pastor section CMS
- Hero image CMS integration
- CTA CMS migration
- Section heading CMS migration
- Hardcoded URL migration

---

## Future Rule

Whenever a new phase completes:
- append summary to this file

---

### B5.6 — Media URL Origin Fix (Option A: resolveMediaUrl)

**Problem:** Admin uploads saved `/media/...` paths that rendered as broken
images on the Astro site. `/media/` is served by Django (:8000), but the
browser resolved the relative URL against the Astro origin (:4321 → 404),
while `/images/...` worked because it is Astro-native (`public/images/`).

**Fix:** Central `resolveMediaUrl()` helper in `website/src/lib/api.ts` —
`/media/...` → absolute `{PUBLIC_MEDIA_URL ?? PUBLIC_API_URL}/media/...`;
`/images/...`, `http(s)://`, `data:`, `blob:` pass through untouched.
Applied in all image mappers (`toSermonView`, `toSeriesView`, `toEventView`,
`toLeaderView`, `toTestimonialView`) + normalized raw payloads in
`getHomepage()` (hero `hero_background_image`, `pastorProfile.image`,
`serviceTimes[].image`), `getAbout()` (theme `image`), `getSiteConfig()`
(`heroBackgroundImage`). No DB migration, no component/CSS changes.
Verified: Kenneth M. `/media/...` renders absolute + loads 200, static
`/images/...` fallbacks unchanged, `/`, `/about`, `/sermons`, `/events` 200.

---

### B5.7 — Visit Section Models (admin-managed Visit page content)

**Pattern:** Exactly mirrors B5.5 About — dedicated models per section, grouped
under a **Visit** admin card; singleton sections rendered latest-record-wins
(`-updated_at`); child rows (ExpectStep, Faq) are FK TabularInlines with
`sort_order` + `is_published`.

**Models added** (`content` app): `VisitHero` (title, subtitle, scripture,
variant), `VisitLocation` (eyebrow, title, description, button, map embed/title),
`VisitExpectSection` + `VisitExpectStep` (icon choices: music, book-open, users,
trending-up), `VisitFaqSection` + `VisitFaq`, `VisitRsvpSection` (form copy only —
`VisitRsvp` submissions untouched), `VisitComingSunday`. Migrations `0021`
(schema) + `0022` (seed from hardcoded copy + live `SystemConfig['site']
['visitFaqs']`; reversible, never modifies SystemConfig).

**Backend:** `VisitContentRepository` + 6 read serializers + `visit_page` view +
`GET /api/visit` returning `{hero, location, expect{eyebrow,title,items[]},
faqs{title,items[]}, rsvp, comingSunday}` (null when record missing → client
fallback). Section on/off still `/api/sections` via `VisitSections` proxy — no
duplicate switches; service times still shared from `/api/homepage`.

**Frontend:** `api.ts` +`visit` endpoint, Visit content types, `getVisit()`
(text-only payload — no resolveMediaUrl needed); `visit.astro` consumes
`getVisit()` for all six sections with the original hardcoded copy as fallback;
`RsvpForm.astro` accepts optional copy props (heading, subheading, submitLabel,
successTitle, successMessage) with original defaults.

**Verified:** `manage.py check` clean; `/api/visit` 200 with all six keys
(hero=1, location=1, expect 4 steps, faqs 8 rows, rsvp=1, comingSunday=1); all 6
admins registered in Visit card; live-edit (hero title `[B57-EDIT]`) reflected on
`/visit` then reverted; `/visit` 200 with API-served copy; regression `/`,
`/about`, `/sermons`, `/events` 200. Docs: `RP/docs/B5_7_VISIT_SECTION_MODELS_PLAN.md`.

---

### B5.8 — Sermons Section Models (admin-managed Sermons page content, sections 1–5)

**Pattern:** Same as B5.7 Visit — dedicated singleton models per section,
latest-record-wins; new **Sermons** admin card entry added to
`PAGE_CONTENT_GROUPS`. Per-sermon/series *records* (`PublicSermon`,
`SermonSeries`) untouched — their admin-card move stays on the roadmap.

**Models added:** `SermonsHero` (image, image_alt, label, preacher, title,
button_label/url, register — static admin copy, D1-A: NOT auto-filled from the
latest sermon), `SermonsBrowseSection` (heading), `SermonsGridSection` (heading,
empty_text), `SermonDetailCopy` (video_note, watch_button_label, secondary
label/url — shared copy on `/sermons/[slug]`, no registry toggles),
`SermonsRelatedSection` (heading). Migrations `0023` (schema) + `0024` (seed =
the exact previously hardcoded strings; reversible).

**Backend:** `SermonsContentRepository` + 5 read serializers + `sermons_page`
view + `GET /api/sermons-page` → `{hero, browse, grid, detail, related}` (each
null when missing). Path suffix `-page` because the DRF router owns
`/api/sermons{,/slug}`. Section on/off still `SermonsSections` / `/api/sections`.

**Frontend:** `api.ts` +`sermonsPage` endpoint, content types, `getSermonsPage()`
(hero image via `resolveMediaUrl`); `sermons.astro` binds hero/browse/grid with
original copy as fallback; `sermons/[slug].astro` binds detail copy + related
heading the same way.

**Verified:** `manage.py check` clean; `/api/sermons-page` 200 with exact live
copy (all 5 keys); all 5 admins registered; `/sermons` 200 rendering API copy;
`/sermons/salvation-charles-muchemi` 200 with detail copy ("Watch on YouTube"
×2, "Kingdom Formation", "Related Sermons"); live-edit `SermonsGridSection`
`[B58-EDIT]` reflected then reverted; regression `/`, `/about`, `/visit`,
`/series`, `/events` 200. Docs: `RP/docs/B5_8_SERMONS_SECTION_MODELS_PLAN.md`.