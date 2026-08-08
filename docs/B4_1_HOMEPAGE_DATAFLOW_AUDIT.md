# B4.1 Homepage Data Flow Audit

**Date:** 2026-07-23  
**Project:** Royal Priesthood Embassy Website  
**Purpose:** Determine exactly how the Astro frontend obtains homepage content for Django CMS design

---

## Executive Summary

The Astro frontend homepage (`index.astro`) obtains content from **4 API endpoints** served by Django REST Framework. The data flow is entirely API-driven with no server-side rendering beyond initial fetch. The homepage relies on `SystemConfig` for centralized site configuration (including service times, what-to-expect items, beliefs, values, etc.) and uses individual endpoints for sermons and events.

---

## 1. Endpoint Inventory

### Homepage-Consumed Endpoints

| Endpoint | Method | View/Handler | Purpose |
|----------|--------|--------------|---------|
| `GET /api/site-config` | Function-based | `views.site_config()` | Site-wide configuration (hero, service times, what-to-expect, beliefs, values, theme) |
| `GET /api/sermons` | ViewSet (list) | `views.SermonViewSet` | All published sermons |
| `GET /api/events` | ViewSet (list) | `views.EventViewSet` | Published events for upcoming events carousel |
| `GET /api/testimonials` | ViewSet (list) | `views.TestimonialViewSet` | Published testimonials |

### Complete Endpoint Registry

| Endpoint | View/Serializer | Model | Purpose |
|----------|-----------------|-------|---------|
| `/api/sermons` | `SermonViewSet` + `PublicSermonReadSerializer` | `PublicSermon` | Sermon listings |
| `/api/sermons/{slug}` | `SermonViewSet` (detail) | `PublicSermon` | Single sermon |
| `/api/series` | `SeriesViewSet` + `SermonSeriesReadSerializer` | `SermonSeries` | Sermon series listings |
| `/api/series/{slug}` | `SeriesViewSet` (detail) | `SermonSeries` | Single series |
| `/api/events` | `EventViewSet` + `ChurchEventReadSerializer` | `ChurchEvent` | Events listings |
| `/api/events/{id}` | `EventViewSet` (detail) | `ChurchEvent` | Single event |
| `/api/leaders` | `LeaderViewSet` + `WebsiteLeaderReadSerializer` | `WebsiteLeader` | Leadership team |
| `/api/testimonials` | `TestimonialViewSet` + `WebsiteTestimonialReadSerializer` | `WebsiteTestimonial` | Testimonials |
| `/api/academy` | `AcademyModuleViewSet` + `WebsiteAcademyModuleReadSerializer` | `WebsiteAcademyModule` | Academy modules |
| `/api/site-config` | Function-based view | `SystemConfig` | Site-wide configuration |
| `/api/contact` | POST only | `ContactSubmissionWriteSerializer` | Contact form submissions |
| `/api/rsvp` | POST only | `VisitRsvpWriteSerializer` | Visit RSVP submissions |

---

## 2. Model Inventory

### Homepage-Consumed Models (from `content/models.py`)

#### SystemConfig (Primary Source)
```python
class SystemConfig(models.Model):
    id: UUID
    key: str              # 'site' is the key used for homepage config
    value: JSON           # Contains nested site configuration
    description: str
    updated_at: datetime
    updated_by: FK(User)
```

The `value` JSON field contains the full site configuration structure including:
- `name`, `shortName`, `tagline`, `scripture`, `description`
- `address`, `contact`, `social`, `giving`
- `serviceTimes[]` - Array of service time objects
- `whatToExpect[]` - Array of what-to-expect items with icons
- `beliefs[]`, `values[]`, `visitFaqs[]`
- `theme2026` - Annual theme configuration

#### PublicSermon (Latest Sermon Section)
```python
class PublicSermon(models.Model):
    id: UUID
    slug: str
    title: str
    description: str
    series: FK(SermonSeries)  # nullable
    scripture: str
    speaker: str
    date: datetime
    video_url: str
    audio_url: str
    notes_url: str
    thumbnail_url: str
    duration: str
    tags: JSON
    is_published: bool
```

#### ChurchEvent (Events Carousel)
```python
class ChurchEvent(models.Model):
    id: UUID
    title: str
    description: str
    type: str  # SERVICE, FELLOWSHIP, OUTREACH, CONFERENCE, FUNDRAISER, OTHER
    start_date_time: datetime
    end_date_time: datetime
    location: str
    image_url: str
    registration_required: bool
    max_attendees: int
    cost_cents: int
    status: str  # DRAFT, PUBLISHED, CANCELLED, COMPLETED
```

