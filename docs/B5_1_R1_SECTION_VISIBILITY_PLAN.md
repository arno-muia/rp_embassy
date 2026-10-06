# B5_1 — R1: Unified Section Visibility (Revised Plan)

**Status:** ✅ Implemented & verified (2026-09-23) — decisions D1b, D2b, D3 per-page groups, D4a all pages
**Date:** 2026-09-23
**Scope:** R1 only (admin enable/disable of every admin-managed section on every page). **R2 (media uploads) deferred** — its draft stays in `B5_UNIFIED_SECTION_VISIBILITY_AND_MEDIA_UPLOAD_PLAN.md` §4 for separate approval later.
**Supersedes:** the R1 design in `B5_UNIFIED_SECTION_VISIBILITY_AND_MEDIA_UPLOAD_PLAN.md` §3 — **discarded per the correction in §2 below.**

---

## 1. Requirement (R1)

Every section in the admin panel, from every page, can be disabled from display on the website **without deleting anything** — content, ordering, and functionality remain intact and return on re-enable. Sections added to the admin in the future inherit the same mechanism automatically.

---

## 2. Correction applied — `HomepageSection` discarded

**Correction (2026-09-23):** the seeded rows of `HomepageSection` (`welcome`, `mission`, `vision`, `kingdom-culture`, `cell-groups`) do **not** match the actual sections of the current homepage, which are exactly:

1. Hero Section
2. Service Times
3. Upcoming Events
4. Latest Sermon
5. Website Testimonials
6. Pastor Profile

These are precisely the six models grouped under **Homepage** in the admin index (`HomepageGroupedAdminSite.HOMEPAGE_GROUP` = HeroSectionConfig, ServiceTime, HomepageUpcomingEvent, HomepageLatestSermon, WebsiteTestimonial, PastorProfile).

**Consequences carried into this design:**
- Nothing is built on `HomepageSection`; no legacy row is mapped, preserved, or "reserved".
- The old model, its 5 rows, its admin entry, and its dead `homepage.sections` API payload are disposed of per **D1**.

---

## 3. Design-relevant audit facts

| # | Fact | Why it matters |
|---|------|----------------|
| 1 | `HomepageSection` rows match nothing rendered; no frontend consumer; its `sections` payload in `/api/homepage` is read by nobody (grep-verified) | Safe to discard — no dependency |
| 2 | The 6 admin Homepage-group models map 1:1 to 6 sections rendered in `index.astro` | Registry keys named after them |
| 3 | `index.astro` also renders **What-to-Expect** and **CTA Banner** — not in your list, not separate admin models | Decision **D2** (default: exclude, matching your list) |
| 4 | Homepage payloads arrive from 5 endpoints (`/api/homepage`, `/api/site-config`, `/api/events`, `/api/sermons`, `/api/testimonials`) | Flags delivered via new `/api/sections`; enforcement at SSR render time (§4.6) |
| 5 | Row-level `is_published` already enforced server-side (B4.3L); `ChurchEvent.status` / `ContentBlock.is_active` unchanged | Section toggles are an independent second gate |
| 6 | All involved models `managed=True` | New table = one `CreateModel` migration, nothing else |

---

## 4. Design

### 4.1 New model `SiteSection` (fresh table, zero legacy)

```python
PAGE_CHOICES = [('homepage', 'Home'), ('about', 'About'), ('events', 'Events'),
                ('visit', 'Visit'), ('sermons', 'Sermons'), ('series', 'Series'),
                ('give', 'Give'), ('prayer', 'Prayer'), ('contact', 'Contact')]

class SiteSection(models.Model):
    """Admin visibility toggle for one rendered section on one page."""
    page       = models.CharField(max_length=32, choices=PAGE_CHOICES, default='homepage')
    key        = models.SlugField(max_length=64)      # 'hero', 'service-times', ...
    title      = models.CharField(max_length=128)      # 'Hero Section' — admin label
    enabled    = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('page', 'key'),)
        ordering = ('page', 'id')      # registry seed order = admin list order
        verbose_name = 'Page Section'
        verbose_name_plural = 'Page Sections'
```

- **No `display_order` — deliberate:** this model controls *visibility only*; page layout order is code-owned. Avoids the false affordance of an "order" field that would not reorder the site.
- New empty table → one `CreateModel` migration; **no data migration of any kind**.

