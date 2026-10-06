# B5 — Unified Section Visibility + Admin Media Uploads (Implementation Plan)

**Status:** ⚠️ SUPERSEDED for R1 — redesigned in `B5_1_R1_SECTION_VISIBILITY_PLAN.md` (2026-09-23): the `HomepageSection`-based design in §3 was discarded per user correction (its seeded rows do not match the actual homepage sections). **R2 (media uploads, §4) remains a deferred draft** pending its own plan/approval. Do not implement anything from §3 or §7 of this document.
**Date:** 2026-09-23
**Scope:** (R1) Disable/enable any admin-managed section on any page without deleting it — inherited by future sections. (R2) Admin image upload from the panel (e.g. weekly testimony photos) that inherits existing section styling automatically.
**Builds on:** `docs/B4_3L_SERVICETIME_ENABLE_DISABLE_PLAN.md` (row-level toggle), ADR-001 Future Evolution items "B4 media pipeline" and "HomepageSection toggles".

---

## 1. Requirements

- **R1 — Uniform section toggle:** Every section in the admin panel, from every page, can be disabled from display on the website. Nothing is deleted — content, ordering, and functionality remain intact and restore on re-enable. Any *future* section added to the admin inherits the same mechanism without new plumbing.
- **R2 — In-panel image upload:** The admin can drop/import an image in the panel to change an image on the website (no code, no image folders). Example: 3 weekly testimonies — admin uploads each testifier's photo, and it renders in the section with the **current styling** (shape, border, `object-cover`, etc.) automatically.

---

## 2. Audit Findings

### 2.1 Section visibility today

| Finding | Location |
|---|---|
| `HomepageSection(section_name UNIQUE, enabled, display_order)` exists, seeded with 5 rows: `welcome, mission, vision, kingdom-culture, cell-groups` | `content/models.py:386` |
| It is serialized into `/api/homepage` as `sections` — but **no frontend page ever reads it** → toggling it today changes nothing | `views.py:163`, `website/src` (grep-verified) |
| The 5 seeded keys (`welcome/mission/vision/kingdom-culture/cell-groups`) appear **nowhere** in the frontend → orphan/aspirational rows | grep-verified |
| Row-level `is_published` is now uniform across content models (ServiceTime enforced in B4.3L; sermons/leaders/testimonials/series/academy repositories all filter it) | `repositories.py` |
| Page payloads are **fragmented across 5 endpoints**: homepage sections come from `/api/homepage`, `/api/site-config`, `/api/events`, `/api/sermons`, `/api/testimonials` | `index.astro:20-28` |
| Admin groups homepage models via custom `HomepageGroupedAdminSite`; `HomepageSectionAdmin` exists (list_editable `enabled`) but sits outside the Homepage group | `content/admin.py:32-87, 209-216` |

### 2.2 Image handling today

| Finding | Location |
|---|---|
| **All models are `managed = True`** (content + events) → schema changes are migration-safe | models grep-verified |
| **Pillow 11.0.0 already installed** in `tf_env` → no new dependency | `pip` check |
| All image refs are plain strings: `photo_url/image_url/thumbnail_url/image` (CharField) + `hero_background_image` (URLField). **No `ImageField`, no upload logic anywhere** | models grep-verified |
| **No `MEDIA_URL`/`MEDIA_ROOT` in settings; no `/media/` route** | `settings.py`, `urls.py` |
| Sampled DB values: legacy frontend paths (`/images/team/...`, `/images/services/...`, `/images/events/...`), one external Unsplash URL (hero bg), testimonial `photo_url` = **all NULL** | live DB query |
| **Testimonial photos are hardcoded by name convention** — `src={/images/${firstName}.jpg}` — the DB `photo_url` field is ignored entirely by the frontend | `TestimonialsCarousel.astro:41` |
| All `<img>` slots already carry final styling (e.g. testimonial: `h-32 w-32 rounded-full border-4` + `object-cover`) → swapping the `src` inherits styling automatically | carousel, LeaderCard, SermonCard, EventCard, PastorSection, ServiceTimesSection |
| `MediaAsset` model exists but is **schema-only** ("no upload logic, no storage integration"), `file_path` is a CharField | `media/models.py` |
| Frontend mappers already exist: `photo_url → photo` (`toTestimonialView`, `toLeaderView`), types include `photo?` | `api.ts:276-284`, `types/testimonial.ts` |

