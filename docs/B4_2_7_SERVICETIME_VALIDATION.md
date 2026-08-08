# B4.2.7 — ServiceTime Validation

## Validation Commands and Results

### Django Shell Count
```python
from backend.apps.content.models import ServiceTime
ServiceTime.objects.count()
# Result: 5
```

### Django Shell Values
```python
ServiceTime.objects.all().values('day','time','label','display_order')
# Result:
# SUNDAY 06:00 Sunday Online Service 1
# SATURDAY 09:00 Saturday Physical Service 2
# TUESDAY 20:30 Kingdom Formation 3
# THURSDAY 00:00 Thursday Partner's Meeting 4
# WEDNESDAY 00:00 Cell Group Meetings 5
```

### API Response
`GET /api/homepage` `serviceTimes` returned 5 records in correct display_order:
1. Sunday Online Service
2. Saturday Physical Service
3. Kingdom Formation
4. Thursday Partner's Meeting
5. Cell Group Meetings

### Admin Validation
ServiceTime records are visible in Django Admin at `/admin/content/servicetime/`. The model is registered with `ServiceTimeAdmin` providing list display, search, filters, and ordering.

### Idempotency Validation
Re-running `seed_homepage_content.py` produced:
```
ServiceTime exists: SUNDAY 06:00 — Sunday Online Service
ServiceTime exists: SATURDAY 09:00 — Saturday Physical Service
ServiceTime exists: TUESDAY 20:30 — Kingdom Formation
ServiceTime exists: THURSDAY 00:00 — Thursday Partner's Meeting
ServiceTime exists: WEDNESDAY 00:00 — Cell Group Meetings
```
No duplicates created. Count remains 5.

## Files Modified
- `rpwebsite/RP/backend/seed_homepage_content.py`
- `rpwebsite/RP/backend/seed_homepage_content_pg.py`

## Reports Created
- `rpwebsite/RP/docs/B4_2_7_SERVICETIME_SCHEMA_GAP_ANALYSIS.md`
- `rpwebsite/RP/docs/B4_2_7_SERVICETIME_DATA_CORRECTION.md`

## Notes
- Current model does not support `platform`, `location`, `link`, `description`, `image`, or time ranges
- Seed uses best-effort mapping: name → `label`, start time → `time`, order → `display_order`
- Admin and API now reflect homepage source-of-truth names and ordering