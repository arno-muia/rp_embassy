# B3.1 Ownership Conversion Audit

**Phase:** B3.1 — Prisma → Django Ownership Conversion Audit  
**Date:** 2026-07-21  
**Status:** Complete  
**Related:** `RP/docs/B1_MODEL_OWNERSHIP_MATRIX.md`, `RP/docs/B2_2_SCHEMA_DRIFT_AUDIT.md`

---

## Executive Summary

This audit identifies and documents all Prisma-owned tables currently exposed through Django `managed=False` models, analyzing their readiness for ownership conversion to Django. The audit reveals **8 legacy Prisma-owned tables** with varying degrees of conversion readiness.

### Key Findings

| Finding | Count | Status |
|---------|-------|--------|
| Prisma-owned tables audited | 8 | ✅ Complete |
| Tables with schema drift (blocker) | 1 | ⚠️ WebsiteLeader |
| Tables with complex FK relationships | 4 | ChurchEvent, EventRegistration, PublicSermon, GivingTransaction |
| Tables consumed by frontend | 6 | PublicSermon, SermonSeries, ChurchEvent, WebsiteLeader, WebsiteTestimonial, WebsiteAcademyModule, VisitRsvp |
| Tables with submission endpoints | 3 | ContactSubmission, VisitRsvp, PrayerSubmission |
| Django-owned models (already managed=True) | 6 | GlobalSettings, HomepageSettings, ChurchProfile, ContentBlock, ServiceTime, MediaAsset, Announcement, PrayerRequest |

---

## 1. Prisma-Owned Table Inventory

### 1.1 Content Domain Models (`backend/apps/content/models.py`)

| Model | Table | PK | Fields | Status |
|-------|-------|-----|--------|--------|
| SystemConfig | SystemConfig | UUID | 6 | ✅ Ready |
| SermonSeries | SermonSeries | UUID | 9 | ✅ Ready |
| PublicSermon | PublicSermon | UUID | 17 | ⚠️ Pending |
| WebsiteLeader | WebsiteLeader | UUID | 10 | ❌ Schema Drift |
| WebsiteTestimonial | WebsiteTestimonial | UUID | 10 | ✅ Ready |
| WebsiteAcademyModule | WebsiteAcademyModule | UUID | 9 | ✅ Ready |
| ContactSubmission | ContactSubmission | UUID | 5 | ✅ Ready |
| VisitRsvp | VisitRsvp | UUID | 9 | ✅ Ready |

### 1.2 Events Domain Models (`backend/apps/events/models.py`)

| Model | Table | PK | Fields | Status |
|-------|-------|-----|--------|--------|
| ChurchEvent | ChurchEvent | UUID | 14 | ✅ Ready |
| EventRegistration | EventRegistration | UUID | 12 | ✅ Ready |

### 1.3 Accounts Domain Models (`backend/apps/accounts/models.py`)

| Model | Table | PK | Fields | Status |
|-------|-------|-----|--------|--------|
| User | User | UUID | 12 | ⚠️ Auth Critical |
| AuditLog | AuditLog | String | 10 | ⚠️ Auth Critical |

### 1.4 Members Domain Models (`backend/apps/members/models.py`)

| Model | Table | PK | Fields | Status |
|-------|-------|-----|--------|--------|
| Member | Member | UUID | 20 | ⚠️ Complex Relationships |
| Household | Household | UUID | 9 | ⚠️ Complex Relationships |
| HouseholdMember | HouseholdMember | UUID | 6 | ⚠️ Complex Relationships |

### 1.5 Giving Domain Models (`backend/apps/giving/models.py`)

| Model | Table | PK | Fields | Status |
|-------|-------|-----|--------|--------|
| GivingTransaction | GivingTransaction | UUID | 17 | ⚠️ Financial Data |

### 1.6 Prayer Domain Models (`backend/apps/prayer/models.py`)

| Model | Table | PK | Fields | Status |
|-------|-------|-----|--------|--------|
| PrayerSubmission | PrayerSubmission | UUID | 3 | ✅ Ready |

---

## 2. Database Structure Analysis

### 2.1 SystemConfig

**Table:** `SystemConfig`  
**Primary Key:** `id` (UUID)  
**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NOT NULL | gen_random_uuid() |
| key | varchar(255) | NOT NULL | - |
| value | jsonb | NOT NULL | - |
| description | varchar(2000) | NULL | NULL |
| updatedAt | timestamp | NOT NULL | - |
| updatedById | uuid | NULL | NULL |

**Constraints:**
- Primary key on `id`
- Unique constraint on `key`
- Foreign key to `User.id` (db_constraint=False in Django)