### 2.3 Section inventory (page × key × render target × admin source)

| Page | Key | Renders | Admin source |
|---|---|---|---|
| homepage | `hero` | Hero banner | HomepageSettings |
| homepage | `service-times` | Service Times tabs | ServiceTime |
| homepage | `events` | Upcoming events carousel | ChurchEvent (Upcoming Events) |
| homepage | `what-to-expect` | What to Expect cards | SystemConfig `site` JSON |
| homepage | `latest-sermon` | Latest sermon block | HomepageLatestSermon / PublicSermon |
| homepage | `testimonials` | Testimonies (3 cards) | WebsiteTestimonial |
| homepage | `pastor` | Pastor section | PastorProfile |
| homepage | `cta` | CTA banner | HomepageSettings (cta_*) |
| about | `welcome`, `vision`, `mission` | Intro quotes block (3 sub-groups — matches the 3 seeded keys) | block text is code-owned; toggle hides it |
| about | `values` | Our Values grid | SystemConfig `site` JSON (ContentBlock VALUE) |
| about | `leadership` | Leadership Team grid | WebsiteLeader |
| about | `theme-2026` | 2026 Theme block | SystemConfig `site` JSON |
| events | `page-hero`, `upcoming`, `past` | Hero banner, upcoming grid, past grid | ChurchEvent (grid data) |
| visit | `page-hero`, `service-times`, `location`, `what-to-expect`, `faqs`, `rsvp`, `coming-sunday` | Hero, carousel, location, steps, FAQ accordion, RSVP form, CTA card | ServiceTime / SystemConfig / form |
| sermons | `sermons-grid` | Sermon cards grid | PublicSermon |
| series | `page-hero`, `series-grid` | Hero, series grid | SermonSeries |
| give / prayer / contact | `page-hero` | PageHero banners | static (`site.ts`) — toggle hides only |
| — | `kingdom-culture`, `cell-groups` | **no rendered block exists** | seeded legacy rows → kept as reserved (see D5) |
| academy | — | portal dashboard uses placeholder data, not CMS | out of scope (see §6) |

---

## 3. Feature 1 — Unified Section Visibility (R1)

### 3.1 Model change — `HomepageSection` gains a `page` scope

```python
PAGE_CHOICES = [
    ('homepage', 'Home'), ('about', 'About'), ('events', 'Events'),
    ('visit', 'Visit'), ('sermons', 'Sermons'), ('series', 'Series'),
    ('give', 'Give'), ('prayer', 'Prayer'), ('contact', 'Contact'),
]

class HomepageSection(models.Model):
    page = models.CharField(max_length=32, choices=PAGE_CHOICES, default='homepage')
    section_name = models.CharField(max_length=128)          # unique=True REMOVED
    enabled = models.BooleanField(default=True)
    ...
    class Meta:
        unique_together = (('page', 'section_name'),)        # composite uniqueness
        verbose_name = 'Page Section'
        verbose_name_plural = 'Page Sections'
```

- Migration = `AddField page` + `AlterUniqueTogether` (safe: table is Django-owned, only 5 rows).
- Same key may exist per page (e.g. `service-times` on homepage **and** visit → independent control).
- **Data migration:** `welcome/mission/vision → page='about'`; `kingdom-culture/cell-groups` stay `page='homepage'` as reserved rows (never deleted).
- Class name `HomepageSection` kept (avoids `RenameModel` churn across serializers/admin group); only the **admin labels** change to "Page Sections".

### 3.2 Registry — the inheritance mechanism

New module `content/sections_registry.py` holding one flat table of `(page, key, title, order)` — the §2.3 inventory (~30 entries).

```python
def ensure_registered():
    """Create missing rows (enabled=True). Never deletes, never resets admin's toggles."""
    for page, key, title, order in SECTION_REGISTRY:
        HomepageSection.objects.get_or_create(
            page=page, section_name=key,
            defaults={'enabled': True, 'display_order': order})
```

Called from the sections API view and the Sections admin changelist.

**→ Inheritance guarantee:** to add a future section, a developer adds **one registry line + one frontend `isEnabled(...)` wrap**. The toggle row auto-appears in the admin, enabled by default — no migration, no new model, no new admin code. Recipe documented in the report + `MEMORY.md`.

