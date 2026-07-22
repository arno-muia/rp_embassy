# B1 API Contract Matrix

**Phase:** B1.5 — Final Architecture Validation
**Date:** 2026-07-20
**Status:** Approved
**Related:** `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md`

---

## Purpose

This document defines the complete API contract between the Django backend and Astro frontend before B2 implementation. It eliminates ambiguity about endpoint shapes, authentication, caching, filtering, and pagination.

---

## Authentication & Authorization Summary

| Audience | Authentication | Permission |
|----------|----------------|------------|
| Public reads | None (AllowAny) | Read-only access to published content |
| Submission endpoints | None (AllowAny) | POST-only; rate-limited |
| Admin endpoints | Session / Token (IsAuthenticated) | Role-based |
| Media public | None (AllowAny) | Read-only; only `is_public=True` |

---

## Public Read Endpoints

### `GET /api/site-config`

**Purpose:** Returns all site-wide configuration consumed by the frontend.

**Response Schema:**
```json
{
  "global_settings": {
    "church_name": "string",
    "short_name": "string",
    "tagline": "string",
    "address": "string",
    "email": "string",
    "phone": "string",
    "whatsapp": "string",
    "social_links": {},
    "mpesa_till": "string",
    "mpesa_account_name": "string",
    "academy_url": "string"
  },
  "homepage_settings": {
    "hero_title": "string",
    "hero_subtitle": "string",
    "homepage_scripture_ref": "string",
    "homepage_scripture_text": "string",
    "homepage_tagline": "string",
    "cta_text": "string",
    "cta_link_url": "string"
  },
  "church_profile": {
    "mission_text": "string",
    "vision_text": "string",
    "welcome_message": "string",
    "church_history": "string",
    "pastor_bio_title": "string",
    "pastor_bio_subtitle": "string",
    "pastor_bio_body": "string",
    "pastor_cta_text": "string",
    "pastor_cta_link_url": "string",
    "pastor_image_url": "string"
  },
  "service_times": [
    {
      "id": "integer",
      "day": "string",
      "time": "string",
      "label": "string",
      "display_order": "integer"
    }
  ],
  "content_blocks": [
    {
      "key": "string",
      "category": "string",
      "title": "string",
      "body": "string",
      "display_order": "integer",
      "is_active": "boolean"
    }
  ]
}
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=300` (5 min). Invalidated on any singleton change.

**Filtering:** None

**Pagination:** None

**Search Support:** No

**Consumed By:** Homepage, About, Visit, Contact, Give, Footer

---

### `GET /api/homepage`

**Purpose:** Returns homepage-specific aggregated data (sections).

**Response Schema:**
```json
{
  "hero": { /* from HomepageSettings */ },
  "sermon": {
    "latest_sermon": { /* PublicSermon serialized */ }
  },
  "events": {
    "upcoming": [ /* ChurchEvent list */ ]
  },
  "testimonials": {
    "featured": [ /* WebsiteTestimonial list */ ]
  },
  "announcements": {
    "active": [ /* Announcement list */ ]
  },
  "pastor": { /* from ChurchProfile */ },
  "what_to_expect": [ /* ContentBlock category=EXPECTATION */ ]
}
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=300`. Invalidated on any contributing content change.

**Filtering:** None (server aggregates)

**Pagination:** None

**Search Support:** No

**Consumed By:** Homepage (`index.astro`)

---

### `GET /api/announcements/active`

**Purpose:** Returns currently active announcements for display.

**Response Schema:**
```json
[
  {
    "id": "integer",
    "title": "string",
    "body": "string",
    "severity": "string",
    "priority": "integer",
    "display_from": "datetime",
    "display_until": "datetime",
    "target_audience": "string",
    "image_url": "string",
    "link_url": "string",
    "is_active": "boolean"
  }
]
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=60` (1 min). Invalidated on Announcement save/delete.

**Filtering:** Server-side: `is_active=True`, `display_from <= now`, `display_until >= now`.

**Pagination:** None (returns all active)

**Search Support:** No

**Consumed By:** Homepage announcement banner, Admin dashboard

---

### `GET /api/sermons`

**Purpose:** Returns published sermon list.

**Response Schema:**
```json
{
  "count": "integer",
  "next": "string | null",
  "previous": "string | null",
  "results": [
    {
      "id": "integer",
      "slug": "string",
      "title": "string",
      "date": "date",
      "speaker": "string",
      "description": "string",
      "thumbnail_url": "string",
      "is_featured": "boolean",
      "series": {
        "id": "integer",
        "slug": "string",
        "title": "string"
      }
    }
  ]
}
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=300`. Invalidated on sermon save/delete.

**Filtering:** `?series=&speaker=&tag=&featured=&search=`

**Pagination:** `?page=1&page_size=12` (max 50)

