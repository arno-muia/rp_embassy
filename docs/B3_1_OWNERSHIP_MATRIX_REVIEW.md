# B3.1 Ownership Matrix Review

**Phase:** B3.1 — Ownership Matrix Review  
**Date:** 2026-07-21  
**Status:** Complete  
**Related:** `RP/docs/B1_MODEL_OWNERSHIP_MATRIX.md`, `RP/docs/B3_1_OWNERSHIP_CONVERSION_AUDIT.md`

---

## Executive Summary

This document validates current ownership assumptions against PostgreSQL schema, Prisma schema references, and Django models. It identifies schema drift, missing constraints, unmanaged relationships, and ownership ambiguities that must be resolved before Prisma removal.

---

## 1. Ownership Validation Matrix

### 1.1 Current State Verification

| Model | Django Managed | DB Exists | Prisma Schema | Match Status |
|-------|----------------|-----------|---------------|------------|
| SystemConfig | False | ✅ Yes | Referenced | ✅ Valid |
| SermonSeries | False | ✅ Yes | Referenced | ✅ Valid |
| PublicSermon | False | ✅ Yes | Referenced | ✅ Valid |
| WebsiteLeader | False | ✅ Yes | Referenced | ⚠️ Schema Drift |
| WebsiteTestimonial | False | ✅ Yes | Referenced | ✅ Valid |
| WebsiteAcademyModule | False | ✅ Yes | Referenced | ✅ Valid |
| ContactSubmission | False | ✅ Yes | Referenced | ✅ Valid |
| VisitRsvp | False | ✅ Yes | Referenced | ✅ Valid |
| ChurchEvent | False | ✅ Yes | Referenced | ✅ Valid |
| EventRegistration | False | ✅ Yes | Referenced | ✅ Valid |
| User | False | ✅ Yes | Referenced | ✅ Valid |
| AuditLog | False | ✅ Yes | Referenced | ✅ Valid |
| Member | False | ✅ Yes | Referenced | ✅ Valid |
| Household | False | ✅ Yes | Referenced | ✅ Valid |
| HouseholdMember | False | ✅ Yes | Referenced | ✅ Valid |
| GivingTransaction | False | ✅ Yes | Referenced | ✅ Valid |
| PrayerSubmission | False | ✅ Yes | Referenced | ✅ Valid |

---

## 2. Schema Drift Analysis

### 2.1 Identified Schema Drift

| Model | Django Field | DB Column | Prisma Field | Severity |
|-------|--------------|-----------|--------------|----------|
| WebsiteLeader | `is_archived` | ❌ Missing | ❌ Missing | CRITICAL |

### 2.2 WebsiteLeader Detailed Analysis

**Current Django Model Fields:**
- `id` (UUID)
- `name` (CharField)
- `role` (CharField)
- `bio` (TextField)
- `photo_url` (CharField)
- `sort_order` (IntegerField)
- `social` (JSONField, nullable)
- `is_published` (BooleanField)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)
- `is_archived` — **EXTRA FIELD (NOT IN DB/PRISMA)**

**Database Columns (Confirmed):**
- `id`, `name`, `role`, `bio`, `photoUrl`, `sortOrder`, `social`, `isPublished`, `createdAt`, `updatedAt`

**Resolution Required:** Remove `is_archived` field from Django model before any ownership conversion.

---

## 3. Missing Constraints Analysis

### 3.1 Missing Foreign Key Constraints

All foreign key relationships are declared in Django models with `db_constraint=False`. This was intentional for managed=False models but represents unresolved referential integrity:

| Table | FK Column | Referenced Table | Currently Enforced |
|-------|-----------|------------------|-------------------|
| SystemConfig | updatedById | User | ❌ No |
| PublicSermon | seriesId | SermonSeries | ❌ No |
| ChurchEvent | createdById | User | ❌ No |
| EventRegistration | memberId | Member | ❌ No |
| EventRegistration | eventId | ChurchEvent | ❌ No |
| GivingTransaction | memberId | Member | ❌ No |
| GivingTransaction | householdId | Household | ❌ No |
| GivingTransaction | createdById | User | ❌ No |
| Member | householdId | Household | ❌ No |
| Member | userId | User | ❌ No |
| Member | createdById | User | ❌ No |
| Member | updatedById | User | ❌ No |
| Household | createdById | User | ❌ No |
| Household | updatedById | User | ❌ No |
| AuditLog | userId | User | ❌ No |