### 3.3 API — `GET /api/sections`

```json
{ "homepage": {"hero": true, "testimonials": false, ...},
  "about": {"leadership": true, ...}, ... }
```
Built after `ensure_registered()`. Missing key on read ⇒ **enabled** (safe default: unregistered sections render exactly as today). `/api/homepage`'s existing `sections` array left untouched (back-compat).

### 3.4 Frontend — helper + gates

New `src/lib/sections.ts`:

```ts
export async function getSections(): Promise<SectionFlags>;   // {} on any failure → all enabled
export function isEnabled(flags, page, key): boolean;         // default true
```

Each page fetches it once in frontmatter (index/visit/about add one entry to their existing `Promise.all`; events/sermons/series/give/prayer/contact add one call), then wraps sections:

```astro
{isEnabled(sec,'homepage','testimonials') && <TestimonialsSection ... />}
```

Gate points = every row of §2.3. Special case: the `about` intro hides if `welcome ∥ vision ∥ mission` is enabled, with each quote group gated individually (putting the 3 seeded keys to real use). Astro runs `output: 'server'` → disabled sections are absent from served HTML (no SEO leakage) and toggles apply on the next request.

### 3.5 Admin UX

- `HomepageSectionAdmin`: `list_display = (page, section_name, enabled, display_order, updated_at)`, `list_filter = (page, enabled)`, `list_editable = (enabled, display_order)`, ordering `('page','display_order')`.
- **Placement (D1):** recommended — extend `HomepageGroupedAdminSite.get_app_list` to emit a synthetic **"Sections" app pinned first** on the admin index containing just this model; alternative — leave it in Content with a page filter.
- Row-level `is_published` stays independent (double-gate: item published **and** section enabled).

### 3.6 Why render-time (frontend) gating for sections — unlike B4.3L

Row-level `is_published` is *content truth* → enforced server-side (B4.3L). Section flags are *layout truth*, and one payload often serves several pages (`/api/events` → homepage carousel **and** events page grid); the API cannot know the caller's page. Server-side omission would need page-context params on 5 endpoints and would break shared payloads. Frontend SSR gating is the correct uniform enforcement point for R1 — same visible result, less coupling. Recorded as an architecture decision in §9.

---

## 4. Feature 2 — Admin Image Uploads (R2)

### 4.1 Media plumbing

`settings.py`:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'      # → RP/backend/media/
```
`backend/urls.py`: append `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` (Django's `static()` no-ops when `DEBUG=False` → production must serve `/media/` via the web server, §4.7). **Pillow 11.0.0 already installed** in `tf_env` — no new dependency.

### 4.2 Field conversions (in-place, no data migration)

Convert the 8 public-site image fields `CharField/URLField → ImageField(upload_to=...)`. DB column type stays `varchar(512)` → **`max_length=512` MUST be passed explicitly** (ImageField defaults to 100 — omitting it would generate a truncating `ALTER`): ⚠ critical implementation detail.

| Model | Field (name & db_column kept) | `upload_to` | Admin size hint (help_text) |
|---|---|---|---|
| WebsiteTestimonial | `photo_url` (`photoUrl`) | `testimonials/` | 600×600 square |
| WebsiteLeader | `photo_url` (`photoUrl`) | `leaders/` | 600×600 |
| PublicSermon | `thumbnail_url` (`thumbnailUrl`) | `sermons/` | 1280×720 (16:9) |
| SermonSeries | `image_url` (`imageUrl`) | `series/` | 1280×720 |
| ChurchEvent | `image_url` (`imageUrl`) | `events/` | 1200×630 poster |
| PastorProfile | `image` | `pastors/` | 800×800 |
| ServiceTime | `image` | `services/` | 1200×630 |
| HomepageSettings | `hero_background_image` (URLField) | `hero/` | 1920×1080 |

Existing values (`/images/...`, external `https://...`, NULL) stay untouched and valid — ImageField only validates *newly uploaded files*. One `AlterField` migration per affected app (content + events), no meaningful SQL column change.

### 4.3 URL resolution — shared serializer field

Custom `ResolvedImageField(serializers.CharField)` applied to those 8 fields on the read serializers; output rules:

1. empty → `''`
2. starts `http(s)://` → passthrough (Unsplash hero keeps working)
3. starts `/media/` → `request.build_absolute_uri(...)` (new uploads → absolute API-origin URL)
4. starts `/` → passthrough (legacy `/images/...` resolved against frontend origin, as today)
5. bare relative (`testimonials/x.jpg`) → `MEDIA_URL` join + absolute

Manually instantiated serializers in `homepage()` gain `context={'request': request}`. Frontend needs **no URL changes and no styling changes** — same `<img>` tags/classes ⇒ current styling inherited automatically (R2). Existing fallbacks (`?? "/images/posters/..."`) untouched.

### 4.4 Admin UX ("drop images in the panel")

- Native `ImageField` widget: click-to-choose **and** drag-and-drop onto the field (Chromium), plus **Clear** checkbox to revert to legacy/fallback (D4 covers a custom drop-zone JS if needed).
- Each image admin gains a read-only **preview thumbnail** method (~120px `<img>`) beside the field — instant confirmation of what is live.
- `help_text` carries the §4.2 size hint; existing CSS (`object-cover`, fixed shapes) does the rest.
- **Weekly testimony workflow:** Admin → Testimonials → open "Sarah W." → drop photo → Save → homepage shows it on next request; replace/unpublish rows via existing row-level `is_published` as before.

### 4.5 Validation & safety

- Pillow content validation (inherent to `ImageField`); whitelist **jpg/jpeg/png/webp/gif**; **SVG rejected** (XSS).
- Custom size validator **≤ 5 MB**.
- Collision-safe storage (Django `get_available_name` suffixes duplicates) → weekly uploads never overwrite each other.

### 4.6 Frontend fix required (part of R2)

`TestimonialsCarousel.astro:41` fabricates `src` from the testifier's first name and ignores the API. Change to:

```astro
src={testimonial.photo || `/images/${testimonial.name.split(" ")[0].toLowerCase()}.jpg`}
```

`TestimonialView.photo` already exists and is already populated by `index.astro` — it is simply unused. The legacy name-path stays as fallback → identical look until the first upload. Leader/Sermon/Event/Pastor/ServiceTime cards already read their image fields correctly — no changes.

### 4.7 Production serving (deployment note, not code)

Dev: Django serves `/media/` via the `DEBUG` route. Prod: web server aliases `/media/` → `MEDIA_ROOT` (nginx `location /media/ { alias ...; }` or Caddy `file_server`). No CORS impact (`<img>` is cross-origin-allowed). Recorded in the implementation report.

---

## 5. Phased Implementation Steps

**Phase 1 — Section visibility (backend)**
1. `content/models.py` — add `page`, remove `section_name unique=True`, add `unique_together`, update Meta verbose_names to "Page Section(s)".
2. Migration `AddField page` + `AlterUniqueTogether`.
3. Data migration — `welcome/mission/vision → page='about'` (other rows untouched).
4. New `content/sections_registry.py` — registry table + `ensure_registered()`.
5. `content/views.py` + `content/urls.py` — `GET /api/sections`.
6. `content/admin.py` — HomepageSectionAdmin updates (`page` in display/filter, `list_editable`) + placement per D1.

**Phase 2 — Section visibility (frontend)**
7. New `website/src/lib/sections.ts` — `getSections()` (fail-open `{}`) + `isEnabled()`.
8. Gate every §2.3 key: `index.astro` (8), `about.astro` (6, incl. intro sub-groups), `events.astro` (3), `visit.astro` (7), `sermons.astro` (1), `series.astro` (2), `give/prayer/contact.astro` (1 each = 3).
9. `npm run check` + manual toggle pass.

**Phase 3 — Media plumbing & fields**
10. `settings.py` MEDIA_URL/MEDIA_ROOT; `backend/urls.py` DEBUG media route.
11. 8 fields → `ImageField(upload_to=..., max_length=512)` ⚠ (preserve `db_column`/`null`/`blank`; add size-hint `help_text`).
12. `AlterField` migrations (content + events).
13. `content/serializers.py` — `ResolvedImageField` applied to the 8 read serializers; `context={'request': request}` in `homepage()`.
14. Admin preview-thumbnail methods + fieldset labels on the 8 image admins (content + events).
15. Validators (≤5 MB, format whitelist) on each converted field.
16. Frontend: `TestimonialsCarousel.astro` photo fix (**only** frontend media change).

**Phase 4 — optional, decision-gated:** D2 auto-resize · D3 MediaAsset registration signal · D4 custom drop-zone JS.