**Search Support:** Yes — `?search=` (PostgreSQL FTS on title, description, speaker, scripture_ref)

**Consumed By:** Sermons page, Homepage latest sermon, Series detail

---

### `GET /api/sermons/:slug`

**Purpose:** Returns sermon detail.

**Response Schema:**
```json
{
  "id": "integer",
  "slug": "string",
  "title": "string",
  "date": "date",
  "speaker": "string",
  "description": "string",
  "transcript_url": "string",
  "audio_url": "string",
  "video_url": "string",
  "thumbnail_url": "string",
  "is_featured": "boolean",
  "published_at": "datetime",
  "series": { ... }
}
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=300`. Invalidated on sermon update.

**Filtering:** None

**Pagination:** None

**Search Support:** No

**Consumed By:** Sermon detail page

---

### `GET /api/series`

**Purpose:** Returns published series list.

**Response Schema:**
```json
{
  "count": "integer",
  "next": "string | null",
  "previous": "string | null",
  "results": [
    {
      "id": "integer",
      "slug": "string",
      "title": "string",
      "description": "string",
      "artwork_url": "string",
      "is_featured": "boolean"
    }
  ]
}
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=600`. Invalidated on series save/delete.

**Filtering:** `?featured=&search=`

**Pagination:** `?page=1&page_size=12` (max 50)

**Search Support:** Yes — `?search=` (PostgreSQL FTS on title, description)

**Consumed By:** Series page, Sermon detail

---

### `GET /api/series/:slug`

**Purpose:** Returns series detail with sermons.

**Response Schema:**
```json
{
  "id": "integer",
  "slug": "string",
  "title": "string",
  "description": "string",
  "artwork_url": "string",
  "is_featured": "boolean",
  "sermons": [ /* PublicSermon list */ ]
}
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=600`. Invalidated on series or sermon update.

**Filtering:** None

**Pagination:** None

**Search Support:** No

**Consumed By:** Series detail page

---

### `GET /api/events`

**Purpose:** Returns upcoming/past event list.

**Response Schema:**
```json
{
  "count": "integer",
  "next": "string | null",
  "previous": "string | null",
  "results": [
    {
      "id": "integer",
      "title": "string",
      "description": "string",
      "start_date_time": "datetime",
      "end_date_time": "datetime",
      "location": "string",
      "category": "string",
      "poster_url": "string",
      "is_featured": "boolean",
      "rsvp_enabled": "boolean"
    }
  ]
}
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=300`. Invalidated on event save/delete.

**Filtering:** `?status=published&category=&featured=&search=&start_after=&start_before=`

**Pagination:** `?page=1&page_size=12` (max 50)

**Search Support:** Yes — `?search=` (PostgreSQL FTS on title, description, location)

**Consumed By:** Events page, Homepage events carousel

---

### `GET /api/events/:id`

**Purpose:** Returns event detail.

**Response Schema:**
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "start_date_time": "datetime",
  "end_date_time": "datetime",
  "location": "string",
  "category": "string",
  "poster_url": "string",
  "is_featured": "boolean",
  "rsvp_enabled": "boolean",
  "status": "string",
  "registrations_count": "integer"
}
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=300`. Invalidated on event update.

**Filtering:** None

**Pagination:** None

**Search Support:** No

**Consumed By:** Event detail page

---

### `GET /api/leaders`

**Purpose:** Returns active leadership list.

**Response Schema:**
```json
[
  {
    "id": "integer",
    "name": "string",
    "role": "string",
    "photo_url": "string",
    "sort_order": "integer"
  }
]
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=600`. Invalidated on leader update.

**Filtering:** None

**Pagination:** None (all leaders)

**Search Support:** No

**Consumed By:** About page

---

### `GET /api/testimonials`

**Purpose:** Returns published testimonials.

**Response Schema:**
```json
[
  {
    "id": "integer",
    "name": "string",
    "quote": "string",
    "role": "string",
    "photo_url": "string",
    "is_featured": "boolean"
  }
]
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=300`. Invalidated on testimonial update.

**Filtering:** `?featured=true`

**Pagination:** None (all)

**Search Support:** No

**Consumed By:** Homepage testimonials, Testimonials page

---

### `GET /api/academy`

**Purpose:** Returns academy module list.

**Response Schema:**
```json
[
  {
    "id": "integer",
    "title": "string",
    "description": "string",
    "image_url": "string",
    "instructor": "string"
  }
]
```

**Authentication:** None

**Cache Strategy:** `Cache-Control: public, max-age=600`. Invalidated on module update.

**Filtering:** None

**Pagination:** None (all)

**Search Support:** No

**Consumed By:** Academy page

---

### `GET /api/media/:id`

**Purpose:** Returns public media asset metadata.

**Response Schema:**
```json
{
  "id": "uuid",
  "title": "string",
  "url": "string",
  "alt_text": "string",
  "width": "integer",
  "height": "integer",
  "mime_type": "string"
}
```

**Authentication:** None (only `is_public=True`)

**Cache Strategy:** `Cache-Control: public, max-age=600`. Invalidated on media update/delete.

**Filtering:** None

**Pagination:** None

**Search Support:** No

**Consumed By:** Frontend image rendering, CMS admin

---

## Submission Endpoints

### `POST /api/contact`

**Purpose:** Submit contact form.

**Request:**
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "message": "string"
}
```