#### WebsiteTestimonial (Testimonials Section)
```python
class WebsiteTestimonial(models.Model):
    id: UUID
    quote: str
    name: str
    role: str
    photo_url: str
    sort_order: int
    is_published: bool
```

### CMS-Managed Models (for Admin Consideration)

| Model | Purpose | Singleton? |
|-------|---------|------------|
| `GlobalSettings` | Church name, contact, social links, giving config | Yes (should be) |
| `HomepageSettings` | Hero title, subtitle, CTA, background | Yes (should be) |
| `ChurchProfile` | Mission, vision, welcome message | Yes (should be) |
| `ContentBlock` | Beliefs, values, FAQs, page sections | No (categorized) |
| `ServiceTime` | Service times with ordering | No (multiple) |
| `HomepageSection` | Section visibility control | No |

---

## 3. Serializer Inventory

### Read Serializers (Homepage Consumption)

| Serializer | Model | Fields Returned |
|------------|-------|-----------------|
| `PublicSermonReadSerializer` | PublicSermon | `id`, `slug`, `title`, `description`, `series`, `series_slug`, `series_title`, `scripture`, `speaker`, `date`, `video_url`, `audio_url`, `notes_url`, `thumbnail_url`, `duration`, `tags`, `is_published`, `created_at`, `updated_at` |
| `ChurchEventReadSerializer` | ChurchEvent | `id`, `title`, `description`, `type`, `start_date_time`, `end_date_time`, `location`, `image_url`, `gallery_url`, `registration_required`, `max_attendees`, `cost_cents`, `registration_open_date`, `status`, `created_at`, `updated_at`, `created_by` |
| `WebsiteTestimonialReadSerializer` | WebsiteTestimonial | `id`, `quote`, `name`, `role`, `photo_url`, `sort_order`, `is_published`, `created_at`, `updated_at` |
| `SystemConfigReadSerializer` | SystemConfig | `id`, `key`, `value`, `description`, `updated_at`, `updated_by` |

### Frontend Type Mapping (from `api.ts`)

The `toSermonView()`, `toEventView()`, and `toTestimonialView()` functions convert Django snake_case fields to frontend camelCase:

```typescript
// Sermon transformation: snake_case → camelCase
toSermonView: {
  thumbnail_url → thumbnail
  series_slug → seriesSlug
  is_published → published
  video_url → videoUrl
  audio_url → audioUrl
  notes_url → notesUrl
}
```

---

## 4. JSON Structure Returned to Astro

### Site Configuration Response (`GET /api/site-config`)

```json
{
  "name": "Royal Priesthood Embassy",
  "shortName": "Royal Priesthood",
  "tagline": "Discover Your True Identity in Christ",
  "scripture": "1 Peter 2:9",
  "description": "Join Royal Priesthood Embassy...",
  "address": {
    "street": "Voice of Grace, Behind Spoonzoom",
    "city": "Thika",
    "country": "Kenya",
    "mapsUrl": "https://maps.app.goo.gl/..."
  },
  "contact": { "email": "...", "whatsapp": "..." },
  "social": { "instagram": "...", "facebook": "...", "youtube": "..." },
  "giving": { "mpesaTill": "...", "accountName": "..." },
  "academyUrl": "...",
  "serviceTimes": [
    {
      "name": "Sunday Online Service",
      "day": "Sunday",
      "time": "6:00 AM – 8:00 AM",
      "platform": "online",
      "location": "Google Meet",
      "link": "https://youtube.com/...",
      "description": "..."
    }
  ],
  "whatToExpect": [
    { "title": "...", "description": "...", "icon": "music" }
  ],
  "values": [
    { "id": "...", "title": "...", "description": "..." }
  ],
  "beliefs": [...],
  "visitFaqs": [...],
  "theme2026": { ... }
}
```

### Sermons Response (`GET /api/sermons`)

```json
[
  {
    "id": "uuid-string",
    "slug": "sermon-slug",
    "title": "Sermon Title",
    "description": "Description text",
    "series": "Series Name",
    "series_slug": "series-slug",
    "series_title": "Series Title",
    "scripture": "John 3:16",
    "speaker": "Pastor Name",
    "date": "2024-01-15T10:00:00Z",
    "video_url": "https://...",
    "audio_url": "https://...",
    "notes_url": "https://...",
    "thumbnail_url": "https://...",
    "duration": "45:30",
    "tags": ["faith", "grace"],
    "is_published": true
  }
]
```

### Events Response (`GET /api/events`)

```json
[
  {
    "id": "uuid-string",
    "title": "Event Title",
    "description": "...",
    "type": "SERVICE",
    "start_date_time": "2024-02-01T10:00:00Z",
    "end_date_time": "2024-02-01T14:00:00Z",
    "location": "Thika, Kenya",
    "image_url": "https://...",
    "registration_required": false,
    "status": "PUBLISHED"
  }
]
```

