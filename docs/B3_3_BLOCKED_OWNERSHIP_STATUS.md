# B3.3 BLOCKED — Ownership Conversion Incomplete

**Date:** 2026-07-21  
**Status:** BLOCKED — Do not proceed with B3.3 Admin Integration

## Summary

Phase 0 audit identified 2 models that still have `managed = False`. These models remain under Prisma ownership and require B3.2 conversion work before Django Admin registration can proceed.

## Blocked Models

| Model | App | File | Current Status | Required Work |
|-------|-----|------|----------------|---------------|
| WebsiteLeader | content | `backend/apps/content/models.py` (line 135) | `managed = False` | Convert to Django ownership (`managed = True`). Update migration to reflect ownership transfer. |
| EventRegistration | events | `backend/apps/events/models.py` (line 124) | `managed = False` | Convert to Django ownership (`managed = True`). Update migration to reflect ownership transfer. |

## Expected Converted Models (from B3.2)

The following models were expected to be converted to Django ownership (`managed = True`):

### Content App
- [x] SystemConfig
- [x] SermonSeries
- [x] PublicSermon
- [ ] WebsiteLeader **← BLOCKED**
- [x] WebsiteTestimonial
- [x] WebsiteAcademyModule
- [x] ContactSubmission
- [x] VisitRsvp
- [x] GlobalSettings
- [x] HomepageSettings
- [x] ChurchProfile
- [x] ContentBlock
- [x] ServiceTime

### Events App
- [x] ChurchEvent
- [ ] EventRegistration **← BLOCKED**
- [x] Announcement

### Prayer App
- [x] PrayerSubmission
- [x] PrayerRequest

### Media App
- [x] MediaAsset

## Required Actions Before B3.3 Can Proceed

1. **Convert WebsiteLeader to Django ownership**
   - Change `managed = False` to `managed = True` in `backend/apps/content/models.py`
   - Ensure database table `WebsiteLeader` is properly migrated under Django management
   - Verify no Prisma dependency remains for this model

2. **Convert EventRegistration to Django ownership**
   - Change `managed = False` to `managed = True` in `backend/apps/events/models.py`
   - Ensure database table `EventRegistration` is properly migrated under Django management
   - Verify no Prisma dependency remains for this model

3. **Run migrations**
   - `python manage.py makemigrations`
   - `python manage.py migrate`

4. **Re-run Phase 0 audit**
   - Verify all expected models show `managed = True`
   - Confirm zero models remain with `managed = False` in the target list

5. **Only then proceed with B3.3 Admin Integration**

## Decision

**B3.3 Admin Integration is NOT READY to proceed.**

Do not create admin registrations, do not modify admin.py files, and do not run Django validation until ownership conversion is complete for all blocked models.

---

**Next Step:** Complete B3.2 ownership conversion for `WebsiteLeader` and `EventRegistration`, then re-audit before restarting B3.3.