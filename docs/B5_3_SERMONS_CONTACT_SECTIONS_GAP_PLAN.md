# B5_3 — Sermons & Contact Section Gaps (Sections Not Exposed in Admin)

**Status:** ✅ Implemented & verified (2026-09-26) — approved with recommendations: D1 "Contact Details & Form" · D2 registry/page order · D3 Prayer included · D4 "Page Hero" · **no migrations**
**Date:** 2026-09-26
**Scope:** Register + gate the **2 missing Sermons sections** ("Page Hero", "Browse by Series") and the **1 missing Contact section** (details + form block) so every section of those pages is individually controllable in the admin.
**Builds on:** B5.1 / R1 (mechanism) and B5.2 (rules: registry-only additions, **no migrations**, display-layer naming).

---

## 1. Requirement

1. **Sermons group** — currently shows only **"All Sermons"**. The page has **2 more sections**: the **page hero** (latest-sermon banner) and **"Browse by Series"**. Both must appear in the admin.
2. **Contact group** — currently shows only **"Page Hero"**. The page has **2 sections**; the second (contact details + form block) must appear in the admin.

---

## 2. Audit findings

| Page | Registered / gated today | Actual sections on the page | Missing from admin |
|---|---|---|---|
| **Sermons** | 1 → `sermons-grid` "All Sermons" | **3** | **Page Hero** (ungated, unregistered) · **Browse by Series** (ungated, unregistered) |
| **Contact** | 1 → `page-hero` "Page Hero" | **2** | **Contact details + form block** (ungated, unregistered) |
| **Prayer** ⚠️ *same class of gap discovered during this audit* | 1 → `page-hero` "Page Hero" | **2** | **Prayer form block** (ungated, unregistered) — see decision **D3** |
| Series | 2 → `page-hero`, `series-grid` | 2 | none ✓ |
| Homepage / About / Events / Visit / Partner | match (B5.1/B5.2) | — | none ✓ |

### Evidence (exact blocks that are ungated today)

| Page | Block | Location | Anchor text |
|---|---|---|---|
| Sermons | Latest-sermon hero banner (image + "Latest sermon" + preacher + Watch link) | `sermons.astro:14-42` | `Latest sermon` / `Pst Charles Muchemi` |
| Sermons | Browse-by-series pill list | `sermons.astro:44-60` | `<h2>Browse by Series</h2>` |
| Sermons | All-Sermons grid *(already controllable)* | `sermons.astro:62-79` | `<h2>All Sermons</h2>`, gate `sermons-grid` |
| Contact | Page hero *(already controllable)* | `contact.astro:16-22` | `PageHero` "Contact Us" |
| Contact | Contact details (Email/Location/Social) + `ContactForm` side-by-side | `contact.astro:23-77` | `Social Media`, `Send Message` |
| Prayer | Page hero *(already controllable)* | `prayer.astro:15-22` | `PageHero` "Prayer Request" |
| Prayer | `PrayerForm` block | `prayer.astro:23-27` | `PrayerForm` |

### Database / registry state (today)

- Registry: 31 keys. `SiteSection` rows: sermons = 1, contact = 1, prayer = 1 (total 31, all enabled).
- Admin cards confirmed: **Sermons → [All Sermons only]**, **Contact → [Page Hero only]**, **Prayer → [Page Hero only]**.

### E2E marker uniqueness (verified against live HTML — for the test plan)

- `/sermons`: `Latest sermon`=1 · `Browse by Series`=1 · `All Sermons`=1 (all unique)
- `/contact`: `Contact Us`=1 (hero) · `Social Media`=1 · `Send Message`=1 (block)
- `/prayer`: `We believe in the power of prayer`=1 (hero) · `Share what you'd like us to pray for`=1 (form)

---

## 3. Design

### 3.1 Registry additions (`content/sections_registry.py`)

**Sermons — 1 → 3 keys** (registry order = page order):

```python
    # --- Sermons / Series ---
    (SectionPage.SERMONS, 'page-hero', 'Page Hero'),
    (SectionPage.SERMONS, 'browse-by-series', 'Browse by Series'),
    (SectionPage.SERMONS, 'sermons-grid', 'All Sermons'),
```

**Contact — 1 → 2 keys**:

```python
    (SectionPage.CONTACT, 'page-hero', 'Page Hero'),
    (SectionPage.CONTACT, 'contact-details', 'Contact Details & Form'),   # naming per D1
```

**Prayer — 1 → 2 keys** *(only if D3 = include)*:

