# B4.3J.2 — Homepage Admin Navigation Refinement Report

## 1. Before Navigation Structure

```
Homepage
├── Hero Settings
├── Homepage Events
├── Homepage Sermons
│   ├── Sermon Series
│   └── Sermons
├── Homepage Testimonials
├── HomepageSection
└── ChurchProfile
```

## 2. After Navigation Structure

```
Homepage
├── Hero Section      → SystemConfig (key='site')
├── Pastor Profile    → PastorProfile
├── Service Times     → ServiceTime
├── Upcoming Events   → HomepageUpcomingEvent (filtered)
├── Latest Sermon     → PublicSermon
└── Homepage Testimonials → WebsiteTestimonial
```

## 3. Items Removed

- `HomepageSection` — not rendered on homepage
- `ChurchProfile` — not rendered on homepage
- `SermonSeries` — homepage only uses latest sermon
- `Hero Settings` — pointed to dead `HomepageSettings.hero_*` fields

## 4. Items Renamed

- `Homepage Sermons` → `Latest Sermon`
- `Homepage Events` → `Upcoming Events`
- `Hero Settings` → `Hero Section`

## 5. Hero Source-of-Truth

Frontend reads hero content from `/api/site-config` → `SystemConfig` where `key='site'`.
`HomepageSettings.hero_*` fields are dead code.

## 6. Event Filtering Logic

Same as homepage API: published + upcoming/ongoing only.

## 7. Sermon Filtering Logic

Homepage consumes only the single most recently published sermon.

## 8. Files Modified

- `backend/apps/content/models.py` — added `HeroSectionConfig`
- `backend/apps/content/admin.py` — updated `HOMEPAGE_GROUP`, added `HeroSectionConfigAdmin`
- `backend/apps/events/models.py` — added `HomepageUpcomingEvent`
- `backend/apps/events/admin.py` — added `HomepageUpcomingEventAdmin`

## 9. Validation

Blocked by missing `tf_env` conda environment in current shell. Structural changes are complete. Run `python manage.py check` in `tf_env` to validate admin loads and all links resolve.

## 10. Compliance

No models deleted. No data deleted. No API endpoints removed. Admin-navigation and usability refactor only.