### 4.2 Registry — the inheritance mechanism

New `content/sections_registry.py` holding flat tuples `(page, key, title)`:

```python
def ensure_registered():
    """Idempotent: creates missing rows (enabled=True); never deletes, never resets toggles."""
    for page, key, title in SECTION_REGISTRY:
        SiteSection.objects.get_or_create(page=page, key=key, defaults={'title': title})
```

Called from the sections API view and the SiteSection admin changelist.

**Inheritance recipe (for any future section):** add **one registry tuple + one `isEnabled(page, key)` wrap** in the page → its toggle row auto-appears in the admin, enabled by default. No migration, no model change, no admin code. Recipe documented here and in `MEMORY.md`.

### 4.3 API — `GET /api/sections`

```json
{ "homepage": {"hero": true, "service-times": true, "testimonials": false, ...},
  "about": {"leadership": true, ...} }
```

Built after `ensure_registered()`. A missing/unknown key reads as **enabled** (fail-open: an unregistered section renders exactly as today). Under D1a this replaces the dead `homepage.sections` payload.

### 4.4 Frontend — helper + gates

New `website/src/lib/sections.ts`:

```ts
export async function getSections(): Promise<SectionFlags>;   // {} on failure → all enabled
export function isEnabled(flags, page, key): boolean;         // default true
```

One fetch per page in frontmatter (index/about/visit add a slot to their existing `Promise.all`; events/sermons/series/give/prayer/contact add one call), then each section is gated per §5:

```astro
{isEnabled(sec, 'homepage', 'testimonials') && <TestimonialsSection ... />}
```

Astro runs `output: 'server'` → disabled sections are absent from served HTML (no SEO leakage); toggles apply on the next request.

### 4.5 Admin UX

- `SiteSectionAdmin`: `list_display = ('page', 'title', 'key', 'enabled', 'updated_at')`, `list_filter = ('page', 'enabled')`, `list_editable = ('enabled',)`, `search_fields = ('title', 'key')`, `ordering = ('page', 'id')`.
- Placement per **D3** — recommended: synthetic top-level **"Sections"** group pinned first in the custom AdminSite (contains only this model); alternative: inside the existing Homepage group.
- **Double-gate semantics:** an item renders only if it is row-published (or `status=PUBLISHED`) **and** its section is enabled. Row flags untouched.

### 4.6 Enforcement split (architecture decision)

Row flags = *content truth* → enforced server-side (B4.3L). Section flags = *layout truth* → **render-time gating**, because one endpoint's payload serves multiple pages (`/api/events` feeds both the homepage carousel and the events grid) — the API cannot know the caller's page. Same visible result as server-side omission without page-context parameters on five endpoints.

---

## 5. Section inventory v2 (registry seed + gate points)

**Homepage — exactly the six you named:**

| Key | Title (admin label) | Gate in `index.astro` | Admin source (row-level flag) |
|---|---|---|---|
| `hero` | Hero Section | `<HeroSection>` | HeroSectionConfig / HomepageSettings |
| `service-times` | Service Times | `<ServiceTimesSection>` | ServiceTime (`is_published`) |
| `upcoming-events` | Upcoming Events | `<EventsCarouselSection>` | HomepageUpcomingEvent (`status=PUBLISHED`) |
| `latest-sermon` | Latest Sermon | `<LatestSermonSection>` | HomepageLatestSermon (`is_published`) |
| `testimonials` | Website Testimonials | `<TestimonialsSection>` | WebsiteTestimonial (`is_published`) |
| `pastor-profile` | Pastor Profile | `<PastorSection>` | PastorProfile |

(What-to-Expect and CTA Banner are handled per **D2**.)

**Other pages — same mechanism:**

| Page | Keys | Gate targets |
|---|---|---|
| about | `intro`, `values`, `leadership`, `theme-2026` | welcome/vision/mission quotes block (**one** new gate — its three old sub-keys died with HomepageSection), values grid, leadership grid, 2026 theme block |
| events | `page-hero`, `upcoming`, `past` | PageHero banner, upcoming grid, past grid |
| visit | `page-hero`, `service-times`, `location`, `what-to-expect`, `faqs`, `rsvp`, `coming-sunday` | PageHero, carousel, location block, steps, FAQ accordion, RSVP form, CTA card |
| sermons | `sermons-grid` | sermon card grid |
| series | `page-hero`, `series-grid` | PageHero banner, series grid |
| give / prayer / contact | `page-hero` (1 each) | PageHero banners (confirm via D4) |