```python
    (SectionPage.PRAYER, 'page-hero', 'Page Hero'),
    (SectionPage.PRAYER, 'prayer-form', 'Prayer Form'),
```

Registry total: **31 → 34** keys (35 if D3 includes prayer). Rows are auto-created (enabled) by `ensure_registered()` on the next registry touch — existing rows and their toggle states are untouched.

### 3.2 Frontend gates

| File | Wrap | Gate |
|---|---|---|
| `sermons.astro` | hero banner `:14-42` | `{on("page-hero") && ( … )}` |
| `sermons.astro` | browse-by-series `:44-60` | `{on("browse-by-series") && ( … )}` |
| `contact.astro` | details+form block `:23-77` | `{on("contact-details") && ( … )}` |
| `prayer.astro` *(if D3)* | form block `:23-27` | `{on("prayer-form") && ( … )}` |

Existing gates (`sermons-grid`, contact/prayer `page-hero`) are unchanged — same `on(...)` pattern already used on the page.

### 3.3 No migrations (B5.2 rule continues)

- No model, field, or choices change → `makemigrations --check` must stay **"No changes detected"**.
- The new admin rows are **data** created at runtime by `ensure_registered()` (idempotent; never resets an existing toggle; never deletes).

### 3.4 Admin list order (decision D2)

`SiteSection.Meta.ordering = ('page', 'id')`, so a page's rows list in **creation order**. For sermons that means the report will read **"All Sermons" first, then the 2 new rows** — while the registry docstring promises *"order defines the admin list order"* and the page order is hero → browse → grid.

Option (a) — recommended: make the list follow **registry (page) order** with an admin-level ordering only (no migration):

```python
# BaseSectionsAdmin.get_ordering — order rows by their registry position for this page
Case(*[When(key=k, then=Value(i)) for i, k in enumerate(page_keys)], output_field=IntegerField())
```

- Applies to all groups; for every page except Sermons the visible order is unchanged (they already match). It future-proofs new sections to appear in their proper position instead of being appended.
Option (b): leave creation order as-is (zero risk, sermons list order differs from the page).

---

## 4. Exact changes (implementation preview)

| File | Change |
|---|---|
| `content/sections_registry.py` | Sermons block +2 tuples; Contact +1 tuple; *(Prayer +1 if D3)* |
| `website/src/pages/sermons.astro` | 2 new gates |
| `website/src/pages/contact.astro` | 1 new gate |
| `website/src/pages/prayer.astro` | 1 new gate *(if D3)* |
| `content/admin.py` | `get_ordering` via registry position *(if D2a)* — no migration |
| **migrations** | **none** |
| `docs/B5_3_*.md`, `MEMORY.md` | results + memory entry after validation |

**Unchanged:** models, API (`/api/sections` shape), `sections.ts`, other pages, existing DB rows, URLs.

---

## 5. Implementation steps

1. `sections_registry.py` — add the new tuples (§3.1; +prayer per D3).
2. `sermons.astro` — wrap the 2 blocks; `contact.astro` — wrap the block; *(prayer.astro per D3)*.
3. *(If D2a)* `admin.py` — `get_ordering` in `BaseSectionsAdmin`.
4. Restart Django (admin changes need it); trigger `ensure_registered()` via `/api/sections`.
5. Run verification (§6), then update docs/MEMORY.

---

## 6. Verification plan

1. `manage.py check` clean; `makemigrations content --check` → **"No changes detected"** (no migration, no drift).
2. `ensure_registered()` (double-call) → sermons = **3** rows, contact = **2** (*prayer = 2*); all enabled; pre-existing rows (`sermons-grid`, contact/prayer `page-hero`) preserved with their states.
3. Admin: Sermons card lists 3 rows (order per D2), Contact card 2, *(Prayer 2)*; all 9 changelists HTTP 200; other groups unchanged.
4. API: `/api/sections` → `sermons` 3 keys, `contact` 2, *(prayer 2)*; total **34** (35).
5. Live E2E `/sermons` (unique markers): all 3 present → disable `page-hero` → `Latest sermon` 1→0, other 2 intact → disable `browse-by-series` → `Browse by Series` 1→0 → restore → byte-exact baseline.
6. Live E2E `/contact`: `Social Media` + `Send Message` present → disable `contact-details` → both 1→0, hero `Contact Us` intact → restore.
7. *(If D3)* Live E2E `/prayer`: disable `prayer-form` → `Share what you'd like us to pray for` 1→0, hero intact → restore.
8. All-off per page: `/sermons` (3 off) and `/contact` (2 off) still HTTP 200 with header/nav/footer intact → restore.
9. Regression: all 9 pages HTTP 200; `astro check` same file set/totals as previous run (13 files, 35/0/17); 34(35)/34(35) keys enabled at rest.

