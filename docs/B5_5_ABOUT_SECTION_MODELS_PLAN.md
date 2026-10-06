# B5.5 — About Sections: Dedicated Models (admin-managed content components)

**Status:** ✅ IMPLEMENTED & VERIFIED — 2026-09-28 (decisions approved by the user on 2026-09-28: D1-A, D2-A, D3, D4, D5, D6)
**Supersedes:** the B5.4 v2 three-SystemConfig-JSON-proxy editors for the About page
(`AboutIntroConfig` / `AboutValuesConfig` / `AboutThemeConfig`).

---

## 1. Goal

Each individual section under the admin's **About** group holds *all* of its rendered
components as real, labelled fields — exactly like **Website leaders** — so every title,
text, image and label on the About page is managed from the admin panel, with no code edits.

## 2. What the admin now shows (About group, page order)

| Entry | Model | Management |
|---|---|---|
| Welcome, Vision & Mission | `AboutWelcome` (one record) | eyebrow, title, vision label + text, mission label + text |
| Our Values | `AboutValuesSection` + inline `AboutValue` rows | heading, subtitle, and each card's title / description / order / published (add, edit, delete, reorder) |
| Website leaders | `WebsiteLeader` | unchanged (the reference implementation) |
| 2026 Theme | `AboutTheme` (one record) | eyebrow, title, scripture reference, scripture text, image (path/URL + preview), button label + URL |
| Sections | `AboutSections` | unchanged — enable/disable each About section |

## 3. Data flow

```
Admin (About group) → PostgreSQL tables
    content_aboutwelcome · content_aboutvaluessection · content_aboutvalue · content_abouttheme
        → GET /api/about  {intro, values{heading,subtitle,items[]}, theme}
            → about.astro (fallbacks = the original copy when the API is unreachable)
```

- `/api/about` returns each section as `null` when its record has not been created;
  only **published** cards are returned, ordered by `sort_order`.
- No add/delete restrictions on the new models (D5) — the API renders the **most recently
  updated** record per section, so the latest admin edit is always what the page shows.
- Section on/off remains the existing **Sections** toggles (`/api/sections`); no duplicate
  switches were added. `/api/site-config` is unchanged.

## 4. Decisions (user-approved)

| # | Decision |
|---|---|
| D1 | **Dedicated models (A)** — rejected field-level forms over the SystemConfig 'site' JSON |
| D2 | **2026 Theme image included AND rendered (A)** — poster shows beneath the scripture text; blank hides it |
| D3 | Intro author **omitted** — exact previous rendering retained |
| D4 | Value cards keep **title + description** (current design) |
| D5 | **No add/delete restrictions** — the API renders the most recently updated record |
| D6 | Scope: the live site only |

## 5. Data seeding (zero visual change)

Migration `content.0020` copies the live `SystemConfig 'site'` content
(`welcomeMessage`, `values`, `theme2026`) plus the labels that were previously hardcoded in
the page (eyebrow `1 Peter 2:9`, `our Vision`, `Our Mission`, `Our Values`, the values
subtitle, `2026 Theme`, `Join Us` → `/visit`) into the new tables. `SystemConfig` is never
modified; the migration is reversible (reverse deletes only the seeded rows).

## 6. Files changed

**Backend — `RP/backend/backend/apps/content/`**

| File | Change |
|---|---|
| `models.py` | +`AboutWelcome`, +`AboutValuesSection`, +`AboutValue`, +`AboutTheme`; −3 JSON proxies |
| `migrations/0019_abouttheme_aboutvalue_aboutvaluessection_and_more.py` | schema: 4 Creates + 3 proxy Deletes + FK |
| `migrations/0020_about_seed_content.py` | data seed from live content (reversible) |
| `admin.py` | 3 new admins (`StackedInline` for cards; image preview); About card registry updated; old proxy admins/forms removed; raw SystemConfig editor note |
| `repositories.py` | +`AboutContentRepository` |
| `serializers.py` | +3 read serializers |
| `views.py` | +`about_page` |
| `urls.py` | +`/api/about` |

**Frontend — `RP/website/`**

| File | Change |
|---|---|
| `src/lib/api.ts` | +`about` endpoint, AboutContent types, `getAbout()` |
| `src/pages/about.astro` | all three sections read the new endpoint (original copy as fallback); theme poster rendered when set |

## 7. Verification results

1. `manage.py check` → **No issues**; `makemigrations --check` → no pending changes.
2. `migrate` → `0019` + `0020` applied; seeded records match the live copy exactly
   (welcome title/message, 3 value cards in order, theme fields + image).
3. Admin (authenticated walkthrough): About card lists exactly
   **Welcome, Vision & Mission → Our Values → Website leaders → 2026 Theme → Sections**;
   all new changelists + change forms → 200; removed proxies → 404.
4. `GET /api/about` → 200 with every component; `GET /api/site-config` and
   `GET /api/sections` → unchanged (regression).
5. `astro check` / build → clean.

## 8. Notes / follow-ups

- Image fields are path/URL + admin preview — the same pattern as **Website leaders**'
  photo. Real-time **upload** is the next approved workstream.
- The legacy `SystemConfig 'site'` subkeys (`welcomeMessage`, `values`, `theme2026`) remain
  in the database for reference only; the raw SystemConfig editor carries a note saying so.
