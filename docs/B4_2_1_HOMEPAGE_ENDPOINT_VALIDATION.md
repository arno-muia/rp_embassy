# B4.2.1 — Homepage Endpoint Validation Report

**Date:** 2026-07-23  
**Project:** Royal Priesthood Embassy Website  
**Purpose:** Complete validation of `/api/homepage` endpoint and Django Admin CMS functionality  

---

## Phase 1 — Endpoint Validation

### Test Execution

**Request:**
```bash
curl http://127.0.0.1:8000/api/homepage
```

**Result:**
```
Status: NameError (500 Internal Server Error)
Exception: name 'ServiceTimeRepository' is not defined
Location: backend/apps/content/views.py, line 149
```

**Error Details:**
The endpoint fails with a `NameError` because `ServiceTimeRepository` is not imported in `views.py`.

---

## Phase 2 — Structure Validation

### Expected Response Structure
```json
{
  "hero": {},
  "churchProfile": {},
  "serviceTimes": [],
  "values": [],
  "beliefs": [],
  "faqs": [],
  "whatToExpect": [],
  "sections": [],
  "latestSermon": null,
  "events": [],
  "testimonials": [],
  "leaders": []
}
```

### Status
- ❌ Endpoint returned HTTP 500 error
- ❌ Structure validation could not be performed
- ❌ No JSON response was returned

---

## Phase 3 — Data Source Verification

### Model-to-Endpoint Source Mapping Analysis

Based on code inspection of `views.py`, `repositories.py`, `serializers.py`, and `models.py`:

| Endpoint Key | Expected Source Model | Repository Confirmed | Serializer Confirmed | Status |
|-------------|---------------------|---------------------|---------------------|--------|
| hero | HomepageSettings | HomepageSettingsRepository ✅ | HomepageSettingsSerializer ✅ | ⚠️ Implementation correct |
| churchProfile | ChurchProfile | ChurchProfileRepository ✅ | ChurchProfileSerializer ✅ | ⚠️ Implementation correct |
| serviceTimes | ServiceTime | ServiceTimeRepository ✅ | ServiceTimeSerializer ✅ | ❌ **MISSING IMPORT** |
| values | ContentBlock (type=VALUE) | ContentBlockRepository ✅ | ContentBlockSerializer ✅ | ⚠️ Implementation correct |
| beliefs | ContentBlock (type=BELIEF) | ContentBlockRepository ✅ | ContentBlockSerializer ✅ | ⚠️ Implementation correct |
| faqs | ContentBlock (type=FAQ) | ContentBlockRepository ✅ | ContentBlockSerializer ✅ | ⚠️ Implementation correct |
| whatToExpect | ContentBlock (type=EXPECTATION) | ContentBlockRepository ✅ | ContentBlockSerializer ✅ | ⚠️ Implementation correct |
| sections | HomepageSection | HomepageSectionRepository ✅ | HomepageSectionSerializer ✅ | ⚠️ Implementation correct |
| latestSermon | PublicSermon | SermonRepository ✅ | PublicSermonReadSerializer ✅ | ⚠️ Implementation correct |
| events | ChurchEvent | EventRepository ✅ | ChurchEventReadSerializer ✅ | ⚠️ Implementation correct |
| testimonials | WebsiteTestimonial | WebsiteTestimonialRepository ✅ | WebsiteTestimonialReadSerializer ✅ | ⚠️ Implementation correct |
| leaders | WebsiteLeader | WebsiteLeaderRepository ✅ | WebsiteLeaderReadSerializer ✅ | ⚠️ Implementation correct |

---

## Phase 4 — Django Admin Verification

### Admin Registration Status

Based on `backend/apps/content/admin.py` and `backend/apps/events/admin.py`:

