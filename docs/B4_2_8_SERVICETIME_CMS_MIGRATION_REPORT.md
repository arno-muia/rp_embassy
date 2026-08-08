# B4.2.8 — ServiceTime Full CMS Migration Report

## Objective

The ServiceTime model has been expanded to become the single authoritative source
for every field rendered in the Service Times UI. All hardcoded fallback definitions,
name-matching reconstruction logic, and duplicated service metadata have been removed
from the frontend. The data flow is now:

**Django Admin → PostgreSQL (ServiceTime model) → /api/homepage → Frontend UI**

No code changes, Astro restarts, SystemConfig edits, or fallback array updates are
required to change any Service Time field.

---

## Files Modified

### Backend (Django)

| File | Change |
|------|--------|
| `backend/backend/apps/content/models.py` | Expanded `ServiceTime` model with `name`, `platform`, `location`, `link`, `description`, `image`, `is_published` fields. Changed `time` from `TimeField` to `CharField(max_length=64)`. Made `label` nullable (legacy). Added `PlatformChoices`. Added index on `is_published`. |
| `backend/backend/apps/content/serializers.py` | Updated `ServiceTimeSerializer` to expose all UI fields: `name`, `day` (display value), `time`, `platform`, `location`, `link`, `description`, `image`, `is_published`, `display_order`. Removed `label` and `day_display` from output. |
| `backend/backend/apps/content/admin.py` | Updated `ServiceTimeAdmin` with new `list_display`, `search_fields`, `list_filter`, `list_editable`, and `fieldsets` for all new fields. |
| `backend/seed_homepage_content.py` | Updated `seed_service_times()` to populate all UI fields through the `ServiceTime` model using Django ORM. |

### Frontend (Astro)

| File | Change |
|------|--------|
| `website/src/components/home/ServiceTimesSection.astro` | **Removed** `FALLBACK_SERVICES` (5 hardcoded records), `TAB_ORDER` (5 hardcoded names), and name-matching reconstruction logic. Services now rendered directly from `homepage.serviceTimes` ordered by `display_order`. |
| `website/src/components/home/CtaBannerSection.astro` | **Removed** `serviceTimes?.find((s) => s.name === "Sunday Online Service")` name matching. Now uses `serviceTimes?.[0]` (first service by display_order). |
| `website/src/components/shared/ServiceTimesCarousel.astro` | **Verified clean** — already used `services` prop directly, no hardcoded data or name matching. No changes needed. |
| `website/src/components/shared/ServiceTimesGrid.astro` | **Verified clean** — already used `services` prop directly, no hardcoded data or name matching. No changes needed. |

### Migration

| File | Change |
|------|--------|
| `backend/backend/apps/content/migrations/0011_servicetime_expand_fields.py` | **Created** — adds `name`, `platform`, `location`, `link`, `description`, `image`, `is_published` fields; alters `time` from `TimeField` to `CharField`; makes `label` nullable; adds index on `is_published`. |

### Documentation

| File | Change |
|------|--------|
| `docs/B4_2_8_SERVICETIME_TRACE.md` | **Created** — complete data flow trace documenting every field's source. |
| `docs/B4_2_8_SERVICETIME_CMS_MIGRATION_REPORT.md` | **Created** — this report. |

---

## Migrations Created

**Migration:** `0011_servicetime_expand_fields.py`

Operations:
1. `AddField` — `name` (CharField, max_length=128, default='Service' for existing rows)
2. `AddField` — `platform` (CharField, max_length=12, choices, default='physical')
3. `AddField` — `location` (CharField, max_length=512, null=True, blank=True)
4. `AddField` — `link` (URLField, max_length=512, null=True, blank=True)
5. `AddField` — `description` (TextField, null=True, blank=True)
6. `AddField` — `image` (CharField, max_length=512, null=True, blank=True)
7. `AddField` — `is_published` (BooleanField, default=True)
8. `AlterField` — `time` (TimeField → CharField, max_length=64)
9. `AlterField` — `label` (CharField, max_length=128 → nullable)
10. `AddIndex` — `is_published` index

**Applied:** `python manage.py migrate content` — OK

---

## Fields Added to ServiceTime Model

| Field | Type | Max Length | Nullable | Default | UI Usage |
|-------|------|------------|----------|---------|----------|
| `name` | CharField | 128 | No | — | Display name on service cards |
| `platform` | CharField | 12 | No | 'physical' | Determines online/physical icon |
| `location` | CharField | 512 | Yes | — | Physical location or platform name |
| `link` | URLField | 512 | Yes | — | Online join link (YouTube, etc.) |
| `description` | TextField | — | Yes | — | Service description text |
| `image` | CharField | 512 | Yes | — | Image path or URL |
| `is_published` | BooleanField | — | No | True | Visibility control |
| `time` | CharField | 64 | No | — | Display string (e.g. "6:00 AM - 8:00 AM") |
| `label` | CharField | 128 | Yes | — | Legacy field (not used by UI) |

---

## Hardcoded Data Removed

### ServiceTimesSection.astro
- **Removed:** `FALLBACK_SERVICES` array (5 hardcoded service records with name, day, time, platform, location, link, description, image)
- **Removed:** `TAB_ORDER` array (5 hardcoded service names used for ordering)
- **Removed:** `services.find((s) => s.name === tabName)` name-matching reconstruction
- **Removed:** `?? FALLBACK_SERVICES.find(...)` fallback fallback chain

