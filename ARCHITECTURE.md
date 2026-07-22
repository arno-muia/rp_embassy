# Architecture

## Official Architecture

The Royal Priesthood Embassy website is built as a monorepo with a clear separation between frontend presentation and backend data management.

**Official Stack:**
- **Astro** + **Django** + **Django Admin** + **PostgreSQL**

The authoritative data layer is PostgreSQL managed through Django ORM and Django Admin.

---

## Technology Stack

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Astro       │     │      Django     │     │   PostgreSQL    │
│   (Frontend)    │◄──►│  (REST API +    │◄──►│   (Database)    │
│                 │     │   Admin)        │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                        ▲                       ▲
        │                        │                       │
        │              ┌───────────┼───────────┐           │
        │              │         │           │           │
        ▼              ▼         ▼           ▼           ▼
        │     ┌─────────────┐   ┌─────────┐   ┌─────────┐ │
        └──────│TypeScript    │   │  DRF    │   │  ORM    │ │
               │  (Frontend) │   │(Backend)│   │(Backend)│ │
               └─────────────┘   └─────────┘   └─────────┘ │
```

---

## Request Flow Diagram

```
User Request
     │
     ▼
┌─────────────────┐
│   Astro Site    │
│  (localhost:    │
│   4321)         │
└────────┬────────┘
         │
         │ Fetch API calls (GET/POST)
         ▼
┌─────────────────┐
│  Django CORS    │
│   Middleware    │
│  (corsheaders)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django REST    │
│   Framework     │
│   (ViewSets)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django ORM     │
│  (Data Access)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (Primary DB)  │
└─────────────────┘
```

**Flow Description:**
1. User visits the Astro site in their browser (served at `http://localhost:4321`)
2. Astro components make API requests to the Django backend (via `PUBLIC_API_URL`)
3. Django CORS middleware validates the request origin
4. Django REST Framework routes the request to the appropriate ViewSet
5. The ViewSet uses the repository layer to query Django ORM
6. Django ORM translates operations to PostgreSQL queries
7. Response flows back through the same path to the user

---

## Component Responsibilities

### Astro Frontend

| Component | Responsibility |
|-----------|---------------|
| `src/pages/` | File-based routing for all site pages |
| `src/components/home/` | Homepage sections (Hero, SermonSection, EventsSection, Testimonials, CTA, etc.) |
| `src/components/layout/` | SiteHeader, SiteFooter, base Layout component |
| `src/components/ui/` | Reusable UI primitives (Button, DecoratedText, etc.) |
| `src/components/forms/` | ContactForm, PrayerForm, RsvpForm, LoginForm, ChangePasswordForm |
| `src/components/content/` | Content cards (SermonCard, EventCard, SeriesCard, etc.) |
| `src/lib/api.ts` | Fetch client for Django REST API integration |
| `src/types/` | TypeScript domain types mirroring API models |

### Django Backend

| Component | Responsibility |
|-----------|---------------|
| `backend/urls.py` | Root URL routing, health check endpoint |
| `apps/content/` | Sermons, series, leaders, testimonials, academy modules, site configuration |
| `apps/events/` | Church events management |
| `apps/prayer/` | Prayer request submissions |
| `apps/accounts/` | User authentication (future member portal) |
| `apps/members/` | Member profiles and household management (future) |
| `apps/giving/` | Donations and giving records (future) |

### Django REST APIs

| App | Endpoints | Purpose |
|-----|-----------|---------|
| content | `/api/sermons/`, `/api/series/`, `/api/leaders/`, `/api/testimonials/`, `/api/academy/`, `/api/site-config`, `/api/contact`, `/api/rsvp` | Content management APIs |
| events | `/api/events/` | Event listing and retrieval |
| prayer | `/api/prayer/` | Prayer request submission |
| system | `/api/health/` | Health check monitoring |

### Django Admin

The Django Admin interface provides content management capabilities:

- **GlobalSettings** - Church name, contact info, social media
- **HomepageSettings** - Hero title, subtitle, CTA text
- **ChurchProfile** - Mission, vision, pastor message
- **ContentBlock** - Reusable content sections
- **ServiceTime** - Weekly service schedules
- **HomepageSection** - Section enable/disable and ordering
- **SystemConfig** - Key-value configuration pairs
- **SermonSeries** - Sermon series management
- **PublicSermon** - Sermon content with speakers, dates, scripture
- **WebsiteLeader** - Leadership team profiles
- **WebsiteTestimonial** - Testimonial content
- **WebsiteAcademyModule** - Academy course information
- **ContactSubmission** - View submitted contact messages
- **VisitRsvp** - Manage visit RSVP requests

### PostgreSQL

PostgreSQL serves as the authoritative data store:

- Primary database for all production environments
- Uses GIN indexes for search functionality (sermons, events, testimonials)
- Stores all content via Django ORM models
- Accessible via Django Admin for content management
- Local SQLite fallback available for development

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Production                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│ │    Vercel    │     │  WSGI Host   │     │  PostgreSQL  │    │
│ │  (Static     │────►│  (Gunicorn/  │────►│  (Database   │    │
│ │   Astro)     │     │   Uvicorn)   │     │   Server)    │    │
│ └──────────────┘     └──────────────┘     └──────────────┘    │
│        │                     │                     │          │
│        │                     │                     │          │
│        └─────────────────────┴─────────────────────┘          │
│                              ▲                                  │
│                              │                                  │
│                    PUBLIC_API_URL                                │
│                    (env var in Vercel)                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Hosting Configuration

- **Frontend**: Deployed to Vercel as static Astro build
- **Backend**: Deployed to any WSGI-compatible host (e.g., Heroku, Railway, DigitalOcean)
- **Database**: PostgreSQL server (production) or SQLite (development)
- **Environment Variables**: `PUBLIC_API_URL` on Vercel points to the production API

---

## Data Ownership Model

```
┌─────────────────┐
│   PostgreSQL    │
│   (Authoritative)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Django ORM    │
│ (Data Access)   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────────┐
│Read   │ │ Write     │
│(API)  │ │ (Admin)   │
└───────┘ └───────────┘
    ▲         ▲
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│ Astro Frontend  │
│ (Presentation)  │
└─────────────────┘
```

**Data Flow Rules:**
- All data originates in PostgreSQL
- Django ORM provides the sole data access layer
- Django Admin is the primary write interface for content
- Django REST APIs provide read access for the frontend
- Astro frontend consumes APIs for user-facing content
- No direct database access from the frontend

---

## Legacy Components

Some historical repository components remain for archival purposes and are not part of the active platform architecture.