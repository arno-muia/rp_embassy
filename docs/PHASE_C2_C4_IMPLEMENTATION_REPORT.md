# PHASE C2–C4 — IMPLEMENTATION REPORT

**Royal Priesthood Embassy — Django Backend + Astro Frontend Migration**

Generated: 2026-07-11  
Status: **COMPLETE**  
Next: Phase C2–C5 API completion (member/ops/admin endpoints) and Astro route polishing

---

## 1. PHASE C2 — DATABASE MAPPINGS

### Models Implemented (P1 Public Domains)

| Django Model | Django App | Source (Prisma Model) | db_table | managed |
|-------------|-----------|----------------------|----------|---------|
| User | accounts | User | User | False |
| AuditLog | accounts | AuditLog | AuditLog | False |
| Member | members | Member | Member | False |
| Household | members | Household | Household | False |
| HouseholdMember | members | HouseholdMember | HouseholdMember | False |
| SystemConfig | content | SystemConfig | SystemConfig | False |
| SermonSeries | content | SermonSeries | SermonSeries | False |
| PublicSermon | content | PublicSermon | PublicSermon | False |
| WebsiteLeader | content | WebsiteLeader | WebsiteLeader | False |
| WebsiteTestimonial | content | WebsiteTestimonial | WebsiteTestimonial | False |
| WebsiteAcademyModule | content | WebsiteAcademyModule | WebsiteAcademyModule | False |
| ContactSubmission | content | ContactSubmission | ContactSubmission | False |
| VisitRsvp | content | VisitRsvp | VisitRsvp | False |
| ChurchEvent | events | ChurchEvent | ChurchEvent | False |
| EventRegistration | events | EventRegistration | EventRegistration | False |
| GivingTransaction | giving | GivingTransaction | GivingTransaction | False |
| PrayerSubmission | prayer | PrayerSubmission | PrayerSubmission | False |

### Index Mapping

All `Meta.indexes` reference the Django Python field names and use names ≤30 characters. Real indexes exist in the PostgreSQL schema (managed by Prisma); these declarations are for Django validation and documentation only.

| Django Field | Index Name | Table |
|-------------|-----------|-------|
| role | user_role_idx | User |
| user | auditlog_user_idx | AuditLog |
| action | auditlog_action_idx | AuditLog |
| entity_type | auditlog_entitytype_idx | AuditLog |
| timestamp | auditlog_timestamp_idx | AuditLog |
| entity_id | auditlog_entityid_idx | AuditLog |
| household | member_house_idx | Member |
| email | member_email_idx | Member |
| status | household_status_idx | Household |
| member_id | hmember_member_idx | HouseholdMember |
| household | hmember_house_idx | HouseholdMember |
| key | syscfg_key_idx | SystemConfig |
| is_published | series_ispub_idx | SermonSeries |
| sort_order | series_sort_idx | SermonSeries |
| series_slug | sermon_serislug_idx | PublicSermon |
| is_published | sermon_ispub_idx | PublicSermon |
| date | sermon_date_idx | PublicSermon |
| sort_order | leader_sort_idx | WebsiteLeader |
| sort_order | testi_sort_idx | WebsiteTestimonial |
| sort_order | academy_sort_idx | WebsiteAcademyModule |
| created_at | contactsub_creat_idx | ContactSubmission |
| created_at | rsvp_created_idx | VisitRsvp |
| status | rsvp_status_idx | VisitRsvp |
| start_date_time | event_start_idx | ChurchEvent |
| status | event_status_idx | ChurchEvent |
| type | event_type_idx | ChurchEvent |
| event | reg_event_idx | EventRegistration |
| member | reg_member_idx | EventRegistration |
| registration_date | reg_regdate_idx | EventRegistration |
| member | gtx_member_idx | GivingTransaction |
| household | gtx_house_idx | GivingTransaction |
| status | gtx_status_idx | GivingTransaction |
| fund | gtx_fund_idx | GivingTransaction |
| created_at | gtx_created_idx | GivingTransaction |
| mpesa_request_id | gtx_mpesa_idx | GivingTransaction |
| created_at | prayer_created_idx | PrayerSubmission |

### Foreign Key Mapping

