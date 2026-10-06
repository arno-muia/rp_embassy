# B5.4 (v2) — About Page Group: Per-Section Content Components

**Status:** SUPERSEDED (2026-09-28) by **B5.5** (`docs/B5_5_ABOUT_SECTION_MODELS_PLAN.md`) —
the three SystemConfig JSON proxy editors (`AboutIntroConfig` / `AboutValuesConfig` /
`AboutThemeConfig`) were replaced by dedicated, admin-managed models. The card-grouping
machinery (`PAGE_CONTENT_GROUPS`) introduced here remains in place.
**Original status line (kept for history):** PLAN — AWAITING USER APPROVAL.
**Date:** 2026-09-26
**Supersedes:** v1 ("Option 3" — WebsiteLeader-only move), which was implemented and then
**fully reverted on user instruction**: *"NO. Not that way. ... Study how the sections have
been added under the Homepage and Prayer groups ... come up with a plan."*

---

## 1. Revert record (v1 → nothing left behind)

All Option-3 changes were reverted and verified on 2026-09-26:

| Item | Status |
|---|---|
| `content/admin.py` docstring, `PAGE_CONTENT_GROUPS`, content-extraction block, injection rewrite | Reverted — lines 42–161 byte-identical to the pre-v1 read; `grep` = **0** "B5.4"/`PAGE_CONTENT_GROUPS` markers |
| Temp script `RP/admin_b54_check.py` | Deleted |
| `manage.py check` | Clean ("No issues") |
| `makemigrations content --check` | "No changes detected" |
| DB / API / frontend / live server | Never touched by v1 (server was never restarted with v1 code) |

v1's flaw: it put **only `WebsiteLeader`** under About. The requirement is one admin entry
**per About section** (its content components), like the Homepage/Prayer cards.

---

## 2. Goal

About card lists each of the 4 About sections with its manageable component, in page order,
with the existing `Sections` toggle **last** — mirroring the Homepage and Prayer cards.

---

## 3. Binding constraints (this task)

1. **`ChurchProfile` untouched** — not grouped, not wired (user will remove it later).
2. **No DB schema change** — no tables/columns; proxy-model *state* migration only (⇒ decision **D4**).
3. **No API contract changes**; frontend edits limited to what decision **D2** selects.
4. **No data loss** — edits must merge into `SystemConfig('site').value`, never clobber sibling keys.
5. `SiteSection` registry & `/api/sections` (35 keys) unchanged.

---

## 4. Study — how the Homepage group manages each section

Homepage card (`HOMEPAGE_GROUP`, admin.py:55–64) = **one admin entry per registry section**
(sections_registry.py:21–28), built by extracting models from their app cards into a synthetic
card; `HomepageSections` toggle renders **last**:

| Registry section | Card entry | Mechanism | Admin scoping |
|---|---|---|---|
| `hero` | Hero Section (`HeroSectionConfig`) | **Proxy over `SystemConfig`**, same table, `key='site'` (models.py:50) | `get_queryset → filter(key='site')`; add/delete disabled; fieldset explains the JSON (admin.py:291–322) |
| `service-times` | ServiceTimes (`ServiceTime`) | Dedicated table, 1 row/service | `list_editable` order/publish; sectioned fieldsets |
| `upcoming-events` | HomepageUpcomingEvents (`HomepageUpcomingEvent`) | **Proxy over `ChurchEvent`** | Read-only admin filtered to homepage-eligible events (events/admin.py:39) |
| `latest-sermon` | Latest Sermon (`HomepageLatestSermon`) | **Proxy over `PublicSermon`** (migration 0016 — proxy precedent!) | Queryset limited to the single latest record (admin.py:381) |
| `testimonials` | Website testimonials (`WebsiteTestimonial`) | Dedicated table | `sort_order`/`is_published` list_editable |
| `pastor-profile` | Pastor Profiles (`PastorProfile`) | Dedicated singleton | `clean()` enforces one active |
| `what-to-expect` | — (absent) | site-blob only | Gap: raw `SystemConfig` admin only |
| `cta-banner` | — (absent; `HomepageSettings` sits in "Public Website Content") | Dedicated table, NOT carded | Precedent: the card covers sections, not every table |
| (visibility) | `HomepageSections` | Proxy over `SiteSection` | **Toggle last** |

