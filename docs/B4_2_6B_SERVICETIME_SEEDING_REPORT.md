# B4.2.6B — ServiceTime Content Population Report

## Summary
Extended the homepage seed scripts to create ServiceTime records with idempotent logic. The seed had been missing ServiceTime entries; this implementation adds 4 realistic church service schedule records and ensures re-runs do not create duplicates.

## Files Modified
- `rpwebsite/RP/backend/seed_homepage_content.py`
- `rpwebsite/RP/backend/seed_homepage_content_pg.py`

## Records Created
4 ServiceTime records were seeded:

| Day | Time | Label | Display Order |
|---|---|---|---|
| SUNDAY | 09:00 | Main Service | 1 |
| WEDNESDAY | 18:00 | Midweek Service | 2 |
| FRIDAY | 18:00 | Prayer Service | 3 |
| SATURDAY | 14:00 | Youth Service | 4 |

## Seed Script Changes
- `seed_homepage_content.py`: added `seed_service_times()` using Django ORM `get_or_create` with `day`, `time`, and `label` as unique identifiers, updating `display_order` when changed.
- `seed_homepage_content_pg.py`: added `seed_service_times()` using PostgreSQL `INSERT ... ON CONFLICT (day, time) DO UPDATE` for idempotency.

## Validation Results

### Django Shell
```python
from backend.apps.content.models import ServiceTime
ServiceTime.objects.count()  # 4
ServiceTime.objects.all().values(
    "day", "time", "label", "display_order"
)
# [
#   {'day': 'SUNDAY', 'time': datetime.time(9, 0), 'label': 'Main Service', 'display_order': 1},
#   {'day': 'WEDNESDAY', 'time': datetime.time(18, 0), 'label': 'Midweek Service', 'display_order': 2},
#   {'day': 'FRIDAY', 'time': datetime.time(18, 0), 'label': 'Prayer Service', 'display_order': 3},
#   {'day': 'SATURDAY', 'time': datetime.time(14, 0), 'label': 'Youth Service', 'display_order': 4}
# ]
```

### API Validation
`GET /api/homepage` returned populated `serviceTimes`:
```json
"serviceTimes": [
  {"id": 2, "day": "SUNDAY", "day_display": "Sunday", "time": "09:00:00", "label": "Main Service", "display_order": 1},
  {"id": 3, "day": "WEDNESDAY", "day_display": "Wednesday", "time": "18:00:00", "label": "Midweek Service", "display_order": 2},
  {"id": 4, "day": "FRIDAY", "day_display": "Friday", "time": "18:00:00", "label": "Prayer Service", "display_order": 3},
  {"id": 5, "day": "SATURDAY", "day_display": "Saturday", "time": "14:00:00", "label": "Youth Service", "display_order": 4}
]
```

### Admin Validation
`ServiceTime` is registered in Django Admin with list display, search, filters, and ordering. Seeded records are visible at `/admin/content/servicetime/`.

### Idempotency
Re-running `seed_homepage_content.py` produced:
```
ServiceTime exists: SUNDAY 09:00 — Main Service
ServiceTime exists: WEDNESDAY 18:00 — Midweek Service
ServiceTime exists: FRIDAY 18:00 — Prayer Service
ServiceTime exists: SATURDAY 14:00 — Youth Service
```
No duplicates were created.

## Success Criteria
1. ServiceTime records exist in PostgreSQL - PASS
2. ServiceTime records appear in Django Admin - PASS
3. ServiceTime records appear in /api/homepage - PASS
4. Seed scripts contain ServiceTime seeding logic - PASS
5. Re-running the seed does not create duplicates - PASS