**Indexes:**
- `syscfg_key_idx` on `key`

### 2.2 SermonSeries

**Table:** `SermonSeries`  
**Primary Key:** `id` (UUID)  
**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NOT NULL | gen_random_uuid() |
| slug | varchar(255) | NOT NULL | - |
| title | varchar(255) | NOT NULL | - |
| description | text | NOT NULL | - |
| imageUrl | varchar(512) | NOT NULL | - |
| sermonCount | integer | NOT NULL | 0 |
| sortOrder | integer | NOT NULL | 0 |
| isPublished | boolean | NOT NULL | true |
| createdAt | timestamp | NOT NULL | - |
| updatedAt | timestamp | NOT NULL | - |

**Constraints:**
- Primary key on `id`
- Unique constraint on `slug`

### 2.3 PublicSermon

**Table:** `PublicSermon`  
**Primary Key:** `id` (UUID)  
**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NOT NULL | gen_random_uuid() |
| slug | varchar(255) | NOT NULL | - |
| title | varchar(255) | NOT NULL | - |
| description | text | NOT NULL | - |
| seriesId | uuid | NULL | NULL |
| seriesSlug | varchar(255) | NOT NULL | - |
| seriesTitle | varchar(255) | NOT NULL | - |
| scripture | varchar(255) | NULL | NULL |
| speaker | varchar(255) | NOT NULL | - |
| date | timestamp | NOT NULL | - |
| videoUrl | varchar(512) | NOT NULL | - |
| audioUrl | varchar(512) | NULL | NULL |
| notesUrl | varchar(512) | NULL | NULL |
| thumbnailUrl | varchar(512) | NOT NULL | - |
| duration | varchar(64) | NULL | NULL |
| tags | jsonb | NOT NULL | '[]' |
| isPublished | boolean | NOT NULL | true |
| createdAt | timestamp | NOT NULL | - |
| updatedAt | timestamp | NOT NULL | - |

**Constraints:**
- Primary key on `id`
- Unique constraint on `slug`
- Foreign key to `SermonSeries.id` (db_constraint=False)

### 2.4 WebsiteLeader (BLOCKER: Schema Drift)

**Table:** `WebsiteLeader`  
**Primary Key:** `id` (UUID)  
**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NOT NULL | gen_random_uuid() |
| name | varchar(255) | NOT NULL | - |
| role | varchar(255) | NOT NULL | - |
| bio | text | NOT NULL | - |
| photoUrl | varchar(512) | NOT NULL | - |
| sortOrder | integer | NOT NULL | 0 |
| social | jsonb | NULL | NULL |
| isPublished | boolean | NOT NULL | true |
| createdAt | timestamp | NOT NULL | - |
| updatedAt | timestamp | NOT NULL | - |

**Critical Issue:** Django model declares `is_archived` field which does NOT exist in database.

### 2.5 ChurchEvent

**Table:** `ChurchEvent`  
**Primary Key:** `id` (UUID)  
**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NOT NULL | gen_random_uuid() |
| title | varchar(255) | NOT NULL | - |
| description | text | NULL | NULL |
| type | varchar(20) | NOT NULL | - |
| startDateTime | timestamp | NOT NULL | - |
| endDateTime | timestamp | NULL | NULL |
| location | varchar(255) | NULL | NULL |
| imageUrl | varchar(512) | NULL | NULL |
| galleryUrl | varchar(512) | NULL | NULL |
| registrationRequired | boolean | NOT NULL | false |
| maxAttendees | integer | NULL | NULL |
| costCents | integer | NULL | NULL |
| registrationOpenDate | timestamp | NULL | NULL |
| status | varchar(20) | NOT NULL | 'DRAFT' |
| createdAt | timestamp | NOT NULL | - |
| updatedAt | timestamp | NOT NULL | - |
| createdById | uuid | NULL | NULL |

**Constraints:**
- Primary key on `id`
- Foreign key to `User.id` (db_constraint=False)

### 2.6 VisitRsvp

**Table:** `VisitRsvp`  
**Primary Key:** `id` (UUID)  
**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NOT NULL | gen_random_uuid() |
| name | varchar(255) | NOT NULL | - |
| phone | varchar(64) | NOT NULL | - |
| email | varchar(255) | NULL | NULL |
| partySize | integer | NOT NULL | 1 |
| firstVisit | boolean | NOT NULL | true |
| visitDate | timestamp | NULL | NULL |
| notes | text | NULL | NULL |
| status | varchar(32) | NOT NULL | 'PENDING' |
| createdAt | timestamp | NOT NULL | - |

### 2.7 WebsiteTestimonial

