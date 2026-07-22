# B3.4A — Prisma Dependency Audit

**Project:** Royal Priesthood Embassy Website  
**Audit Date:** 2026-07-22  
**Repository:** rpwebsite/apps/web  
**Objective:** Identify all Prisma dependencies for removal in favor of Django + PostgreSQL

---

## Executive Summary

Prisma is actively used as the primary ORM for the frontend Next.js application. The `website/` Astro project does NOT use Prisma. The `apps/web/` Next.js project contains significant Prisma dependencies including schema, client, scripts, and API integrations.

---

## 1. Prisma Files Found

### Location: `rpwebsite/apps/web/prisma/`

| File | Purpose | Removal Complexity |
|------|---------|------------------|
| `schema.prisma` | Prisma schema definition (1145 lines) defining 34 models total | **HIGH** - Must be migrated to Django models |
| `seed.ts` | Database seeding script using Prisma client | **MEDIUM** - Replace with Django management command |
| `turso-client.ts` | Prisma client singleton for Turso LibSQL | **HIGH** - Critical Prisma integration |

### Prisma Schema Models (34 total)

**Core Identity Domain:**
- User
- Member

**Household Domain:**
- Household
- HouseholdMember

**Attendance & Sessions:**
- ServiceSession
- Attendance
- Visitor

**Follow-up:**
- FollowUp

**Cell Groups:**
- CellGroup
- CellGroupMembership

**Giving:**
- GivingTransaction
- GivingCampaign

**Discipleship (LMS):**
- DiscipleshipModule
- DiscipleshipLesson
- MemberProgress
- Quiz
- QuizQuestion

**Events:**
- ChurchEvent
- EventRegistration

**Volunteers:**
- VolunteerRole
- VolunteerAssignment

**Pastoral Care:**
- CareCase
- CareNote

**Communications:**
- Announcement
- MessageLog

**Prayer:**
- PrayerRequest

**Audit & System:**
- AuditLog
- SystemConfig

**Public Website Content:**
- SermonSeries
- PublicSermon
- WebsiteLeader
- WebsiteTestimonial
- WebsiteAcademyModule
- ContactSubmission
- PrayerSubmission
- VisitRsvp

---

## 2. Prisma Imports Found

### Location: `rpwebsite/apps/web/src/lib/prisma.ts`
- **Primary Prisma client singleton** - 138 lines of Prisma integration
- Imports `PrismaClient` from `@prisma/client`
- Imports `PrismaLibSQL` from `@prisma/adapter-libsql`
- Contains lazy initialization and Turso connection logic

### Location: `rpwebsite/apps/web/src/app/api/health/route.ts`
- `import { getPrisma } from "@/lib/prisma"`
- Uses `getPrisma().$queryRaw` for database connectivity check

### Location: `rpwebsite/apps/web/src/app/api/contact/route.ts`
- `import { getPrisma } from "@/lib/prisma"`
- Uses `getPrisma().contactSubmission.create()` for form submissions

### Source Files Using Prisma Client (Inferred)
Based on the schema and patterns observed, the following would require Prisma imports:
- Sermons pages (PublicSermon queries)
- Events pages (ChurchEvent queries)
- Prayer submission endpoints
- RSVP endpoints
- Academy pages (WebsiteAcademyModule queries)
- Leadership/about pages (WebsiteLeader queries)

---

## 3. Prisma Packages Found

### Location: `rpwebsite/apps/web/package.json`

**Dependencies:**
| Package | Version | Purpose |
|---------|---------|---------|
| `@prisma/client` | ^6.6.0 | Prisma ORM client |
| `@prisma/adapter-libsql` | ^6.6.0 | Turso LibSQL adapter |

**DevDependencies:**
| Package | Version | Purpose |
|---------|---------|---------|
| `prisma` | ^6.6.0 | Prisma CLI tool |

### Location: `rpwebsite/package-lock.json`
- Confirms `@prisma/client@^6.6.0` as workspace dependency
- Confirms `prisma@^6.6.0` dev dependency

---

## 4. Prisma Scripts Found

### Location: `rpwebsite/apps/web/package.json`

```json
"scripts": {
  "build": "prisma generate && next build",
  "db:generate": "prisma generate",
  "db:push": "prisma db push",
  "db:migrate": "prisma db push",
  "db:push:turso": "npx tsx scripts/db-push-turso.ts",
  "db:seed": "npx tsx prisma/seed.ts",
  "db:setup": "npm run db:push:turso && npm run db:seed",
  "db:studio": "prisma studio"
}
```

### Location: `rpwebsite/apps/web/scripts/db-push-turso.ts`
- Uses `execSync` with `npx prisma migrate diff` for Turso deployment