Seed total: homepage 6 + others 20 = **26 keys** (+2 if D2b) — all created by `ensure_registered()`, never by hand.

---

## 6. Decision points

| ID | Question | Options / default |
|----|----------|--------------------|
| D1 | Disposal of discarded `HomepageSection` (model, admin entry, dead `homepage.sections` payload, its 5 never-rendered rows) | **(a) full cleanup** — unregister admin, remove payload key + `HomePageResponse.sections` type, `DropModel` migration **[recommended — honors "discard"; rows grep-verified never rendered]** · (b) minimal — unregister admin only; model dormant, rows kept |
| D2 | Homepage extras: What-to-Expect + CTA Banner (they render on the homepage but are absent from your list of six) | **(a) exclude — match your list exactly [default]** · (b) include → 2 extra keys + gates |
| D3 | Sections admin placement | **(a) pinned top-level "Sections" group [recommended]** · (b) inside existing Homepage group |
| D4 | Scope of other pages in this delivery | **(a) all pages of §5 now [recommended — original R1]** · (b) homepage six first, other pages follow up |

---

## 7. Implementation steps

**Phase A — backend**
1. `content/models.py`: add `PAGE_CHOICES` + `SiteSection` (§4.1).
2. Migration: `CreateModel SiteSection` (nothing else touches existing tables).
3. New `content/sections_registry.py`: registry tuples (scope per D2/D4) + `ensure_registered()`.
4. `content/views.py` + `content/urls.py`: `GET /api/sections` (runs `ensure_registered()` first).
5. `content/admin.py`: `SiteSectionAdmin` (§4.5) + placement per D3.
6. **If D1a:** unregister `HomepageSectionAdmin`; remove `sections` key from `homepage()` and `sections` from `HomePageResponse` (`api.ts`); add `DropModel HomepageSection` migration.

**Phase B — frontend**
7. New `website/src/lib/sections.ts`: `getSections()` (fail-open `{}`) + `isEnabled()`.
8. Gates per §5 — `index.astro` (6, +2 if D2b), `about.astro` (4), `events.astro` (3), `visit.astro` (7), `sermons.astro` (1), `series.astro` (2), `give/prayer/contact.astro` (3).
9. `npm run check`.

**Phase C — validation & docs**
10. Run §9 battery → append Implementation Report to this document → append B5_1 summary **and the inheritance recipe** to `MEMORY.md`.

---

## 8. Out of scope

- **R2 (media uploads)** — deferred entirely; draft preserved in `B5_UNIFIED_SECTION_VISIBILITY_AND_MEDIA_UPLOAD_PLAN.md` §4 for its own plan and approval.
- The 5 legacy `HomepageSection` rows — destroyed **only** if D1a is chosen (explicit consent via D1; never rendered anywhere).
- Row-level flags (`is_published`, `status`, `is_active`) — unchanged (B4.3L intact).
- Nav/header/footer/logo (ADR-001 structural), academy portal, give/prayer/contact body content (`site.ts` static).
- Backend-side omission of section payloads (see §4.6).

---

## 9. Verification plan

1. `manage.py check` clean; `makemigrations --check` → only the expected new migration(s) (+ pre-existing `accounts`/`events` drift, noted).
2. `migrate`; `SiteSection` table exists and is empty until first registry call.
3. `ensure_registered()` idempotent — two consecutive calls → exact expected key set (homepage = the six, seed order preserved), **no duplicates, existing toggles never reset**.
4. `GET /api/sections` → nested `{page: {key: bool}}` map; fail-open verified (`isEnabled({}, 'homepage', 'anything') === true`).
5. Admin: "Sections" group present per D3; `page` filter works; inline enable/disable works; titles display ("Hero Section", not `hero`).
6. Regression — all enabled: every page visually identical to current.
7. Each of the six homepage toggles disabled one at a time → that section absent from served HTML, the other five intact; re-enable → restored.
8. All six off → homepage still renders (header/footer/nav intact), no console errors.
9. Other-page spot checks: `about.leadership`, `visit.rsvp`, `events.past` off → hidden, error-free; re-enable → restored.
10. API unreachable → site renders fully (fail-open, site never blanks).
11. **If D1a:** `/api/homepage` has no `sections` key; admin has no "Homepage Sections" entry; old table dropped; `manage.py check` still clean.
12. `npm run check` passes.

