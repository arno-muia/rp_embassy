# API Schema Drift Audit

**Date:** 2026-07-21  
**Status:** Complete  
**Scope:** All models with stale migration references

---

## Drift Summary Table

| Model | Django Field | DB Column | Prisma Field | Status |
|-------|--------------|-----------|--------------|--------|
| **ChurchEvent** | `category` | ❌ Missing | ❌ Missing | **REMOVED** |
| **ChurchEvent** | `workflow_status` | ❌ Missing | ❌ Missing | **REMOVED** |
| **ChurchEvent** | `is_featured` | ❌ Missing | ❌ Missing | **REMOVED** |
| **ChurchEvent** | `rsvp_enabled` | ❌ Missing | ❌ Missing | **REMOVED** |
| **ChurchEvent** | `published_at` | ❌ Missing | ❌ Missing | **REMOVED** |
| **ChurchEvent** | `archived_at` | ❌ Missing | ❌ Missing | **REMOVED** |
| **WebsiteLeader** | `is_archived` | ❌ Missing | ❌ Missing | **REMOVED** |
| **PublicSermon** | `is_featured` | ❌ Missing | ❌ Missing | **REMOVED** |
| **PublicSermon** | `workflow_status` | ❌ Missing | ❌ Missing | **REMOVED** |
| **PublicSermon** | `published_at` | ❌ Missing | ❌ Missing | **REMOVED** |
| **PublicSermon** | `archived_at` | ❌ Missing | ❌ Missing | **REMOVED** |
| **SermonSeries** | `is_featured` | ❌ Missing | ❌ Missing | **REMOVED** |
| **SermonSeries** | `published_at` | ❌ Missing | ❌ Missing | **REMOVED** |
| **WebsiteAcademyModule** | `is_featured` | ❌ Missing | ❌ Missing | **REMOVED** |
| **WebsiteTestimonial** | `is_featured` | ❌ Missing | ❌ Missing | **REMOVED** |
| **WebsiteTestimonial** | `expiration_date` | ❌ Missing | ❌ Missing | **REMOVED** |
| **WebsiteTestimonial** | `archived_at` | ❌ Missing | ❌ Missing | **REMOVED** |

---

## Detailed Drift Matrix

### ChurchEvent Drift (6 fields)

| Django Field | DB Column | Prisma Column | Status |
|--------------|-----------|---------------|--------|
| `category` | ❌ Missing | ❌ Missing | REMOVED |
| `workflow_status` | ❌ Missing | ❌ Missing | REMOVED |
| `is_featured` | ❌ Missing | ❌ Missing | REMOVED |
| `rsvp_enabled` | ❌ Missing | ❌ Missing | REMOVED |
| `published_at` | ❌ Missing | ❌ Missing | REMOVED |
| `archived_at` | ❌ Missing | ❌ Missing | REMOVED |

**Severity:** CRITICAL  
**Affected endpoint:** `GET /api/events/`

### WebsiteLeader Drift (1 field)

| Django Field | DB Column | Prisma Column | Status |
|--------------|-----------|---------------|--------|
| `is_archived` | ❌ Missing | ❌ Missing | REMOVED |

**Severity:** CRITICAL  
**Affected endpoint:** `GET /api/leaders/`

### PublicSermon Drift (4 fields)

| Django Field | DB Column | Prisma Column | Status |
|--------------|-----------|---------------|--------|
| `is_featured` | ❌ Missing | ❌ Missing | REMOVED |
| `workflow_status` | ❌ Missing | ❌ Missing | REMOVED |
| `published_at` | ❌ Missing | ❌ Missing | REMOVED |
| `archived_at` | ❌ Missing | ❌ Missing | REMOVED |

**Severity:** LOW  
**Affected endpoint:** `GET /api/sermons/`

### SermonSeries Drift (2 fields)

| Django Field | DB Column | Prisma Column | Status |
|--------------|-----------|---------------|--------|
| `is_featured` | ❌ Missing | ❌ Missing | REMOVED |
| `published_at` | ❌ Missing | ❌ Missing | REMOVED |

**Severity:** LOW  
**Affected endpoint:** `GET /api/series/`

### WebsiteAcademyModule Drift (1 field)

| Django Field | DB Column | Prisma Column | Status |
|--------------|-----------|---------------|--------|
| `is_featured` | ❌ Missing | ❌ Missing | REMOVED |

**Severity:** LOW  
**Affected endpoint:** `GET /api/academy/`

### WebsiteTestimonial Drift (3 fields)

| Django Field | DB Column | Prisma Column | Status |
|--------------|-----------|---------------|--------|
| `is_featured` | ❌ Missing | ❌ Missing | REMOVED |
| `expiration_date` | ❌ Missing | ❌ Missing | REMOVED |
| `archived_at` | ❌ Missing | ❌ Missing | REMOVED |

**Severity:** LOW  
**Affected endpoint:** `GET /api/testimonials/`

---

## PostgreSQL Column Verification

### ChurchEvent Columns (verified)

| Column | Status |
|--------|--------|
| id | ✅ Present |
| title | ✅ Present |
| description | ✅ Present |
| type | ✅ Present |
| startDateTime | ✅ Present |
| endDateTime | ✅ Present |
| location | ✅ Present |
| imageUrl | ✅ Present |
| galleryUrl | ✅ Present |
| registrationRequired | ✅ Present |
| maxAttendees | ✅ Present |
| costCents | ✅ Present |
| registrationOpenDate | ✅ Present |
| status | ✅ Present |
| createdAt | ✅ Present |
| updatedAt | ✅ Present |
| createdById | ✅ Present |

### WebsiteLeader Columns (verified)

| Column | Status |
|--------|--------|
| id | ✅ Present |
| name | ✅ Present |
| role | ✅ Present |
| bio | ✅ Present |
| photoUrl | ✅ Present |
| sortOrder | ✅ Present |
| social | ✅ Present |
| isPublished | ✅ Present |
| createdAt | ✅ Present |
| updatedAt | ✅ Present |

---

## Source of Truth

Per `B1_MODEL_OWNERSHIP_MATRIX.md`:
- **Prisma schema** is authoritative for all legacy content models.
- Django models are projections only (`managed = False`).
- No Django migrations may touch Prisma-owned tables.

All removed fields were stale Django projection artifacts that never existed in the actual database schema.