**Table:** `WebsiteTestimonial`  
**Primary Key:** `id` (UUID)  
**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NOT NULL | gen_random_uuid() |
| quote | text | NOT NULL | - |
| name | varchar(255) | NOT NULL | - |
| role | varchar(255) | NULL | NULL |
| photoUrl | varchar(512) | NULL | NULL |
| sortOrder | integer | NOT NULL | 0 |
| isPublished | boolean | NOT NULL | true |
| createdAt | timestamp | NOT NULL | - |
| updatedAt | timestamp | NOT NULL | - |

### 2.8 WebsiteAcademyModule

**Table:** `WebsiteAcademyModule`  
**Primary Key:** `id` (UUID)  
**Columns:**

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NOT NULL | gen_random_uuid() |
| title | varchar(255) | NOT NULL | - |
| description | text | NOT NULL | - |
| instructor | varchar(255) | NOT NULL | - |
| lessonsCount | integer | NOT NULL | - |
| duration | varchar(64) | NOT NULL | - |
| sortOrder | integer | NOT NULL | 0 |
| isPublished | boolean | NOT NULL | true |
| createdAt | timestamp | NOT NULL | - |
| updatedAt | timestamp | NOT NULL | - |

---

## 3. Django Projection Analysis

### 3.1 Model Locations

| Model | File Path | Managed Status |
|-------|-----------|----------------|
| SystemConfig | `backend/apps/content/models.py` | False |
| SermonSeries | `backend/apps/content/models.py` | False |
| PublicSermon | `backend/apps/content/models.py` | False |
| WebsiteLeader | `backend/apps/content/models.py` | False |
| WebsiteTestimonial | `backend/apps/content/models.py` | False |
| WebsiteAcademyModule | `backend/apps/content/models.py` | False |
| ContactSubmission | `backend/apps/content/models.py` | False |
| VisitRsvp | `backend/apps/content/models.py` | False |
| ChurchEvent | `backend/apps/events/models.py` | False |
| EventRegistration | `backend/apps/events/models.py` | False |
| User | `backend/apps/accounts/models.py` | False |
| AuditLog | `backend/apps/accounts/models.py` | False |
| Member | `backend/apps/members/models.py` | False |
| Household | `backend/apps/members/models.py` | False |
| HouseholdMember | `backend/apps/members/models.py` | False |
| GivingTransaction | `backend/apps/giving/models.py` | False |
| PrayerSubmission | `backend/apps/prayer/models.py` | False |

### 3.2 Field Mapping Verification

All models use explicit `db_column` parameters matching Prisma camelCase to Django snake_case convention. Foreign keys consistently use `db_constraint=False` to avoid Django attempting to create constraints on unmanaged tables.

### 3.3 Managers

All models use default Django manager (`objects`). No custom managers defined.

### 3.4 Serializers

Each Prisma-owned model has corresponding Read/Write serializers:

| Model | Read Serializer | Write Serializer |
|-------|-----------------|------------------|
| SystemConfig | SystemConfigReadSerializer | SystemConfigWriteSerializer |
| SermonSeries | SermonSeriesReadSerializer | SermonSeriesWriteSerializer |
| PublicSermon | PublicSermonReadSerializer | PublicSermonWriteSerializer |
| WebsiteLeader | WebsiteLeaderReadSerializer | WebsiteLeaderWriteSerializer |
| WebsiteTestimonial | WebsiteTestimonialReadSerializer | WebsiteTestimonialWriteSerializer |
| WebsiteAcademyModule | WebsiteAcademyModuleReadSerializer | WebsiteAcademyModuleWriteSerializer |
| ContactSubmission | ContactSubmissionReadSerializer | ContactSubmissionWriteSerializer |
| VisitRsvp | VisitRsvpReadSerializer | VisitRsvpWriteSerializer |
| ChurchEvent | ChurchEventReadSerializer | ChurchEventWriteSerializer |
| EventRegistration | EventRegistrationReadSerializer | EventRegistrationWriteSerializer |
| PrayerSubmission | PrayerSubmissionWriteSerializer | - |

### 3.5 ViewSets

| Model | ViewSet | Endpoints |
|-------|---------|-----------|
| PublicSermon | SermonViewSet | GET /api/sermons, GET /api/sermons/:slug |
| SermonSeries | SeriesViewSet | GET /api/series, GET /api/series/:slug |
| ChurchEvent | EventViewSet | GET /api/events, GET /api/events/:id |
| WebsiteLeader | LeaderViewSet | GET /api/leaders |
| WebsiteTestimonial | TestimonialViewSet | GET /api/testimonials |
| WebsiteAcademyModule | AcademyModuleViewSet | GET /api/academy |
| SystemConfig | Function view | GET /api/site-config |
| ContactSubmission | Function view | POST /api/contact |
| VisitRsvp | Function view | POST /api/rsvp |

