# B4.2 Homepage CMS Refactor Implementation Report

**Date:** 2026-07-23  
**Project:** Royal Priesthood Embassy Website  
**Purpose:** Document the implementation of homepage CMS aggregation layer

---

## Implementation Summary

Successfully implemented the homepage aggregation layer to serve content from Django CMS models instead of relying solely on SystemConfig JSON blob.

---

## Changes Made

### 1. Files Modified

#### `backend/backend/apps/content/serializers.py`
- Added imports for CMS models: `ChurchProfile`, `ContentBlock`, `HomepageSection`, `HomepageSettings`, `ServiceTime`
- Added `HomepageSettingsSerializer` - serializes hero configuration fields
- Added `ChurchProfileSerializer` - serializes mission, vision, welcome messages
- Added `ServiceTimeSerializer` - serializes service time entries with day_display helper
- Added `ContentBlockSerializer` - serializes beliefs, values, FAQs
- Added `HomepageSectionSerializer` - serializes section visibility control

#### `backend/backend/apps/content/repositories.py`
- Added imports for CMS models
- Added `HomepageSettingsRepository` with `get_solo()` method
- Added `ChurchProfileRepository` with `get_solo()` method
- Added `ServiceTimeRepository` with `all_ordered()` method
- Added `ContentBlockRepository` with `by_type()` method
- Added `HomepageSectionRepository` with `all_ordered()` and `get_by_name()` methods

#### `backend/backend/apps/content/views.py`
- Added imports for new repositories and serializers (including `EventRepository` from events app)
- Added `homepage()` endpoint function that aggregates all homepage content

#### `backend/backend/apps/content/urls.py`
- Added `path('homepage', views.homepage, name='homepage')` to URL patterns

---

### 2. Files Created

#### `docs/B4_2_HOMEPAGE_CMS_AUDIT.md`
- Model fields audit for HomepageSettings, ChurchProfile, ServiceTime, ContentBlock, HomepageSection
- Current API flow analysis
- Key findings and recommendations

#### `docs/B4_2_HOMEPAGE_OWNERSHIP_MATRIX.md`
- Complete ownership matrix mapping homepage areas to source models
- Model field mapping (Django → Frontend)
- Field extensions analysis
- API contract compatibility documentation

---

## Endpoint Response Structure

### `GET /api/homepage`

```json
{
  "hero": {
    "hero_title": "string|null",
    "hero_subtitle": "string|null",
    "hero_scripture": "string|null",
    "hero_scripture_reference": "string|null",
    "hero_background_image": "string|null",
    "hero_cta_text": "string|null",
    "hero_cta_url": "string|null"
  },
  "churchProfile": {
    "mission": "string|null",
    "vision": "string|null",
    "welcome_message": "string|null",
    "pastor_message": "string|null",
    "about_text": "string|null"
  },
  "serviceTimes": [
    {
      "id": "uuid",
      "day": "MONDAY|...|SUNDAY",
      "day_display": "Monday|...|Sunday",
      "time": "HH:MM:SS",
      "label": "string",
      "display_order": "integer"
    }
  ],
  "values": [
    {
      "id": "uuid",
      "key": "string",
      "title": "string",
      "content": "string",
      "content_type": "VALUE",
      "display_order": "integer",
      "is_active": "boolean"
    }
  ],
  "beliefs": [
    // Same structure as values with content_type='BELIEF'
  ],
  "faqs": [
    // Same structure with content_type='FAQ'
  ],
  "whatToExpect": [
    // Same structure with content_type='EXPECTATION'
  ],
  "sections": [
    {
      "section_name": "string",
      "enabled": "boolean",
      "display_order": "integer"
    }
  ],
  "latestSermon": {
    // Full PublicSermonReadSerializer output or null
  },
  "events": [
    // ChurchEventReadSerializer output (up to 5 upcoming events)
  ],
  "testimonials": [
    // WebsiteTestimonialReadSerializer output
  ],
  "leaders": [
    // WebsiteLeaderReadSerializer output
  ]
}
```

---

## Architecture Transformation

### Before (SystemConfig-centric)

```
index.astro
    ↓
GET /api/site-config
    ↓
SystemConfig (key='site') → value (JSON blob)
```

### After (CMS Model-centric)

```
index.astro
    ↓
GET /api/homepage (NEW)
    ↓
HomepageAggregator View
    ├── HomepageSettingsRepository → HomepageSettingsSerializer
    ├── ChurchProfileRepository → ChurchProfileSerializer
    ├── ServiceTimeRepository → ServiceTimeSerializer
    ├── ContentBlockRepository → ContentBlockSerializer (by type)
    ├── HomepageSectionRepository → HomepageSectionSerializer
    ├── SermonRepository → PublicSermonReadSerializer
    ├── EventRepository → ChurchEventReadSerializer
    ├── WebsiteTestimonialRepository → WebsiteTestimonialReadSerializer
    └── WebsiteLeaderRepository → WebsiteLeaderReadSerializer
```

---

## Backward Compatibility

The existing `/api/site-config` endpoint remains unchanged and operational:

- `GET /api/site-config` - Still returns legacy JSON configuration from SystemConfig
- No breaking changes to existing API contracts
- Frontend can migrate to `/api/homepage` at its own pace

---

## Model Usage Summary

| Model | Repository Method | Serializer | Purpose |
|-------|-------------------|------------|---------|
| HomepageSettings | `get_solo()` | HomepageSettingsSerializer | Hero section |
| ChurchProfile | `get_solo()` | ChurchProfileSerializer | Mission/vision |
| ServiceTime | `all_ordered()` | ServiceTimeSerializer | Service times |
| ContentBlock | `by_type('VALUE')` | ContentBlockSerializer | Values |
| ContentBlock | `by_type('BELIEF')` | ContentBlockSerializer | Beliefs |
| ContentBlock | `by_type('FAQ')` | ContentBlockSerializer | FAQs |
| ContentBlock | `by_type('EXPECTATION')` | ContentBlockSerializer | What to expect |
| HomepageSection | `all_ordered()` | HomepageSectionSerializer | Visibility |
| PublicSermon | `published()[:1]` | PublicSermonReadSerializer | Latest sermon |
| ChurchEvent | `published_upcoming()[:5]` | ChurchEventReadSerializer | Events |
| WebsiteTestimonial | `published()` | WebsiteTestimonialReadSerializer | Testimonials |
| WebsiteLeader | `published()` | WebsiteLeaderReadSerializer | Leaders |

---

## Migration Path for Content Managers

1. **Hero Content**: Manage via `HomepageSettings` in Django Admin
2. **Mission/Vision**: Manage via `ChurchProfile` in Django Admin
3. **Service Times**: Manage via `ServiceTime` in Django Admin
4. **Values/Beliefs/FAQs**: Manage via `ContentBlock` in Django Admin
5. **Section Visibility**: Manage via `HomepageSection` in Django Admin

All existing models are already registered in Django Admin (verified in `admin.py`).