| Model | Admin Registration | List View | Add Form | Edit Form | Status |
|-------|-------------------|-----------|----------|-----------|--------|
| HomepageSettings | ✅ Registered | ✅ Configured | ✅ Default | ✅ Default | Ready |
| ChurchProfile | ✅ Registered | ✅ Configured | ✅ Default | ✅ Default | Ready |
| ServiceTime | ✅ Registered | ✅ Configured | ✅ Default | ✅ Default | Ready |
| ContentBlock | ✅ Registered | ✅ Configured | ✅ Default | ✅ Default | Ready |
| HomepageSection | ✅ Registered | ✅ Configured | ✅ Default | ✅ Default | Ready |
| PublicSermon | ✅ Registered | ✅ Configured | ✅ Default | ✅ Default | Ready |
| ChurchEvent | ✅ Registered | ✅ Configured | ✅ Default | ✅ Default | Ready |
| WebsiteLeader | ✅ Registered | ✅ Configured | ✅ Default | ✅ Default | Ready |
| WebsiteTestimonial | ✅ Registered | ✅ Configured | ✅ Default | ✅ Default | Ready |

**Note:** Admin verification could not be completed via UI due to endpoint error, but code inspection confirms all admin registrations are present and properly configured.

---

## Phase 5 — Source-of-Truth Verification

**Status:** ⚠️ Could not be performed - endpoint error prevents verification

The endpoint must be functional before source-of-truth verification can proceed.

---

## Phase 6 — Gap Analysis

### Critical Issues Found

1. **Missing Import in views.py (CRITICAL)**
   - **File:** `backend/apps/content/views.py`
   - **Line:** 18-31 (imports section)
   - **Issue:** `ServiceTimeRepository` is used in the `homepage()` view (line 149) but NOT imported
   - **Impact:** Endpoint returns HTTP 500 error
   - **Required Fix:** Add `ServiceTimeRepository` to the imports

2. **Missing Import in views.py (CRITICAL)**
   - **File:** `backend/apps/content/views.py`
   - **Line:** 152-154 (usage)
   - **Issue:** `ContentBlockRepository` and filtering calls exist but `ContentBlock` model is not imported
   - **Note:** Repository is imported, but model imports should be verified

### Additional Findings

3. **Repository Pattern Implementation Status**
   - ServiceTimeRepository exists in repositories.py (lines 148-155)
   - All required repository methods are implemented correctly:
     - `ServiceTimeRepository.all_ordered()` - returns ordered queryset
     - `ContentBlockRepository.by_type()` - filters by content_type
     - `HomepageSectionRepository.all_ordered()` - returns ordered queryset

4. **Serializer Field Verification**
   - ServiceTimeSerializer fields: `id`, `day`, `day_display`, `time`, `label`, `display_order`
   - ContentBlockSerializer fields: `id`, `key`, `title`, `content`, `content_type`, `display_order`, `is_active`
   - HomepageSettingsSerializer fields: `hero_title`, `hero_subtitle`, `hero_scripture`, `hero_scripture_reference`, `hero_background_image`, `hero_cta_text`, `hero_cta_url`

---

## Technical Evidence

### views.py Import Section (Lines 18-31)
```python
from .repositories import (
    ChurchProfileRepository,
    ContactSubmissionRepository,
    ContentBlockRepository,
    HomepageSectionRepository,
    HomepageSettingsRepository,
    SermonRepository,
    SeriesRepository,
    SystemConfigRepository,
    VisitRsvpRepository,
    WebsiteAcademyModuleRepository,
    WebsiteLeaderRepository,
    WebsiteTestimonialRepository,
)
```

### Missing Repository
`ServiceTimeRepository` should be added to the above import list.

### views.py Usage (Line 149)
```python
service_times = ServiceTimeSerializer(ServiceTimeRepository.all_ordered(), many=True).data
```

This line references `ServiceTimeRepository` which is not imported.

---

## Recommendations

1. **Immediate Fix Required:**
   - Add `ServiceTimeRepository` to the imports in `backend/apps/content/views.py`
   
2. **After Fix:**
   - Restart Django server
   - Re-test `/api/homepage` endpoint
   - Verify all response keys are present
   - Test Django Admin functionality with test data

3. **Verification to Complete:**
   - Source-of-truth verification (Phase 5)
   - Full endpoint response validation
   - Admin create/edit/save operations

---

## Summary

| Category | Status |
|----------|--------|
| Endpoint Functional | ❌ FAIL |
| Structure Validation | ❌ NOT TESTED |
| Data Source Mapping | ⚠️ CODE CORRECT, RUNTIME FAIL |
| Admin Registration | ✅ READY |
| Source-of-Truth Verification | ❌ NOT COMPLETED |
| Critical Issues | 1 found (missing import) |