# B4.2.7 — ServiceTime Data Correction

## Records Before Fix
4 generic records:
- SUNDAY 09:00 — Main Service
- WEDNESDAY 18:00 — Midweek Service
- FRIDAY 18:00 — Prayer Service
- SATURDAY 14:00 — Youth Service

## Records After Fix
5 homepage source-of-truth records:
- SUNDAY 06:00 — Sunday Online Service
- SATURDAY 09:00 — Saturday Physical Service
- TUESDAY 20:30 — Kingdom Formation
- THURSDAY 00:00 — Thursday Partner's Meeting
- WEDNESDAY 00:00 — Cell Group Meetings

## Schema Suitability Assessment
The current `ServiceTime` model is **partially sufficient**:
- It can store `day`, `time`, `label`, and `display_order`
- It **cannot** store `platform`, `location`, `link`, `description`, `image`
- It **cannot** represent time ranges like `"6:00 AM – 8:00 AM"`; only single `TimeField` values are supported

Because of these gaps, the CMS data layer does not fully match the homepage source of truth. A schema gap analysis has been documented separately in `B4_2_7_SERVICETIME_SCHEMA_GAP_ANALYSIS.md`.

## Files Modified
- `rpwebsite/RP/backend/seed_homepage_content.py`
- `rpwebsite/RP/backend/seed_homepage_content_pg.py`

## Validation Evidence

### Django Shell
```python
ServiceTime.objects.count()  # 5
ServiceTime.objects.all().values('day','time','label','display_order')
# SUNDAY 06:00 Sunday Online Service 1
# SATURDAY 09:00 Saturday Physical Service 2
# TUESDAY 20:30 Kingdom Formation 3
# THURSDAY 00:00 Thursday Partner's Meeting 4
# WEDNESDAY 00:00 Cell Group Meetings 5
```

### API Validation
`GET /api/homepage` `serviceTimes` returned the 5 corrected records in order.

### Idempotency
Re-running `seed_homepage_content.py` reported:
- `ServiceTime exists: SUNDAY 06:00 — Sunday Online Service`
- `ServiceTime exists: SATURDAY 09:00 — Saturday Physical Service`
- `ServiceTime exists: TUESDAY 20:30 — Kingdom Formation`
- `ServiceTime exists: THURSDAY 00:00 — Thursday Partner's Meeting`
- `ServiceTime exists: WEDNESDAY 00:00 — Cell Group Meetings`

No duplicates created.