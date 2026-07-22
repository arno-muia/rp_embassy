# B3.1 Conversion Strategy

**Phase:** B3.1 — Conversion Strategy  
**Date:** 2026-07-21  
**Status:** Complete  
**Related:** `RP/docs/B3_1_OWNERSHIP_CONVERSION_AUDIT.md`, `RP/docs/B3_1_OWNERSHIP_MATRIX_REVIEW.md`

---

## Executive Summary

This document provides a phased migration strategy for converting Prisma-owned tables to Django ownership. The strategy is organized into three phases based on risk level and dependency complexity.

---

## Phase 1: Safest Models (Low Risk, No Cross-App Dependencies)

### Priority Order

| Order | Model | Table | Risk | Conversion Steps |
|-------|-------|-------|------|-----------------|
| 1 | WebsiteAcademyModule | WebsiteAcademyModule | LOW | Model change → Migration → Verify |
| 2 | WebsiteTestimonial | WebsiteTestimonial | LOW | Model change → Migration → Verify |
| 3 | ContactSubmission | ContactSubmission | LOW | Model change → Migration → Verify |
| 4 | VisitRsvp | VisitRsvp | LOW | Model change → Migration → Verify |
| 5 | PrayerSubmission | PrayerSubmission | LOW | Model change → Migration → Verify |
| 6 | SermonSeries | SermonSeries | MEDIUM | Model change → Migration → Verify |

### Phase 1 Conversion Steps

#### Step 1.1: WebsiteAcademyModule (Isolated Table)

**Prerequisites:** None

**Conversion Steps:**
1. Change `managed = False` to `managed = True` in `WebsiteAcademyModule.Meta`
2. Run `python manage.py makemigrations content` to create migration
3. Review migration - should produce `ALTER TABLE ... ALTER COLUMN ... SET NOT NULL` statements only
4. Apply migration: `python manage.py migrate content`
5. Verify API endpoint: `GET /api/academy` returns data
6. Verify frontend: academy page renders correctly

**Migration Requirements:**
- No data migration needed (table exists)
- Indexes will be claimed: `academy_sort_idx`

**Rollback Strategy:**
- Revert model to `managed = False`
- No database changes to revert

**Verification Requirements:**
- API endpoints functional
- Frontend renders correctly
- Admin can view records (after admin registration)

---

#### Step 1.2: WebsiteTestimonial

**Prerequisites:** None

**Conversion Steps:**
1. Change `managed = False` to `managed = True` in `WebsiteTestimonial.Meta`
2. Create migration
3. Apply migration
4. Verify: `GET /api/testimonials` endpoint
5. Verify frontend: testimonials section renders

---

#### Step 1.3: ContactSubmission

**Prerequisites:** None

**Conversion Steps:**
1. Change `managed = False` to `managed = True` in `ContactSubmission.Meta`
2. Create migration
3. Apply migration
4. Verify: `POST /api/contact` endpoint
5. Verify frontend: contact form submission works

---

#### Step 1.4: VisitRsvp

**Prerequisites:** None

**Conversion Steps:**
1. Change `managed = False` to `managed = True` in `VisitRsvp.Meta`
2. Create migration
3. Apply migration
4. Verify: `POST /api/rsvp` endpoint
5. Verify frontend: RSVP form submission works

---

#### Step 1.5: PrayerSubmission

**Prerequisites:** None

**Conversion Steps:**
1. Change `managed = False` to `managed = True` in `PrayerSubmission.Meta`
2. Create migration
3. Apply migration
4. Verify: `POST /api/prayer` endpoint
5. Verify frontend: prayer form submission works

---

#### Step 1.6: SermonSeries

**Prerequisites:** None (no incoming FKs from other apps)

**Conversion Steps:**
1. Change `managed = False` to `managed = True` in `SermonSeries.Meta`
2. Create migration
3. Apply migration
4. Verify: `GET /api/series` and `GET /api/series/:slug` endpoints
5. Verify: Sermon filtering by series works
6. Verify frontend: series pages render correctly

