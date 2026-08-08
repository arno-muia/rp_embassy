# B4.2.1 — Homepage Readiness Report

**Date:** 2026-07-23  
**Project:** Royal Priesthood Embassy Website  
**Purpose:** B4.3 Astro Homepage Migration readiness assessment  

---

## EXECUTIVE SUMMARY

**B4.2.1 STATUS: FAIL**  
The homepage endpoint is **NOT READY** for B4.3 Astro Homepage Migration.

A critical bug was discovered during validation that prevents the `/api/homepage` endpoint from functioning.

---

## PASS / FAIL Status

| Phase | Requirement | Status | Notes |
|-------|-------------|--------|-------|
| Phase 1 | Endpoint Response (JSON) | ❌ FAIL | HTTP 500 - NameError |
| Phase 2 | Expected Keys Present | ❌ NOT TESTED | Blocked by Phase 1 |
| Phase 3 | Data Source Mapping | ⚠️ CODE CORRECT | Runtime failure only |
| Phase 4 | Admin Registration | ✅ PASS | All models registered |
| Phase 5 | Source-of-Truth Verification | ❌ NOT COMPLETED | Blocked by Phase 1 |
| Phase 6 | Gap Analysis | ✅ COMPLETE | Issue documented |

**Overall Result:** ❌ FAIL

---

## B4.3 Readiness Assessment

### Current State
- Endpoint returns HTTP 500 error
- JSON response cannot be validated
- No functional API to integrate with Astro frontend

### Blocking Issues

#### Critical Blockers (Must Fix Before B4.3)

| # | Issue | Location | Fix Required |
|---|-------|----------|--------------|
| 1 | `ServiceTimeRepository` not imported | `backend/apps/content/views.py:18-31` | Add missing import |

### Non-Blocking Observations

| Observation | Impact | Required Action |
|-------------|--------|-----------------|
| All repository classes exist | None | No action needed |
| All serializers exist | None | No action needed |
| All models defined | None | No action needed |
| All admin registrations present | None | No action needed |

---

## Risk Assessment

### Risk Level: **HIGH**

| Risk Category | Assessment | Impact |
|---------------|------------|--------|
| Endpoint Unavailability | HIGH | B4.3 cannot proceed without working API |
| Data Integrity | LOW | Models and repositories are correctly implemented |
| Admin Functionality | LOW | All models properly registered |
| Migration Complexity | LOW | Single import fix required |

### Root Cause Analysis

The `homepage()` view function uses `ServiceTimeRepository.all_ordered()` but this repository class was never added to the import statement. This is likely a code review oversight during the B4.2 implementation.

---

## Recommended Actions

### Pre-Migration (Required)

1. **Add Missing Import** (Critical)
   - File: `backend/apps/content/views.py`
   - Add to import block:
     ```python
     from .repositories import (
         ...
         ServiceTimeRepository,  # ADD THIS LINE
         ...
     )
     ```

2. **Re-run Validation** (Critical)
   - Restart Django server
   - Execute `curl http://127.0.0.1:8000/api/homepage`
   - Verify JSON response structure matches expected schema

3. **Complete Source-of-Truth Verification** (Required)
   - Create test data via Django Admin
   - Verify endpoint reflects admin changes immediately

### Post-Import Fix Validation Checklist

After the import is fixed, verify:

- [ ] `/api/homepage` returns HTTP 200
- [ ] Response contains all 11 required keys
- [ ] `hero` object fields match HomepageSettings model
- [ ] `churchProfile` object fields match ChurchProfile model
- [ ] `serviceTimes` array uses ServiceTime model data
- [ ] `values` array filtered by content_type='VALUE'
- [ ] `beliefs` array filtered by content_type='BELIEF'
- [ ] `faqs` array filtered by content_type='FAQ'
- [ ] `whatToExpect` array filtered by content_type='EXPECTATION'
- [ ] `sections` array uses HomepageSection model data
- [ ] `latestSermon` returns newest published sermon
- [ ] `events` returns upcoming published events (max 5)
- [ ] `testimonials` filtered by is_published=True
- [ ] `leaders` filtered by is_published=True

---

## Blockers (If No Fix Applied)

If the missing import is not fixed:

- B4.3 Astro Homepage Migration will fail during integration
- Frontend cannot consume `/api/homepage` endpoint
- All homepage content sections will be empty/unavailable
- Source-of-truth verification cannot be completed

---

## Verification Evidence

### Endpoint Error (Current)

```
GET /api/homepage
Status: 500 Internal Server Error
Error: NameError: name 'ServiceTimeRepository' is not defined
Location: backend/apps/content/views.py, line 149
```

### Repository Exists (Verified)

```python
# File: backend/apps/content/repositories.py (lines 148-155)
class ServiceTimeRepository:
    """Repository for ServiceTime entries."""
    model = ServiceTime

    @classmethod
    def all_ordered(cls):
        """Get all service times ordered by display_order."""
        return ServiceTime.objects.all().order_by('display_order', 'day')
```

### Required Import (Missing)

```python
# File: backend/apps/content/views.py (lines 18-31)
# Current imports - MISSING SERVICE TIME REPOSITORY
from .repositories import (
    ChurchProfileRepository,
    ContactSubmissionRepository,
    ContentBlockRepository,
    HomepageSectionRepository,
    HomepageSettingsRepository,
    # ... ServiceTimeRepository is NOT in this list
)
```

---

## Decision

**B4.2.1 FAIL** - Do not proceed to B4.3 until:

1. ✅ Missing `ServiceTimeRepository` import is added to `views.py`
2. ✅ `/api/homepage` endpoint returns valid JSON response
3. ✅ All response keys are verified present
4. ✅ Source-of-truth verification is completed

---

## Next Steps

1. **Apply Fix:** Add missing import (see above)
2. **Re-validate:** Run full validation pass again
3. **Update Report:** Once fixed, update this report with successful test results
4. **Approve:** B4.3 may proceed after successful re-validation