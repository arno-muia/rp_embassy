# ASTRO UI MIGRATION INVENTORY

## Executive Summary

Source: `apps/web` (Next.js 14, React, TypeScript, Tailwind, NextAuth, Prisma)  
Target: `RP/website` (Astro, TypeScript, Tailwind, Django REST API)  
Strategy: Islands architecture with server-side rendering, no client-side framework coupling

---

## 1. PAGES INVENTORY

### Public Pages (11 pages)

| Source File | Classification | Rationale | Migration Complexity |
|-------------|----------------|-----------|----------------------|
| `app/(public)/page.tsx` | REWRITE_REQUIRED | Homepage with complex dynamic data fetching from Prisma. Needs complete Astro page structure with fetch to Django API. | HIGH |
| `app/(public)/about/page.tsx` | REWRITE_REQUIRED | Static content page with potential dynamic leader/testimonial data. Different routing paradigm (Next.js segments → Astro file-based). | MEDIUM |
| `app/(public)/academy/page.tsx` | REWRITE_REQUIRED | Dynamic content from Prisma `WebsiteAcademyModule`. Needs API fetch rewrite. | MEDIUM |
| `app/(public)/contact/page.tsx` | REWRITE_REQUIRED | Form page with client-side validation. Needs island component for form submission to `/api/contact`. | MEDIUM |
| `app/(public)/events/page.tsx` | REWRITE_REQUIRED | Dynamic event listing. Prisma query → Django API fetch. | MEDIUM |
| `app/(public)/events/[slug]/page.tsx` | REWRITE_REQUIRED | Dynamic event detail route. Slug-based routing different in Astro. | MEDIUM |
| `app/(public)/give/page.tsx` | DO_NOT_MIGRATE | Giving functionality deferred to Phase 5+ (P3 domain). | N/A |
| `app/(public)/prayer/page.tsx` | REWRITE_REQUIRED | Form page for prayer submission. Needs island for POST to `/api/prayer`. | LOW |
| `app/(public)/series/page.tsx` | REWRITE_REQUIRED | Sermon series listing. Prisma → Django API. | MEDIUM |
| `app/(public)/series/[slug]/page.tsx` | REWRITE_REQUIRED | Series detail with sermons. | MEDIUM |
| `app/(public)/sermons/page.tsx` | REWRITE_REQUIRED | Sermon listing with filtering. | MEDIUM |
| `app/(public)/sermons/[slug]/page.tsx` | REWRITE_REQUIRED | Sermon detail page. | MEDIUM |
| `app/(public)/visit/page.tsx` | REWRITE_REQUIRED | RSVP form page. Needs island for POST to `/api/rsvp`. | LOW |
| `app/(public)/privacy/page.tsx` | REWRITE_REQUIRED | Static legal page. | LOW |
| `app/(public)/terms/page.tsx` | REWRITE_REQUIRED | Static legal page. | LOW |

### Authenticated Pages (5+ pages, deferred)

| Source File | Classification | Rationale | Migration Complexity |
|-------------|----------------|-----------|----------------------|
| `app/(member)/dashboard/page.tsx` | DO_NOT_MIGRATE | Member dashboard requires authentication (Phase 3). | N/A |
| `app/(member)/profile/page.tsx` | DO_NOT_MIGRATE | Member profile requires auth. | N/A |
| `app/(member)/household/page.tsx` | DO_NOT_MIGRATE | Member household requires auth. | N/A |
| `app/(member)/giving-history/page.tsx` | DO_NOT_MIGRATE | Member giving history requires auth + P3 backend. | N/A |
| `app/(member)/discipleship/page.tsx` | DO_NOT_MIGRATE | Discipleship tracking requires auth + LMS backend. | N/A |
| `app/(ops)/admin/page.tsx` | DO_NOT_MIGRATE | Admin ops require authentication + P2 backend. | N/A |

---

## 2. COMPONENTS INVENTORY

### Content Components