| Source Field | Source App | Target Model | Target App | db_column | on_delete | db_constraint |
|-------------|-----------|-------------|-----------|-----------|-----------|--------------|
| AuditLog.user | accounts | User | accounts | userId | DO_NOTHING | False |
| Member.household | members | Household | members | householdId | DO_NOTHING | False |
| Member.user | members | User | accounts | userId | DO_NOTHING | False |
| Member.created_by | members | User | accounts | createdById | DO_NOTHING | False |
| Member.updated_by | members | User | accounts | updatedById | DO_NOTHING | False |
| Household.created_by | members | User | accounts | createdById | DO_NOTHING | False |
| Household.updated_by | members | User | accounts | updatedById | DO_NOTHING | False |
| HouseholdMember.household | members | Household | members | householdId | DO_NOTHING | False |
| SystemConfig.updated_by | content | User | accounts | updatedById | DO_NOTHING | False |
| PublicSermon.series | content | SermonSeries | content | seriesId | DO_NOTHING | False |
| ChurchEvent.created_by | events | User | accounts | createdById | DO_NOTHING | False |
| EventRegistration.member | events | Member | members | memberId | DO_NOTHING | False |
| EventRegistration.event | events | ChurchEvent | events | eventId | DO_NOTHING | False |
| GivingTransaction.member | giving | Member | members | memberId | DO_NOTHING | False |
| GivingTransaction.household | giving | Household | members | householdId | DO_NOTHING | False |
| GivingTransaction.created_by | giving | User | accounts | createdById | DO_NOTHING | False |

Deferred FKs (not modeled in P1):
- Member.cellGroupId → groups.CellGroup
- Member.attendances → attendance.Attendance

---

## 2. PHASE C3 — PUBLIC API

### Endpoint Inventory

| Method | Route | Purpose | Auth | Domain |
|--------|-------|---------|------|--------|
| GET | / | Home page | Public | content |
| GET | /api/sermons | List published sermons | AllowAny | content |
| GET | /api/sermons/{slug} | Get sermon by slug | AllowAny | content |
| GET | /api/series | List published series | AllowAny | content |
| GET | /api/series/{slug} | Get series by slug | AllowAny | content |
| GET | /api/leaders | List published leaders | AllowAny | content |
| GET | /api/testimonials | List published testimonials | AllowAny | content |
| GET | /api/academy | List academy modules | AllowAny | content |
| GET | /api/events | List published/upcoming events | AllowAny | events |
| GET | /api/events/{id} | Get event by UUID | AllowAny | events |
| GET | /api/site-config | Get site configuration JSON | AllowAny | content |
| POST | /api/contact | Submit contact form | AllowAny | content |
| POST | /api/prayer | Submit prayer request | AllowAny | prayer |
| POST | /api/rsvp | Submit visit RSVP | AllowAny | content |
| GET | /api/health | Health check | AllowAny | backend |

### API Details

**ViewSets Implemented:**
- `SermonViewSet` (content) — ReadOnlyModelViewSet, queryset via `SermonRepository.published()`, lookup by `slug`, serializer `PublicSermonReadSerializer`
- `SeriesViewSet` (content) — ReadOnlyModelViewSet, queryset via `SeriesRepository.published()`, lookup by `slug`, serializer `SermonSeriesReadSerializer`
- `LeaderViewSet` (content) — ReadOnlyModelViewSet, queryset via `WebsiteLeaderRepository.published()`, serializer `WebsiteLeaderReadSerializer`
- `TestimonialViewSet` (content) — ReadOnlyModelViewSet, queryset via `WebsiteTestimonialRepository.published()`, serializer `WebsiteTestimonialReadSerializer`
- `AcademyModuleViewSet` (content) — ReadOnlyModelViewSet, queryset via `WebsiteAcademyModuleRepository.published()`, serializer `WebsiteAcademyModuleReadSerializer`
- `EventViewSet` (events) — ReadOnlyModelViewSet, queryset via `EventRepository.published_upcoming()`, lookup by `id` (UUID), serializer `ChurchEventReadSerializer`

**Function-based endpoints:**
- `site_config()` → GET /api/site-config → reads SystemConfig key='site'
- `contact_submit()` → POST /api/contact → validated via ContactSubmissionWriteSerializer
- `prayer_submit()` → POST /api/prayer → validated via PrayerSubmissionWriteSerializer
- `rsvp_submit()` → POST /api/rsvp → validated via VisitRsvpWriteSerializer
- `health_check()` → GET /api/health → returns JSON health payload

### URL Configuration

**backend/urls.py:**
- `admin/` → Django admin
- `api/` → includes `backend.apps.content.urls`
- `api/` → includes `backend.apps.events.urls`
- `api/health` → `health_check`

