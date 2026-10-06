# B5.7 — Visit Sections: Dedicated Models (admin-managed content components)

**Status:** ✅ IMPLEMENTED & VERIFIED — 2026-09-29 (plan approved by the user; mirrors the B5.5 About pattern exactly)

---

## 1. Goal

Each individual section under the admin's **Visit** group holds *all* of its rendered
components as real, labelled fields — so every title, text, label, map URL and FAQ row on
the Visit page is managed from the admin panel, with no code edits.

## 2. What the admin now shows (Visit group, page order)

| Entry | Model | Management |
|---|---|---|
| Page Hero | `VisitHero` (one record) | title, subtitle, scripture, variant (`warm` / `celestial` / `parchment`) |
| Location & Map | `VisitLocation` (one record) | eyebrow, title, description, button label + URL, map embed URL + iframe title |
| What to Expect | `VisitExpectSection` + inline `VisitExpectStep` rows | eyebrow, title; each card's step / description / icon (`music`, `book-open`, `users`, `trending-up`) / order / published |
| FAQs | `VisitFaqSection` + inline `VisitFaq` rows | heading; each row's question / answer / order / published |
| RSVP Form Copy | `VisitRsvpSection` (one record) | heading, subheading, submit label, success title + message (copy only — **not** submissions) |
| RSVP submissions | `VisitRsvp` | unchanged — existing form-submission list |
| I Am Coming This Sunday | `VisitComingSunday` (one record) | title, description, button label + URL |
| Sections | `VisitSections` | unchanged — enable/disable each Visit section |

## 3. Data flow

```
Admin (Visit group) → PostgreSQL tables
    content_visithero · content_visitlocation · content_visitexpectsection(+steps)
    content_visitfaqsection(+faqs) · content_visitrsvpsection · content_visitcomingsunday
        → GET /api/visit  {hero, location, expect{eyebrow,title,items[]},
                           faqs{title,items[]}, rsvp, comingSunday}
            → visit.astro (fallbacks = the original hardcoded copy when the API is unreachable)
```

- `/api/visit` returns each section as `null` when its record has not been created;
  only **published** steps/FAQ rows are returned, ordered by `sort_order`.
- Singleton sections are ordered `-updated_at` — the **most recently updated** record wins,
  so the latest admin edit is always what the page shows (same as B5.5).
- Section on/off remains the existing **Sections** toggles (`/api/sections`); no duplicate
  switches. `/api/site-config` is unchanged (its `visitFaqs` subkey stays as fallback data).
- Service times on the Visit page remain shared via `/api/homepage` (no duplicate model).

## 4. Decisions (from approved plan)

| # | Decision |
|---|---|
| D1 | **Dedicated models** mirroring B5.5 — rejected editing SystemConfig 'site' JSON |
| D2 | Toggles stay on the `VisitSections` proxy — new models hold content only |
| D3 | Seed FAQs from the live `SystemConfig['site']['visitFaqs']` (real data), SystemConfig never modified |
| D4 | Existing `VisitRsvp` (form submissions) untouched; `VisitRsvpSection` holds form copy only |
| D5 | No add/delete restrictions — latest-record-wins rendering |
| D6 | RSVP copy = heading, subheading, submit label, success title + message |

## 5. Data seeding (zero visual change)

Migration `content.0021` creates the schema; `content.0022` seeds every record from the
previously hardcoded page copy (hero, location incl. Google Maps embed, 4 expect steps with
icons, RSVP copy, coming-sunday CTA) plus the 8 FAQs from live `SystemConfig 'site'`
→ `visitFaqs`. Both are reversible (reverse deletes only the seeded rows); `SystemConfig`
is never modified.


## 6. Files changed

**Backend — `RP/backend/backend/apps/content/`**

| File | Change |
|---|---|
| `models.py` | +`VisitHero`, +`VisitLocation`, +`VisitExpectSection`, +`VisitExpectStep` (+`VisitExpectStepIcon`), +`VisitFaqSection`, +`VisitFaq`, +`VisitRsvpSection`, +`VisitComingSunday` |
| `migrations/0021_visit_section_models.py` | schema (auto-generated) |
| `migrations/0022_visit_seed_content.py` | data seed from live copy (reversible) |
| `admin.py` | 6 new admins (TabularInlines for steps/FAQ rows); Visit card registry updated (`VisitHero → VisitLocation → VisitExpectSection → VisitFaqSection → VisitRsvpSection → VisitRsvp → VisitComingSunday`) |
| `repositories.py` | +`VisitContentRepository` (`hero`, `location`, `expect_section`, `published_steps`, `faq_section`, `published_faqs`, `rsvp_section`, `coming_sunday`) |
| `serializers.py` | +6 read serializers |
| `views.py` | +`visit_page` |
| `urls.py` | +`/api/visit` |

**Frontend — `RP/website/`**

| File | Change |
|---|---|
| `src/lib/api.ts` | +`visit` endpoint, Visit content types, `getVisit()` (text-only — no media fields, so no `resolveMediaUrl` needed) |
| `src/pages/visit.astro` | all six sections read the new endpoint (original hardcoded copy as fallback); location eyebrow/title/button/map fields, per-card icon from the model, FAQ heading from the model |
| `src/components/forms/RsvpForm.astro` | optional props `heading`, `subheading`, `submitLabel`, `successTitle`, `successMessage` (defaults = original copy); submit-button error path restores the admin-set label |

## 7. Verification results

1. `manage.py check` → **No issues**; migrations `0021` + `0022` applied.
2. Seeded records verified via shell: hero=1 (`You're Welcome Here` / `warm`),
   location=1 (`Find Us` / `Visit Us in Thika` + Google Maps embed), expect section=1 +
   4 steps, faq section=1 + 8 FAQs, rsvp copy=1, coming-sunday=1.
3. `GET /api/visit` → 200 with all six keys (`hero`, `location`, `expect{items:4}`,
   `faqs{items:8}`, `rsvp`, `comingSunday`); Django Test Client also 200.
4. Admin: all 6 models registered (verified in `admin.site._registry`), grouped under the
   **Visit** card next to the existing RSVP submissions + Sections toggles.
5. Live-edit test: updated `VisitHero.title` in the DB → `/visit` rendered
   `[B57-EDIT]` on the next request → reverted → original copy restored.
6. `http://localhost:4321/visit` → **200**, all six sections render from the API;
   regression `/`, `/about`, `/sermons`, `/events` → **200**.
7. `astro check` → clean.

## 8. Notes / follow-ups

- The `VisitSections` toggles and `/api/sections` registry are untouched — content models
  and visibility switches stay decoupled exactly as in B5.5.
- `RsvpForm` keeps working standalone (props optional with original defaults) in case it is
  reused on another page later.
- Legacy `SystemConfig['site']['visitFaqs']` remains in the DB as reference/fallback only;
  the admin should edit FAQs via the new **FAQs** inline rows.
