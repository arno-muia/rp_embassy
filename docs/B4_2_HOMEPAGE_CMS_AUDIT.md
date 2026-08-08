# B4.2 Homepage CMS Refactor Audit

**Date:** 2026-07-23  
**Project:** Royal Priesthood Embassy Website  
**Purpose:** Document the current homepage architecture and prepare for CMS ownership refactor

---

## 1. Model Fields Audit

### HomepageSettings (Singleton - managed=True)

| Field | Type | Null/Blank | Description |
|-------|------|------------|-------------|
| `hero_title` | CharField(255) | nullable | Hero section main title |
| `hero_subtitle` | CharField(512) | nullable | Hero section subtitle |
| `hero_scripture` | TextField | nullable | Scripture reference text |
| `hero_scripture_reference` | CharField(128) | nullable | Scripture citation |
| `hero_background_image` | URLField(512) | nullable | Hero background image URL |
| `hero_cta_text` | CharField(128) | nullable | Call-to-action button text |
| `hero_cta_url` | URLField(512) | nullable | Call-to-action button URL |
| `created_at` | DateTimeField | auto | Creation timestamp |
| `updated_at` | DateTimeField | auto | Update timestamp |

### ChurchProfile (Singleton - managed=True)

| Field | Type | Null/Blank | Description |
|-------|------|------------|-------------|
| `mission` | TextField | nullable | Church mission statement |
| `vision` | TextField | nullable | Church vision statement |
| `welcome_message` | TextField | nullable | Welcome message text |
| `pastor_message` | TextField | nullable | Pastor's message |
| `about_text` | TextField | nullable | About section text |
| `created_at` | DateTimeField | auto | Creation timestamp |
| `updated_at` | DateTimeField | auto | Update timestamp |

### ServiceTime (Multiple entries - managed=True)

| Field | Type | Null/Blank | Description |
|-------|------|------------|-------------|
| `day` | CharField(12) | - | Day of week choice (MONDAY-SUNDAY) |
| `time` | TimeField | - | Service time |
| `label` | CharField(128) | - | Service name/label |
| `display_order` | IntegerField | default=0 | Ordering for display |
| `created_at` | DateTimeField | auto | Creation timestamp |
| `updated_at` | DateTimeField | auto | Update timestamp |

### ContentBlock (Multiple entries - managed=True)

| Field | Type | Null/Blank | Description |
|-------|------|------------|-------------|
| `key` | CharField(128) | unique | Unique identifier for content block |
| `title` | CharField(255) | - | Content block title |
| `content` | TextField | - | Main content text |
| `content_type` | CharField(20) | choices | BELIEF, VALUE, FAQ, EXPECTATION, PAGE_SECTION, THEME |
| `display_order` | IntegerField | default=0 | Ordering for display |
| `is_rich_text` | BooleanField | default=False | Rich text flag |
| `is_active` | BooleanField | default=True | Active status |
| `created_at` | DateTimeField | auto | Creation timestamp |
| `updated_at` | DateTimeField | auto | Update timestamp |

### HomepageSection (Multiple entries - managed=True)

| Field | Type | Null/Blank | Description |
|-------|------|------------|-------------|
| `section_name` | CharField(128) | unique | Section identifier |
| `enabled` | BooleanField | default=True | Section visibility |
| `display_order` | IntegerField | default=0 | Ordering for display |
| `created_at` | DateTimeField | auto | Creation timestamp |
| `updated_at` | DateTimeField | auto | Update timestamp |

---

## 2. Current API Flow Analysis

### Homepage Data Sources