**content/urls.py:**
- `sermons/` → SermonViewSet
- `series/` → SeriesViewSet
- `leaders/` → LeaderViewSet
- `testimonials/` → TestimonialViewSet
- `academy/` → AcademyModuleViewSet
- `site-config` → site_config
- `contact` → contact_submit
- `prayer` → prayer_submit
- `rsvp` → rsvp_submit

**events/urls.py:**
- `events/` → EventViewSet

---

## 3. PHASE C4 — ASTRO PUBLIC PAGES

### Page Inventory

| Page | Route | Domain | API Dependency |
|------|-------|--------|----------------|
| Index | / | content | None (navigation scaffold) |
| Sermons | /sermons | content | GET /api/sermons, GET /api/series |
| Sermon Detail | /sermons/[slug] | content | GET /api/sermons/{slug} |
| Series | /series | content | GET /api/series |
| Series Detail | /series/[slug] | content | GET /api/series/{slug}, GET /api/sermons |
| Events | /events | events | GET /api/events |
| About | /about | content | GET /api/leaders, GET /api/testimonials |
| Academy | /academy | content | GET /api/academy |
| Contact | /contact | content | POST /api/contact |
| Prayer | /prayer | prayer | POST /api/prayer |
| Visit | /visit | content | POST /api/rsvp |
| Give | /give | giving | None (placeholder) |
| Login | /login | accounts | POST /api/auth/login (placeholder) |
| Change Password | /change-password | accounts | POST /api/auth/change-password (placeholder) |

### Page Structure

- **Layout:** `src/layouts/Layout.astro` — shared HTML shell with SEO title/description props
- **Data fetching:** SSR via `fetch()` inside frontmatter (`---`), hitting `http://localhost:8000/api`
- **Styling:** Plain HTML (no Tailwind/CSS framework yet) — responsive structure preserved
- **Navigation:** All public routes linked from `/`
- **Placeholder pages:** `give`, `login`, `change-password` contain scaffold forms pointing to placeholder API endpoints

### Deferred Pages (Future Phases)

- `/ops` — operations dashboard
- `/admin` — content administration
- `/dashboard` — member dashboard
- `/profile` — member profile
- `/household` — household management
- `/giving-history` — giving records
- `/discipleship` — discipleship tracking

---

## 4. REPOSITORY INVENTORY

All Phase C1 repositories are in place. No new repositories added in C2–C4.

| App | Repository | Methods |
|-----|-----------|---------|
| accounts | UserRepository | 5 methods |
| accounts | AuditLogRepository | 4 methods |
| members | MemberRepository | 6 methods |
| members | HouseholdRepository | 3 methods |
| members | HouseholdMemberRepository | 2 methods |
| content | SystemConfigRepository | 2 methods |
| content | SermonRepository | 4 methods |
| content | SeriesRepository | 2 methods |
| content | EventRepository | 1 method |
| content | WebsiteLeaderRepository | 1 method |
| content | WebsiteTestimonialRepository | 1 method |
| content | WebsiteAcademyModuleRepository | 1 method |
| content | ContactSubmissionRepository | 1 method |
| content | VisitRsvpRepository | 2 methods |
| events | EventRepository | 4 methods |
| events | EventRegistrationRepository | 2 methods |
| giving | GivingTransactionRepository | 5 methods |
| prayer | PrayerSubmissionRepository | 3 methods |

**Total:** 17 repository classes across 6 apps.

---

## 5. SERIALIZER INVENTORY

All Phase C1 serializers are in place. ViewSets use Read serializers. Write serializers are available for POST endpoints.

| App | Read Serializer | Write Serializer |
|-----|----------------|-----------------|
| content | SystemConfigReadSerializer | SystemConfigWriteSerializer |
| content | SermonSeriesReadSerializer | SermonSeriesWriteSerializer |
| content | PublicSermonReadSerializer | PublicSermonWriteSerializer |
| content | WebsiteLeaderReadSerializer | WebsiteLeaderWriteSerializer |
| content | WebsiteTestimonialReadSerializer | WebsiteTestimonialWriteSerializer |
| content | WebsiteAcademyModuleReadSerializer | WebsiteAcademyModuleWriteSerializer |
| content | ContactSubmissionReadSerializer | ContactSubmissionWriteSerializer |
| content | VisitRsvpReadSerializer | VisitRsvpWriteSerializer |
| events | ChurchEventReadSerializer | ChurchEventWriteSerializer |
| events | EventRegistrationReadSerializer | EventRegistrationWriteSerializer |
| giving | GivingTransactionReadSerializer | GivingTransactionWriteSerializer |
| prayer | PrayerSubmissionReadSerializer | PrayerSubmissionWriteSerializer |

