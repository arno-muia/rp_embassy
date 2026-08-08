# B4.3J.1 — Homepage Content Reality Audit

## 1. Homepage Render Map

| # | Homepage Section | Frontend Component | API Endpoint | Serializer | Model | Admin Registration | Admin Location |
|---|---|---|---|---|---|---|---|
| 1 | Hero Banner | `HeroSection.astro` | `/api/homepage` (hero) + `/api/site-config` | `HomepageSettingsSerializer` + `SystemConfig` | `HomepageSettings` + `SystemConfig` | `HomepageSettingsAdmin` + `SystemConfigAdmin` | Homepage > Hero Settings + Public Website Content > System Config |
| 2 | Service Times | `ServiceTimesSection.astro` | `/api/homepage` (serviceTimes) | `ServiceTimeSerializer` | `ServiceTime` | `ServiceTimeAdmin` | Homepage > Service Times |
| 3 | Upcoming Events | `EventsCarouselSection.astro` | `/api/homepage` (events) | `ChurchEventReadSerializer` | `ChurchEvent` | `ChurchEventAdmin` | Homepage > Homepage Events |
| 4 | What to Expect | `WhatToExpectSection.astro` | `/api/site-config` (whatToExpect) | `ContentBlockSerializer` | `ContentBlock` | `ContentBlockAdmin` | Public Website Content > Content Blocks |
| 5 | Latest Sermon | `LatestSermonSection.astro` | `/api/homepage` (latestSermon) | `PublicSermonReadSerializer` | `PublicSermon` | `PublicSermonAdmin` | Homepage > Homepage Sermons |
| 6 | Testimonials | `TestimonialsSection.astro` | `/api/homepage` (testimonials) | `WebsiteTestimonialReadSerializer` | `WebsiteTestimonial` | `WebsiteTestimonialAdmin` | Homepage > Homepage Testimonials |
| 7 | Pastor Profile | `PastorSection.astro` | `/api/homepage` (pastorProfile) | `PastorProfileSerializer` | `PastorProfile` | `PastorProfileAdmin` | Homepage > Pastor Profile |
| 8 | CTA Banner | `CtaBannerSection.astro` | `/api/homepage` (hero + serviceTimes) | `HomepageSettingsSerializer` + `ServiceTimeSerializer` | `HomepageSettings` + `ServiceTime` | `HomepageSettingsAdmin` + `ServiceTimeAdmin` | Homepage > Hero Settings + Service Times |

---

## 2. Hero Audit

**File:** `website/src/components/home/HeroSection.astro`

### Fields rendered in the hero:

| UI Element | Variable | Source API | Source Model | Admin Editable? | Hardcoded Fallback |
|---|---|---|---|---|---|
| Scripture reference (top label) | `config?.scripture` | `/api/site-config` | `SystemConfig` (key="site") | ✅ Yes (SystemConfig) | `site.scripture` = "1 Peter 2:9" |
| Tagline (H1 heading) | `config?.tagline` | `/api/site-config` | `SystemConfig` (key="site") | ✅ Yes (SystemConfig) | `site.tagline` = "Discover Your True Identity in Christ" |
| Description (paragraph) | `config?.description` | `/api/site-config` | `SystemConfig` (key="site") | ✅ Yes (SystemConfig) | `site.description` = long paragraph |
| Background image | `config?.heroBackgroundImage` | `/api/site-config` | `SystemConfig` (key="site") | ✅ Yes (SystemConfig) | `/images/services/kingdom-formation-1.jpg` |
| Primary CTA text | `hero?.hero_cta_text` | `/api/homepage` (hero) | `HomepageSettings` | ✅ Yes (HomepageSettings) | "Plan Your Visit" |
| Primary CTA URL | `hero?.hero_cta_url` | `/api/homepage` (hero) | `HomepageSettings` | ✅ Yes (HomepageSettings) | "/visit" |
| Secondary CTA text | `hero?.hero_secondary_cta_text` | `/api/homepage` (hero) | `HomepageSettings` | ✅ Yes (HomepageSettings) | undefined (hidden if missing) |
| Secondary CTA URL | `hero?.hero_secondary_cta_url` | `/api/homepage` (hero) | `HomepageSettings` | ✅ Yes (HomepageSettings) | undefined (hidden if missing) |

