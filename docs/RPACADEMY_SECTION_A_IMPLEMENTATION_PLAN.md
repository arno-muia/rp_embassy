# Section A Implementation Plan — UI Components

This is a **brief plan** for building the 10 Section A items from `RPACADEMY_REFERENCE_AUDIT.md` from scratch in the current `rp` project (Astro + Django). No code is written here — this is the proposed order, scope, and touch-points for review before any work begins.

All constraints from the audit still apply unless explicitly relaxed in a later approval: do not change the existing theme, navbar, sidebar, authentication, or Academy UI. New pages/components are additive only (filling in unimplemented sidebar routes).

---

## Guiding Principles
1. **Astro-first**: server-render pages; use vanilla JS or tiny React islands only where interactivity is unavoidable.
2. **Reuse existing tokens**: `glass-gold`, gold/charcoal palette, Cinzel font, and the existing `AcademyLayout`/`AcademySidebar`/`AcademyHeader` are the source of truth — never import rpacademy's theme.
3. **Backend-agnostic where possible**: hardcode/fixture data first, swap to Django endpoints later — so UI work isn't blocked on schema changes.
4. **Additive only**: new `.astro` pages under `/academy/...` map to sidebar entries that already exist but currently 404. No sidebar edits.

---

## Phase 1 — Pure-Frontend Components (no Django schema change)
These need no new models. Safe to build immediately.

### 1.1 Progress Bar (animated) — Item #6
- **Touches:** new `rp/website/src/components/ui/AcademyProgressBar.astro` (or extend existing bar in `academy.astro`).
- **Approach:** a `<div>` track + inner fill `<div>`; CSS `transition: width 0.6s ease-out`; `width` set from a prop. No JS needed.
- **Reuse:** the dashboard already has a static bar — replace its fill with the animated variant.
- **Dependencies:** none.

### 1.2 Student Dashboard KPI Cards — Item #3
- **Touches:** `rp/website/src/pages/academy.astro` (extend the existing welcome section), optional new `components/ui/StatCard.astro`.
- **Approach:** 4-up grid using `glass-gold`; numbers come from Django `/api/academy` (lessons passed, modules active, etc.). Until endpoints exist, render `—` placeholders.
- **Dependencies:** none (placeholder data first).

### 1.3 Module Catalog with Filter Chips — Item #2
- **Touches:** new `rp/website/src/components/academy/ModuleFilters.astro`, restyle `AcademyModuleCard.astro` to accept `pillar`/`difficulty` badges.
- **Approach:** pill filters at top; client-side `data-pillar` filtering with ~20 lines of vanilla JS. Cards restyled with a small `PillarBadge.astro` sub-component.
- **Dependencies:** needs `pillar` + `difficulty` on module data. **Decision**: store on `WebsiteAcademyModule` (Django columns) OR hold as a static client-side map keyed by module id (no schema change). Recommend static map first to defer the migration.
- **Destination:** `/academy` dashboard OR a future `/academy/modules` page — recommend rendering the catalog on the existing dashboard to avoid adding routes.

---

## Phase 2 — Flashcards (needs model, but small)

### 2.1 Flashcard data model + seed — supports Items #1, #16
- **Backend:** new `FlashcardDeck` + `Flashcard` models in a new `apps.academy` Django app (or extend `content`). Fields: `title`, `description`, `category`, `module_id` (optional), `front`, `back`, `order`.
- **Migration:** one Django migration; seed ~80 cards from `rpacademy/packages/shared/src/data/flashcards.ts` via a `loaddata` fixture (port the TS to JSON).
- **API:** add `GET /api/academy/flashcards` to the existing `AcademyModuleViewSet` router (or a new `FlashcardViewSet`). Protected by `IsAcademyAuthorized`.
- **Dependencies:** new migration, new endpoint.

### 2.2 Flashcard Deck Viewer — Item #1
- **Touches:** new `rp/website/src/pages/academy/resources/flashcards.astro` (sidebar route already exists).
- **Components:** `FlashcardDeckView.astro` + `FlashcardCard.astro`.
- **Approach:** server-render deck list; one card visible; CSS `transform-style: preserve-3d` + `rotateY(180deg)` on flip; vanilla JS toggles `.is-flipped`; prev/next/shuffle in ~30 lines of JS. Progress meter uses the animated progress bar from Phase 1.
- **Dependencies:** Phase 2.1 endpoints.

---

## Phase 3 — Lessons (needs 2 models)

### 3.1 Lesson data model + seed — supports Items #5, #11
- **Backend:** `Lesson` (FK `WebsiteAcademyModule`, `slug`, `title`, `video_url`, `notes`, `order`, `published`) and `Attachment` (`name`, `url`, `type`, FK Lesson).
- **Migration + fixture:** port `LESSONS` from `rpacademy/packages/shared/src/data/modules.ts`.
- **API:** `GET /api/academy/modules/<slug>/lessons`, `GET /api/academy/lessons/<slug>`.
- **Dependencies:** new migration, new endpoints.

### 3.2 Lesson Player Layout — Item #5
- **Touches:** new `rp/website/src/pages/academy/modules/[slug]/lessons/[lessonSlug].astro` + `components/academy/LessonSidebar.astro`, `LessonVideo.astro`, `CompleteLessonButton.astro`.
- **Approach:** 3-column layout — reuse `AcademySidebar` for global nav; add an in-page lesson sidebar with lock/complete badges; center pane renders video + notes + attachments; "Mark Complete" calls a `POST` endpoint (stub returns 200 until enrollments exist).
- **Dependencies:** Phase 3.1 endpoints.