---

## 6. VIEWS INVENTORY

| File | ViewSet | Endpoints |
|------|---------|-----------|
| content/views.py | SermonViewSet | list, retrieve (by slug) |
| content/views.py | SeriesViewSet | list, retrieve (by slug) |
| content/views.py | LeaderViewSet | list |
| content/views.py | TestimonialViewSet | list |
| content/views.py | AcademyModuleViewSet | list |
| content/views.py | site_config | GET /site-config |
| content/views.py | contact_submit | POST /contact |
| content/views.py | prayer_submit | POST /prayer |
| content/views.py | rsvp_submit | POST /rsvp |
| events/views.py | EventViewSet | list, retrieve (by UUID) |
| backend/urls.py | health_check | GET /health |

---

## 7. FRONTEND INVENTORY

### Astro Pages Created

| File | Route | Data Source |
|------|-------|------------|
| src/pages/index.astro | / | None |
| src/pages/sermons.astro | /sermons | GET /api/sermons, GET /api/series |
| src/pages/sermons/[slug].astro | /sermons/[slug] | GET /api/sermons/{slug} |
| src/pages/series.astro | /series | GET /api/series |
| src/pages/series/[slug].astro | /series/[slug] | GET /api/series/{slug}, GET /api/sermons |
| src/pages/events.astro | /events | GET /api/events |
| src/pages/about.astro | /about | GET /api/leaders, GET /api/testimonials |
| src/pages/academy.astro | /academy | GET /api/academy |
| src/pages/contact.astro | /contact | POST /api/contact |
| src/pages/prayer.astro | /prayer | POST /api/prayer |
| src/pages/visit.astro | /visit | POST /api/rsvp |
| src/pages/give.astro | /give | None (placeholder) |
| src/pages/login.astro | /login | POST /api/auth/login (placeholder) |
| src/pages/change-password.astro | /change-password | POST /api/auth/change-password (placeholder) |

### Astro Layout

| File | Purpose |
|------|---------|
| src/layouts/Layout.astro | Shared layout with SEO title/description props |

---

## 8. VALIDATION

### Backend

- `manage.py check` → **0 issues**
- `autoreload` requires no migrations (`managed = False`)
- All URL namespaces resolve correctly
- All cross-app imports validated

### Frontend

- Astro scaffold verified (Layout + index page)
- All 12 required pages created with correct route files
- Data fetching patterns using SSR frontmatter confirmed
- Placeholder auth pages reference placeholder endpoints (not yet implemented)

---

## 9. REMAINING WORK

### Backend (To complete /ops, /admin)

**Accounts auth views needed:**
- POST /api/auth/login → UserService authenticate, return JWT/token
- POST /api/auth/logout → invalidate session
- POST /api/auth/change-password → UserService update password
- GET /api/auth/me → return current user

**Members views:**
- GET/POST /api/members → MemberViewSet
- GET/PUT /api/members/{id} → Member detail
- GET /api/households → HouseholdViewSet
- GET /api/households/{id} → Household detail

**Giving views:**
- GET /api/giving/transactions → GivingTransactionViewSet (authenticated)
- POST /api/giving/initiate → initiate M-PESA payment

**Admin views:**
- /api/admin/dashboard → aggregate stats
- /api/admin/events → full CRUD
- /api/admin/sermons → full CRUD
- /api/admin/series → full CRUD
- /api/admin/content → full CRUD

### Frontend

- Add `getStaticPaths()` to events/[id].astro and about.astro where applicable
- Implement responsive CSS/Tailwind styling
- Add shared navigation component
- Add SEO metadata generation (e.g., churchSchema)
- Implement protected routes for /ops, /admin, /dashboard, /profile
- Build authentication forms with proper CSRF handling
- Connect giving page to M-PESA API
- Implement error boundaries and loading states

### Data

- Seed SystemConfig with site configuration
- Verify Prisma-managed schema matches Django models exactly
- Load initial data (sermons, series, events, leaders, testimonials, academy modules)

---
*End of Phase C2–C4 Report*