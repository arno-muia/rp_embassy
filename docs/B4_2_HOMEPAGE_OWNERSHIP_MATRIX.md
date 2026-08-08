# B4.2 Homepage Ownership Matrix

**Date:** 2026-07-23  
**Project:** Royal Priesthood Embassy Website  
**Purpose:** Define definitive ownership for each homepage area

---

## Complete Ownership Matrix

| Homepage Area | Source Model | Status | Notes |
|--------------|--------------|--------|-------|
| Hero Title | `HomepageSettings.hero_title` | ✅ **CMS-Owned** | Replace SystemConfig.tagline |
| Hero Scripture | `HomepageSettings.hero_scripture` | ✅ **CMS-Owned** | Replace SystemConfig.scripture |
| Hero Description | `HomepageSettings.hero_subtitle` | ✅ **CMS-Owned** | Replace SystemConfig.description |
| Hero Background | `HomepageSettings.hero_background_image` | ✅ **CMS-Owned** | New field available |
| Hero CTA Text | `HomepageSettings.hero_cta_text` | ✅ **CMS-Owned** | New field available |
| Hero CTA URL | `HomepageSettings.hero_cta_url` | ✅ **CMS-Owned** | New field available |
| Mission | `ChurchProfile.mission` | ✅ **CMS-Owned** | Currently in SystemConfig |
| Vision | `ChurchProfile.vision` | ✅ **CMS-Owned** | Currently in SystemConfig |
| Welcome Message | `ChurchProfile.welcome_message` | ✅ **CMS-Owned** | Frontend uses site.welcomeMessage |
| Pastor Message | `ChurchProfile.pastor_message` | ✅ **CMS-Owned** | For PastorSection |
| Service Times | `ServiceTime` | ✅ **CMS-Owned** | Model exists, frontend uses SystemConfig |
| Values | `ContentBlock` (VALUE) | ✅ **CMS-Owned** | Model exists, frontend uses SystemConfig |
| Beliefs | `ContentBlock` (BELIEF) | ✅ **CMS-Owned** | Model exists, frontend uses SystemConfig |
| FAQs | `ContentBlock` (FAQ) | ✅ **CMS-Owned** | Model exists, frontend uses SystemConfig |
| What to Expect | `ContentBlock` (EXPECTATION) | ✅ **CMS-Owned** | Model exists, frontend uses SystemConfig |
| Section Visibility | `HomepageSection` | ✅ **CMS-Owned** | Model exists, not yet implemented |
| Latest Sermon | `PublicSermon` | ✅ **CMS-Owned** | Already working via `/api/sermons` |
| Upcoming Events | `ChurchEvent` | ✅ **CMS-Owned** | Already working via `/api/events` |
| Testimonials | `WebsiteTestimonial` | ✅ **CMS-Owned** | Already working via `/api/testimonials` |
| Leaders | `WebsiteLeader` | ✅ **CMS-Owned** | Already working via `/api/leaders` |

---

## Model Field Mapping

### Hero Section (HomepageSettings → Frontend)

| Model Field | Frontend Property | JSON Key (Current) |
|-------------|-------------------|-------------------|
| `hero_title` | `heroTitle` | Not currently mapped |
| `hero_subtitle` | `description` | `description` |
| `hero_scripture` | `scripture` | `scripture` |
| `hero_scripture_reference` | `scriptureRef` | Not currently mapped |
| `hero_background_image` | `backgroundImage` | Not currently mapped |
| `hero_cta_text` | `ctaText` | Static "Plan Your Visit" |
| `hero_cta_url` | `ctaUrl` | Static "/visit" |

### Church Profile (ChurchProfile → Frontend)

| Model Field | Frontend Property | JSON Key (Current) |
|-------------|-------------------|-------------------|
| `mission` | `mission` | Not directly exposed (in about) |
| `vision` | `vision` | Not directly exposed (in about) |
| `welcome_message` | `welcomeMessage` | `welcomeMessage` (nested in config) |
| `pastor_message` | `pastorMessage` | Not currently mapped |
| `about_text` | `aboutText` | Not currently exposed |

### Service Times (ServiceTime → Frontend)

| Model Field | Frontend Property | JSON Key (Current) |
|-------------|-------------------|-------------------|
| `day` | `day` | `day` |
| `time` | `time` | `time` |
| `label` | `name` | `name` |
| - | `platform` | Hardcoded "physical" or "online" in frontend |
| - | `location` | Optional, from JSON |
| - | `link` | Optional, from JSON |
| - | `description` | Optional, from JSON |
| - | `image` | Optional, from JSON |

**Note:** The `platform`, `location`, `link`, `description`, and `image` fields are not in `ServiceTime` model. These are currently in SystemConfig JSON but will need to be added to the model or handled differently.

### Content Blocks (ContentBlock → Frontend)

| Content Type | Model Location | JSON Key |
|-------------|----------------|----------|
| VALUE | `content_type='VALUE'` | `values[]` |
| BELIEF | `content_type='BELIEF'` | `beliefs[]` |
| FAQ | `content_type='FAQ'` | `visitFaqs[]` |
| EXPECTATION | `content_type='EXPECTATION'` | `whatToExpect[]` |