### 9.1 Results (2026-09-23)

| # | Check | Evidence |
|---|-------|----------|
| 1 | `manage.py check` | ✅ clean; `0017_sitesection_visibility` is the only new migration (pre-existing `accounts`/`events` drift untouched) |
| 2 | Migration applied | ✅ last content migration = `0017_sitesection_visibility` |
| 3 | `ensure_registered()` idempotent | ✅ 28 rows / 9 pages, no duplicates, toggles never reset (repeated shell + changelist calls) |
| 4 | `GET /api/sections` | ✅ 9 pages × 28 keys, nested `{page: {key: bool}}` |
| 5 | Admin (D3/D4) | ✅ 9 per-page "Sections" admins registered; 9 changelists HTTP 200 with correct page-scoped rows; add/delete disabled; legacy `HomepageSection` unregistered |
| 6 | All-enabled regression | ✅ 28/28 enabled; pages render identical to baseline |
| 7 | Per-toggle live E2E | ✅ homepage `what-to-expect` 1→0 and `pastor-profile` 1→0 while `cta-banner`/`upcoming-events` unchanged; `visit/location` heading removed (global footer label unaffected); API flags `false`; re-enable → exact baseline |
| 8 | All homepage sections off | ✅ HTTP 200 (84 KB); all section markers 0; header/nav/footer intact; API all `false`; restore → 28/28 with markers back |
| 9 | Gate coverage | ✅ 28 gates across 9 pages, matching registry counts (8/4/3/7/1/2/1/1/1) |
| 10 | Fail-open | ✅ bundled-module test 6/6 PASS (connection refused → `{}`, HTTP 500 → `{}`, missing page/key / undefined flags → enabled) |
| 11 | D1b legacy retention | ✅ `HomepageSection` model + 5 dormant rows kept; hidden from admin registry; never rendered anywhere |
| 12 | `astro check` | ✅ zero new diagnostics vs committed baseline (only pre-existing issues, e.g. `EventsCarouselSection.astro`, `AcademyHeader.astro`) |

**Out-of-scope finding (pre-existing, not caused by R1):** with the backend fully
down, SSR pages that await ungated data helpers (`/`, `/about`, `/events`,
`/sermons`) return 500 — `getUpcomingEvents`/`getLatestSermon`/`getTestimonials`
do not catch errors. R1's `getSections()` itself fails open (test 10); whole-page
resilience when the backend is down is a separate hardening item.

---

## 10. Risks & mitigations

- New empty table → negligible migration risk; no existing table is modified. The only destructive step is the optional D1a drop, explicitly consented via D1 (rows never rendered anywhere — grep-verified).
- Fail-open defaults prioritize availability over hide-accuracy (an API hiccup shows sections rather than blanking the site) — accepted trade-off.
- Same key on different pages (e.g. `service-times` on homepage and visit) is safe via `(page, key)` uniqueness; the helper always takes both arguments.
- Future pages added to `PAGE_CHOICES` may emit a choices-only `AlterField` (no SQL effect) — harmless; can be avoided by dropping `choices` if churn is unwanted.
- `index.astro` line numbers shift over time — §5 gates are identified by component name, not line number.

---

## 11. Approval checklist

- [x] R1 design approved (`SiteSection` + registry + `/api/sections` + SSR gates)
- [x] **D1 = (b)** HomepageSection kept dormant (model + 5 rows retained, removed from admin registry)
- [x] **D2 = (b)** Homepage extras included (What-to-Expect + CTA Banner → 8 homepage keys)
- [x] **D3 = per-page** grouping — each page's Sections toggles live inside that page's admin group
- [x] **D4 = (a)** All pages delivered (homepage, about, events, visit, sermons, series, give, prayer, contact)
- [x] Implementation authorized & completed 2026-09-23