| Source File | Classification | Rationale | Dependencies |
|--------------|----------------|-----------|--------------|
| `components/content/event-card.tsx` | REWRITE_REQUIRED | Displays event data from Prisma. Convert to Astro component, data from Django API. | Django API `/api/events` |
| `components/content/sermon-card.tsx` | REWRITE_REQUIRED | Displays sermon data from Prisma. Convert to Astro component. | Django API `/api/sermons` |
| `components/content/faq-accordion.tsx` | COPY_WITH_MINOR_CHANGES | Pure UI component (collapsible). Minimal changes to remove React hooks if any. | None |

### Form Components

| Source File | Classification | Rationale | Dependencies |
|--------------|----------------|-----------|--------------|
| `components/forms/contact-form.tsx` | REWRITE_REQUIRED | Form with validation and submission. Requires client-side JavaScript. Implement as Astro island with fetch to `/api/contact`. | Django API `/api/contact` |
| `components/forms/prayer-form.tsx` | REWRITE_REQUIRED | Form with validation. Astro island with POST to `/api/prayer`. | Django API `/api/prayer` |
| `components/forms/rsvp-form.tsx` | REWRITE_REQUIRED | Form with validation. Astro island with POST to `/api/rsvp`. | Django API `/api/rsvp` |
| `components/forms/login-form.tsx` | DO_NOT_MIGRATE | NextAuth-dependent authentication form. Defer to Phase 3. | NextAuth |
| `components/forms/change-password-form.tsx` | DO_NOT_MIGRATE | NextAuth-dependent. Defer to Phase 3. | NextAuth |

### Home Components

| Source File | Classification | Rationale | Dependencies |
|--------------|----------------|-----------|--------------|
| `components/home/hero-section.tsx` | REWRITE_REQUIRED | Hero banner. Prisma data → Django API fetch. | Django API for hero content |
| `components/home/events-section.tsx` | REWRITE_REQUIRED | Events listing. | Django API `/api/events` |
| `components/home/events-carousel-section.tsx` | REWRITE_REQUIRED | Carousel UI. Needs marquee or swipe library alternative. | Django API |
| `components/home/latest-sermon-section.tsx` | REWRITE_REQUIRED | Featured sermon. | Django API `/api/sermons` |
| `components/home/sermon-section.tsx` | REWRITE_REQUIRED | Sermon showcase. | Django API |
| `components/home/testimonials-section.tsx` | REWRITE_REQUIRED | Testimonial display. | Django API `/api/testimonials` |
| `components/home/testimonials-carousel.tsx` | REWRITE_REQUIRED | Testimonial carousel UI. | Django API |
| `components/home/pastor-section.tsx` | COPY_WITH_MINOR_CHANGES | Static pastor bio. May use leader data from API. | Optional: `/api/leaders` |
| `components/home/cta-banner-section.tsx` | REWRITE_REQUIRED | Call-to-action banner. May need dynamic data. | Static/low |
| `components/home/service-times-section.tsx` | COPY_WITH_MINOR_CHANGES | Service times display. Currently static data. | Site config |
| `components/home/service-times-carousel.tsx` | REWRITE_REQUIRED | Carousel variant. | Static/low |
| `components/home/teaching-events-section.tsx` | REWRITE_REQUIRED | Teaching/events display. | Django API |
| `components/home/what-to-expect-section.tsx` | COPY_WITH_MINOR_CHANGES | Static informational section. | None |
| `components/home/welcome-section.tsx` | COPY_WITH_MINOR_CHANGES | Static welcome message. | None |

### Layout Components

| Source File | Classification | Rationale | Dependencies |
|--------------|----------------|-----------|--------------|
| `components/layout/site-header.tsx` | REWRITE_REQUIRED | Main navigation. Needs Astro component rewrite with conditional auth links. | Auth state (Phase 3) |
| `components/layout/site-footer.tsx` | REWRITE_REQUIRED | Site footer with navigation links. | Static links |

### Motion Components

