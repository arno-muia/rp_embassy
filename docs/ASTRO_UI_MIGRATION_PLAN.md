# ASTRO UI MIGRATION PLAN

## Strategy

Migrate from Next.js (apps/web) to Astro (RP/website) using islands architecture. Public pages are server-rendered with selective client-side hydration for interactive components.

---

## PHASE 1: INFRASTRUCTURE (Week 1)

**Objective:** Establish foundation for all subsequent migration work.

### Tasks

1. **Tailwind Configuration**
   - Copy `tailwind.config.ts` from apps/web to RP/website
   - Migrate color scheme, typography, spacing tokens
   - Update `postcss.config.mjs`
   - Verify Tailwind classes work in Astro components

2. **Global Styles**
   - Copy `app/globals.css` → `src/styles/global.css`
   - Migrate custom CSS animations, utility classes
   - Ensure CSS imports work in Astro layout

3. **Utilities & Helpers**
   - `lib/cn.ts` → `src/lib/cn.ts` (class name utility)
   - `lib/slug.ts` → `src/lib/slug.ts` (slug generation)
   - `lib/site.ts` → `src/lib/site.ts` (site configuration)
   - `lib/form-classes.ts` → `src/lib/form-classes.ts`
   - `lib/animations.ts` → `src/lib/animations.ts`

4. **TypeScript Types**
   - `types/index.ts` → `src/types/index.ts`
   - Adapt interfaces for Django API response shapes
   - Remove NextAuth type augmentations

5. **Assets Migration**
   - Copy all `public/` assets to `RP/website/public/`
   - Favicons, logos, icons
   - Image directories: `events/`, `posters/`, `services/`, `team/`

6. **Base Layout Enhancement**
   - Expand `src/layouts/Layout.astro` with:
     - Global navigation structure
     - Meta tags template
     - Font imports
     - Dark mode support foundation

### Deliverables

- Astro project builds successfully
- Tailwind styling matches Next.js design
- All static assets accessible
- Base layout renders correctly

---

## PHASE 2: PUBLIC PAGES (Week 2-3)

**Objective:** Migrate all public-facing pages and components.

### Priority Order

#### Week 2: Core Content Pages

1. **Homepage** (`src/pages/index.astro`)
   - REWRITE_REQUIRED: Complete rebuild
   - Fetch data from Django APIs: `/api/sermons`, `/api/events`, `/api/testimonials`
   - Implement as Astro page with server-side fetching
   - Create island components for any interactive elements

2. **Components: Shared**
   - `src/components/shared/page-hero.astro` - REWRITE_REQUIRED
   - `src/components/shared/service-times-grid.astro` - COPY_WITH_MINOR_CHANGES

3. **Components: Layout**
   - `src/components/layout/site-header.astro` - REWRITE_REQUIRED
   - `src/components/layout/site-footer.astro` - REWRITE_REQUIRED

4. **Components: Content**
   - `src/components/content/sermon-card.astro` - REWRITE_REQUIRED
   - `src/components/content/event-card.astro` - REWRITE_REQUIRED

#### Week 3: Secondary Public Pages

5. **Sermons**
   - `src/pages/sermons.astro` - REWRITE_REQUIRED
   - `src/pages/sermons/[slug].astro` - REWRITE_REQUIRED
   - Components: sermon-card, FAQ accordion

6. **Series**
   - `src/pages/series.astro` - REWRITE_REQUIRED
   - `src/pages/series/[slug].astro` - REWRITE_REQUIRED

7. **Events**
   - `src/pages/events.astro` - REWRITE_REQUIRED
   - `src/pages/events/[id].astro` - REWRITE_REQUIRED (note: source uses `[slug]`, target uses `[id]` - align with Django API)

8. **Static Content Pages**
   - `src/pages/about.astro` - REWRITE_REQUIRED
   - `src/pages/academy.astro` - REWRITE_REQUIRED
   - `src/pages/privacy.astro` - REWRITE_REQUIRED
   - `src/pages/terms.astro` - REWRITE_REQUIRED