---

## 4. Dependency Analysis

### 4.1 Foreign Key Relationships

| Model | FK Field | Target Model | Constraint Status |
|--------|----------|--------------|-------------------|
| SystemConfig | updated_by | accounts.User | db_constraint=False |
| PublicSermon | series | content.SermonSeries | db_constraint=False |
| ChurchEvent | created_by | accounts.User | db_constraint=False |
| EventRegistration | member | members.Member | db_constraint=False |
| EventRegistration | event | events.ChurchEvent | db_constraint=False |
| GivingTransaction | member | members.Member | db_constraint=False |
| GivingTransaction | household | members.Household | db_constraint=False |
| GivingTransaction | created_by | accounts.User | db_constraint=False |
| Member | household | members.Household | db_constraint=False |
| Member | user | accounts.User | db_constraint=False |
| Member | created_by | accounts.User | db_constraint=False |
| Member | updated_by | accounts.User | db_constraint=False |
| Household | created_by | accounts.User | db_constraint=False |
| Household | updated_by | accounts.User | db_constraint=False |
| AuditLog | user | accounts.User | db_constraint=False |

### 4.2 Frontend Consumers

| Model | Pages | Components |
|-------|-------|------------|
| PublicSermon | sermons.astro, sermons/[slug].astro | SermonCard |
| SermonSeries | series.astro, series/[slug].astro | SeriesCard |
| ChurchEvent | events.astro, events/[id].astro | EventCard |
| WebsiteLeader | about.astro | LeaderCard |
| WebsiteTestimonial | index.astro, testimonials section | TestimonialCard |
| WebsiteAcademyModule | academy.astro | AcademyModuleCard |
| VisitRsvp | visit.astro | RsvpForm |
| ContactSubmission | contact.astro | ContactForm |

### 4.3 API Consumers

All Prisma-owned models are consumed via:
- Astro frontend (`website/src/lib/api.ts`) - primary consumer
- Admin endpoints defined in API contract matrix (read-only for now)

---

## 5. Ownership Conversion Feasibility

### 5.1 Conversion Complexity Assessment

| Model | Complexity | Rationale |
|-------|------------|-----------|
| WebsiteAcademyModule | LOW | Simple table, no FKs, minimal frontend impact |
| WebsiteTestimonial | LOW | Simple table, no FKs, moderate frontend impact |
| VisitRsvp | LOW | Simple table, no FKs, submission endpoint exists |
| ContactSubmission | LOW | Simple table, no FKs, submission endpoint exists |
| SystemConfig | MEDIUM | Has FK to User, singleton-like usage |
| SermonSeries | MEDIUM | Has FK from PublicSermon, denormalized data in PublicSermon |
| PublicSermon | MEDIUM | Has FK to SermonSeries, denormalized seriesSlug/seriesTitle |
| ChurchEvent | MEDIUM | Has FK from EventRegistration, status workflows |
| EventRegistration | HIGH | Two FKs, event registration workflows |
| PrayerSubmission | LOW | Simple table, submission endpoint |
| User | HIGH | Authentication-critical, session management |
| AuditLog | HIGH | Auth-critical, logging infrastructure |
| Member | HIGH | Complex member/household relationships |
| Household | HIGH | Multi-FK relationships |
| HouseholdMember | HIGH | Bridge table for household relationships |
| GivingTransaction | HIGH | Financial data, complex FK relationships |

---

## 6. Blockers and Risks

### 6.1 Critical Blockers

1. **WebsiteLeader Schema Drift**: The `is_archived` field exists in Django model but not in database. Must be removed before conversion.

### 6.2 Dependencies for Resolution

- Remove `is_archived` field from WebsiteLeader Django model before B3.2
- Verify existing GIN indexes remain compatible with Django-managed schema
- Confirm Prisma no longer managing any schema changes before cutover

---

## 7. Recommendations

### 7.1 Immediate Actions

1. Fix WebsiteLeader schema drift (remove `is_archived` field from model)
2. Verify all column types match Django field types exactly
3. Test write operations on all tables before migration

### 7.2 Conversion Readiness

| Category | Models | Status |
|----------|--------|--------|
| Ready for Immediate Conversion | AcademyModule, Testimonial, VisitRsvp, ContactSubmission, PrayerSubmission | ✅ |
| Ready for Phase 1 (Safest) | SystemConfig, SermonSeries, PublicSermon, ChurchEvent | ✅ |
| Requires Special Handling | EventRegistration, Member, Household, HouseholdMember, GivingTransaction, User, AuditLog | ⚠️