**Response:** `201 Created` with submission reference.

**Authentication:** None (rate-limited)

**Cache Strategy:** No cache

**Consumed By:** Contact page

---

### `POST /api/prayer`

**Purpose:** Submit prayer request.

**Request:**
```json
{
  "name": "string",
  "email": "string",
  "prayer_request": "string",
  "is_anonymous": "boolean"
}
```

**Response:** `201 Created` with submission reference.

**Authentication:** None (rate-limited)

**Cache Strategy:** No cache

**Consumed By:** Prayer page

---

### `POST /api/rsvp`

**Purpose:** Submit event RSVP.

**Request:**
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "event_id": "integer"
}
```

**Response:** `201 Created` with registration reference.

**Authentication:** None (rate-limited)

**Cache Strategy:** No cache

**Consumed By:** Event detail, Visit page

---

## Admin Write Endpoints

### `POST /api/admin/sermons`

**Purpose:** Create sermon (draft).

**Authentication:** `IsAuthenticated` + Media Team or Content Editor

**Request:** Multipart (JSON + optional thumbnail file)

**Response:** 201 with sermon data

**Validation:** title, date required.

**AuditLog:** Yes

---

### `PUT/PATCH /api/admin/sermons/:id`

**Purpose:** Update sermon.

**Authentication:** `IsAuthenticated` + role-based (draft: any author/editor; published: Admin/Pastor)

**Request:** Multipart

**Response:** 200 with updated data

**AuditLog:** Yes

---

### `POST /api/admin/sermons/:id/submit-review`

**Purpose:** Transition DRAFT → IN_REVIEW.

**Authentication:** `IsAuthenticated` + Content Editor (author)

**Response:** 200 with updated status

**AuditLog:** Yes

---

### `POST /api/admin/sermons/:id/approve`

**Purpose:** Transition IN_REVIEW → APPROVED.

**Authentication:** `IsAuthenticated` + Pastor

**Response:** 200 with updated status

**AuditLog:** Yes

---

### `POST /api/admin/sermons/:id/publish`

**Purpose:** Transition APPROVED → PUBLISHED.

**Authentication:** `IsAuthenticated` + Administrator

**Response:** 200 with updated status

**AuditLog:** Yes

---

### `POST /api/admin/sermons/:id/archive`

**Purpose:** Transition to ARCHIVED.

**Authentication:** `IsAuthenticated` + Administrator or Super Admin

**Response:** 200 with updated status

**AuditLog:** Yes

---

### `POST /api/admin/events`

**Purpose:** Create event.

**Authentication:** `IsAuthenticated` + Content Editor or Media Team

**Request:** JSON + optional image

**Response:** 201

**AuditLog:** Yes

---

### `POST/PUT/PATCH/DELETE /api/admin/events/:id`

Follows same pattern as sermons with workflow transitions.

---

### `POST /api/admin/announcements`

**Purpose:** Create announcement.

**Authentication:** `IsAuthenticated` + Content Editor or Administrator

**Request:** JSON + optional image

**Response:** 201

**AuditLog:** Yes

---

### `POST /api/admin/testimonials`

**Purpose:** Create testimonial.

**Authentication:** `IsAuthenticated` + Content Editor

**Request:** JSON + optional photo

**Response:** 201

**AuditLog:** Yes

**Workflow:** DRAFT → IN_REVIEW → APPROVED → PUBLISHED → ARCHIVED (same as sermons)

---

### `POST /api/admin/leaders`

**Purpose:** Create/update leader.

**Authentication:** `IsAuthenticated` + Church Administrator

**Request:** JSON + optional photo

**Response:** 201/200

**AuditLog:** Yes

**Workflow:** Simple DRAFT → PUBLISHED (no Pastor approval)

---

### `POST /api/admin/academy`

**Purpose:** Create/update academy module.

**Authentication:** `IsAuthenticated` + Content Editor

**Request:** JSON + optional image

**Response:** 201/200

**AuditLog:** Yes

**Workflow:** Simple DRAFT → PUBLISHED

---

### `POST /api/admin/global-settings`

**Purpose:** Update GlobalSettings singleton.

**Authentication:** `IsAuthenticated` + Church Administrator or Super Admin

**Request:** JSON

**Response:** 200 with full settings object

**AuditLog:** Yes (always logs old/new values)

---

### `POST /api/admin/homepage-settings`

**Purpose:** Update HomepageSettings singleton.

**Authentication:** `IsAuthenticated` + Content Editor (draft) or Pastor (approve) or Administrator (publish)

**Request:** JSON

**Response:** 200

**AuditLog:** Yes

**Workflow:** Draft → In Review → Approved → Published (singleton workflow)

---

### `POST /api/admin/church-profile`

**Purpose:** Update ChurchProfile singleton.

**Authentication:** `IsAuthenticated` + Content Editor (draft) or Pastor (approve) or Administrator (publish)

**Request:** JSON + optional image

**Response:** 200

**AuditLog:** Yes

**Workflow:** Draft → In Review → Approved → Published (singleton workflow)

---

### `POST /api/admin/content-blocks`

**Purpose:** Create/update ContentBlock.

**Authentication:** `IsAuthenticated` + Content Editor

**Request:** JSON

**Response:** 201/200

**AuditLog:** Yes

**Workflow:** Category BELIEF/VALUE/FAQ follows full approval workflow. PAGE_SECTION/EXPECTATION/THEME follow simple publish.

---

### `POST /api/admin/content-blocks/:id/submit-review`
### `POST /api/admin/content-blocks/:id/approve`
### `POST /api/admin/content-blocks/:id/publish`
### `POST /api/admin/content-blocks/:id/archive`

Same pattern as sermons, conditional on category.

---

### `POST /api/admin/service-times`

**Purpose:** Create/update ServiceTime.

**Authentication:** `IsAuthenticated` + Church Administrator

**Request:** JSON

**Response:** 201/200

**AuditLog:** Yes

**Workflow:** No approval required; always live.

---

### `POST /api/admin/media/upload`

**Purpose:** Upload media asset.

**Authentication:** `IsAuthenticated` + Media Team or Content Editor

**Request:** Multipart (file + alt_text)

**Response:** 201 with MediaAsset data

**AuditLog:** Yes

**Validation:** file required; alt_text required; max size enforced.

---

### `PUT /api/admin/media/:id`

**Purpose:** Update media metadata (alt_text, title, focal point).

**Authentication:** `IsAuthenticated` + Media Team

**Request:** JSON

**Response:** 200

**AuditLog:** Yes

---

### `DELETE /api/admin/media/:id`

**Purpose:** Delete media asset.

**Authentication:** `IsAuthenticated` + Media Team or Administrator

**Response:** 204

**AuditLog:** Yes

**Validation:** Check `usage_count > 0` — warn or prevent deletion if referenced.

---

### `GET /api/admin/prayer-requests`

**Purpose:** List prayer requests for moderation.

**Authentication:** `IsAuthenticated` + Pastor or Content Editor

**Response:** List with status filter

**Pagination:** Yes

---

### `POST /api/admin/prayer-requests/:id/approve`

**Purpose:** Set `is_public=True`, `status=ACTIVE`.

**Authentication:** `IsAuthenticated` + Pastor

**Response:** 200

**AuditLog:** Yes

---

### `POST /api/admin/prayer-requests/:id/mark-answered`

**Purpose:** Set `status=ANSWERED`, `answered_note`.

**Authentication:** `IsAuthenticated` + Pastor

**Response:** 200

**AuditLog:** Yes

---

### `GET /api/admin/audit-log`

**Purpose:** List audit log entries.

**Authentication:** `IsAuthenticated` + Super Admin

**Response:** Paginated list with filters

**Pagination:** Yes (default 50, max 200)

**Filters:** `?model=&action=&performed_by=&date_from=&date_to=`

---

### `GET /api/admin/users`

**Purpose:** List users for role management.

**Authentication:** `IsAuthenticated` + Church Administrator or Super Admin

**Response:** Paginated user list

**Pagination:** Yes

---

### `POST /api/admin/users/:id/change-role`

**Purpose:** Change user role.

**Authentication:** `IsAuthenticated` + Super Admin

**Request:** `{ "role": "string" }`

**Response:** 200

**AuditLog:** Yes

---

## Rate Limiting

| Endpoint Type | Limit |
|---------------|-------|
| Public reads | No limit (cached) |
| Submissions (contact, prayer, rsvp) | 5 requests per minute per IP |
| Admin writes | No limit (authenticated) |

## Versioning

- Base URL: `/api/v1/` (reserved for future; current implementation omits version prefix).
- Breaking changes require version bump.

## Error Responses

Standard DRF error format:
```json
{
  "detail": "Error message"
}
```

Validation errors:
```json
{
  "field_name": ["Error 1", "Error 2"]
}
```

## Webhooks / Hooks

No webhooks in B2. Cache invalidation handled via `post_save` / `post_delete` signals synchronously.