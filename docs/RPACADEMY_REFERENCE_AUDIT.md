# RPACADEMY REFERENCE AUDIT — Simple List

**Reference:** `rpacademy` (Next.js / Prisma)
**Current:** `rp` (Astro / Django)
**Purpose:** Design ideas only — replicate the *look/UX* by building from scratch in Astro + Django. Nothing is migrated or implemented until approved.

---

## A. UI Components (Design to Rebuild in Astro + Tailwind)

### 1. Flashcard Deck Viewer
- **What it does:** Study cards with a 3D flip animation (front/back), shuffle button, prev/next navigation, and a progress meter showing "3 of 10 · 30%".
- **Relevant files:**
  - `rpacademy/apps/academy/components/flashcards/flashcard-card.tsx`
  - `rpacademy/apps/academy/components/flashcards/flashcard-deck-view.tsx`
  - `rpacademy/apps/academy/app/flashcards/page.tsx`
- **Replicate in rp:** Astro component + small vanilla JS for the flip state; CSS `perspective`/`rotateY` for the 3D effect. Page would fit at `/academy/resources/flashcards` (sidebar link already exists).
- **Dependencies:** None (CSS/JS only).

### 2. Module Catalog with Filter Chips
- **What it does:** Grid of module cards with clickable pill filters at the top — filter by Pillar (Identity / Authority / Execution) and by Difficulty (Beginner / Intermediate / Advanced).
- **Relevant files:**
  - `rpacademy/apps/academy/components/modules/module-catalog.tsx`
  - `rpacademy/apps/academy/components/module/module-card.tsx`
- **Replicate in rp:** Astro page with filter buttons + vanilla JS client-side filtering; restyle `AcademyModuleCard.astro` to include a pillar badge, difficulty label, and enrollment count.
- **Dependencies:** Needs `pillar` and `difficulty` fields on the module data (Django model or fixture).

### 3. Student Dashboard KPI Cards
- **What it does:** 4 glass-gold cards showing big numbers — Lessons Completed, Quizzes Passed, Active Modules, Certificates.
- **Relevant files:**
  - `rpacademy/apps/academy/components/dashboard/stats-cards.tsx`
  - `rpacademy/apps/academy/app/dashboard/page.tsx`
- **Replicate in rp:** Astro grid of 4 stat cards using the existing `glass-gold` class in `academy.astro`; numbers come from Django aggregation endpoints.
- **Dependencies:** None for layout; data from Django.

### 4. Timed Quiz Interface
- **What it does:** One question per screen, progress bar at top, optional countdown timer (auto-submits on expiry), attempt counter ("Attempt 1 of 3"), MCQ / True-False / Short-Answer question types, pass/fail result screen, retake button.
- **Relevant files:**
  - `rpacademy/apps/academy/components/quiz/quiz-interface.tsx`
  - `rpacademy/apps/academy/components/quiz/quiz-timer.tsx`
  - `rpacademy/apps/academy/app/modules/[slug]/quiz/page.tsx`
- **Replicate in rp:** Astro page for the shell + a client island (React or vanilla JS) for the interactive flow. Question data from Django `Quiz`/`Question` models.
- **Dependencies:** `Quiz`, `Question`, `QuizAttempt` models in Django.

### 5. Lesson Player Layout
- **What it does:** 3-column layout — left sidebar with the lesson list (locked/unlocked states), center video/content pane, "Mark Complete" button, prev/next navigation.
- **Relevant files:**
  - `rpacademy/apps/academy/app/modules/[slug]/lessons/[lessonSlug]/page.tsx`
  - `rpacademy/apps/academy/components/lesson/lesson-sidebar.tsx`
  - `rpacademy/apps/academy/components/lesson/video-player.tsx`
  - `rpacademy/apps/academy/components/lesson/complete-lesson-button.tsx`
- **Replicate in rp:** Astro page under `/academy/modules/[slug]/lessons/[lessonSlug]` using the existing `AcademySidebar` pattern; lock icons for lessons not yet completed.
- **Dependencies:** `Lesson`, `LessonCompletion` models in Django.

### 6. Progress Bar (animated)
- **What it does:** Rounded fill bar that animates from 0 to the target percentage on load.
- **Relevant files:** `rpacademy/apps/academy/components/module/progress-bar.tsx`
- **Replicate in rp:** Pure CSS width transition (no framework needed) — reuse the existing progress bar markup in `academy.astro`.
- **Dependencies:** None.

### 7. Certificate PDF Design
- **What it does:** Royal Priesthood themed certificate — gold double border, Cinzel-style title, "This certifies that…", student name, module title, instructor, issue date, scripture (1 Peter 2:9), verification code.
- **Relevant files:**
  - `rpacademy/apps/academy/components/certificate/certificate-pdf.tsx`
  - `rpacademy/apps/academy/app/api/certificates/[code]/pdf/route.ts`
- **Replicate in rp:** Django renders an HTML print template (Cinzel font already loaded) or a server-side PDF; unique verification code generated in Python.
- **Dependencies:** `Certificate` model in Django; optional `reportlab`/`weasyprint`.