**Note:** PublicSermon has a FK to SermonSeries but with `db_constraint=False`, so can be converted independently.

---

## Phase 2: Medium-Risk Models (Cross-App FK Dependencies)

### Priority Order

| Order | Model | Table | Risk | Dependencies |
|-------|-------|-------|------|--------------|
| 1 | PublicSermon | PublicSermon | MEDIUM | SermonSeries FK |
| 2 | ChurchEvent | ChurchEvent | MEDIUM | User FK (accounts) |
| 3 | SystemConfig | SystemConfig | MEDIUM | User FK (accounts) |

### Phase 2 Prerequisites

- Phase 1 must be complete
- For ChurchEvent and SystemConfig: User model must be converted or kept unmanaged

### Phase 2 Conversion Steps

#### Step 2.1: PublicSermon

**Prerequisites:** SermonSeries converted (can be done simultaneously)

**Conversion Steps:**
1. Change `managed = False` to `managed = True` in `PublicSermon.Meta`
2. Create migration
3. Apply migration
4. Verify GIN search indexes exist and work
5. Verify: `GET /api/sermons` and `GET /api/sermons/:slug` endpoints
6. Verify frontend: sermon pages render correctly

**GIN Index Verification:**
```sql
-- Already exists from B2.3
CREATE INDEX IF NOT EXISTS sermon_search_idx ON "PublicSermon" 
USING GIN (to_tsvector('english', "title" || ' ' || "description"));
```

---

#### Step 2.2: ChurchEvent

**Prerequisites:** 
- Option A: User model also converted (higher risk)
- Option B: Keep `db_constraint=False` during conversion

**Conversion Steps (Option B recommended):**
1. Keep `db_constraint=False` on `created_by` FK
2. Change `managed = False` to `managed = True` in `ChurchEvent.Meta`
3. Create migration
4. Apply migration
5. Verify: `GET /api/events` and `GET /api/events/:id` endpoints
6. Verify frontend: events pages render correctly

---

#### Step 2.3: SystemConfig

**Prerequisites:**
- Option A: User model also converted
- Option B: Keep `db_constraint=False` on `updated_by` FK

**Conversion Steps:**
1. Keep `db_constraint=False` on `updated_by` FK
2. Change `managed = False` to `managed = True` in `SystemConfig.Meta`
3. Create migration
4. Apply migration
5. Verify: `GET /api/site-config` endpoint
6. Verify frontend: homepage loads correctly

---

## Phase 3: High-Risk Models (Authentication & Financial Critical)

### Priority Order

| Order | Model | Table | Risk | Dependencies |
|-------|-------|-------|------|--------------|
| 1 | User | User | HIGH | Authentication system |
| 2 | AuditLog | AuditLog | HIGH | Authentication logging |
| 3 | Household | Household | HIGH | User FK |
| 4 | Member | Member | HIGH | User, Household FKs |
| 5 | HouseholdMember | HouseholdMember | HIGH | Member, Household FKs |
| 6 | GivingTransaction | GivingTransaction | HIGH | Member, Household, User FKs |
| 7 | EventRegistration | EventRegistration | MEDIUM | Member, ChurchEvent FKs |

### Phase 3 Prerequisites

- Phases 1 & 2 complete
- Backup all authentication and financial data
- Schedule during low-traffic maintenance window

### Phase 3 Conversion Steps

#### Step 3.1: User & AuditLog (Authentication Critical)

**Risk:** Authentication system depends on this table

**Conversion Steps:**
1. Backup User and AuditLog tables
2. Change `managed = False` to `managed = True` for both models
3. Create migration
4. Apply migration during maintenance window
5. Run full authentication tests:
   - Login endpoint
   - Password change
   - User session management
6. Verify AuditLog entries are still being written

**Warning:** This is the most critical conversion. If issues arise, rollback immediately.

---

#### Step 3.2: Household → Member → HouseholdMember (Members Domain)

**Order:** Household → Member → HouseholdMember (respect FK dependencies)