---

## 5. Homepage Rendering Flow

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE (PostgreSQL)                     │
├─────────────────────────────────────────────────────────────────┤
│  SystemConfig.key='site' → value (JSON config)                    │
│  PublicSermon.* (published=true)                                 │
│  ChurchEvent.* (status=PUBLISHED)                                │
│  WebsiteTestimonial.* (published=true)                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     REPOSITORY LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  SystemConfigRepository.get_by_key('site')                       │
│  SermonRepository.published() → ordered by -date                 │
│  EventRepository.published_upcoming() → ordered by start_date     │
│  WebsiteTestimonialRepository.published() → by sort_order        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERIALIZER (DRF)                              │
├─────────────────────────────────────────────────────────────────┤
│  SystemConfigReadSerializer → JSON config                         │
│  PublicSermonReadSerializer → array of sermons                   │
│  ChurchEventReadSerializer → array of events                     │
│  WebsiteTestimonialReadSerializer → array of testimonials         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API ENDPOINT                                │
├─────────────────────────────────────────────────────────────────┤
│  GET /api/site-config → config (SiteConfig type)                 │
│  GET /api/sermons → all sermons → sorted for latest              │
│  GET /api/events → events → filtered for upcoming                │
│  GET /api/testimonials → testimonials                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ASTRO FRONTEND (index.astro)                  │
├─────────────────────────────────────────────────────────────────┤
│  Page fetch in frontmatter:                                      │
│    const config = await getSiteConfig()                          │
│    const events = await getUpcomingEvents(5)                     │
│    const latestSermon = await getLatestSermon()                  │
│    const testimonials = await getTestimonials()                    │
│                                                                  │
│  Data mapping via toEventView(), toSermonView()                  │
│  Component composition:                                          │
│    <HeroSection config={config} />                                │
│    <ServiceTimesSection services={config.serviceTimes} />          │
│    <EventsCarouselSection events={events} />                     │
│    <WhatToExpectSection items={config.whatToExpect} />           │
│    <LatestSermonSection sermon={latestSermon} />                  │
│    <TestimonialsSection testimonials={testimonials} />            │
│    <PastorSection />                                             │
│    <CtaBannerSection config={config} />                            │
└─────────────────────────────────────────────────────────────────┘
```

### Homepage Sections Breakdown

| Section | Component | Data Source | API Endpoint(s) |
|---------|-----------|-------------|-----------------|
| Hero | `HeroSection.astro` | `config.tagline`, `config.scripture`, `config.description` | `/api/site-config` |
| Service Times | `ServiceTimesSection.astro` | `config.serviceTimes[]` | `/api/site-config` |
| Events Carousel | `EventsCarouselSection.astro` | `events[]` (up to 5 upcoming) | `/api/events` (also fallback to static in component) |
| What to Expect | `WhatToExpectSection.astro` | `config.whatToExpect[]` | `/api/site-config` |
| Latest Sermon | `LatestSermonSection.astro` | `sermon{slug,title,thumbnail,speaker,date,description}` | `/api/sermons` |
| Testimonials | `TestimonialsSection.astro` → `TestimonialsCarousel.astro` | `testimonials[]` | `/api/testimonials` |
| Pastor | `PastorSection.astro` | Static/imported leaders | `/api/leaders` |
| CTA Banner | `CtaBannerSection.astro` | `config.serviceTimes[].sunday` | `/api/site-config` |

---

## 6. Recommended Admin UX Improvements

### 6.1 SystemConfig Content Organization

**Current State:** All site configuration is stored in a single JSON blob (`SystemConfig.value`) accessible via `/api/site-config?key=site`. This makes content management difficult in Django admin.

**Recommended Improvements:**

1. **Create a dedicated Site Configuration Admin page** that presents the JSON structure as individual fields/inline forms:
   - Basic Info (name, tagline, scripture, description)
   - Address block (inline editing)
   - Contact block (inline editing)
   - Social links (inline editing)
   - Giving configuration (inline editing)
   - Service times (tabbed inline forms)
   - What-to-expect items (tabular inline editing)
   - Values and beliefs (tabular inline editing)

2. **Migrate JSON content to CMS-managed models:**
   - `ServiceTime` model → Direct admin editing with drag-drop ordering
   - `ContentBlock` with `content_type='VALUE'` → Values management
   - `ContentBlock` with `content_type='BELIEF'` → Beliefs management
   - `ContentBlock` with `content_type='EXPECTATION'` → What-to-expect management

3. **Add computed API endpoints** that consolidate CMS models into the expected JSON structure for backward compatibility.

### 6.2 Homepage Settings Enhancement

**Current State:** `HomepageSettings` model exists but is not used by the homepage. Hero section uses `SystemConfig` for data.

**Recommended Improvements:**

1. **Connect HomepageSettings to frontend:**
   - Add hero_background_image selection via media library
   - Add hero_cta_url to be consumed by HeroSection
   - Create API endpoint `/api/homepage` aggregating all homepage-specific content

2. **Section visibility control via HomepageSection:**
   - Enable/disable homepage sections without code changes
   - Reorder sections via drag-drop or numeric ordering
   - Status badges showing "Published" state based on source model

### 6.3 Sermon Management Improvements

**Current State:** Basic admin interface for `PublicSermon` with list editing.

**Recommended Improvements:**

1. **Add series autocomplete** with thumbnail preview in sermon admin form
2. **Bulk publish/unpublish actions** for sermons
3. **Date-based filtering** in admin changelist
4. **Media URL validation** to ensure video/audio URLs are accessible

### 6.4 Events Management Improvements

**Current State:** Basic event admin in `events/admin.py`.

**Recommended Improvements:**

1. **Add date range picker** for start/end datetime fields
2. **Event status workflow visualization** (Draft → Published → Completed)
3. **Registration analytics** (show count from EventRegistration)
4. **Location autocomplete** or saved locations

### 6.5 Testimonials Management Improvements

**Current State:** Simple list with sort_order editing.

**Recommended Improvements:**

1. **Photo preview** in changelist
2. **Approval workflow** before publishing (especially for anonymous submissions)
3. **Date range filtering** for when testimonials were added

---

## 7. Architecture Observations

### 7.1 Migration Status

- **Prisma-owned models**: `PublicSermon`, `WebsiteLeader`, `WebsiteTestimonial`, `WebsiteAcademyModule` have `managed=True` (originally `managed=False` for Prisma)
- **Django-owned models**: `GlobalSettings`, `HomepageSettings`, `ChurchProfile`, `ContentBlock`, `ServiceTime`, `HomepageSection` are fully Django-owned

### 7.2 Key Architecture Decisions

1. **SystemConfig singleton pattern**: The `key='site'` should be enforced as a singleton with custom save logic
2. **Service time configuration**: Currently comes from SystemConfig JSON, but Django has `ServiceTime` model that should be used instead
3. **ContentBlock flexibility**: The `ContentBlock` model allows storing misc content without creating new models

### 7.3 Missing Admin Integration

The following models exist but need enhanced admin for CMS experience:
- `HomepageSettings` - Not connected to frontend
- `ServiceTime` - Exists but frontend reads from SystemConfig
- `ContentBlock` - Not used for homepage content currently
- `ChurchProfile` - Mission/vision not displayed on homepage

---

## Appendix A: API Endpoints Summary

```
GET  /api/site-config        → SystemConfig (key='site')
GET  /api/sermons            → PublicSermon[] (published only)
GET  /api/sermons/{slug}     → PublicSermon detail
GET  /api/series             → SermonSeries[] (published only)
GET  /api/series/{slug}      → SermonSeries detail
GET  /api/events             → ChurchEvent[] (status=PUBLISHED)
GET  /api/events/{id}        → ChurchEvent detail
GET  /api/leaders            → WebsiteLeader[] (published only)
GET  /api/testimonials       → WebsiteTestimonial[] (published only)
GET  /api/academy            → WebsiteAcademyModule[] (published only)
POST /api/contact            → ContactSubmission
POST /api/prayer             → PrayerSubmission
POST /api/rsvp               → VisitRsvp
GET  /api/health             → Health check
```

---

## Appendix B: File References

| Layer | File Path |
|-------|-----------|
| Views | `backend/backend/apps/content/views.py`, `backend/backend/apps/events/views.py` |
| Serializers | `backend/backend/apps/content/serializers.py`, `backend/backend/apps/events/serializers.py` |
| URLs | `backend/backend/urls.py`, `backend/backend/apps/content/urls.py`, `backend/backend/apps/events/urls.py` |
| Models | `backend/backend/apps/content/models.py`, `backend/backend/apps/events/models.py` |
| Repositories | `backend/backend/apps/content/repositories.py`, `backend/backend/apps/events/repositories.py` |
| Admin | `backend/backend/apps/content/admin.py` |
| Frontend Page | `website/src/pages/index.astro` |
| Frontend API | `website/src/lib/api.ts` |
| Frontend Types | `website/src/types/*.ts` |
| Frontend Components | `website/src/components/home/*.astro` |