**Phase 5 — Validation & docs:** §8 battery → append Implementation Report to this doc → append B5 summary to `MEMORY.md`.

---

## 6. Explicitly Out of Scope

- **No deletion** of any row, content, or functional form — disabling hides, re-enabling restores.
- give/prayer/contact body content & academy dashboard: CMS migration from `site.ts`/placeholder data (future content migration; registry is ready to receive their keys).
- Header/nav/footer/logo (ADR-001: structural, code-owned).
- Legacy `SystemConfig 'site'` JSON hero background (HomepageSettings is the live source).
- Member `profile_image_url` (portal, not the public site).
- CDN/optimization pipeline beyond optional D2 (ADR's full B4 media pipeline comes later).
- Row-level `is_published` semantics (unchanged).

---

## 7. Decision Points (confirm or amend)

| ID | Question | Recommended default |
|----|----------|---------------------|
| D1 | Sections admin placement | (a) pinned top-level **"Sections"** group on admin index |
| D2 | Auto-resize uploads server-side (max 2000px, q85) | **ON** (protects weekly mobile uploads) |
| D3 | MediaAsset auto-registration on upload | **Later (Phase 4)** — not in MVP |
| D4 | Upload widget | **Native file input** (Chromium drag-drop) — custom drop-zone JS later if wanted |
| D5 | Reserved rows `kingdom-culture`/`cell-groups` | **Keep** (never auto-delete) |
| D6 | `page-hero` toggles for give/prayer/contact (static banners) | **Include** |

Say *"approved as recommended"* or list amendments.

---

## 8. Verification Plan

**Backend**
1. `manage.py check` clean; `makemigrations --check` shows only the expected new migrations (plus pre-existing `accounts`/`events` drift, noted).
2. `migrate` — section rows mapped correctly (3 about, 2 reserved homepage); image `AlterField`s apply without column truncation (verify `varchar(512)` retained).
3. `GET /api/sections` → full nested map; second call idempotent (no duplicate rows).
4. Admin: all ~30 keys listed, `page` filter works, inline `enabled` toggle works, reserved rows visible.

**Sections (frontend)**
5. Everything enabled → all pages visually unchanged (regression).
6. Disable `homepage.testimonials` → absent from served HTML; others intact; re-enable → restored.
7. Disable `about.leadership`, `visit.rsvp`, `events.upcoming` individually → each hidden, page loads error-free; all-off stress test per page → renders, no console errors.
8. API down → site renders fully (fail-open).

**Media**
9. Shell-upload testimonial photo (`SimpleUploadedFile`) → API returns absolute `/media/testimonials/...` → `GET` 200 → homepage `<img>` shows it with unchanged styling (rounded/cover).
10. Legacy regression: leaders/sermons/events/pastor/service-times still show `/images/...`; Unsplash hero unchanged; name-based testimonial fallback works when `photo` empty.
11. Rejections: >5 MB → error; `.svg`/non-image → rejected; **Clear** reverts to legacy value.
12. Weekly cycle E2E: swap photo → refresh homepage → live; unpublish testimonial row → card hidden (B4.3L semantics intact).
13. `npm run check` passes.

---

## 9. Risks & Architecture Decisions

- ⚠ **ImageField defaults to `max_length=100`** → always pass `max_length=512`; verification step 2 checks the column.
- **Split enforcement decision:** row flags = content truth → server-side (B4.3L); section flags = layout truth → render-time gating (rationale §3.6).
- `unique → unique_together` on a 5-row Django-owned table: negligible risk; reversible.
- Fail-open section defaults prioritize availability (API hiccup never blanks the site).
- Legacy `/images/...` passed through untouched → zero visual regressions by construction.
- Prod `/media/` serving must be configured on deploy (dev works out of the box) — deployment checklist item.
- Missing serializer `request` context → resolver guard (passthrough rules; verified by tests 9–10).

---

## 10. Approval Checklist

- [ ] R1 design approved (registry + page-scoped HomepageSection + `/api/sections` + frontend gates)
- [ ] R2 design approved (MEDIA setup + 8 ImageField conversions + `ResolvedImageField` + admin upload/preview + testimonial photo fix)
- [ ] Decisions D1–D6 (approve defaults or amend)
- [ ] **Go ahead for implementation**