| Homepage Area | Current Source | API Endpoint | Model Relationship |
|--------------|----------------|--------------|-------------------|
| **Hero** | SystemConfig JSON | `/api/site-config` | Should use HomepageSettings |
| **Mission/Vision/About** | SystemConfig JSON | `/api/site-config` | Should use ChurchProfile |
| **Service Times** | SystemConfig JSON | `/api/site-config` | Should use ServiceTime |
| **Values** | SystemConfig JSON | `/api/site-config` | Should use ContentBlock (VALUE type) |
| **Beliefs** | SystemConfig JSON | `/api/site-config` | Should use ContentBlock (BELIEF type) |
| **FAQs** | SystemConfig JSON | `/api/site-config` | Should use ContentBlock (FAQ type) |
| **Section Visibility** | Not implemented | N/A | Should use HomepageSection |
| **Sermons** | PublicSermon | `/api/sermons` | Already correct |
| **Events** | ChurchEvent | `/api/events` | Already correct |
| **Testimonials** | WebsiteTestimonial | `/api/testimonials` | Already correct |
| **Leaders** | WebsiteLeader | `/api/leaders` | Already correct |

### Current Flow Diagram

```
GET /api/site-config
    ↓
SystemConfigRepository.get_by_key('site')
    ↓
SystemConfig.value (JSON blob)
    ↓
Returns: {
    name, shortName, tagline, scripture, description,
    address, contact, social, giving,
    serviceTimes[], whatToExpect[],
    beliefs[], values[], visitFaqs[],
    theme2026?
}
```

---

## 3. SystemConfig JSON Structure Analysis

Based on `api.ts` `SiteConfig` interface, the current structure includes:

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
    "mapsUrl": "..."
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
      "link": "...",
      "description": "..."
    }
  ],
  "whatToExpect": [...],
  "beliefs": [...],
  "values": [...],
  "visitFaqs": [...],
  "theme2026": {...}
}
```

---

## 4. Key Findings

### Issues Identified

1. **Hero Section Dependency**: HomepageSettings model exists but frontend reads hero data from SystemConfig JSON instead
2. **Static Service Times**: ServiceTime model exists but is not used by frontend
3. **ContentBlock Underutilization**: ContentBlock model supports BELIEF, VALUE, FAQ types but frontend reads from JSON
4. **No Section Control**: HomepageSection model exists for visibility ordering but is not implemented
5. **Singleton Pattern Not Enforced**: HomepageSettings and ChurchProfile should be singletons but no enforcement code exists

### Models Ready for Migration

| Model | Status | Ready for Homepage Use? |
|-------|--------|-------------------------|
| HomepageSettings | Registered in admin | Yes (add hero_background_image) |
| ChurchProfile | Registered in admin | Yes (already has all needed fields) |
| ServiceTime | Registered in admin | Yes (frontend needs platform field extension) |
| ContentBlock | Registered in admin | Yes (content_type covers all needed categories) |
| HomepageSection | Registered in admin | Yes (for visibility control) |
| SystemConfig | Registered in admin | Must remain for backward compatibility |

---

## 5. Recommendations

1. Create dedicated serializers for CMS models (HomepageSettings, ChurchProfile, ServiceTime, ContentBlock, HomepageSection)
2. Create repository methods for all CMS models
3. Create aggregation endpoint `/api/homepage` that:
   - Returns hero data from HomepageSettings
   - Returns church profile from ChurchProfile
   - Returns service times from ServiceTime
   - Returns values/beliefs from ContentBlock
   - Returns section visibility from HomepageSection
4. Maintain backward compatibility with `/api/site-config`
5. Document migration path for existing JSON content

---

## 6. File Inventory

| Layer | File | Status |
|-------|------|--------|
| Models | `backend/apps/content/models.py` | ✅ Exists with all required models |
| Serializers | `backend/apps/content/serializers.py` | ⚠️ Missing CMS model serializers |
| Repositories | `backend/apps/content/repositories.py` | ⚠️ Missing CMS model repositories |
| Views | `backend/apps/content/views.py` | ⚠️ Missing homepage aggregation view |
| URLs | `backend/apps/content/urls.py` | ⚠️ Missing homepage endpoint |
| Admin | `backend/apps/content/admin.py` | ✅ All models registered |
| Frontend Types | `website/src/types/*.ts` | ✅ Sermon, Event, Leader, Testimonial types exist |
| Frontend API | `website/src/lib/api.ts` | ✅ getSiteConfig() exists |
| Frontend Page | `website/src/pages/index.astro` | ⚠️ Uses SystemConfig, needs migration