**Recipe:** each section gets a *section-scoped admin entry* — dedicated table, **or proxy over
an existing table** (no duplicate storage), or a read-only/limited view — plus the toggle last.

## 5. Study — how the Prayer group does it

| Entry | Mechanism | Role |
|---|---|---|
| PrayerRequests (`PrayerRequest`) | Dedicated table, full ModelAdmin (prayer/admin.py:6) | Moderated content rows — individually managed |
| PrayerSubmissions (`PrayerSubmission`) | Dedicated table, full ModelAdmin (prayer/admin.py:19) | Incoming form data — individually managed |
| `PrayerSections` | Proxy over `SiteSection` | Toggle, **last** |

Note: Prayer's `page-hero` section has **no** component — an entry exists where content is
manageable; not every section is forced to have one.

---

## 6. Study — About page's 4 sections (live evidence)

| # | Registry key / title (registry:30–33) | Rendered in `about.astro` | Live data source | Manageable today? |
|---|---|---|---|---|
| 1 | `intro` — "Welcome, Vision & Mission" | **35–58, fully hardcoded** (h1 "Welcome to the Embassy", vision & mission quotes) | `SystemConfig('site').welcomeMessage {title,message,author?}` — served by `/api/site-config`, typed as `SiteConfig.welcomeMessage` (api.ts:382) but **never read by the page**; `ChurchProfile` excluded | ❌ |
| 2 | `values` — "Our Values" | 60–81 → `config.values` | `'site'.values` — **live DB: list, len 3** | Only via raw JSON in the SystemConfig card |
| 3 | `leadership` — "Leadership Team" | 83–123 → `getWebsiteLeaders()` | `WebsiteLeader` rows (wired API ✓) | ✅ Admin exists — but misfiled in "Public Website Content" |
| 4 | `theme-2026` — "2026 Theme" | 125–145 → `config?.theme2026 ?? site` fallback | `'site'.theme2026` — **live DB: dict** `{title, scripture, scriptureText, image}` | Only via raw JSON in the SystemConfig card |

Live-DB probe (read-only, 2026-09-26): `'site'` keys include `welcomeMessage`, `values`,
`theme2026`; `values` len 3; separate `key='welcomeMessage'` row exists (unused by Astro).
Seed parity: `site.json` `welcomeMessage.title` = **"Welcome to the Embassy"** and `message`
= the exact paragraph hardcoded in `about.astro` → intro can be wired with **content parity**.

---

## 7. Proposed About card (page order, toggle last)

```
About   (synthetic card — already created by the AboutSections toggle)
├─ Welcome, Vision & Mission   AboutIntroConfig    NEW proxy over SystemConfig 'site'  [D2]
├─ Our Values                  AboutValuesConfig   NEW proxy over SystemConfig 'site'
├─ Leadership Team             WebsiteLeader       moved from "Public Website Content"
├─ 2026 Theme                  AboutThemeConfig    NEW proxy over SystemConfig 'site'
└─ Sections                    AboutSections       existing toggle — ALWAYS LAST
```

`ChurchProfile` remains in "Public Website Content" (untouched, per user).

---

## 8. Design

1. **Proxies** (models.py): 3 new proxy models over `SystemConfig` — exact precedent:
   `HeroSectionConfig` (models.py:50) + proxy migration precedent `0016_add_homepage_latest_sermon_proxy`.
   Same table, **zero duplicate storage, zero DDL**.
2. **Per-section ModelAdmins** (admin.py), mirroring `HeroSectionConfigAdmin`:
   `get_queryset → filter(key='site')`, add/delete disabled (single row), verbose names =
   registry titles so card entries mirror the `Sections` list.
3. **Subfield forms [D3-A]**: each admin exposes **only its section's JSON subkey**
   (`welcomeMessage` / `values` / `theme2026`) as a `JSONField` on a `ModelForm`.
   `save()` = fresh-read row → dict-merge the subkey → `save(update_fields=['value','updated_at'])`
   → sibling keys never clobbered. Fieldset description warns about shared-row concurrency
   and points to raw `SystemConfig` as the escape hatch.
4. **Grouping machinery**: reinstate v1's generalized extraction/injection (the *machinery*
   was sound; only the scope was wrong) — `PAGE_CONTENT_GROUPS = [('about', 'About',
   [('AboutIntroConfig','content'), ('AboutValuesConfig','content'),
   ('WebsiteLeader','content'), ('AboutThemeConfig','content')])]`, extracted before toggles;
   card = content entries (page order) + `AboutSections` last; safety-net loop retained so an
   extracted model can never vanish from the index.