### 3.2 Recommendation

Upon conversion to `managed=True`, Django will attempt to create these constraints. This requires:
1. All referenced tables must be converted first or simultaneously
2. Constraint names must be unique across schema
3. Consider using `db_constraint=False` during transition if phased conversion is used

---

## 4. Unmanaged Relationship Analysis

### 4.1 Cross-Domain Dependencies

The following cross-app relationships exist:

| Source Model | Source App | Target Model | Target App | Conversion Impact |
|--------------|------------|--------------|------------|-------------------|
| PublicSermon.series | content | SermonSeries | content | Same app - safe |
| ChurchEvent.created_by | events | User | accounts | Cross-app dependency |
| EventRegistration.member | events | Member | members | Cross-app dependency |
| EventRegistration.event | events | ChurchEvent | events | Same app - safe |
| GivingTransaction.member | giving | Member | members | Cross-app dependency |
| GivingTransaction.household | giving | Household | members | Cross-app dependency |
| GivingTransaction.created_by | giving | User | accounts | Cross-app dependency |
| Member.household | members | Household | members | Same app - safe |
| Member.user | members | User | accounts | Cross-app dependency |
| SystemConfig.updated_by | content | User | accounts | Cross-app dependency |

### 4.2 Implications for Conversion Order

Cross-app dependencies require coordinated conversion:
1. **Accounts (User)** must be converted before or with content/giving events
2. **Members (Household/Member)** must be converted before GivingTransaction
3. **Content (SermonSeries)** must be converted before PublicSermon (if separate)

---

## 5. Ownership Ambiguities

### 5.1 Ambiguous Models

| Ambiguity | Current State | Resolution |
|-----------|---------------|------------|
| Who owns `isPublished`? | Prisma | Prisma |
| Who seeds `SystemConfig.key='site'`? | Prisma seed | Prisma |
| Who creates new sermons? | Currently read-only via API | Will become Django-managed |
| Who updates event status? | Currently read-only via API | Will become Django-managed |

### 5.2 Write Operations Current State

| Model | Has Write Serializer | Has ViewSet | Submission Endpoint | Admin Endpoint |
|-------|---------------------|-------------|---------------------|----------------|
| SystemConfig | ✅ Yes | ❌ No (function view) | ❌ No | ❌ No |
| SermonSeries | ✅ Yes | ✅ Yes (ReadOnly) | ❌ No | ❌ No |
| PublicSermon | ✅ Yes | ✅ Yes (ReadOnly) | ❌ No | ❌ No |
| WebsiteLeader | ✅ Yes | ✅ Yes (ReadOnly) | ❌ No | ❌ No |
| WebsiteTestimonial | ✅ Yes | ✅ Yes (ReadOnly) | ❌ No | ❌ No |
| WebsiteAcademyModule | ✅ Yes | ✅ Yes (ReadOnly) | ❌ No | ❌ No |
| ContactSubmission | ✅ Yes | ❌ No (function view) | ✅ POST /api/contact | ❌ No |
| VisitRsvp | ✅ Yes | ❌ No (function view) | ✅ POST /api/rsvp | ❌ No |
| ChurchEvent | ✅ Yes | ✅ Yes (ReadOnly) | ❌ No | ❌ No |
| EventRegistration | ✅ Yes | ❌ No | ❌ No | ❌ No |

---

## 6. GIN Index Ownership

### 6.1 Existing Indexes (B2.3)

The following GIN indexes were created during B2.3 PostgreSQL Full Text Search:

| Migration File | Table | Index Purpose | Ownership Status |
|----------------|-------|---------------|------------------|
| `0002_gin_search_indexes.py` (content) | PublicSermon | FTS on title, description, speaker, scripture | Applied to Prisma-owned table |
| `0002_gin_search_indexes.py` (events) | ChurchEvent | FTS on title, description, location | Applied to Prisma-owned table |
| `0002_gin_search_indexes.py` (prayer) | PrayerSubmission | FTS on name, request | Applied to Prisma-owned table |

### 6.2 Index Ownership Risk