9. **Form Pages (with islands)**
   - `src/pages/contact.astro` + ContactForm island - REWRITE_REQUIRED
   - `src/pages/prayer.astro` + PrayerForm island - REWRITE_REQUIRED
   - `src/pages/visit.astro` + RsvpForm island - REWRITE_REQUIRED

### Deliverables

- All 11 public pages migrated and functional
- Forms submit to Django backend APIs
- Content pages display data from Django APIs
- SEO meta tags implemented per page
- Mobile responsive design matches source

---

## PHASE 3: AUTHENTICATED PAGES (Week 4-5+)

**Objective:** Migrate member and admin pages (deferred until Phase 3 backend complete).

**Prerequisites:**
- Django authentication APIs implemented
- Session/JWT auth flow established
- Role-based access control in place

### Tasks (Future)

1. **Member Pages**
   - Dashboard
   - Profile
   - Household management
   - Giving history
   - Discipleship tracking

2. **Admin/Ops Pages**
   - Admin dashboard
   - Member management
   - Event management
   - Content management

3. **Auth Pages**
   - Login
   - Change password
   - Magic link authentication

### Deliverables

- Full authentication flow operational
- Protected routes render correctly
- User sessions persist
- Role-based UI rendering

---

## PHASE 4: CLEANUP & POLISH (Week 6)

**Objective:** Finalize migration, remove legacy code.

### Tasks

1. **Code Cleanup**
   - Remove all Next.js-specific code
   - Remove NextAuth dependencies
   - Remove Prisma client code
   - Clean up unused utilities

2. **Performance Optimization**
   - Implement image optimization via Astro assets
   - Configure view transitions
   - Optimize bundle sizes
   - Lazy load islands

3. **Testing**
   - Cross-browser testing
   - Mobile responsiveness verification
   - Form submission testing
   - API integration testing
   - SEO tag verification

4. **Documentation**
   - Update deployment guides
   - Document environment variables
   - Create component library docs

5. **Deployment**
   - Configure Astro for production
   - Set up CI/CD pipeline
   - Deploy to hosting platform

### Deliverables

- Production-ready Astro site
- No legacy Next.js code remaining
- Full test coverage
- Deployment pipeline operational

---

## MIGRATION DEPENDENCIES

```
Phase 1 (Infrastructure)
    ↓
Phase 2 (Public Pages) ← depends on: Django APIs complete (Phase C2+C3)
    ↓
Phase 3 (Auth Pages) ← depends on: Django auth backend
    ↓
Phase 4 (Cleanup)
```

---

## RISK MITIGATION

| Risk | Mitigation |
|------|------------|
| React→Astro component logic loss | Document all interactive behaviors; implement as Astro islands |
| Design system drift | Use same Tailwind config; visual regression testing |
| API contract mismatch | Reuse TypeScript types from Django serializer schemas |
| SEO regression | Implement same meta tags; test with SEO tools |
| Performance degradation | Benchmark against Next.js; optimize islands |

---

## ESTIMATED EFFORT

| Phase | Duration | Complexity |
|-------|----------|------------|
| Phase 1: Infrastructure | 1 week | LOW |
| Phase 2: Public Pages | 2 weeks | MEDIUM-HIGH |
| Phase 3: Authenticated Pages | 2-3 weeks | HIGH |
| Phase 4: Cleanup | 1 week | LOW |
| **Total** | **6-7 weeks** | **MEDIUM** |

---

## SUCCESS CRITERIA

- [ ] All public pages render correctly
- [ ] All forms submit successfully to Django backend
- [ ] Design matches Next.js source exactly
- [ ] SEO meta tags identical to source
- [ ] Page load performance ≥ Next.js baseline
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Accessible (WCAG 2.1 AA)

---

## NOTES

- Do not start Phase 3 until Django authentication backend is complete
- Maintain parallel run of Next.js and Astro during migration for A/B testing
- Use feature flags if necessary for gradual rollout
- All API endpoints already implemented in Django (Phase C2+C3)