---

## 5. Prisma Deployment Dependencies Found

### Location: `rpwebsite/apps/web/.env.example`
```
DATABASE_URL="file:./prisma/dev.db"
TURSO_DATABASE_URL="libsql://rpwebsite-YOURORG.aws-eu-west-1.turso.io"
TURSO_AUTH_TOKEN="your-turso-token"
DATABASE_AUTH_TOKEN="your-turso-token"
```

### Location: `rpwebsite/apps/web/.env`
```
DATABASE_URL="postgresql://postgres:arno@localhost:5432/RP?schema=public"
```

### Location: `rpwebsite/apps/web/vercel.json`
- No explicit Prisma commands in Vercel config
- Headers configured for `connect-src` including `https://*.turso.io`

---

## 6. Prisma Documentation References Found

### Location: `rpwebsite/README.md`
- Line 45: `| **ORM** | Prisma 6 |`
- Lines 73-76: Database setup instructions using Prisma commands
- Lines 109-116: Database commands documentation referencing Prisma
- Line 141: Reference to `prisma/` folder in directory structure

---

## 7. Risk Assessment for Removal

### Critical Prisma-Dependent Components

| Component | Risk Level | Justification |
|-----------|------------|---------------|
| `schema.prisma` | HIGH | Defines complete data model; requires Django migration |
| `src/lib/prisma.ts` | HIGH | Core database connection layer; requires Django ORM replacement |
| API endpoints (contact, health, prayer, rsvp) | HIGH | Direct Prisma queries; requires Django view replacement |
| Seeding scripts | MEDIUM | Can be replaced with Django management commands |
| Public content pages | HIGH | Query Prisma models; require Django ORM integration |

### Infrastructure Dependencies

| Item | Risk Level | Notes |
|------|------------|-------|
| Turso LibSQL | HIGH | Tied to Prisma adapter; requires PostgreSQL connection |
| NextAuth authentication | HIGH | Uses Prisma adapter; requires Django session backend |
| Rate limiting (Upstash) | LOW | Independent of Prisma |
| Vercel deployment | MEDIUM | Build command runs `prisma generate` |

---

## 8. Removal Readiness Assessment

| Item | Removal Complexity | Required Actions |
|------|------------------|------------------|
| `prisma/schema.prisma` | High | Full schema migration to Django models |
| `prisma/seed.ts` | Medium | Replace with Django data migration/management command |
| `prisma/turso-client.ts` | High | Replace with Django database backend |
| `src/lib/prisma.ts` | High | Replace with Django ORM integration |
| API routes using Prisma | High | Rewrite to use Django REST API or direct ORM |
| Package dependencies | Low | Remove from package.json |
| Build/postinstall scripts | Low | Remove `prisma generate` hooks |
| Environment variables | Medium | Replace DATABASE_URL with Django database config |

---

## 9. Key Findings

1. **Two separate frontend codebases exist:**
   - `/rpwebsite/website/` (Astro) - **NO Prisma usage**
   - `/rpwebsite/apps/web/` (Next.js) - **Active Prisma integration**

2. **Prisma is deeply integrated:**
   - Database schema defines 34 models
   - Client singleton with Turso LibSQL adapter
   - API endpoints directly query Prisma
   - Build process requires Prisma generation

3. **Current configuration mismatch:**
   - `.env` uses PostgreSQL connection URL
   - Schema configured for PostgreSQL in datasource
   - But code uses Turso LibSQL adapter

4. **Django backend exists:**
   - `/rpwebsite/RP/backend/` contains Django application
   - Models already defined in `backend/apps/*/models.py`
   - Admin integration completed (per B3.3 documentation)

---

## Final Conclusion

**NOT READY FOR B3.4B PRISMA USAGE REMOVAL**

The `apps/web/` Next.js application has extensive Prisma integration that cannot be safely removed without:

1. **Critical data model migration** - All 34 Prisma models need equivalent Django models with data migration
2. **API route rewrite** - All API endpoints using Prisma client must be converted to Django REST Framework or removed
3. **Frontend data layer change** - All database queries in React components must switch to Django API endpoints
4. **Build process update** - Remove `prisma generate` from build pipeline
5. **Authentication refactoring** - NextAuth with Prisma adapter needs Django session integration

The Django backend (`RP/backend/`) is prepared with models and admin integration, but the Next.js frontend still relies entirely on Prisma for database operations. The Astro `website/` project is independent and already Prisma-free.

**Recommendation:** Complete full-stack migration before removing Prisma. Either:
- Migrate Next.js to use Django REST API endpoints, OR
- Migrate Next.js to Django templates with server-side rendering