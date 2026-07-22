# B3.4A — Architecture Update Report

## Summary

Created `RP/ARCHITECTURE.md` to document the current production architecture for the Royal Priesthood Embassy website.

## Changes Made

### 1. Astro Frontend Documentation
- Documented frontend component structure:
  - `src/pages/` - File-based routing
  - `src/components/home/` - Homepage sections
  - `src/components/layout/` - SiteHeader, SiteFooter, Layout
  - `src/components/ui/` - Reusable UI primitives
  - `src/components/forms/` - Form components
  - `src/components/content/` - Content cards
  - `src/lib/api.ts` - Fetch client for API integration
  - `src/types/` - TypeScript domain types

### 2. Django Backend Documentation
- Documented backend apps and their responsibilities:
  - `apps/content/` - Sermons, series, leaders, testimonials, academy modules
  - `apps/events/` - Church events management
  - `apps/prayer/` - Prayer request submissions
  - `apps/accounts/` - User authentication (future)
  - `apps/members/` - Member profiles (future)
  - `apps/giving/` - Donations (future)

### 3. Django REST APIs Documentation
- Listed all API endpoints:
  - `/api/sermons/` - Sermon content
  - `/api/series/` - Sermon series
  - `/api/leaders/` - Leadership team
  - `/api/testimonials/` - Testimonials
  - `/api/academy/` - Academy modules
  - `/api/site-config` - Site configuration
  - `/api/contact` - Contact submissions
  - `/api/rsvp` - Event RSVPs
  - `/api/events/` - Events listing
  - `/api/prayer` - Prayer requests
  - `/api/health` - Health check endpoint

### 4. Django Admin Documentation
- Documented all admin-managed models:
  - GlobalSettings, HomepageSettings, ChurchProfile
  - ContentBlock, ServiceTime, HomepageSection, SystemConfig
  - SermonSeries, PublicSermon
  - WebsiteLeader, WebsiteTestimonial, WebsiteAcademyModule
  - ContactSubmission, VisitRsvp

### 5. PostgreSQL Documentation
- Documented as the authoritative data layer
- Noted GIN indexes for search functionality
- Confirmed integration via Django ORM

### 6. Django ORM Documentation
- Described the ORM as the sole data access layer
- Mapped the layered pattern: models → repositories → services → serializers → views → urls

### 7. Request Flow Diagram
- Created ASCII diagram showing:
  - User request flow through Astro
  - API calls to Django
  - CORS middleware handling
  - REST Framework processing
  - ORM to PostgreSQL communication

### 8. Component Responsibilities
- Created tables documenting:
  - Astro frontend components
  - Django backend apps
  - REST API endpoints
  - Django Admin models

### 9. Deployment Architecture
- Documented Vercel for frontend hosting
- Documented WSGI host for backend (Gunicorn/Uvicorn)
- Documented PostgreSQL server for database
- Noted `PUBLIC_API_URL` environment variable configuration

### 10. Data Ownership Model
- Created diagram showing:
  - PostgreSQL as authoritative source
  - Django ORM as data access layer
  - Separate read (API) and write (Admin) paths
  - Astro frontend for presentation only

### 11. Official Architecture Statement
- Clearly stated: "The authoritative data layer is PostgreSQL managed through Django ORM and Django Admin."

### 12. Legacy Components Section
- Added section as required:
  > "Some historical repository components remain for archival purposes and are not part of the active platform architecture."

## Validation Checklist

- [x] ARCHITECTURE reflects current production architecture
- [x] No references to Next.js
- [x] No references to Prisma as an active dependency
- [x] Official stack clearly stated: Astro + Django + Django Admin + PostgreSQL
- [x] Request flow diagram included
- [x] Component responsibilities documented
- [x] Deployment architecture documented
- [x] Data ownership model documented
- [x] Legacy Components section added without mentioning apps/web by name
- [x] No code changes made (documentation only)

## Files Created

- `RP/ARCHITECTURE.md` - New architecture documentation file