### HomepageSettings fields NOT used by HeroSection.astro:

| Field | Used? | Where Used? |
|---|---|---|
| `hero_title` | ❌ **NOT USED** | Not consumed by any component |
| `hero_subtitle` | ❌ **NOT USED** | Not consumed by any component |
| `hero_scripture` | ❌ **NOT USED** | Not consumed by any component |
| `hero_scripture_reference` | ❌ **NOT USED** | Not consumed by any component |
| `hero_background_image` | ❌ **NOT USED** | Hero uses `config.heroBackgroundImage` from SystemConfig instead |
| `cta_heading` | ✅ Used | `CtaBannerSection.astro` |
| `cta_title` | ✅ Used | `CtaBannerSection.astro` |
| `cta_description` | ✅ Used | `CtaBannerSection.astro` |
| `cta_button_text` | ✅ Used | `CtaBannerSection.astro` |
| `cta_button_url` | ✅ Used | `CtaBannerSection.astro` |
| `cta_secondary_button_text` | ✅ Used | `CtaBannerSection.astro` |
| `cta_secondary_button_url` | ✅ Used | `CtaBannerSection.astro` |
| `cta_location` | ✅ Used | `CtaBannerSection.astro` |

### CRITICAL FINDING

**The hero heading, scripture, description, and background image come from SystemConfig (site-config API), NOT from HomepageSettings.** The `HomepageSettings` model's `hero_title`, `hero_subtitle`, `hero_scripture`, `hero_scripture_reference`, and `hero_background_image` fields are **not consumed by any frontend component**. Only the CTA button fields from HomepageSettings are actually used.

---

## 3. Events Audit

**Files:**
- `website/src/components/home/EventsCarouselSection.astro`
- `website/src/lib/api.ts` → `getUpcomingEvents(5)`
- `backend/apps/events/repositories.py` → `EventRepository.published_upcoming()`
- `backend/apps/content/views.py` → `homepage()` view → `EventRepository.published_upcoming()[:5]`

### Data flow:
```
index.astro
  → getUpcomingEvents(5)          [frontend API call]
    → getEvents()                 [GET /api/events]
      → EventViewSet              [backend: EventRepository.published_upcoming()]
        → ChurchEvent.objects.filter(status='PUBLISHED').order_by('start_date_time')
    → filter(status === "upcoming" || "ongoing")
    → slice(0, 5)

ALSO:
  → getHomepage()                 [GET /api/homepage]
    → homepage() view
      → EventRepository.published_upcoming()[:5]
        → ChurchEvent.objects.filter(status='PUBLISHED').order_by('start_date_time')[:5]
```

### Answers:

1. **Are all ChurchEvent records rendered?** No. Only those with `status='PUBLISHED'` are returned by the backend. The frontend further filters to `status === "upcoming" || "ongoing"`.

2. **Is there filtering?** Yes. Backend filters `status='PUBLISHED'`. Frontend filters to `upcoming` or `ongoing` status (computed from date comparison).

3. **Is there limiting?** Yes. Backend limits to 5 (`[:5]`). Frontend also limits to 5 (`getUpcomingEvents(5)`).

4. **Is there a featured flag?** No. There is no `featured` or `is_featured` field on `ChurchEvent`. The selection is purely based on `status='PUBLISHED'` and date ordering.

5. **Why do only two events appear on homepage?** Because only 2 `ChurchEvent` records have `status='PUBLISHED'` and are upcoming/ongoing. The limit of 5 is not the constraint — the data is.

---

## 4. Sermon Audit

**Files:**
- `website/src/components/home/LatestSermonSection.astro`
- `website/src/lib/api.ts` → `getLatestSermon()`
- `backend/apps/content/views.py` → `homepage()` view → `SermonRepository.published()[:1]`
- `backend/apps/content/repositories.py` → `SermonRepository.published()`