### 6.1 Results (2026-09-26)

| # | Check | Evidence |
|---|-------|----------|
| 1 | System check / drift | ✅ `manage.py check` clean; `makemigrations content --check` → **"No changes detected"** (no migration, no drift) |
| 2 | Registry & rows | ✅ registry = **35** keys; rows 35; double-call idempotent; sermons = 3, contact = 2, prayer = 2 — pre-existing rows preserved |
| 3 | Admin | ✅ all 9 changelists HTTP 200; **row order = registry order everywhere** (`cl.result_list` verified): sermons `Page Hero → Browse by Series → All Sermons`, contact `Page Hero → Contact Details & Form`, prayer `Page Hero → Prayer Form`; give/visit/about/events/series/homepage orders unchanged |
| 4 | API | ✅ `/api/sections` → sermons 3, contact 2, prayer 2; total **35**; flags all true at rest |
| 5 | Live E2E `/sermons` | ✅ disable `page-hero` + `browse-by-series` → `Latest sermon` 1→0, `Browse by Series` 1→0, `All Sermons` stays 1; restore → baseline |
| 6 | Live E2E `/contact` | ✅ disable `contact-details` → `Social Media` 1→0, `Send Message` 1→0, hero `Contact Us` stays 1; restore → baseline |
| 7 | Live E2E `/prayer` | ✅ disable `prayer-form` → form marker 1→0, hero stays 1; restore → baseline |
| 8 | All-off per page | ✅ 7 toggles off → `/sermons` HTTP 200, all 3 markers 0, chrome intact (logo/nav/footer); restore → 0 disabled |
| 9 | Regression | ✅ all 9 pages HTTP 200; `astro check` no new diagnostics vs previous run; 35/35 keys enabled at rest |

**E2E detail:** during the disable phase the API served `{'page-hero': False, 'browse-by-series': False, …}` per page — flags and rendered output matched exactly.

---

## 7. Risks & mitigations

- **Non-destructive:** registry additions + SSR gates only; nothing deleted; existing rows and toggle states preserved.
- **No migration:** no model/field/choices change — verified plan-wise; re-verified at implementation (`makemigrations --check`).
- **Sermons hero is bespoke & hardcoded** (image, "Pst Charles Muchemi", "Emotional Intelligence", self-link to `/sermons`). This change only makes it *hideable*; CMS-ifying its content is separate work (see §8). Disabling it hides a full-width banner on the sermons page — intended admin power.
- **Marker discipline:** E2E markers were verified unique against live HTML (§2), so disable/restore assertions are exact (no footer/nav false positives).
- **Admin ordering (D2a):** implemented at the ModelAdmin level only (`get_ordering`) — no Meta change, no migration. Validated by checking sermon order + unchanged order on the other 8 groups.

---

## 8. Out of scope (noted, not included)

- CMS-ification of the sermons hero content (hardcoded latest-sermon name/title/link).
- Renaming/visual redesign of any section.
- Gating inside components (e.g. hero/footer are chrome, not page sections).
- B5 R2 media/image uploads — still deferred (separate approval).

---

## 9. Decisions

| | Decision | Resolution (approved 2026-09-26) |
|---|---|---|
| **D1** | Contact block naming (key `contact-details`) | ✅ **"Contact Details & Form"** |
| **D2** | Admin list order | ✅ **Registry/page order** via `BaseSectionsAdmin.get_ordering` (Case over registry position) — no migration; verified on all 9 groups |
| **D3** | Prayer page (same gap found) | ✅ **Included** — `prayer-form` / "Prayer Form" |
| **D4** | Sermons hero title | ✅ **"Page Hero"** |
| — | Sermons: add "Page Hero" + "Browse by Series" | ✅ Done (1 → 3) |
| — | No migrations (B5.2 rule) | ✅ Enforced — `makemigrations --check` clean |

---

## 10. Approval checklist

- [x] Sermons: add Page Hero + Browse by Series (1 → 3 sections)
- [x] Contact: add the missing 2nd section (1 → 2)
- [x] **D1** Contact section title: "Contact Details & Form"
- [x] **D2** Admin ordering: registry order
- [x] **D3** Prayer page: included
- [x] **D4** Sermons hero title: "Page Hero"
- [x] **No migrations** confirmed
- [x] **Implementation completed (2026-09-26)** — see §6.1