### 8. Certificate Verification Page
- **What it does:** Public page — anyone entering a code can verify a certificate's authenticity (shows name, module, issue date).
- **Relevant files:** `rpacademy/apps/academy/app/verify/[code]/page.tsx`
- **Replicate in rp:** Astro route `/academy/verify/[code]` calling a public Django endpoint.
- **Dependencies:** `Certificate` model.

### 9. Instructor Analytics Charts
- **What it does:** Enrollment trend line chart (30 days), lesson completion rate bar chart, and stat cards for enrolled/completed counts.
- **Relevant files:**
  - `rpacademy/apps/academy/components/instructor/analytics-charts.tsx`
  - `rpacademy/apps/academy/components/instructor/module-analytics.tsx`
  - `rpacademy/apps/academy/app/api/analytics/route.ts`
- **Replicate in rp:** Astro component with Chart.js (CDN) or hand-drawn SVG bars; data from a Django aggregation endpoint. Fits the existing `/academy/performance` sidebar link.
- **Dependencies:** None beyond Django endpoints.

### 10. Instructor Dashboard Stat Cards
- **What it does:** 3-card row — My Modules, Total Enrollments, Completions — plus a quick-actions button and module list.
- **Relevant files:** `rpacademy/apps/academy/app/instructor/page.tsx`
- **Replicate in rp:** Same card pattern as the student dashboard; gated by an instructor role check.
- **Dependencies:** Instructor role flag; Django queries.

---

## B. Features / Logic (To Rebuild Server-Side in Django)

### 11. Lesson Prerequisite Locking
- **What it does:** Lesson N is locked until Lesson N-1 is marked complete.
- **Relevant files:** `rpacademy/apps/academy/lib/academy-data.ts` (`getLessonAccess`)
- **Replicate in rp:** Check `LessonCompletion` in the Django view before returning lesson content.
- **Dependencies:** `LessonCompletion` model.

### 12. Quiz Attempt Limits & Pass Logic
- **What it does:** Enforces `maxAttempts` (default 3), computes score vs `passingScore` (default 70), locks quiz after max attempts, blocks retake once passed.
- **Relevant files:** `rpacademy/apps/academy/components/quiz/quiz-interface.tsx`
- **Replicate in rp:** Django view validates attempts and computes pass/fail on submit.
- **Dependencies:** `QuizAttempt` model.

### 13. Biblical Pseudonym Leaderboard
- **What it does:** Privacy-preserving leaderboard — users get pseudonyms like "RoyalPriest247" with generated avatar colors, points, badges (Newcomer/Dedicated/Scholar/Master), and streaks.
- **Relevant files:** `rpacademy/packages/shared/src/data/leaderboard.ts`
- **Replicate in rp:** Python utility in `accounts` app; leaderboard list on an Astro page.
- **Dependencies:** None (optional feature).

### 14. Verification Code Generator
- **What it does:** Generates codes like `RPA-AB3CD9XK` using a readable alphabet (no ambiguous characters).
- **Relevant files:** `rpacademy/apps/academy/lib/utils.ts` (`generateVerificationCode`)
- **Replicate in rp:** ~5-line Python function in `accounts` or `content` services.
- **Dependencies:** None.

---

## C. Content / Data (Seed Material, Port as Django Fixtures)

### 15. 12 Discipleship Modules
- **What it does:** Complete curriculum — Sonship & Identity, Ministry of the Word, Foundations of Prayer, Sensitivity to the Spirit, Spiritual Gifts, Dominion through Partnership, Art of Priesthood, Spiritual Warfare, Soul Winning & Evangelism, Worship & Devotion, Kingdom Stewardship, Consecration & The High Call (titles, descriptions, instructors, durations).
- **Relevant files:** `rpacademy/packages/shared/src/data/modules.ts`
- **Replicate in rp:** JSON fixture for the existing `WebsiteAcademyModule` table.
- **Dependencies:** None.

### 16. Flashcard Question Bank
- **What it does:** ~80 front/back study cards across the 12 modules, categorised (Identity, Word, Prayer, etc.).
- **Relevant files:** `rpacademy/packages/shared/src/data/flashcards.ts`
- **Replicate in rp:** JSON fixture for `Flashcard`/`FlashcardDeck` tables.
- **Dependencies:** `FlashcardDeck`, `Flashcard` models.

### 17. Quiz Question Bank
- **What it does:** Pre-written MCQ / True-False / Short-Answer questions with correct answers and explanations.
- **Relevant files:** `rpacademy/packages/shared/src/data/modules.ts` (embedded quizzes)
- **Replicate in rp:** JSON fixture for `Quiz`/`Question` tables.
- **Dependencies:** `Quiz`, `Question` models.

---

## Not Needed / Skip
- Next.js App Router / Route Handlers — replaced by Astro pages + Django views.
- Prisma / Turso — replaced by Django ORM.
- GSAP landing animations — rp has its own motion system.
- rpacademy theme tokens (`glass-frost`, `glass-dark`) — rp has its own `glass-gold` theme.

---

**AUDIT COMPLETE.** Reference only — no changes implemented. Awaiting approval.