**Model fields used:**
- `key` → `id` (unique identifier)
- `title` → `title` 
- `content` → `description` (or `answer` for FAQs)
- `display_order` → ordering in arrays

### Homepage Sections (HomepageSection → Visibility)

| Section Name | Current Component | Purpose |
|--------------|------------------|---------|
| `hero` | HeroSection | Main hero banner |
| `service_times` | ServiceTimesSection | Service schedule display |
| `events` | EventsCarouselSection | Upcoming events carousel |
| `what_to_expect` | WhatToExpectSection | Visitor expectations |
| `latest_sermon` | LatestSermonSection | Most recent sermon |
| `testimonials` | TestimonialsSection | Member testimonials |
| `pastor` | PastorSection | Pastor introduction |
| `cta_banner` | CtaBannerSection | Call to action banner |

---

## Current vs. Target Architecture

### Current Architecture (SystemConfig-centric)

```
index.astro
    ↓
GET /api/site-config
    ↓
SystemConfig (key='site') → value (JSON)
    ↓
{
    tagline → HeroSection
    scripture → HeroSection
    description → HeroSection
    serviceTimes[] → ServiceTimesSection
    whatToExpect[] → WhatToExpectSection
    values[] → CtaBannerSection (future)
    beliefs[] → Not used yet
    visitFaqs[] → Not used yet
    welcomeMessage → HeroSection (fallback)
}
```

### Target Architecture (CMS Model-centric)

```
index.astro
    ↓
GET /api/homepage
    ↓
HomepageAggregator
    ├── HomepageSettings → HeroSection
    ├── ChurchProfile → Welcome/Pastor
    ├── ServiceTime → ServiceTimesSection
    ├── ContentBlock (VALUE) → Values
    ├── ContentBlock (BELIEF) → Beliefs
    ├── ContentBlock (FAQ) → FAQs
    ├── ContentBlock (EXPECTATION) → WhatToExpectSection
    ├── HomepageSection → Section visibility
    ├── PublicSermon (latest) → LatestSermonSection
    ├── ChurchEvent (upcoming) → EventsCarouselSection
    ├── WebsiteTestimonial → TestimonialsSection
    └── WebsiteLeader → Leaders
```

---

## Field Extensions Required

### ServiceTime Model Extension Needed

The frontend `ServiceConfig` interface expects additional fields not in the current model:

```typescript
// Current ServiceTime model
{
    day: string;
    time: string;  // TimeField
    label: string;
    display_order: number;
}

// Frontend expects (from api.ts types)
{
    name: string;
    day: string;
    time: string;
    platform: "physical" | "online";
    location?: string;
    link?: string;
    description?: string;
    image?: string;
}
```

**Recommendation:** Add optional fields to ServiceTime model:
- `platform` (choices: 'physical', 'online')
- `location` (CharField, optional)
- `link` (URLField, optional)
- `description` (TextField, optional)
- `image_url` (URLField, optional)

**However:** Per task requirements, we should NOT modify models unless absolutely necessary. We will:
- Use existing `label` field for `name`
- Derive `platform` from context or use Default: "physical"
- Leave `location`, `link`, `description`, `image` as null/undefined (frontend handles gracefully)

---

## API Contract Compatibility

### Current `/api/site-config` Response

```json
{
  "name": "string",
  "shortName": "string",
  "tagline": "string",
  "scripture": "string",
  "description": "string",
  "address": { "street": "...", "city": "...", "country": "...", "mapsUrl": "..." },
  "contact": { "email": "...", "whatsapp": "..." },
  "social": { "instagram": "...", "facebook": "...", "youtube": "..." },
  "giving": { "mpesaTill": "...", "accountName": "..." },
  "academyUrl": "string",
  "welcomeMessage": { "title": "...", "message": "...", "author": "..." },
  "whatToExpect": [...],
  "beliefs": [...],
  "values": [...],
  "visitFaqs": [...],
  "serviceTimes": [...],
  "theme2026": {...}
}
```

### New `/api/homepage` Response Structure

```json
{
  "hero": {
    "title": "string",
    "subtitle": "string",
    "scripture": "string",
    "scriptureReference": "string",
    "backgroundImage": "string",
    "ctaText": "string",
    "ctaUrl": "string"
  },
  "churchProfile": {
    "mission": "string",
    "vision": "string",
    "welcomeMessage": "string",
    "pastorMessage": "string",
    "aboutText": "string"
  },
  "serviceTimes": [...],
  "values": [...],
  "beliefs": [...],
  "faqs": [...],
  "sections": [...],
  "latestSermon": {...},
  "events": [...],
  "testimonials": [...],
  "leaders": [...]
}
```

---

## Implementation Priority

| Priority | Task | Impact |
|----------|------|--------|
| 1 | Add serializers for CMS models | Required for API |
| 2 | Add repositories for CMS models | Required for queries |
| 3 | Create `/api/homepage` endpoint | Core deliverable |
| 4 | Add homepage serializers (aggregated) | API response structure |
| 5 | Validate Django admin configuration | CMS management |
| 6 | Test backward compatibility | Non-breaking change |