### 3.3 Lesson Prerequisite Locking — Item #11 (server logic)
- **Backend:** in the lesson detail view, look up the previous lesson (by `order`) and its completion for the requesting user; if not complete, return a `locked` flag instead of notes/video.
- **Dependencies:** `LessonCompletion` model — see Phase 5. Until then, lock can be optional/gated behind a feature flag.

---

## Phase 4 — Quizzes (needs 2 models)

### 4.1 Quiz data model + seed — supports Items #4, #12, #17
- **Backend:** `Quiz` (`module_id` 1:1, `passing_score`, `time_limit`, `max_attempts`, `published`), `Question` (`type`, `text`, `options` JSON, `correct_answer`, `explanation`, `order`). Seed from modules.ts `QUIZZES`.
- **Migration + fixture.** `GET /api/academy/modules/<slug>/quiz`.
- **Dependencies:** new migration, new endpoints.

### 4.2 Timed Quiz Interface — Item #4
- **Touches:** new `rp/website/src/pages/academy/modules/[slug]/quiz.astro` + `components/academy/QuizInterface.astro` + `QuizTimer.astro`.
- **Approach:** Astro shell renders questions as a JSON island; a small React island (`client:load`) OR vanilla JS manages current index, answers, timer, submit. Result screen shows pass/fail + retake button.
- **Dependencies:** Phase 4.1 endpoints.

### 4.3 Quiz Attempt Limits & Pass Logic — Item #12 (server logic)
- **Backend:** `POST /api/academy/quizzes/<id>/attempt` — validate `attempts < max_attempts`, score the answers, compute `passed = score >= passing_score`, store a `QuizAttempt` row. Reject if already passed.
- **Dependencies:** `QuizAttempt` model — can stub in Phase 4 and persist later.

---

## Phase 5 — Certificates (needs 1 model)

### 5.1 Certificate model — supports Items #7, #8, #14
- **Backend:** `Certificate` (`enrollment_id` 1:1, `issued_at`, `verification_code` unique, `pdf_url` optional). `generateVerificationCode()` in Python (~5 lines).
- **Dependencies:** ideally an `Enrollment` model — but for a v1 the cert can FK directly to `(user_id, module_id)` to defer enrollments (decision item).

### 5.2 Certificate Verification Page — Item #8
- **Touches:** new `rp/website/src/pages/academy/verify/[code].astro` + public `GET /api/academy/verify/<code>` (no auth).
- **Approach:** Astro page shows cert details or "not found".
- **Dependencies:** Phase 5.1.

### 5.3 Certificate PDF Design — Item #7
- **Touches:** Django view renders an HTML template (Cinzel, gold border, scripture) served as `Content-Type: application/pdf` via `weasyprint`, OR a print-styled HTML page the user prints to PDF.
- **Decision item:** `weasyprint` (extra dep) vs HTML-print-only (no dep). Recommend HTML-print initially, optional `reportlab`/`weasyprint` later.
- **Dependencies:** Phase 5.1.

---

## Phase 6 — Instructor Views (needs role decision)

### 6.1 Role check — supports Items #9, #10
- **Decision:** add `INSTRUCTOR` to `UserRole` OR reuse `ADMIN`/`LEADERSHIP`. Recommend starting with `ADMIN`-only (no schema change) and adding `INSTRUCTOR` later if needed.
- **Backend:** new `IsInstructor` DRF permission mirroring `rpacademy/lib/rbac.ts::canAccessInstructor`.

### 6.2 Instructor Analytics Charts — Item #9 + Instructor Dashboard Stat Cards — Item #10
- **Touches:** new `rp/website/src/pages/academy/performance.astro` (sidebar route already exists) + `components/academy/AnalyticsCharts.astro` + `components/academy/StatCards.astro` (shared with the student KPI cards).
- **Approach:** Chart.js via CDN `<script>` (no install) for the line/bar charts; data from a new `GET /api/academy/analytics?moduleId=...` endpoint mirroring `rpacademy/app/api/analytics/route.ts`.
- **Dependencies:** Phase 6.1 + Enrollment/LessonCompletion models from Phases 3/5 (needed to compute real stats; can stub initially).

---

## Recommended Order
1. **Phase 1** (Progress Bar → KPI Cards → Filter Chips) — ship first, no backend changes.
2. **Phase 2** (Flashcards) — smallest model footprint, biggest visible win; fills the sidebar `/academy/resources/flashcards` link.
3. **Phase 3** (Lessons + locking) — unlocks the core learning flow.
4. **Phase 4** (Quizzes) — completes a module's lifecycle.
5. **Phase 5** (Certificates + verification) — closes the loop.
6. **Phase 6** (Instructor analytics) — optional, requires role decision.

Each phase is independently shippable. Phases 2–5 each introduce a small Django migration; Phase 1 introduces none.

---

## Decisions Needed Before Starting
1. **Pillar/difficulty storage**: new `WebsiteAcademyModule` columns vs. static client-side map (recommend static for Phase 1).
2. **Enrollment model**: introduce now (clean) or defer (certs/enrollments can FK user+module directly for v1).
3. **Quiz client**: React island vs. vanilla JS (recommend vanilla JS for the quiz state machine to keep deps minimal).
4. **Certificate PDF**: HTML-print vs. `weasyprint`/`reportlab` (recommend HTML-print for v1).
5. **Instructor role**: add `INSTRUCTOR` enum value vs. reuse `ADMIN` (recommend `ADMIN` for Phase 6 v1).

---

## Out of Scope (per constraints)
- Modifying `rpacademy`.
- Changing the existing Academy theme, navbar, sidebar, or auth.
- Any work not approved phase-by-phase.

**PLAN COMPLETE. Awaiting approval before implementation.**