### Data flow:
```
index.astro
  → getLatestSermon()             [frontend API call]
    → getSermons()                [GET /api/sermons]
      → SermonViewSet             [backend: SermonRepository.published()]
        → PublicSermon.objects.filter(is_published=True).order_by('-date')
    → sort by date descending
    → return sorted[0]

ALSO:
  → getHomepage()                 [GET /api/homepage]
    → homepage() view
      → SermonRepository.published()[:1]
        → PublicSermon.objects.filter(is_published=True).order_by('-date')[:1]
```

### Answers:

1. **Does homepage render all sermons?** No. Only the **latest published sermon** is rendered.

2. **Does homepage render latest sermon only?** Yes. Both the frontend (`getLatestSermon()`) and backend (`homepage()` view) return only the single most recent published sermon.

3. **How is latest determined?** By `order_by('-date')` — the `date` field (DateTimeField) sorted descending.

4. **Which admin model controls it?** `PublicSermon` (admin: `PublicSermonAdmin`). The `SermonSeries` model is also listed under "Homepage Sermons" but is **not directly consumed** by the homepage — it's only used as a FK relationship for sermon detail pages.

---

## 5. Testimonial Audit

**Files:**
- `website/src/components/home/TestimonialsSection.astro`
- `website/src/lib/api.ts` → `getTestimonials()`
- `backend/apps/content/views.py` → `homepage()` view
- `backend/apps/content/repositories.py` → `WebsiteTestimonialRepository.published()`

### Data flow:
```
index.astro
  → getTestimonials()             [GET /api/testimonials]
    → TestimonialViewSet          [backend: WebsiteTestimonialRepository.published()]
      → WebsiteTestimonial.objects.filter(is_published=True).order_by('sort_order')

ALSO:
  → getHomepage()                 [GET /api/homepage]
    → homepage() view
      → WebsiteTestimonialRepository.published()
        → WebsiteTestimonial.objects.filter(is_published=True).order_by('sort_order')
```

### Answers:

1. **Which testimonials render?** All `WebsiteTestimonial` records where `is_published=True`.

2. **How selected?** Ordered by `sort_order`. No limit — all published testimonials are returned.

3. **Is homepage consuming all testimonials?** Yes. The `TestimonialsSection` receives all testimonials and passes them to `TestimonialsCarousel`.

4. **Is there homepage-specific filtering?** No. The same endpoint (`/api/testimonials`) is used for both the homepage and the testimonials page. There is no homepage-specific filter.

---

## 6. Homepage Sections Audit

**Files:**
- `backend/apps/content/models.py` → `HomepageSection` model
- `backend/apps/content/views.py` → `homepage()` view (returns `sections`)
- `backend/apps/content/serializers.py` → `HomepageSectionSerializer`
- `website/src/pages/index.astro`

### Model fields:
- `section_name` (CharField, unique)
- `enabled` (BooleanField, default=True)
- `display_order` (IntegerField, default=0)

### Data flow:
```
homepage() view
  → HomepageSectionRepository.all_ordered()
    → HomepageSection.objects.all().order_by('display_order')
  → Serialized and returned as 'sections' in response

index.astro
  → getHomepage()                 [fetches sections data]
```

### Answers:

1. **What model does it manage?** `HomepageSection` — a visibility/ordering control for homepage sections.

2. **What API consumes it?** The `/api/homepage` endpoint returns `sections` data.

3. **What frontend component consumes it?** **NONE.** The `index.astro` page fetches `homepage.sections` but **never passes it to any component**. The `sections` data is fetched but completely unused in rendering.

4. **Is it rendered on homepage?** **NO.** The data is fetched but not consumed.

5. **Is it partially rendered?** **NO.** Zero fields are used.

6. **Is it unused?** **YES — completely unused.** The `HomepageSection` model, its admin, its serializer, and its API response are all dead code for the homepage rendering.

---

## 7. Church Profile Audit

**Files:**
- `backend/apps/content/models.py` → `ChurchProfile` model
- `backend/apps/content/views.py` → `homepage()` view (returns `churchProfile`)
- `backend/apps/content/serializers.py` → `ChurchProfileSerializer`
- `website/src/pages/index.astro`