These indexes were created by Django migrations but exist on Prisma-owned tables. Upon conversion:
- Django will attempt to recreate/drop these indexes
- Must ensure index definitions match exactly
- Risk of duplicate index creation or missing indexes

---

## 7. Admin Registration Status

### 7.1 Models Registered in Django Admin

| Model | Admin Registered | Source |
|-------|------------------|--------|
| User | ❌ No | accounts/models.py |
| AuditLog | ❌ No | accounts/models.py |
| Member | ❌ No | members/models.py |
| Household | ❌ No | members/models.py |
| HouseholdMember | ❌ No | members/models.py |
| GivingTransaction | ❌ No | giving/models.py |
| SystemConfig | ❌ No | content/models.py |
| SermonSeries | ❌ No | content/models.py |
| PublicSermon | ❌ No | content/models.py |
| WebsiteLeader | ❌ No | content/models.py |
| WebsiteTestimonial | ❌ No | content/models.py |
| WebsiteAcademyModule | ❌ No | content/models.py |
| ContactSubmission | ❌ No | content/models.py |
| VisitRsvp | ❌ No | content/models.py |
| ChurchEvent | ❌ No | events/models.py |
| EventRegistration | ❌ No | events/models.py |

### 7.2 Django-Owned Models (Already in Admin)

| Model | Admin Registered | Source |
|-------|------------------|--------|
| GlobalSettings | ❌ No (but managed=True) | content/models.py |
| HomepageSettings | ❌ No (but managed=True) | content/models.py |
| ChurchProfile | ❌ No (but managed=True) | content/models.py |
| ContentBlock | ❌ No (but managed=True) | content/models.py |
| ServiceTime | ❌ No (but managed=True) | content/models.py |
| Announcement | ❌ No (but managed=True) | events/models.py |
| MediaAsset | ❌ No (but managed=True) | media/models.py |
| PrayerRequest | ❌ No (but managed=True) | prayer/models.py |

---

## 8. Validation Summary

| Check | Result | Action Required |
|-------|--------|-----------------|
| All tables exist in PostgreSQL | ✅ Pass | None |
| Django models match DB schema | ⚠️ WebsiteLeader drift | Remove is_archived field |
| Foreign key relationships documented | ✅ Pass | None |
| GIN indexes exist on expected tables | ✅ Pass | Verify compatibility on conversion |
| Admin registrations consistent | ⚠️ None registered | Register post-conversion |
| Write operations documented | ✅ Pass | None |

---

## 9. Recommendations

### 9.1 Pre-Conversion Checklist

1. ✅ Remove `is_archived` field from WebsiteLeader model
2. ✅ Verify GIN index compatibility with Django's search vector fields
3. ✅ Document exact index definitions to preserve on conversion
4. ⚠️ Register all converted models in Django admin
5. ⚠️ Create admin views for WriteSerializer operations
6. ⚠️ Establish migration naming convention for ownership changes

### 9.2 Ownership Transition Validation

| Model | Can Convert Now | Blocker | Resolution |
|-------|-----------------|---------|------------|
| WebsiteAcademyModule | ✅ Yes | None | Proceed |
| WebsiteTestimonial | ✅ Yes | None | Proceed |
| VisitRsvp | ✅ Yes | None | Proceed |
| ContactSubmission | ✅ Yes | None | Proceed |
| PrayerSubmission | ✅ Yes | None | Proceed |
| SystemConfig | ⚠️ Caution | FK to User | Convert with User or after |
| SermonSeries | ✅ Yes | FK to none | Proceed |
| PublicSermon | ⚠️ Caution | FK to SermonSeries | Convert with SermonSeries |
| ChurchEvent | ⚠️ Caution | FK to User | Convert with User |
| WebsiteLeader | ❌ No | Schema drift | Fix schema drift first |
| EventRegistration | ⚠️ Caution | FKs to Member, ChurchEvent | Convert after dependencies |
| User | ❌ No | Auth critical | Leave for last |
| AuditLog | ❌ No | Auth critical | Leave for last |
| Member | ⚠️ Caution | FKs to User, Household | Convert after User |
| Household | ⚠️ Caution | FKs to User | Convert after User |
| HouseholdMember | ⚠️ Caution | FKs to Member, Household | Convert last |
| GivingTransaction | ⚠️ Caution | FKs to Member, Household, User | Convert last |