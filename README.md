# Royal Priesthood Embassy — Website (`RP`)

**Ministry operating system for Royal Priesthood Embassy (Thika, Kenya).**

This repository contains the **public-facing website** for the church, built as a monorepo with two cooperating parts:

1. **`website/`** — A static-first **Astro** front end (the public site visitors see).
2. **`backend/`** — A **Django + Django REST Framework** API that serves content (sermons, series, events, leaders, testimonials, academy modules, prayer/contact/RSVP submissions) to the front end.

The site is designed to be deployed on **Vercel** (front end) with the Django API served separately (e.g. a WSGI/ASGI host or container).

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Repository Layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Backend Setup (Django API)](#backend-setup-django-api)
- [Frontend Setup (Astro Site)](#frontend-setup-astro-site)
- [Environment Variables](#environment-variables)
- [Database Commands](#database-commands)
- [Running Locally](#running-locally)
- [API Reference](#api-reference)
- [Data Model](#data-model)
- [Project Structure Detail](#project-structure-detail)
- [Building & Deployment](#building--deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend framework** | [Astro](https://astro.build) 7 |
| **Frontend language** | TypeScript 6 (strict) |
| **Frontend styling** | Tailwind CSS v4 (`@tailwindcss/vite`) |
| **Frontend utilities** | clsx, tailwind-merge |
| **Backend framework** | Django 5.2 (WSGI/ASGI) |
| **Backend API** | Django REST Framework (ViewSets + DefaultRouter) |
| **CORS** | django-cors-headers |
| **Database** | PostgreSQL (production) / SQLite (development fallback) |
| **Auth (planned)** | Django auth + DRF (accounts / members apps) |
| **Hosting** | Vercel (front end) + generic WSGI host (API) |

---

## Repository Layout

```
RP/
├── backend/                 # Django REST API
│   ├── manage.py            # Django CLI entrypoint
│   ├── db.sqlite3           # Local SQLite database (dev fallback)
│   ├── database_snapshot.py # Helper to snapshot the database
│   └── backend/             # Django project package
│       ├── settings.py      # Project settings (DB, CORS, apps)
│       ├── urls.py          # Root URL routing + health check
│       ├── wsgi.py / asgi.py
│       └── apps/            # Domain applications
│           ├── accounts/    # User accounts (login, lockout)
│           ├── members/     # Member / household management
│           ├── content/     # Sermons, series, leaders, testimonials, academy
│           ├── events/      # Church events
│           ├── giving/      # Giving / donations
│           └── prayer/      # Prayer requests
│
├── website/                 # Astro public site
│   ├── astro.config.mjs     # Astro + Tailwind config
│   ├── tsconfig.json
│   ├── package.json
│   ├── .env.example         # PUBLIC_API_URL template
│   ├── public/              # Static assets
│   └── src/
│       ├── pages/           # Routes (index, sermons, events, …)
│       ├── components/       # Astro components (home, layout, ui, forms)
│       ├── layouts/          # Base page layouts
│       ├── lib/              # API client, helpers (cn, format, seo, site)
│       ├── types/           # TypeScript domain types
│       ├── styles/          # Global CSS
│       └── assets/          # Bundled assets
│
└── docs/                    # Phase / migration / audit reports
```

---

## Prerequisites

- **Node.js** >= 22.12.0 (front end)
- **Python** >= 3.10 (backend)
- **PostgreSQL** (production) or **SQLite** (local dev — included)
- **npm** and **pip** (or **pipenv** / **venv**)

---

## Backend Setup (Django API)

```bash
cd backend

# (Recommended) create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install django djangorestframework django-cors-headers psycopg2-binary

# Configure environment (see Environment Variables below)
export DJANGO_SECRET_KEY="your-secret-key"
export DJANGO_DEBUG="True"

# Apply migrations
python manage.py migrate

# (Optional) create an admin user
python manage.py createsuperuser

# Start the API server
python manage.py runserver 127.0.0.1:8000
```

The API will be available at `http://127.0.0.1:8000/` and the admin at `http://127.0.0.1:8000/admin/`.

> **Note:** `backend/settings.py` currently ships with a hardcoded `SECRET_KEY`, `DEBUG = True`, and a PostgreSQL `DATABASES` configuration. Override these via environment variables (or edit `settings.py`) before any production deployment. A local `db.sqlite3` is provided for quick start if PostgreSQL is unavailable — switch the `DATABASES` engine to `django.db.backends.sqlite3` to use it.

---

## Frontend Setup (Astro Site)

```bash
cd website

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env and set PUBLIC_API_URL to your running backend, e.g. http://127.0.0.1:8000

# Start the dev server
npm run dev
```

The site will be available at `http://localhost:4321`.

---

## Environment Variables

### Frontend (`website/.env`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `PUBLIC_API_URL` | Yes (dev) | Base URL of the Django API. Default `http://127.0.0.1:8000`. Consumed by `src/lib/api.ts`. |

### Backend (`backend/` environment)

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `DJANGO_SECRET_KEY` | Yes (prod) | hardcoded dev key | Signs sessions / tokens |
| `DJANGO_DEBUG` | Yes | `True` | Debug mode toggle (set `False` in prod) |
| `DB_ENGINE` | No | `postgresql` | `django.db.backends.postgresql` or `sqlite3` |
| `DB_NAME` | No | `RP` | Database name |
| `DB_USER` | No | `postgres` | Database user |
| `DB_PASSWORD` | No | `arno` | Database password |
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |

CORS is configured in `settings.py` to allow `localhost:3000`, `localhost:4321`, and their `127.0.0.1` equivalents, with `CORS_ALLOW_CREDENTIALS = True`.

---

## Database Commands

All commands run from `backend/`:

```bash
# Create / apply migrations
python manage.py makemigrations
python manage.py migrate

# Open the Django admin shell
python manage.py shell

# Create a superuser
python manage.py createsuperuser

# Take a database snapshot (project helper)
python database_snapshot.py

# Collect static files (production)
python manage.py collectstatic
```

To switch to the bundled SQLite database instead of PostgreSQL, edit `backend/backend/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

---

## Running Locally

You need **both** the API and the site running.

**Terminal 1 — API:**
```bash
cd backend
python manage.py runserver 127.0.0.1:8000
```

**Terminal 2 — Site:**
```bash
cd website
npm run dev
```

Then open:
- Site: `http://localhost:4321`
- API health: `http://127.0.0.1:8000/api/health`
- Admin: `http://127.0.0.1:8000/admin/`

---

## API Reference

Base path: `/api/`

### Content (`backend.apps.content`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sermons/` | GET | List / retrieve sermons |
| `/api/series/` | GET | List / retrieve sermon series |
| `/api/leaders/` | GET | List / retrieve leadership team |
| `/api/testimonials/` | GET | List / retrieve testimonials |
| `/api/academy/` | GET | List / retrieve academy modules |
| `/api/site-config` | GET | Site-wide configuration |
| `/api/contact` | POST | Submit contact message |
| `/api/rsvp` | POST | Submit event RSVP |

### Events (`backend.apps.events`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/events/` | GET | List / retrieve events |

### Prayer (`backend.apps.prayer`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/prayer` | POST | Submit prayer request (supports anonymous) |

### System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check (`{ status: "healthy", service: "backend", version: "1.0.0" }`) |

The `accounts`, `members`, and `giving` apps exist in the project but are not yet mounted in the root URL configuration — they are staged for the member portal.

---

## Data Model

Key entities (Django models) live in each app:

- **content** — `Sermon`, `Series`, `Leader`, `Testimonial`, `AcademyModule`, plus `SiteConfig`
- **events** — `Event`
- **prayer** — `PrayerRequest`
- **accounts** — user accounts / authentication
- **members** — member profiles / households
- **giving** — donations / giving records

Each API app follows a layered pattern: `models.py` → `repositories.py` → `services.py` → `serializers.py` → `views.py` → `urls.py`.

---

## Project Structure Detail

### `backend/backend/apps/`
Each app contains:
- `apps.py` — App config
- `models.py` — Django ORM models
- `repositories.py` — Data-access layer
- `services.py` — Business logic
- `serializers.py` — DRF serializers
- `views.py` — API views / viewsets
- `urls.py` — App URL routing (where mounted)

### `website/src/`
- `pages/` — File-based routing (`.astro` files; dynamic routes like `[slug].astro`, `[id].astro`)
- `components/home/` — Homepage sections (Hero, SermonSection, EventsSection, Testimonials, CTA, …)
- `components/layout/` — `SiteHeader`, `SiteFooter`, base `Layout`
- `components/ui/` — Reusable UI primitives (`Button`, `DecoratedText`, …)
- `components/forms/` — `ContactForm`, `PrayerForm`, `RsvpForm`, `LoginForm`, `ChangePasswordForm`
- `components/content/` — Cards (`SermonCard`, `EventCard`, `SeriesCard`, `LeaderCard`, …)
- `lib/` — `api.ts` (fetch client), `cn.ts` (class merge), `format.ts`, `seo.ts`, `site.ts`
- `types/` — Typed domain models mirroring the API

---

## Building & Deployment

### Frontend build
```bash
cd website
npm run build      # Output to ./dist/
npm run preview    # Preview the production build locally
npm run check      # Astro + TypeScript type check
```

Deploy `website/dist/` to **Vercel** (the `astro.config.mjs` `site` is set to `https://rpwebsite.vercel.app`). Define `PUBLIC_API_URL` in the Vercel project environment to point at the production API.

### Backend build
Run as a standard Django project behind a WSGI/ASGI server (e.g. Gunicorn / Uvicorn). Set `DEBUG=False`, a strong `SECRET_KEY`, correct `ALLOWED_HOSTS`, and PostgreSQL credentials. Run `migrate` and `collectstatic` during deployment.

---

## Documentation

The `docs/` directory contains detailed phase, migration, and audit reports generated during development:

- `PHASE_C1_IMPLEMENTATION_REPORT.md`
- `PHASE_C2_C3_REBUILD_REPORT.md`
- `PHASE_C2_C4_IMPLEMENTATION_REPORT.md`
- `PHASE_D1_TYPE_FIX_REPORT.md`
- `PHASE_D2_2_FULL_MIGRATION_AUDIT.md`
- `PHASE_D2_2A_FUNCTIONAL_PARITY_REPORT.md`
- `ASTRO_UI_MIGRATION_PLAN.md` / `ASTRO_UI_MIGRATION_INVENTORY.md`
- `API_BASE_URL_HARDENING_REPORT.md`
- `DEPENDENCY_AUDIT_REPORT.md`
- Plus several section parity / validation reports

---

## Contributing

This is a private repository managed by the Royal Priesthood Tech team.

Before working on the codebase, read the sibling guides at the repository root (`rpwebsite/`):

1. `AI_RULES.md` — AI agent instruction manual
2. `PROJECT_MEMORY.md` — Current project state
3. `TASKS.md` — Active development backlog
4. `CONTEXT.md` — Project context

### Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org):

```
feat(content): add sermon detail page
fix(events): correct event timezone handling
docs(api): document prayer endpoint
refactor(backend): simplify content repository