### Model fields:
- `mission`, `vision`, `welcome_message`, `pastor_message`, `about_text`

### Data flow:
```
homepage() view
  → ChurchProfileRepository.get_solo()
    → ChurchProfile.objects.first()
  → Serialized and returned as 'churchProfile' in response

index.astro
  → getHomepage()                 [fetches churchProfile data]
```

### Answers:

1. **Which homepage section uses ChurchProfile?** **NONE.** The `index.astro` page fetches `homepage.churchProfile` but **never passes it to any component**.

2. **Which fields are rendered?** **NONE.** Zero fields from ChurchProfile are rendered on the homepage.

3. **Is every admin field used?** **NO.** All fields are unused on the homepage.

4. **Which fields are unused?** ALL: `mission`, `vision`, `welcome_message`, `pastor_message`, `about_text`.

**Note:** The `/about` page may use ChurchProfile, but that is outside the homepage scope.

---

## 8. Pastor Profile Audit

**Files:**
- `backend/apps/content/models.py` → `PastorProfile` model
- `backend/apps/content/views.py` → `homepage()` view (returns `pastorProfile`)
- `backend/apps/content/serializers.py` → `PastorProfileSerializer`
- `website/src/components/home/PastorSection.astro`
- `website/src/pages/index.astro`

### Model fields:
- `name`, `title`, `image`, `biography`, `cta_text`, `cta_url`, `display_order`, `is_active`

### Data flow:
```
homepage() view
  → PastorProfileRepository.get_active()
    → PastorProfile.objects.filter(is_active=True).first()
  → Serialized and returned as 'pastorProfile' in response

index.astro
  → getHomepage()
  → <PastorSection pastorProfile={homepage?.pastorProfile} />
```

### Fields rendered in PastorSection.astro:

| Field | Rendered? | UI Element |
|---|---|---|
| `name` | ✅ Yes | H3 heading "Our Pastor" + name displayed |
| `title` | ❌ **NOT USED** | Not consumed by PastorSection |
| `image` | ✅ Yes | Image src |
| `biography` | ✅ Yes | Paragraph text |
| `cta_text` | ✅ Yes | Link text |
| `cta_url` | ✅ Yes | Link href |
| `display_order` | ❌ **NOT USED** | Only used for admin ordering |
| `is_active` | ❌ **NOT USED** | Only used for repository filtering |

### Answers:

1. **Which homepage section uses PastorProfile?** `PastorSection.astro`

2. **Which fields are rendered?** `name`, `image`, `biography`, `cta_text`, `cta_url`

3. **Is every admin field used?** No. `title` and `display_order` are not rendered on the homepage.

4. **Which fields are unused?** `title` (not displayed anywhere in the section), `display_order` (admin-only ordering).

---

## 9. Homepage CMS Truth Matrix

| Homepage Section | Actual Source Model | Admin Screen | Fully Used | Partially Used | Unused |
|---|---|---|---|---|---|
| Hero Settings | `HomepageSettings` (CTA fields only) + `SystemConfig` (heading, scripture, description, background) | Homepage > Hero Settings + Public Website > System Config | ❌ NO | ✅ YES (CTA fields used; hero_title, hero_subtitle, hero_scripture, hero_scripture_reference, hero_background_image NOT used) | ❌ |
| Homepage Sections | `HomepageSection` | Homepage > Homepage Sections | ❌ NO | ❌ NO | ✅ YES (completely unused — data fetched but no component consumes it) |
| Church Profile | `ChurchProfile` | Homepage > Church Profile | ❌ NO | ❌ NO | ✅ YES (completely unused on homepage — data fetched but no component consumes it) |
| Pastor Profile | `PastorProfile` | Homepage > Pastor Profile | ❌ NO | ✅ YES (name, image, biography, cta_text, cta_url used; title, display_order NOT used) | ❌ |
| Service Times | `ServiceTime` | Homepage > Service Times | ✅ YES | ❌ NO | ❌ NO |
| Homepage Events | `ChurchEvent` | Homepage > Homepage Events | ✅ YES (but only PUBLISHED + upcoming/ongoing) | ❌ NO | ❌ NO |
| Homepage Sermons | `PublicSermon` (latest only) + `SermonSeries` (NOT used) | Homepage > Homepage Sermons | ❌ NO | ✅ YES (only latest sermon used; SermonSeries NOT consumed by homepage) | ❌ |
| Homepage Testimonials | `WebsiteTestimonial` | Homepage > Homepage Testimonials | ✅ YES | ❌ NO | ❌ NO |

