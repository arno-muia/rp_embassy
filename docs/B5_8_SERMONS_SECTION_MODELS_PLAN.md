# B5.8 — Sermons Page Sections: Dedicated Models (admin-managed content components)

**Status:** ✅ IMPLEMENTED & VERIFIED — 2026-09-29 (sections 1–5 of the Sermons group approved by the user; mirrors the B5.7 Visit pattern exactly)

---

## 1. Goal

Every fixed string on `/sermons` and `/sermons/[slug]` is managed from the admin
panel's **Sermons** card, with no code edits. Per-sermon data (title, speaker,
description, video URL, thumbnails) stays on `PublicSermon`; per-series data stays
on `SermonSeries` — those were NOT moved in this phase (separate approval).

## 2. What the admin now shows (Sermons group, page order)

| Entry | Model | Management |
|---|---|---|
| Page Hero | `SermonsHero` (one record) | image + alt, label ("Latest sermon"), preacher, sermon title, button label + URL, register (`warm`/`celestial`/`parchment`) |
| Browse by Series | `SermonsBrowseSection` (one record) | heading — pills remain data-driven from `/api/series` |
| All Sermons | `SermonsGridSection` (one record) | heading, empty-state text |
| Sermon Detail Copy | `SermonDetailCopy` (one record) | video note, "Watch on YouTube" label, secondary button label + URL |
| Related Sermons | `SermonsRelatedSection` (one record) | heading on the related grid |
| Sections | `SermonsSections` | unchanged — on/off for `page-hero`, `browse-by-series`, `sermons-grid` |

The roadmap comment (`sermons → PublicSermon/SermonSeries, series → SermonSeries`)
remains in `admin.py` — those record admins were NOT moved in B5.8.

## 3. Data flow

```
Admin (Sermons group) → PostgreSQL tables
    content_sermonshero · content_sermonsbrowsesection · content_sermonsgridsection
    content_sermondetailcopy · content_sermonsrelatedsection
        → GET /api/sermons-page  {hero, browse, grid, detail, related}
            → sermons.astro + sermons/[slug].astro (original copy = fallback)
```

- `/api/sermons-page` returns each section as `null` when its record has not been
  created; the client then renders its fallback (the original hardcoded copy).
- Singletons ordered `-updated_at` — latest record wins (B5.5/B5.7 precedent).
- The path is `sermons-page` because the bare `sermons` path is owned by the DRF
  router (`/api/sermons`, `/api/sermons/{slug}`).
- Section on/off remains `/api/sections` (`SermonsSections` proxy); no duplicate
  switches. Sermon/series records unchanged (`/api/sermons`, `/api/series`).

## 4. Decisions

| # | Decision |
|---|---|
| D1 | **Static admin-managed hero (option A)** — preacher/title are admin copy, not auto-filled from the latest `PublicSermon`; seed matches today's page exactly |
| D2 | **Detail pages included** — `SermonDetailCopy` + `SermonsRelatedSection` cover `/sermons/[slug]`; no section toggles added for detail pages (they have no registry keys) |
| D3 | `PublicSermon`/`SermonSeries` admin moves **deferred** (roadmap comment kept) |
| D4 | `resolveMediaUrl` applied to hero image in `getSermonsPage()` (B5.6 origin fix) |

## 5. Data seeding (zero visual change)

Migration `content.0023` creates the schema; `content.0024` seeds all five records
with the exact copy hardcoded in `sermons.astro` / `sermons/[slug].astro` at the
time (image `/images/Thumbnail_final.jpg`, "Latest sermon", "Pst Charles Muchemi",
"Emotional Intelligence", "Watch Sermon →", "Browse by Series", "All Sermons",
"No sermons available yet.", "Watch this teaching on our YouTube channel",
"Watch on YouTube", "Kingdom Formation" → `/academy`, "Related Sermons").
Both are reversible (reverse deletes only the seeded rows).

## 6. Files changed

**Backend — `RP/backend/backend/apps/content/`**

| File | Change |
|---|---|
| `models.py` | +`SermonsHeroRegister`, +`SermonsHero`, +`SermonsBrowseSection`, +`SermonsGridSection`, +`SermonDetailCopy`, +`SermonsRelatedSection` |
| `migrations/0023_sermondetailcopy_sermonsbrowsesection_and_more.py` | schema (auto-generated) |
| `migrations/0024_sermons_seed_content.py` | data seed (reversible) |
| `admin.py` | 5 new admins with fieldsets; `('sermons', 'Sermons', ...)` added to `PAGE_CONTENT_GROUPS` |
| `repositories.py` | +`SermonsContentRepository` (hero, browse_section, grid_section, detail_copy, related_section) |
| `serializers.py` | +5 read serializers |
| `views.py` | +`sermons_page` |
| `urls.py` | +`path('sermons-page', ...)` |

**Frontend — `RP/website/`**

| File | Change |
|---|---|
| `src/lib/api.ts` | +`sermonsPage` endpoint, 6 content types, `getSermonsPage()` (hero image via `resolveMediaUrl`) |
| `src/pages/sermons.astro` | fetches `getSermonsPage()` in `Promise.all`; hero, browse heading, grid heading/empty text all bound with original copy as fallback |
| `src/pages/sermons/[slug].astro` | video note, both button labels, secondary URL, related heading bound with original copy as fallback |

## 7. Verification results

1. `manage.py check` → **No issues**; `makemigrations --check` → no pending content changes.
2. `migrate` → `0023` + `0024` applied; all five seed rows verified via shell.
3. `GET /api/sermons-page` → 200 with all five keys carrying the exact live copy.
4. Admin: all 5 models registered (verified in `admin.site._registry`).
5. `/sermons` → 200 and renders hero/browse/grid copy from the API;
   `/sermons/salvation-charles-muchemi` → 200 with detail + related copy
   ("Watch on YouTube" ×2, "Kingdom Formation", "Related Sermons").
6. Live-edit test: `SermonsGridSection.heading` → `[B58-EDIT]` appeared on
   `/sermons` next request → reverted to "All Sermons".
7. Regression: `/`, `/about`, `/visit`, `/series`, `/events` → 200.
8. `astro check` → clean on all touched files (session log).

## 8. Notes / follow-ups

- **Series page group** (`/series`: Page Hero title/subtitle/register, Series Grid
  empty text) is the next approved phase — not part of B5.8.
- `PublicSermon`/`SermonSeries` card moves remain on the roadmap (separate approval).
- Detail pages have no `/api/sections` toggles — `SermonDetailCopy` and
  `SermonsRelatedSection` are always rendered when their record exists.