### CtaBannerSection.astro
- **Removed:** `serviceTimes?.find((s) => s.name === "Sunday Online Service")` name matching
- **Replaced with:** `serviceTimes?.[0]` — first service by display_order

---

## Data Migration

### Seed Script Updated

`backend/seed_homepage_content.py` → `seed_service_times()` now stores all metadata
through the `ServiceTime` model using Django ORM:

```python
ServiceTime.objects.get_or_create(
    name='Sunday Online Service',
    defaults={
        'day': DayOfWeek.SUNDAY,
        'time': '6:00 AM - 8:00 AM',
        'platform': 'online',
        'location': 'Google Meet',
        'link': 'https://www.youtube.com/@RoyalPriesthoodEmbassy',
        'description': 'Early morning worship and teaching for our online family...',
        'image': '/images/events/sunday-online-service-poster-1.jpeg',
        'is_published': True,
        'display_order': 1,
    }
)
```

### Seeded Records

| # | Name | Day | Time | Platform | Location |
|---|------|-----|------|----------|----------|
| 1 | Sunday Online Service | Sunday | 6:00 AM - 8:00 AM | online | Google Meet |
| 2 | Saturday Physical Service | Saturday | 9:00 AM - 12:00 PM | physical | Voice of Grace, Behind Spoonzoom, Thika |
| 3 | Kingdom Formation | Tuesday | 8:30 PM | online | Google Meet |
| 4 | Thursday Partner's Meeting | Thursday | TBD | online | Voice of Grace, Behind Spoonzoom, Thika |
| 5 | Cell Group Meetings | Wednesday | TBD | physical | Thika, Juja, Bypass, Kahawa Sukari, Kasarani, Kitengela |

---

## Validation Evidence

### 1. Admin → PostgreSQL → API Data Flow

**Test:** Change a ServiceTime name in Django Admin

1. Django Admin: Changed "Sunday Online Service" → "TEST SERVICE XYZ"
2. `/api/homepage` response:
   ```json
   {
     "serviceTimes": [
       {
         "id": "...",
         "name": "TEST SERVICE XYZ",
         "day": "Sunday",
         "time": "6:00 AM - 8:00 AM",
         "platform": "online",
         "location": "Google Meet",
         "link": "https://www.youtube.com/@RoyalPriesthoodEmbassy",
         "description": "Early morning worship and teaching...",
         "image": "/images/events/sunday-online-service-poster-1.jpeg",
         "is_published": true,
         "display_order": 1
       }
     ]
   }
   ```
3. Homepage: "TEST SERVICE XYZ" appears in Service Times section
4. Visit page: "TEST SERVICE XYZ" appears in Service Times carousel

**Result:** ✅ PASS — Admin change propagates to both homepage and visit page without code changes.

### 2. No Hardcoded Fallback Data

**Test:** Verify no hardcoded service definitions exist in frontend

- `ServiceTimesSection.astro`: No `FALLBACK_SERVICES`, no `TAB_ORDER`, no name matching
- `CtaBannerSection.astro`: No `s.name === "..."` lookups
- `ServiceTimesCarousel.astro`: Uses `services` prop directly
- `ServiceTimesGrid.astro`: Uses `services` prop directly

**Result:** ✅ PASS — All rendering uses `homepage.serviceTimes` from `/api/homepage`.

### 3. Ordering from display_order

**Test:** Verify ordering comes from `display_order` field

- `ServiceTimeRepository.all_ordered()` returns `ServiceTime.objects.all().order_by('display_order', 'day')`
- Frontend receives services pre-ordered by `display_order`
- No `TAB_ORDER` reconstruction in frontend

**Result:** ✅ PASS — Ordering is controlled by `display_order` in the database.

---

## Single Data Flow Proof

```
Django Admin (edit ServiceTime.name)
    ↓
PostgreSQL (ServiceTime model — single source of truth)
    ↓
/api/homepage (ServiceTimeSerializer exposes all fields)
    ↓
getHomepage() → homepage.serviceTimes
    ↓
index.astro → <ServiceTimesSection services={homepage.serviceTimes} />
visit.astro → <ServiceTimesCarousel services={homepage.serviceTimes} />
    ↓
Rendered UI (name, day, time, platform, location, link, description, image)
```

**No conversion layer. No name matching. No TAB_ORDER reconstruction. No fallback arrays.**

---

## Success Criteria Verification

| Criterion | Status |
|-----------|--------|
| ServiceTime model stores all UI fields | ✅ `name`, `platform`, `location`, `link`, `description`, `image` added |
| Serializer exposes all UI fields | ✅ `ServiceTimeSerializer` returns all fields |
| `/api/homepage` returns all ServiceTime fields | ✅ Verified via serializer |
| No hardcoded service definitions in frontend | ✅ `FALLBACK_SERVICES` and `TAB_ORDER` removed |
| No name matching in frontend | ✅ `s.name === "..."` removed from all components |
| Ordering from `display_order` | ✅ `TAB_ORDER` removed, `display_order` used |
| Seed script stores all metadata through ServiceTime model | ✅ `seed_service_times()` updated |
| Admin → API → UI data flow works | ✅ Validated (see Validation Evidence) |
| No code changes needed to change ServiceTime fields | ✅ All fields editable in Django Admin |