---

## 10. Restructure Recommendations

Based strictly on evidence from code analysis:

### KEEP UNDER HOMEPAGE

| Item | Reason | Evidence |
|---|---|---|
| **Hero Settings** | Partially used — CTA fields are consumed by HeroSection and CtaBannerSection | `HeroSection.astro` lines 15-18, `CtaBannerSection.astro` lines 22-29 |
| **Service Times** | Fully used — all fields consumed by ServiceTimesSection | `ServiceTimesSection.astro` renders name, day, time, platform, location, description, image, link |
| **Homepage Events** | Fully used — events are rendered in EventsCarouselSection | `EventsCarouselSection.astro` renders all event fields |
| **Homepage Testimonials** | Fully used — all published testimonials rendered | `TestimonialsSection.astro` + `TestimonialsCarousel.astro` |
| **Pastor Profile** | Partially used — 5 of 8 fields rendered | `PastorSection.astro` lines 3-10 |

### RENAME

| Current Name | Recommended Name | Reason |
|---|---|---|
| **Homepage Sermons** | **Latest Sermon** | Homepage only renders the single most recent published sermon, not all sermons. `SermonSeries` should be removed from this group. |
| **Homepage Events** | **Upcoming Events** | Homepage only renders PUBLISHED events that are upcoming/ongoing, limited to 5. |

### MOVE OUT OF HOMEPAGE

| Item | Action | Reason | Evidence |
|---|---|---|---|
| **Homepage Sections** | **Remove from Homepage group** | Completely unused — no component consumes the data | `index.astro` fetches `sections` but never passes it to any component |
| **Church Profile** | **Remove from Homepage group** | Completely unused on homepage — no component consumes the data | `index.astro` fetches `churchProfile` but never passes it to any component |

### REMOVE FROM HOMEPAGE GROUP

| Item | Action | Reason |
|---|---|---|
| **SermonSeries** | Remove from "Homepage Sermons" group | Only `PublicSermon` is consumed by the homepage. `SermonSeries` is only used for sermon detail pages, not the homepage. |

### REPLACE / FIX

| Item | Recommendation | Evidence |
|---|---|---|
| **Hero Settings admin** | Add note that hero_title, hero_subtitle, hero_scripture, hero_scripture_reference, hero_background_image are NOT consumed by the frontend. The actual hero heading/scripture/description come from SystemConfig. | `HeroSection.astro` lines 11-14 use `config` (SystemConfig), not `hero` (HomepageSettings) |
| **SystemConfig** | Consider adding a "Hero Content" section under Homepage for the SystemConfig fields that actually control the hero heading, scripture, and description. | The hero's scripture, tagline, description, and background image are all controlled by SystemConfig key="site" |

### SUMMARY OF ACTIONS

| Admin Item | Action |
|---|---|
| Hero Settings | ✅ KEEP — but note that only CTA fields are used; hero_title/subtitle/scripture fields are dead |
| Homepage Sections | ❌ REMOVE from Homepage group — completely unused |
| Church Profile | ❌ REMOVE from Homepage group — completely unused on homepage |
| Pastor Profile | ✅ KEEP — partially used (5/8 fields) |
| Service Times | ✅ KEEP — fully used |
| Homepage Events | ✅ KEEP — rename to "Upcoming Events" |
| Homepage Sermons | ✅ KEEP — rename to "Latest Sermon", remove SermonSeries |
| Homepage Testimonials | ✅ KEEP — fully used |

---

## Validation

```
$ python manage.py check
System check identified no issues (0 silenced).
```

No code changes were made during this audit.