# B2.1 Schema Hardening & Ownership Implementation Plan

**Date:** 2026-07-20
**Phase:** B2.1 — Schema Hardening & Ownership Implementation
**Status:** Implementation Plan (Ready)
**Governed By:** All B1 architecture documents

---

## 1. Pre-Implementation Verification

### 1.1 Model Ownership Verification

| Model | File | Declared | Arch Docs Say | Verdict |
|-------|------|----------|---------------|---------|
| SystemConfig | content/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| SermonSeries | content/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| PublicSermon | content/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| WebsiteLeader | content/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| WebsiteTestimonial | content/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| WebsiteAcademyModule | content/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| ContactSubmission | content/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| VisitRsvp | content/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| ChurchEvent | events/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| EventRegistration | events/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| PrayerSubmission | prayer/models.py | managed=False | Prisma-owned | ✅ Correct, leave untouched |
| GlobalSettings | content/models.py | managed=True | Django-owned | ✅ Correct |
| HomepageSettings | content/models.py | managed=True | Django-owned | ✅ Correct |
| ChurchProfile | content/models.py | managed=True | Django-owned | ✅ Correct |
| ContentBlock | content/models.py | managed=True | Django-owned | ✅ Needs enhancement (missing fields) |
| Announcement | events/models.py | managed=True | Django-owned | ✅ Correct |
| PrayerRequest | prayer/models.py | managed=True | Django-owned | ✅ Correct |
| MediaAsset | media/models.py | managed=True | Django-owned | ✅ Needs enhancement (missing governance fields) |

### 1.2 Models to Create (Missing)

| Model | File | Purpose |
|-------|------|---------|
| HomepageSection | content/models.py | Homepage section visibility/ordering |
| ServiceTime | content/models.py | Service time entries with display_order |

### 1.3 No Ownership Conflicts Detected

- All Prisma-owned models correctly use `managed=False` with exact `db_table` names.
- All Django-owned models correctly use `managed=True`.
- No model is declared as both managed and unmanaged.
- No migration will touch Prisma-owned tables (Django respects `managed=False`).

**Verdict: Safe to proceed with migration generation.**

---

## 2. Implementation Order

### Step 1: Enhance ContentBlock — Add missing fields
- Add `content_type` with choices (BELIEF, VALUE, FAQ, EXPECTATION, PAGE_SECTION, THEME)
- Add `display_order`
- Add `is_active`

### Step 2: Create HomepageSection model
- Fields: section_name, enabled, display_order

### Step 3: Create ServiceTime model
- Fields: day, time, label, display_order, poster FK to MediaAsset

### Step 4: Enhance MediaAsset — Add governance fields
- Add `file_size`, `checksum`, `focal_point_x`, `focal_point_y`, `is_public`, `usage_count`

### Step 5: Create migrations
- Run `makemigrations` for content, events, media, prayer apps

### Step 6: Run migrations and validate

---

## 3. Implementation Details

### 3.1 ContentBlock Enhancement

Add to content/models.py:
- `content_type` = CharField with choices (BELIEF, VALUE, FAQ, EXPECTATION, PAGE_SECTION, THEME)
- `display_order` = IntegerField(default=0)
- `is_active` = BooleanField(default=True)
- Update indexing for content_type

### 3.2 HomepageSection Model

New model in content/models.py:
- `section_name` = CharField(max_length=128, unique=True)
- `enabled` = BooleanField(default=True)
- `display_order` = IntegerField(default=0)
- Timestamps (created_at, updated_at)

### 3.3 ServiceTime Model

New model in content/models.py:
- `day` = CharField with day choices
- `time` = TimeField
- `label` = CharField(max_length=128)
- `display_order` = IntegerField(default=0)
- Timestamps (created_at, updated_at)

### 3.4 MediaAsset Enhancement

Add to media/models.py:
- `file_size` = BigIntegerField(null=True, blank=True)
- `checksum` = CharField(max_length=64, null=True, blank=True)
- `focal_point_x` = FloatField(default=0.5)
- `focal_point_y` = FloatField(default=0.5)
- `is_public` = BooleanField(default=True)
- `usage_count` = IntegerField(default=0)

---

## 4. Constraints

- No destructive operations (no table drops, no data loss)
- Prisma-owned tables remain untouched
- Only Django-owned tables are modified or created
- No admin registration, permissions, serializers, viewsets, or frontend changes