**Conversion Steps:**
1. Convert Household (FK to User, keep `db_constraint=False` if User not yet managed)
2. Convert Member (FKs to User and Household)
3. Convert HouseholdMember (FKs to Member and Household)

---

#### Step 3.3: GivingTransaction (Financial Data)

**Prerequisites:** Member, Household, User converted

**Conversion Steps:**
1. Backup GivingTransaction table
2. Change `managed = False` to `managed = True`
3. Migrate all FK constraints with `db_constraint=False` initially
4. Run data validation queries
5. Verify: Giving reports and exports still work

---

#### Step 3.4: EventRegistration

**Prerequisites:** ChurchEvent converted, Member converted

**Conversion Steps:**
1. Convert with `db_constraint=False` on both FKs
2. Verify: Event registration workflows

---

## Migration Sequence Diagram

```
Phase 1 (Low Risk)           Phase 2 (Medium)          Phase 3 (High Risk)
┌─────────────────┐          ┌─────────────────┐       ┌─────────────────┐
│ AcademyModule   │          │ PublicSermon    │       │ User/Auth       │
│ Testimonial     │          │ ChurchEvent     │       │ AuditLog        │
│ ContactSubmit   │          │ SystemConfig    │       │ Household       │
│ VisitRsvp       │          │                 │       │ Member          │
│ PrayerSubmit    │          │                 │       │ HouseholdMember │
│ SermonSeries    │          │                 │       │ GivingTrans     │
└─────────────────┘          └─────────────────┘       │ EventReg        │
                                                        └─────────────────┘
```

---

## Rollback Strategy

### General Rollback Approach

For each model conversion:
```python
# Revert model
managed = False

# If migration added constraints that need removal:
# Create a new migration to drop the constraints
python manage.py migrate content <previous_migration>
```

### Critical Rollback (User/Auth)

If User model conversion fails:
1. Immediately switch to backup database
2. Revert model to `managed = False`
3. Restore from backup: `pg_restore --table=User backup.sql`
4. Investigate authentication issues

---

## Verification Requirements

### Post-Conversion Verification

| Check | Tool | Success Criteria |
|-------|------|------------------|
| API Endpoint Health | curl | 200 OK on all endpoints |
| Frontend Rendering | Browser | Pages load without errors |
| GIN Search Indexes | psql | Indexes exist and functional |
| FK Constraints | psql | Constraints created correctly |
| Admin Access | Browser | Models visible in admin |
| Write Operations | API Tests | POST/PUT/PATCH work |

### Verification Commands

```bash
# API health check
curl -s http://localhost:8000/api/health | jq

# Sermons endpoint
curl -s http://localhost:8000/api/sermons | jq '.count'

# Events endpoint  
curl -s http://localhost:8000/api/events | jq '.count'

# Database index check
psql -d RP -c "\di *gin*" | grep -E "(PublicSermon|ChurchEvent|PrayerSubmission)"
```

---

## Timeline Estimate

| Phase | Models | Estimated Time | Downtime Required |
|-------|--------|---------------|-------------------|
| Phase 1 | 6 models | 2-4 hours | No |
| Phase 2 | 3 models | 4-6 hours | No (or minimal) |
| Phase 3 | 7 models | 6-12 hours | Yes (maintenance window) |

**Total Estimated Conversion Time: 12-22 hours**

---

## Go/No-Go Decision Matrix

| Criterion | Pass | Block |
|-----------|------|-------|
| WebsiteLeader schema drift fixed | ✅ GO | ❌ NO-GO |
| All GIN indexes documented | ✅ GO | ⚠️ REVIEW |
| Backup strategy verified | ✅ GO | ❌ NO-GO |
| Testing environment available | ✅ GO | ⚠️ GO WITH CONDITIONS |
| Maintenance window scheduled (Phase 3) | ✅ GO | ⚠️ GO WITH CONDITIONS |

**Recommended Status: GO WITH CONDITIONS**

Conditions:
1. Fix WebsiteLeader schema drift before Phase 1
2. Schedule maintenance window for Phase 3
3. Complete full data backup before Phase 3