5. **Intro wiring [D2-A] — the ONLY frontend change**: `about.astro` intro reads
   `config?.welcomeMessage?.title ?? "Welcome to the Embassy"` and
   `config?.welcomeMessage?.message ?? <current paragraph>`; eyebrow/labels stay hardcoded.
   Fallback = today's exact copy ⇒ rendering identical until an admin edits.
   `values`/`theme-2026` need **no frontend change** — the page already reads those keys, so
   their proxies are effective immediately.

---

## 9. Decisions requiring approval

| # | Decision | Options | Recommendation |
|---|---|---|---|
| **D1** | Mechanism for values/theme/intro | **A.** Proxies over `SystemConfig 'site'` (HeroSectionConfig precedent; no API change) · **B.** `ContentBlock` VALUE/THEME rows (matches B4 design docs; needs API + page rework; per-item CRUD) · **C.** New dedicated tables (largest; real DDL) | **A** for this task; B/C remain the documented CMS-evolution path |
| **D2** | Intro section | **A.** Wire `welcomeMessage` with hardcoded fallback (1 frontend edit, content parity verified) · **B.** Admin entry only — page stays hardcoded (edits would not appear ⇒ misleading) · **C.** Omit intro (card covers 3 of 4 sections) | **A** |
| **D3** | Edit form style | **A.** Per-section subfield JSON editor (true per-section editing) · **B.** Whole-blob textarea + guidance (exact HeroSectionConfig behavior) | **A** |
| **D4** | Migration | Accept state-only `content.0018` (CreateModel proxy ×3; `sqlmigrate` = no SQL; precedent 0016). Supersedes the B5.2/B5.3 zero-migration rule *for this task* | **Accept** |

## 10. Files

**Changed (on approval):** `content/models.py` (+3 proxies) · `content/migrations/0018_*`
(auto-generated, state-only) · `content/admin.py` (3 ModelAdmins + subfield forms, grouping
machinery) · `website/src/pages/about.astro` (D2-A only) · this doc · `MEMORY.md`.

**Untouched:** `views.py`/`urls`/`serializers` · `sections_registry.py`/`SiteSection` ·
`ChurchProfile` · DB schema and all other SystemConfig keys · the other 12 admin cards ·
`SystemConfigAdmin` (raw escape hatch stays).

## 11. Verification plan (GET-only unless noted)

1. `manage.py check` · `makemigrations content` → 0018 · `sqlmigrate content 0018` → **no SQL**
   · `migrate` (state only).
2. Restart Django; admin index: About card == exactly the 5 entries in §7 order;
   `WebsiteLeader` gone from "Public Website Content"; `ChurchProfile` still there;
   Homepage=7, Events=4, Prayer=3, 12 toggle-only cards unchanged; 13 cards total; Homepage first.
3. Each proxy changelist + change form → 200; `WebsiteLeader` changelist → 200 under About.
4. Merge logic: shell test (no commit) — submit a form with only `values` changed; assert
   sibling keys (`theme2026`, `welcomeMessage`, …) survive unchanged.
5. API: `/api/site-config` shape unchanged · `/api/sections` == 35 keys · all 9 pages HTTP 200 ·
   `npm run build` passes.
6. Visual parity: About page identical pre/post D2-A while DB copy == current hardcoded copy;
   first real content edit left to the user as a manual smoke test.

## 12. Risks

- **Shared-row concurrency:** two admins saving different subkeys simultaneously →
  last-write-wins; mitigated by fresh-read merge + `update_fields`. Theoretical at single-admin scale.
- **Raw `SystemConfigAdmin`** edits can overwrite subkeys (already true today) — fieldset warning.
- **Copy drift:** if DB `welcomeMessage` ≠ page copy at wiring time → align once via admin (step 6).
- **JSON UX** is array/dict editing, not row CRUD — D1-B is the future upgrade path.

## 13. Out of scope / roadmap (separate approvals)

Other page groups (Sermons → PublicSermon/SermonSeries · Series shared-card decision ·
Visit → VisitRsvp · Contact → ContactSubmission · Partner → none) · Homepage gaps
(`what-to-expect`, `cta-banner`/`HomepageSettings` carding) · ContentBlock evolution (D1-B) ·
`ChurchProfile` removal (user).