| Source File | Classification | Rationale | Dependencies |
|--------------|----------------|-----------|--------------|
| `components/motion/page-transition.tsx` | REWRITE_REQUIRED | Framer Motion dependency. Replace with Astro view transitions or CSS animations. | Astro built-ins |
| `components/motion/scroll-reveal.tsx` | REWRITE_REQUIRED | Intersection Observer animation. Can use Astro ` directives or custom JS. | None |
| `components/motion/stagger-container.tsx` | REWRITE_REQUIRED | Animation orchestration. CSS/styled with Astro. | None |

### Provider Components

| Source File | Classification | Rationale | Dependencies |
|--------------|----------------|-----------|--------------|
| `components/providers/session-provider.tsx` | DO_NOT_MIGRATE | NextAuth session provider. Not needed for Astro (Phase 3 auth). | NextAuth |

### Shared Components

| Source File | Classification | Rationale | Dependencies |
|--------------|----------------|-----------|--------------|
| `components/shared/page-hero.tsx` | REWRITE_REQUIRED | Hero banner component. | Dynamic per page |
| `components/shared/service-times-grid.tsx` | COPY_WITH_MINOR_CHANGES | Service times display. Static data. | None |

### Theme Components

| Source File | Classification | Rationale | Dependencies |
|--------------|----------------|-----------|--------------|
| `components/theme/theme-provider.tsx` | DO_NOT_MIGRATE | Next.js theme provider. Astro has built-in dark mode support or use custom script. | Next.js context |
| `components/theme/theme-toggle.tsx` | REWRITE_REQUIRED | Dark mode toggle. Rewrite as Astro component with localStorage. | None |

### UI Components

| Source File | Classification | Rationale | Dependencies |
|--------------|----------------|-----------|--------------|
| `components/ui/button.tsx` | COPY_WITH_MINOR_CHANGES | Button component. Convert to Astro component with Tailwind classes. | Tailwind |
| `components/ui/decorated-text.tsx` | COPY_WITH_MINOR_CHANGES | Text decoration utility. | Tailwind |

---

## 3. LAYOUT INVENTORY

### Next.js App Layouts

| Source File | Classification | Rationale |
|--------------|----------------|-----------|
| `app/(public)/layout.tsx` | REWRITE_REQUIRED | Root layout for public routes. Convert to Astro `src/layouts/Layout.astro`. |
| `app/(member)/layout.tsx` | DO_NOT_MIGRATE | Authenticated member layout. Defer to Phase 3. |
| `app/(ops)/layout.tsx` | DO_NOT_MIGRATE | Admin/ops layout. Defer to Phase 3. |

### Astro Layouts (existing)

| Target File | Status |
|-------------|--------|
| `src/layouts/Layout.astro` | EXISTS - basic structure |

---

## 4. STYLES INVENTORY

### Global Styles

| Source File | Classification | Rationale |
|--------------|----------------|-----------|
| `app/globals.css` | COPY_WITH_MINOR_CHANGES | Tailwind + custom CSS. Copy to Astro `src/styles/global.css`. May need Tailwind config migration. |

### Configuration

| Source File | Classification | Rationale |
|--------------|----------------|-----------|
| `tailwind.config.ts` (implied) | COPY_WITH_MINOR_CHANGES | Copy to Astro project. Ensure same color scheme, fonts. |
| `postcss.config.mjs` | COPY_WITH_MINOR_CHANGES | PostCSS config for Tailwind. |
| `eslint.config.mjs` | COPY_WITH_MINOR_CHANGES | ESLint config (optional). |
| `tsconfig.json` | COPY_WITH_MINOR_CHANGES | TypeScript config. |

---

## 5. ASSETS INVENTORY

### Favicons & Icons

| Source File(s) | Classification | Rationale |
|----------------|----------------|-----------|
| `public/*.ico`, `public/*.svg`, `public/*.png` | DIRECT_COPY | Static assets. Copy to `RP/website/public/`. |
| `public/apple-touch-icon.png` | DIRECT_COPY | Standard favicon. |
| `public/*.svg` (icons) | DIRECT_COPY | SVG icons. |

### Images

| Source Location | Classification | Rationale |
|-----------------|----------------|-----------|
| `public/images/events/` | DIRECT_COPY | Event images. Copy to `RP/website/public/images/events/`. |
| `public/images/posters/` | DIRECT_COPY | Sermon/event posters. |
| `public/images/services/` | DIRECT_COPY | Service images. |
| `public/images/team/` | DIRECT_COPY | Leader/team photos. |
| `public/rp-logo*.png/svg` | DIRECT_COPY | Branding assets. |

---

## 6. SERVER-SIDE CODE INVENTORY

### API Routes (Next.js)

| Source File | Classification | Rationale | Replacement |
|--------------|----------------|-----------|-------------|
| `app/api/contact/route.ts` | DO_NOT_MIGRATE | Next.js API route. Replaced by Django `/api/contact` (already implemented). | Django backend |
| `app/api/prayer/route.ts` | DO_NOT_MIGRATE | Next.js API route. Replaced by Django `/api/prayer` (already implemented). | Django backend |
| `app/api/rsvp/route.ts` (if exists) | DO_NOT_MIGRATE | Next.js API route. Replaced by Django `/api/rsvp`. | Django backend |
| `app/api/health/route.ts` | DO_NOT_MIGRATE | Health check. Replaced by Django `/api/health`. | Django backend |
| `app/api/auth/[...nextauth]/route.ts` | DO_NOT_MIGRATE | NextAuth. Defer to Phase 3 (use Django auth APIs). | Django auth |
| `app/api/revalidate/route.ts` | DO_NOT_MIGRATE | Next.js ISR revalidation. Not needed in Astro. | N/A |
| `app/api/auth/callback/*` | DO_NOT_MIGRATE | Magic link auth. Defer to Phase 3. | Django auth |

### Middleware

| Source File | Classification | Rationale |
|--------------|----------------|-----------|
| `middleware.ts` | DO_NOT_MIGRATE | Next.js middleware for auth/protection. Django handles auth in Phase 3. |

### Server Utilities

| Source File | Classification | Rationale | Replacement |
|--------------|----------------|-----------|-------------|
| `lib/prisma.ts` | DO_NOT_MIGRATE | Prisma client setup. | Django REST API |
| `lib/auth.ts` | DO_NOT_MIGRATE | NextAuth config. | Django auth APIs |
| `lib/auth-edge.ts` | DO_NOT_MIGRATE | Edge runtime auth. | Django auth |
| `lib/magic-link.ts` | DO_NOT_MIGRATE | Magic link auth. | Django auth |
| `lib/api-guard.ts` | DO_NOT_MIGRATE | Rate limiting for API routes. | Django backend handled (optional: add to Astro API routes later) |
| `lib/rate-limit.ts` | DO_NOT_MIGRATE | Rate limiting utility. | Django backend |
| `lib/rbac.ts` | DO_NOT_MIGRATE | Role-based access control. Defer to Phase 3. | Django backend |
| `lib/get-client-ip.ts` | DO_NOT_MIGRATE | IP detection utility. | Optional: Astro API route helper |
| `lib/images.ts` | COPY_WITH_MINOR_CHANGES | Image optimization config. | Astro image config |

---

## 7. PRISMA DEPENDENCY INVENTORY

| Dependency | Classification | Replacement Strategy |
|------------|----------------|----------------------|
| `@prisma/client` | DO_NOT_MIGRATE | Replace all Prisma queries with `fetch()` calls to Django REST API endpoints. |
| Prisma schema | DO_NOT_MIGRATE | Already migrated to Django models in Phase C2. |
| Prisma seed scripts | DO_NOT_MIGRATE | Use Django management commands or fixtures. |
| `prisma/` directory | DO_NOT_MIGRATE | Not needed in Astro project. |

---

## 8. AUTHENTICATION DEPENDENCY INVENTORY

| Dependency | Classification | Replacement Strategy |
|------------|----------------|----------------------|
| `next-auth` | DO_NOT_MIGRATE | Replace with Django session auth + JWT or session cookies in Phase 3. |
| `next-auth/react` | DO_NOT_MIGRATE | Astro uses built-in session handling or custom auth. |
| Magic link flow | DO_NOT_MIGRATE | Implement via Django email backend in Phase 3. |
| OAuth providers (Google, etc.) | DO_NOT_MIGRATE | Implement via Django allauth or similar in Phase 3. |
| Role-based guards | DO_NOT_MIGRATE | Django backend handles authorization; Astro frontend just reflects auth state. |

---

## 9. ADDITIONAL UTILITIES

| Source File | Classification | Rationale |
|--------------|----------------|-----------|
| `hooks/use-scroll-reveal.ts` | REWRITE_REQUIRED | Custom React hook. Convert to Astro directive or client directive. |
| `lib/animations.ts` | COPY_WITH_MINOR_CHANGES | CSS animation utilities. Copy with minimal changes. |
| `lib/cn.ts` | COPY_WITH_MINOR_CHANGES | Class name utility. Copy as-is. |
| `lib/form-classes.ts` | COPY_WITH_MINOR_CHANGES | Form styling utilities. Copy as-is. |
| `lib/seo.ts` | COPY_WITH_MINOR_CHANGES | SEO metadata helpers. Adapt to Astro `head` or Astro SEO component. |
| `lib/site.ts` | COPY_WITH_MINOR_CHANGES | Site configuration object. Copy and adjust paths. |
| `lib/slug.ts` | COPY_WITH_MINOR_CHANGES | Slug generation utility. Copy as-is. |
| `types/index.ts` | COPY_WITH_MINOR_CHANGES | TypeScript interfaces. Adapt to Astro data fetching patterns. |
| `types/next-auth.d.ts` | DO_NOT_MIGRATE | NextAuth type augmentations. Not needed. |

---

## 10. CONTENT DATA INVENTORY

| Source File | Classification | Rationale | Replacement |
|--------------|----------------|-----------|-------------|
| `content/sermons.json` | DO_NOT_MIGRATE | Static JSON data for sermons. | Django API `/api/sermons` |
| `content/series.json` | DO_NOT_MIGRATE | Static JSON data for series. | Django API `/api/series` |
| `content/events.json` | DO_NOT_MIGRATE | Static JSON data for events. | Django API `/api/events` |
| `content/testimonials.json` | DO_NOT_MIGRATE | Static JSON data for testimonials. | Django API `/api/testimonials` |
| `content/leadership.json` | DO_NOT_MIGRATE | Static JSON data for leaders. | Django API `/api/leaders` |
| `content/academy-modules.json` | DO_NOT_MIGRATE | Static JSON data for academy. | Django API `/api/academy` |
| `content/site.json` | DO_NOT_MIGRATE | Static site config. | Django API `/api/site-config` |

---

## 11. SCRIPTS INVENTORY

| Source File | Classification | Rationale |
|--------------|----------------|-----------|
| `scripts/db-push-turso.ts` | DO_NOT_MIGRATE | Database migration script for Turso/LibSQL. Django migrations used instead. |

---

## Summary Statistics

- **Total Files Audited:** ~60 source files + assets
- **DIRECT_COPY:** ~15 (assets only)
- **COPY_WITH_MINOR_CHANGES:** ~15 (utilities, styles, simple UI)
- **REWRITE_REQUIRED:** ~25 (pages, components with data fetching, motion)
- **DO_NOT_MIGRATE:** ~25 (API routes, auth, Prisma, Phase 3+ features)

**Estimated Migration Complexity by Category:**
- Pages: MEDIUM-HIGH (routing paradigm change)
- Components: MEDIUM (React→Astro islands)
- Layouts: LOW-MEDIUM (simpler structure)
- Styles: LOW (copy-over)
- Assets: LOW (direct copy)
- APIs: NONE (already in Django)
- Auth: N/A (deferred)

**Key Risks:**
1. React component logic → Astro island conversion requires careful handling of client-side interactivity
2. NextAuth → Django auth requires full Phase 3 implementation before authenticated pages
3. Content coupling: Many components assume Prisma is available; all must fetch from Django API
4. Animation libraries: Framer Motion needs Astro-compatible replacement

**Recommended Approach:**
Start with Phase 1 (infrastructure), then public-facing content pages, defer authentication entirely.