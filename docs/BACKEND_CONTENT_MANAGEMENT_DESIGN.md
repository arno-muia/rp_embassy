# Backend Content Management Design

**Phase:** B1 — Backend Content Management Architecture Review
**Status:** Approved — With Required Revisions (no code, no models yet)
**Date:** 2026-07-17
**Revised:** 2026-07-20
**Author:** Backend Architecture Review
**Scope:** Old App (`rpwebsite/apps/web`) + New App (`rpwebsite/RP`) — full content audit, design, ADR

---

## 1. Executive Summary

The RP platform currently renders its public website from a **static JSON content layer** (`apps/web/content/*.json`) consumed by both an old Next.js app and the new Astro frontend (`rpwebsite/RP/website`). The new Django backend (`rpwebsite/RP/backend`) re-implements the *same* content as read-only, `managed=False` models mapped 1:1 onto a PostgreSQL schema originally defined in Prisma, exposed via a small set of `ReadOnlyModelViewSet` endpoints.

This document reviews **every existing content type and page component**, classifies each piece of content as static, frequently-changing, admin-editable, code-configured, versioned, or workflow-driven, and defines **who manages what, how often, and why**. It then recommends a Django app structure, a media strategy, a permissions model, an API strategy, a publishing/lifecycle model, and a scalability path from single-church to multi-campus to denomination network.

**Key principle:** *Do not move everything into the Django admin.* Only content that changes regularly, carries business value when delegated to non-developers, or requires governance (publishing, archival, history) should become editable. Structural/brand constants remain code-configured.

Two companion documents:
- `RP/docs/adr/ADR-001-CONTENT-MANAGEMENT-ARCHITECTURE.md` (decision record)
- This file (full design)

---

## 2. Current State Analysis

### 2.1 Old Application (`rpwebsite/apps/web`)
- **Framework:** Next.js (App Router) + Prisma + Turso/LibSQL (PostgreSQL target).
- **Content source of truth:** JSON files in `content/` — `site.json`, `sermons.json`, `series.json`, `events.json`, `testimonials.json`, `leadership.json`, `academy-modules.json`.
- **Authoring model:** A developer edits JSON by hand and redeploys. No admin UI. No publishing workflow. No image management (images are static `/public/images/*` assets referenced by path).
- **Schema:** `prisma/schema.prisma` defines a far richer domain (members, households, giving, attendance, cell groups, prayer requests, care cases, announcements, communications) but the **public website content subset** is only: `SystemConfig`, `SermonSeries`, `PublicSermon`, `WebsiteLeader`, `WebsiteTestimonial`, `WebsiteAcademyModule`, `ContactSubmission`, `PrayerSubmission`, `VisitRsvp`, plus `ChurchEvent`/`EventRegistration` (events).

### 2.2 New Application (`rpwebsite/RP`)
- **Backend:** Django + Django REST Framework. Apps: `accounts`, `members`, `content`, `events`, `giving`, `prayer`.
- **Current state of content models:** All `content.*` and `events.*` models use `managed = False` and mirror Prisma table names. They are **read-only** — views use `ReadOnlyModelViewSet` and `AllowAny`. There is **no write path, no Django admin registration, no image upload field (only `CharField` URL strings), no versioning, no soft-archive beyond `isPublished` booleans.**
- **Frontend:** Astro SSG/SSR consuming the Django API via `src/lib/api.ts`. Site defaults duplicated in `src/lib/site.ts` as fallbacks. SEO via `src/lib/seo.ts`.
- **Gap:** The backend faithfully mirrors the *old static JSON*, including its limitations:
  - No `Announcement` model (despite being in Prisma schema & AuditLog actions).
  - No `FAQ`, `Beliefs`, `Values`, `WelcomeMessage`, `ServiceTimes`, `Theme` as first-class models — they are **baked into a single `SystemConfig` row with key `site`** as one giant JSON blob.
  - `ChurchEvent` has no `category` value mapping to the frontend (frontend hardcodes `category: "special"`).
  - Images are referenced by string URL, not managed uploads.

### 2.3 What the audit revealed

| # | Finding | Impact |
|---|---------|--------|
| 1 | All site-structured content (beliefs, values, FAQs, service times, welcome, theme) lives in one JSON blob | Cannot be edited granularly; one typo breaks the whole site config |
| 2 | Images are hardcoded `/public/images/*` paths | No upload, no CDN, no per-item media |
| 3 | `managed=False` everywhere | Backend cannot yet create/migrate/own the schema |
| 4 | Read-only API only | No admin workflow possible today |
| 5 | Testimonials have no expiry/featured/archive | Stale quotes accumulate |
| 6 | Events `status` enum exists (DRAFT/PUBLISHED/CANCELLED/COMPLETED) but frontend derives its own `past/upcoming/ongoing` | Two sources of truth for "what's live" |
| 7 | No `Announcement`/`Banner` entity | Homepage has no rotating announcement capability |
| 8 | Duplicate site config in `site.ts` (frontend) and `site.json` (backend) | Drift risk between code and DB |

---

## 3. Content Inventory

Every content type consumed by the site, with its current source and classification.

### 3.1 Inventory table (summary)

| Content Type | Source (OLD) | Source (NEW backend) | Frequency | Editable in Admin? | Dedicated Model? | Images? | Publish/Unpublish? | Ordering? | Archival? |
|--------------|--------------|----------------------|-----------|--------------------|------------------|---------|---------------------|-----------|-----------|
| Sermons | sermons.json | PublicSermon | Weekly | YES | YES (legacy, managed=False) | YES (thumb) | YES | by date | YES |
| Series | series.json | SermonSeries | Monthly | YES | YES (legacy, managed=False) | YES (art) | YES | YES | n/a |
| Events | events.json | ChurchEvent | Weekly | YES | YES (legacy, managed=False) | YES (poster) | YES (status) | by date | YES |
| Testimonials | testimonials.json | WebsiteTestimonial | Monthly | YES | YES (legacy, managed=False) | YES (photo) | YES | YES | YES (recommended) |
| Leadership | leadership.json | WebsiteLeader | Quarterly | YES | YES (legacy, managed=False) | YES (photo) | YES | YES | soft |
| Academy Modules | academy-modules.json | WebsiteAcademyModule | Quarterly | YES | YES (legacy, managed=False) | optional | YES | YES | n/a |
| GlobalSettings (church name, contact, social, address, giving) | site.json | GlobalSettings | Rarely | YES (new, managed=True) | YES (new) | no | n/a | n/a | no |
| HomepageSettings (hero, scripture, tagline, CTA) | site.json / site.ts | HomepageSettings | Rarely | YES (new, managed=True) | YES (new) | no | n/a | n/a | no |
| ChurchProfile (mission, vision, welcome, history) | site.json / hardcoded | ChurchProfile | Rarely | YES (new, managed=True) | YES (new) | no | n/a | n/a | no |
| Service Times | site.json | ContentBlock (PAGE_SECTION) or ServiceTime model | Quarterly | YES | YES (new or existing) | optional | no | YES | no |
| Beliefs | site.json | ContentBlock (BELIEF) | Rarely | YES | YES (ContentBlock) | no | no | YES | no |
| Values | site.json | ContentBlock (VALUE) | Rarely | YES | YES (ContentBlock) | no | no | YES | no |
| Visit FAQs | site.json | ContentBlock (FAQ) | Quarterly | YES | YES (ContentBlock) | no | no | YES | no |
| Theme (annual) | site.json (theme2026) | ContentBlock (THEME) | Yearly | YES | YES (ContentBlock) | YES | no | no | YES (yearly) |
| What To Expect | site.json | ContentBlock (EXPECTATION) | Rarely | YES | YES (ContentBlock) | icon only | NO | YES | no |
| Mission / Vision / Welcome | site.json / hardcoded | ChurchProfile | Rarely | YES | YES | no | no | no | no |
| Announcement Banners | NONE | Announcement | Weekly | YES (NEW) | YES (NEW, managed=True) | YES | YES (severity) | YES | YES |
| Prayer Requests (public) | PrayerSubmission | PrayerRequest | Daily | Partial (review) | YES (NEW, managed=True) | no | moderate | no | YES |
| Contact Submissions | ContactSubmission | ContactSubmission | Daily | VIEW only | exists | no | n/a | no | n/a |
| Visit RSVPs | VisitRsvp | VisitRsvp | Daily | VIEW only | exists | no | n/a | no | n/a |
| Navigation | site.ts (navLinks) | code | Rarely | NO (code) | NO | no | n/a | n/a | n/a |
| Footer | site.ts (footerColumns) | code | Rarely | NO (code) | NO | no | n/a | n/a | n/a |
| SEO Metadata | seo.ts + per-page titles | code | Rarely | Partial | Settings (meta) | no | no | n/a | no |
| Brand/Theme tokens (colors, logo) | global.css / assets | static assets | Rarely | NO (code/asset) | NO | YES (logo) | n/a | n/a | n/a |
| Prayer Page copy / Contact copy | hardcoded in .astro | ContentBlock (PAGE_SECTION) | Rarely | Optional | YES | no | no | no | no |
| Homepage Pastor Section | hardcoded in PastorSection.astro | HomepagePastorSection (ContentBlock/ChurchProfile) | Rarely | YES | YES (NEW, managed=True) | YES | no | no | no |

### 3.2 Page-by-page content map

| Page | Dynamic content | Static content |
|------|-----------------|----------------|
| Homepage (`index.astro`) | Hero (config), Service Times, Events carousel, What To Expect, Latest Sermon, Testimonials, CTA banner, Pastor section | Pastor bio text (moved to ChurchProfile/HomepagePastorSection), layout |
| About (`about.astro`) | Values, Leadership grid, Annual Theme | Welcome/mission/vision text (moved to ChurchProfile), "1 Peter 2:9" label |
| Visit (`visit.astro`) | Service Times, RSVP form | Visit FAQ (ContentBlock), map link |
| Events (`events.astro`, `[id].astro`) | Event list/detail from API | Page hero |
| Sermons (`sermons.astro`, `[slug].astro`) | Sermon list/detail, series association | Page hero |
| Series (`series.astro`, `[slug].astro`) | Series list/detail | Page hero |
| Academy (`academy.astro`) | Academy modules | Page hero |
| Prayer (`prayer.astro`) | Prayer submission (write) | Page copy (ContentBlock) |
| Contact (`contact.astro`) | Contact submission (write) | Page copy (ContentBlock), address (GlobalSettings) |
| Give (`give.astro`) | M-Pesa till (config) | Giving explanation copy (ContentBlock) |
| Login / Change Password | Auth (accounts) | Forms |
| Privacy / Terms | Static legal copy | Full page text |

---

## 4. Schema Ownership Strategy

### 4.1 Principle

The existing Prisma schema is the historical source of truth for legacy public content tables. Introducing unnecessary Django ownership of these tables introduces migration risk and permanently couples future schema evolution to Django's migration system. The B1 architecture therefore adopts a **hybrid schema ownership model**.

### 4.2 Prisma-Owned (managed = False)

The following models remain `managed = False`. Django reads and writes these tables but does not manage their schema migrations:
- `PublicSermon`
- `SermonSeries`
- `WebsiteLeader`
- `WebsiteTestimonial`
- `WebsiteAcademyModule`
- `ChurchEvent`
- `EventRegistration`

### 4.3 Django-Owned (managed = True)

The following models are `managed = True` and fully owned by Django:
- `GlobalSettings`
- `HomepageSettings`
- `ChurchProfile`
- `ContentBlock`
- `Announcement`
- `MediaAsset`
- `PrayerRequest`
- Audit extensions
- Future CMS-specific entities

### 4.4 Implications
- Prisma retains historical schema ownership for legacy tables; any future schema changes to those tables must be coordinated through Prisma migrations.
- Django owns migration evolution for new CMS tables.
- Future migration to full Django ownership is possible but intentionally deferred until data stability is proven.

---

## 5. Management Requirements

For each content type: **why manage, who manages, how often, business value.**

### 5.1 Sermons
- **Why:** Core discipleship product; added after every service.
- **Who:** Media Team (uploads video/audio/notes + thumbnail) + Content Editor (metadata) or Pastor (approves).
- **How often:** Weekly.
- **Business value:** Keeps the archive current; drives return visits & YouTube growth.
- **Requires:** dedicated model (yes, legacy managed=False), images (thumbnail + optional audio/video URL), publish/unpublish (yes), ordering (by date desc), archival (yes — keep historical).
- **Lifecycle:** Draft → In Review → Approved → Published → Archived. Featured flag. Series association. Transcript/notes URL.

### 5.2 Series
- **Why:** Groups sermons into study tracks.
- **Who:** Content Editor / Pastor.
- **How often:** Monthly.
- **Business value:** Improves discoverability & sermon consumption.
- **Requires:** model (yes, legacy managed=False), artwork image (yes), publish (yes), ordering (yes), archival (no).
- **Lifecycle:** Draft → Published.

### 5.3 Events
- **Why:** Drives attendance & outreach.
- **Who:** Content Editor (creates), Media Team (poster), Pastor (approves).
- **How often:** Weekly.
- **Business value:** Physical attendance, evangelism, giving.
- **Requires:** model (yes, legacy managed=False), poster image (yes), **status workflow** (Draft/Published/Completed/Archived/Cancelled), RSVP enabled flag, featured flag, ordering (by date).
- **Note:** Frontend currently hardcodes `category: "special"`. Add `category` to model and serializer so the value is real.
- **Lifecycle:** Draft → In Review → Approved → Published → Completed/Archived/Cancelled.

### 5.4 Testimonials
- **Current issue:** Stale quotes accumulate; no rotation control; one testimonial has empty photo.
- **Recommendation (lifecycle):** `publish_date`, `expiration_date`, `featured` flag, `display_order`, `is_archived`, rotation support.
- **Who:** Content Editor.
- **How often:** Monthly.
- **Business value:** Social proof on homepage; freshness improves conversion.
- **Requires:** model (yes, legacy managed=False), photo (yes, optional), publish (yes), ordering (yes), archival (yes).
- **Lifecycle:** Draft → In Review → Approved → Published → Archived (auto-expire).

### 5.5 Leadership
- **Why:** Public trust; changes on appointment/exit.
- **Who:** Church Administrator / Super Admin.
- **How often:** Quarterly / on change.
- **Business value:** Transparency, credibility.
- **Requires:** model (yes, legacy managed=False), photo (yes), publish (yes — hide resigned leaders), ordering (yes — president first), archival (soft hide).
- **Lifecycle:** Published / Archived (hidden). No approval needed; admin controls directly.

### 5.6 Academy Modules
- **Why:** Marketing for the academy; mirrors LMS content at a summary level.
- **Who:** Content Editor (copies from LMS) — **not** the source of truth (LMS `DiscipleshipModule` is).
- **How often:** Quarterly.
- **Business value:** Funnel to paid academy.
- **Requires:** model (yes, legacy managed=False), optional image, publish (yes), ordering (yes), archival (no).
- **Lifecycle:** Draft → Published.

### 5.7 GlobalSettings (church name, phone, email, social, address, giving, academy)
- **Why:** Operational correctness; changes rarely but must be correct.
- **Who:** Church Administrator / Super Admin only.
- **How often:** Rarely (quarterly or on change).
- **Business value:** Avoids wrong contact info / lost giving.
- **Decision:** New `GlobalSettings` model (managed=True, singleton). Inherits church_name, short_name, tagline, address, email, phone, whatsapp, social_links, mpesa_till, mpesa_account_name, academy_url from the old `SiteSettings` design. Do NOT expose to Content Editor.
- **Requires:** model (yes, singleton), no images, no publish, no ordering, no archival. Edit-only.

### 5.8 HomepageSettings (hero text, scripture, tagline, CTA)
- **Why:** Homepage messaging; changes seasonally.
- **Who:** Content Editor (draft) → Pastor (approves) → Administrator (publishes).
- **How often:** Quarterly / seasonally.
- **Business value:** Fresh homepage experience; timely call-to-action.
- **Requires:** model (yes, singleton), no images, publish workflow (yes), no ordering, no archival.

### 5.9 ChurchProfile (mission, vision, welcome, history)
- **Why:** First-impression and theological identity content; changes rarely but should be editable by non-devs.
- **Who:** Pastor (approves) / Content Editor (edits).
- **How often:** Rarely / yearly.
- **Business value:** Theological accuracy, brand consistency, onlines visitors understand church identity.
- **Requires:** model (yes, singleton), no images, publish workflow (yes), no ordering, no archival.

### 5.10 Service Times
- **Why:** Changes with schedule adjustments; currently buried in JSON blob.
- **Who:** Church Administrator.
- **How often:** Quarterly.
- **Business value:** Visitors need accurate times.
- **Recommendation:** Promote to first-class `ServiceTime` model (or `ContentBlock` with category PAGE_SECTION if order complexity is low). FK to optional Campus for future multi-campus.
- **Requires:** model (yes), image (optional poster), ordering (yes), no publish, no archival.

### 5.11 Mission / Vision / Welcome / Beliefs / Values / What To Expect / Visit FAQs / Theme
- **Why:** Doctrine & first-impression content; changes rarely but should be editable by non-devs.
- **Who:** Pastor (approves) / Content Editor (edits).
- **How often:** Rarely / yearly (theme).
- **Business value:** Theological accuracy, brand consistency.
- **Recommendation:** Use `ContentBlock` with categories: BELIEF, VALUE, FAQ, EXPECTATION, PAGE_SECTION, THEME. Keep `WelcomeMessage` as part of `ChurchProfile`. Future dedicated models may be introduced if requirements become more complex (e.g., multi-language, rich media, versioning).
- **Requires:** model (ContentBlock), ordering (yes for lists), no images (THEME may have image), no publish, archival only for theme (yearly rollover).

### 5.12 Announcement Banners (NEW — gap)
- **Why:** No current mechanism for homepage announcements (events, giving drives, closures).
- **Who:** Content Editor / Church Administrator.
- **How often:** Weekly.
- **Business value:** Timely communication; increases event attendance & giving.
- **Recommendation:** New `Announcement` model (already in Prisma schema, not yet in Django). Fields: title, body, severity (INFO/SUCCESS/WARNING/URGENT), priority, `display_from`, `display_until`, `target_audience`, image FK, link_url, is_active.
- **Requires:** model (yes, managed=True), image (yes), publish window (yes), ordering/priority (yes), archival (auto-expire).
- **Lifecycle:** Draft → In Review → Approved → Published → Archived (auto-expire).

### 5.13 Prayer Requests (public)
- **Why:** Congregation submits; some may be shown publicly.
- **Who:** Pastor / Content Editor (moderation); members submit.
- **How often:** Daily submissions.
- **Business value:** Pastoral care, community.
- **Requires:** existing submission model + new `PrayerRequest` public model with status (Active/Answered/Closed), is_public, is_anonymous, category. Moderate workflow (review before publish).

### 5.14 Contact Submissions / RSVPs
- **Why:** Inbound communication; not "content" but data.
- **Who:** Church Administrator (views/exports). Members submit.
- **Requires:** existing models; **view + export only**, no publish.

### 5.15 Navigation / Footer / Brand tokens / SEO
- **Decision:** **Remain code-configured.** Navigation and footer are structural; changing them is a product decision, not a content task. SEO per-page titles can be a `GlobalSettings`/`HomepageSettings`/`ChurchProfile`/`ContentBlock` extension but default to code. Logo & color tokens stay as static assets/CSS.
- **Why:** Avoids giving admins the ability to break site structure; reduces attack surface.

### 5.16 Homepage Pastor Section
- **Current issue:** Pastor homepage content is hardcoded in `PastorSection.astro`.
- **Decision:** Move to managed content. Use `ChurchProfile` biography fields or a dedicated `HomepagePastorSection` model/section:
  - title
  - subtitle
  - biography
  - image
  - CTA text
- **Why:** Pastor changes should not require deployments.
- **Requires:** model or profile fields, image, no publish workflow (low sensitivity), no archival.

---

## 6. Recommended Django Apps

| App | Responsibility | Rationale |
|-----|----------------|-----------|
| `accounts` | Users, roles, auth, audit log | Exists. Super Admin, Admin, Leadership, Cell Leader, Member roles. |
| `members` | Member/household domain | Exists. Not public-content; separate. |
| `content` | Sermons, Series, Leadership, Testimonials, Academy Modules, GlobalSettings, HomepageSettings, ChurchProfile, ContentBlock, ServiceTimes, Beliefs/Values/FAQ/WhatToExpect/Theme, HomepagePastorSection | Consolidates all *public editorial* content. Justified: these share publish/ordering/archive patterns and one admin section. |
| `events` | ChurchEvent + EventRegistration + Announcements | Events deserve their own app (rich workflow, registrations, RSVP). Announcements live here. |
| `media` | Centralized upload model (`MediaAsset`) + helpers | Single place for image management, CDN URLs, alt text. All image fields become FKs/URLs managed here. |
| `prayer` | PrayerSubmission + public PrayerRequest | Exists (submission). Add moderated public request. |
| `giving` | Giving Transactions/Campaigns | Exists. Not editorial content. |

**Decision for B1 implementation phases:** Keep `content`, `events`, `prayer`, `giving`, `accounts`, `members` as-is; **add `media`**. Do **not** over-split — `content` is the right home for the editorial types.

---

## 7. Recommended Models (target shape — NOT created in B1)

> These describe the intended managed models. Legacy models remain `managed=False`; new models are `managed=True`. Listed here for design completeness.

### 7.1 `content` app
- `GlobalSettings` (singleton, managed=True): church_name, short_name, tagline, description, address (JSON or fields), email, whatsapp, phone, social_links (JSON), mpesa_till, mpesa_account_name, academy_url.
- `HomepageSettings` (singleton, managed=True): hero_title, hero_subtitle, homepage_scripture_ref, homepage_scripture_text, homepage_tagline, cta_text, cta_link_url.
- `ChurchProfile` (singleton, managed=True): mission_text, vision_text, welcome_message, church_history, pastor_bio_title, pastor_bio_subtitle, pastor_bio_body, pastor_cta_text, pastor_cta_link_url, pastor_image → MediaAsset FK.
- `ContentBlock` (managed=True): key, category (BELIEF, VALUE, FAQ, EXPECTATION, PAGE_SECTION, THEME), title, body (HTML or text), is_rich_text, display_order, is_active, metadata (JSON). Used for Prayer/Contact page copy, beliefs, values, FAQs, what to expect, theme text, service times (if not dedicated model).
- `ServiceTime` (managed=True, optional): day, time, label, campus (nullable FK), display_order, poster → MediaAsset FK.
- `SermonSeries` → **legacy managed=False**: add `is_featured`, keep slug/title/description/image/order/published.
- `PublicSermon` → **legacy managed=False**: add `status` (DRAFT/PUBLISHED/ARCHIVED), `is_featured`, `transcript_url`, `series` FK (proper FK, not duplicated slug/title), `thumbnail` → MediaAsset FK, `published_at`.
- `WebsiteLeader` → **legacy managed=False**: add `is_archived`, photo → MediaAsset FK.
- `WebsiteTestimonial` → **legacy managed=False**: add `publish_date`, `expiration_date`, `is_featured`, `display_order`, `is_archived`, photo → MediaAsset FK.
- `WebsiteAcademyModule` → **legacy managed=False**: instructor as text or FK to leader/member, image optional.

### 7.2 `events` app
- `ChurchEvent` → **legacy managed=False**: add `category` (real value), `is_featured`, `is_archived`, `rsvp_enabled`, `published_at`, `image` → MediaAsset FK. Keep status workflow.
- `EventRegistration` (exists, legacy managed=False).
- `Announcement` (NEW, managed=True): title, body, severity (INFO/SUCCESS/WARNING/URGENT), priority, display_from, display_until, target_audience, image → MediaAsset FK, link_url, is_active, created_by, updated_by.

### 7.3 `media` app (NEW, managed=True)
- `MediaAsset`: uuid, title, file (ImageField/file), url (generated), alt_text, uploaded_by, created_at, updated_at, width, height, mime_type, file_size, checksum, focal_point_x, focal_point_y, is_public, usage_count. All image fields across apps reference `MediaAsset` (or store the served URL). Provides central upload, reuse, CDN, alt-text for accessibility/SEO.

### 7.4 `prayer` app
- `PrayerSubmission` (exists, legacy managed=False).
- `PrayerRequest` (NEW, managed=True): title, content, category, is_anonymous, is_public, status (ACTIVE/ANSWERED/CLOSED), prayer_count, answered_note, submitted_at, approved_at, approved_by.

---

## 8. Media Management Strategy

### 8.1 Current state
All images are static files in `apps/web/public/images/*` and `RP/website/public/*`, referenced by hardcoded path strings. No upload, no optimization, no CDN, no alt text.

### 8.2 Classification: static vs uploaded

| Asset | Decision | Reason |
|-------|----------|--------|
| Logo (`rp-logo.svg`, mark) | **Static asset** | Brand constant; never edited by admins |
| Favicons / icons | **Static asset** | Build-time |
| Global CSS tokens / backgrounds | **Static asset** | Theme/code |
| Sermon thumbnails | **Uploaded media** | Added per sermon by media team |
| Series artwork | **Uploaded media** | Per series |
| Event posters | **Uploaded media** | Per event |
| Leadership photos | **Uploaded media** | Per leader; reuses member photo |
| Testimonial photos | **Uploaded media (optional)** | Per testimonial |
| Hero / theme images | **Uploaded media** | Annual theme + homepage hero |
| Academy images | **Uploaded media (optional)** | Per module |
| Service-time posters | **Uploaded media (optional)** | Per service |
| Announcement images | **Uploaded media** | Per announcement |
| Pastor homepage image | **Uploaded media** | Managed via ChurchProfile |

### 8.3 Recommendation
- Introduce `media` app with `MediaAsset` (managed=True). All `*_url` string fields become either `ForeignKey(MediaAsset)` or store the CDN URL produced by `MediaAsset`.
- Store on a configurable storage backend (local `MEDIA_ROOT` for dev; S3/Cloudflare R2 for prod). Serve via `MEDIA_URL` or CDN.
- Generate responsive variants (thumbnail/large) at upload for performance.
- Require `alt_text` for accessibility & SEO.
- Reuse: a leader photo can be the same `MediaAsset` referenced by `Member.profileImageUrl`.

### 8.4 MediaAsset Additional Fields
- `file_size` — storage governance, quota enforcement
- `checksum` — duplicate detection
- `focal_point_x`, `focal_point_y` — responsive cropping / smart crop
- `is_public` — media governance (unpublished/draft assets)
- `usage_count` — track references; drive cleanup jobs for unreferenced media

These fields enable:
- **Duplicate detection**: checksum prevents re-uploading identical files.
- **Responsive cropping**: focal point ensures subject remains in frame across breakpoints.
- **Cleanup jobs**: usage_count identifies orphaned assets.
- **Media governance**: is_public enforces draft/preview state.
- **Future CDN optimization**: file_size and mime_type inform cache/transform rules.

---

## 9. Content Workflow

### 9.1 Formal Publishing Workflow

```
Draft
 ↓
In Review
 ↓
Approved
 ↓
Published
 ↓
Archived
```

### 9.2 Persona Transitions

| Persona | Allowed Transitions |
|---------|---------------------|
| **Content Editor** | Draft → In Review. Can create and edit drafts. |
| **Pastor** | In Review → Approved. Can reject back to Draft. |
| **Administrator** | Approved → Published. Can unpublish → Approved. |
| **Super Admin** | All transitions including force-publish, force-archive, and rollback. |

### 9.3 Workflow Enforcement
- Mutating endpoints require `IsAuthenticated` + role-based permission.
- Each transition is logged to `AuditLog` with `old_value`, `new_value`, `ip_address`, `user_agent`.
- Public API exposes only content in `Published` or `Approved` (for scheduled publishing) states.
- `Archived` content is excluded from public API but retained in database.

### 9.4 Content Types Subject to Workflow
- Sermons
- Events
- Testimonials
- Announcements
- Beliefs (ContentBlock category BELIEF)
- Values (ContentBlock category VALUE)

Leadership and Academy Modules follow a simpler Draft → Published workflow (no Pastor approval required).

---

## 10. Permissions Strategy

### 10.1 Personas

| Persona | Allowed actions | Forbidden actions |
|---------|-----------------|-------------------|
| **Church Administrator** | Edit GlobalSettings (contact, address, giving, social), ServiceTimes, Announcements, view/export Contact & RSVP, manage users (invite/deactivate), assign roles | Delete sermons/events arbitrarily, edit theological Beliefs/Values without Pastor approval |
| **Media Team** | Upload media assets; create/edit Sermons (video/audio/thumbnail), Events (poster), Series artwork; mark ready-for-review | Publish without Pastor approval; edit GlobalSettings; delete leaders |
| **Pastor** | Approve/publish Sermons, Events, Testimonials, Announcements, Beliefs, Values, Mission/Vision, Theme; moderate public Prayer Requests; full read | Manage giving financial config (delegated to Admin); technical user management |
| **Content Editor** | Create/edit Testimonials, Leadership (draft), Academy Modules, FAQs, WhatToExpect, Beliefs/Values drafts, Announcements (draft), Prayer page copy | Publish without approval; edit GlobalSettings financials; delete submissions |
| **Super Admin** | Everything: full CRUD, model management, role assignment, audit log access, system config | — (no forbidden; but actions audit-logged) |

### 10.2 Enforcement
- Django `UserRole` (ADMIN, HOSPITALITY, LEADERSHIP, CELL_LEADER, MEMBER) exists. **Add** `SUPER_ADMIN` and `CONTENT_EDITOR` (or reuse ADMIN + a permission group).
- Use DRF permissions + Django admin `ModelAdmin` `has_*_permission` overrides keyed on role/group.
- All mutating actions write to `AuditLog` (already modeled) — satisfies "who changed what."
- Public read endpoints stay `AllowAny`; all write endpoints require `IsAuthenticated` + role check.

---

## 11. API Strategy

### 11.1 Current consumption
Astro calls `GET /api/sermons`, `/series`, `/leaders`, `/testimonials`, `/academy`, `/events`, `/site-config`, and POSTs to `/contact`, `/prayer`, `/rsvp`. All reads are `AllowAny`.

### 11.2 Public (read) endpoints — `AllowAny`, cached
- `GET /api/sermons` (filter: series, speaker, tag, featured; sort: date; paginate)
- `GET /api/sermons/:slug`
- `GET /api/series`, `/api/series/:slug`
- `GET /api/events` (filter: status=published+upcoming, category, featured; sort date)
- `GET /api/events/:id`
- `GET /api/leaders`, `/testimonials`, `/academy`
- `GET /api/announcements/active` (date-window + audience + severity)
- `GET /api/site-config` → returns structured GlobalSettings + HomepageSettings + ChurchProfile + ContentBlocks + ServiceTimes + Theme
- `GET /api/media/:id` (public assets with is_public=True)
- **Caching:** Use `Cache-Control: public, max-age=300` (5 min) + Django cache (Redis) keyed by queryset. Cache invalidation on save/delete.

### 11.3 Cache Invalidation Strategy

When content changes, the following caches are invalidated:

| Content Change | Invalidated Cache |
|----------------|-------------------|
| Sermon created/updated/deleted | sermon list cache, sermon detail cache, series sermon counts |
| Event created/updated/deleted | event list cache, event detail cache |
| Announcement created/updated/deleted | active announcement cache |
| Homepage content changed (GlobalSettings, HomepageSettings, ChurchProfile, ContentBlocks with homepage categories) | homepage cache, `/api/site-config` cache |
| MediaAsset updated/deleted | any cached references to the media URL |

Implementation mechanism:
- `post_save` and `post_delete` Django signals (or model `save()` overrides) trigger cache key deletion.
- Cache keys follow a namespaced convention: `cache:{content_type}:{identifier}`.
- No cache warming required; first request after invalidation repopulates cache.

### 11.4 Admin (write) endpoints — `IsAuthenticated` + role
- `POST/PUT/PATCH/DELETE /api/admin/sermons`, `/series`, `/events`, `/testimonials`, `/leaders`, `/academy`, `/announcements`, `/global-settings`, `/homepage-settings`, `/church-profile`, `/content-blocks`, `/service-times`, `/media`, `/prayer-requests`, `/audit-log`.
- Use `ModelViewSet` (not read-only) for admin; keep public `ReadOnlyModelViewSet` separate to avoid leaking write routes.
- DRF `filter_backends` (DjangoFilterBackend) for filtering; `OrderingFilter` for sort; `PageNumberPagination` (default 12, max 50).
- Search: `SearchFilter` on title/name/description/speaker.

### 11.5 Pagination / Filtering / Search
- Pagination: page-based, `?page=&page_size=`.
- Filtering: by `is_published`, `series`, `category`, `featured`, `tag`, date range.
- Search: `?search=` across title/name/speaker.
- Avoid over-fetching: public sermon list excludes `notes_url`/`audio_url` heavy fields unless detail.

---

## 12. Search Architecture

### 12.1 Phase B2/B3 — PostgreSQL Full Text Search

Use PostgreSQL Full Text Search via Django `SearchVector`, `SearchRank`, and GIN indexes. No dedicated search engine at this stage.

### 12.2 Components
- `SearchVector`: computed field indexing title, description, speaker, scripture_ref.
- `SearchRank`: orders results by relevance.
- `GIN index`: on the `SearchVector` field for fast lookup.

### 12.3 Applies to
- `PublicSermon` — title, description, speaker, scripture_ref, transcript
- `SermonSeries` — title, description
- `ChurchEvent` — title, description, location

### 12.4 Explicit Exclusion
Do NOT introduce Elasticsearch/OpenSearch/Meilisearch at this stage.

Reason: Unnecessary operational complexity for a read-heavy, moderate-content site. PostgreSQL FTS is sufficient for the expected content volume and avoids maintaining a separate search service.

---

## 13. Publishing Strategy

### 13.1 Lifecycle states per content type

| Type | States | Notes |
|------|--------|-------|
| Sermon | DRAFT → IN_REVIEW → APPROVED → PUBLISHED → ARCHIVED | Featured flag; `published_at` |
| Series | DRAFT → PUBLISHED | Hidden if not published |
| Event | DRAFT → IN_REVIEW → APPROVED → PUBLISHED → COMPLETED → ARCHIVED; CANCELLED | `rsvp_enabled`, `featured`; auto-demote to COMPLETED by date job |
| Testimonial | DRAFT → IN_REVIEW → APPROVED → PUBLISHED → ARCHIVED (expiry) | `publish_date`, `expiration_date`, `featured`, `display_order` |
| Leader | PUBLISHED / ARCHIVED (hidden) | `sort_order` |
| Academy | DRAFT → PUBLISHED | |
| Announcement | DRAFT → IN_REVIEW → APPROVED → PUBLISHED → ARCHIVED (scheduled by display_from/until) | severity, audience |
| PrayerRequest | ACTIVE → ANSWERED → CLOSED | moderation gate before `is_public` |
| ContentBlock (Beliefs/Values/FAQ/Theme/Expectation) | DRAFT → IN_REVIEW → APPROVED → PUBLISHED → ARCHIVED | category-based |
| GlobalSettings / HomepageSettings / ChurchProfile | always live (edit) | versioned via AuditLog only |
| ServiceTime | always live (edit) | versioned via AuditLog only |
| HomepagePastorSection | always live (edit) | versioned via AuditLog only |

### 13.2 Workflow
- **Simple publish** (Testimonials, Academy, Leadership): Content Editor saves; Pastor or Admin publishes.
- **Approval** (Sermons, Events, Beliefs/Values/Theme): Media/Editor creates DRAFT; Pastor flips to PUBLISHED.
- **Scheduled** (Announcements, Events): `display_from`/`display_until` or `start_date_time` drives visibility without manual toggle.
- **Lifecycle enforcement:** Status field governs public API visibility. `is_active` and status are kept in sync.
- **Archival:** Testimonials auto-archive on `expiration_date`; Sermons/Events manually or by date job. Archived content excluded from public API but retained (history) — satisfies "versioning/history" via retention + AuditLog.
- **Versioning:** Full content versioning (django-reversion) is **optional**; AuditLog captures change metadata. Recommend reversion only for GlobalSettings/ChurchProfile/Beliefs (low volume, high sensitivity).

---

## 14. Homepage Configuration Architecture

### 14.1 HomepageSection

| Field | Type | Purpose |
|-------|------|---------|
| section_name | CharField | Identifier (e.g., `hero`, `sermon`, `events`) |
| enabled | Boolean | Visibility toggle |
| display_order | Integer | Section ordering on homepage |

### 14.2 Purpose
- Future control of homepage section visibility and ordering.
- Feature toggles for sections without introducing a page-builder system.
- Admin can enable/disable sections per season or campaign.

### 14.3 Documentation
Document as future-ready architecture. Sections may be toggled dynamically in B3+ without requiring frontend deploys.

---

## 15. Announcement Model Enhancement

### 15.1 Severity Levels

| Severity | Intended Frontend Usage |
|----------|------------------------|
| INFO | Neutral informational banners |
| SUCCESS | Positive updates (e.g., event recap, giving milestone) |
| WARNING | Urgent notices (e.g., schedule change, closure) |
| URGENT | Critical alerts (e.g., emergency, cancellation) |

### 15.2 Fields
- `severity` — drives color, icon, and dismissibility on frontend.
- `priority` — ordering when multiple announcements are active.
- `display_from` / `display_until` — scheduling.
- `target_audience` — filters (all, members, visitors).
- `is_active` — manual override.

### 15.3 Frontend Integration
- Frontend fetches `/api/announcements/active`.
- Severity maps to theme colors/icons.
- URGENT banners are non-dismissible.

---

## 16. Scalability Considerations

### 16.1 Single church today
- Current schema is single-tenant. GlobalSettings singleton is fine for one church.

### 16.2 Multiple campuses tomorrow
- Add `Campus` model (name, slug, address, timezone).
- `ServiceTime`, `ChurchEvent`, `Announcement` gain `campus` FK (nullable = all campuses).
- `GlobalSettings` becomes per-campus or a "global + campus override" pattern.
- Media, sermons, series are campus-agnostic (shared).

### 16.3 Denomination network later
- Introduce `Tenant`/`Organization` discriminator. Most content models add `organization_id`.
- Use schema-per-tenant (PostgreSQL schemas) or `organization` FK with row-level filtering.
- Public API gains `?org=` or subdomain routing.
- **Tradeoff:** Tenant isolation adds complexity (migrations per schema, middleware). Defer until needed; design models with `organization` FK *ready* but nullable now to avoid breaking changes.

### 16.4 General
- Read-heavy site → cache public API aggressively; consider static generation (Astro build) for sermons/series/leaders.
- Media on object storage + CDN.
- Audit log grows unbounded → partition/archive yearly.

---

## 17. Implementation Roadmap (post-B1)

1. **B2 — Model hardening:** Introduce managed=True models (GlobalSettings, HomepageSettings, ChurchProfile, ContentBlock, Announcement, MediaAsset, PrayerRequest). Add lifecycle fields to legacy managed=False models. Run initial migrations for new tables.
2. **B3 — Admin & Permissions:** Register ModelAdmins; role-based `has_*` permissions; write endpoints; AuditLog wiring; workflow enforcement.
3. **B4 — Media pipeline:** Storage backend, upload endpoint, image optimization, alt text, Responsive variants.
4. **B5 — API expansion:** Admin write viewsets, filtering/pagination/search, caching, announcements endpoint, cache invalidation hooks.
5. **B5.5 — Search:** PostgreSQL Full Text Search indexes for sermons, series, events.
6. **B6 — Frontend contract:** Update `api.ts` mappers for new fields (category, featured, expiry, media URLs); replace `site.ts` hardcoding with live GlobalSettings/HomepageSettings/ChurchProfile; add Announcement banner component.
7. **B7 — Migration:** Seed from existing JSON/Prisma data; backfill `MediaAsset` from static images; cut over.
8. **B8 — Governance & Cleanup:** Cleanup jobs (unreferenced media), log archival, monitor cache hit rates.

---

## 18. Justification Summary

### 18.1 Kept code-configured

| Kept code-configured | Reason |
|----------------------|--------|
| Navigation, footer links | Structural; breaks layout if mis-edited |
| Logo, favicons, CSS tokens | Brand constants |
| Per-page SEO titles (default) | Developer concern; low change |
| Pastor homepage bio text | Managed via ChurchProfile / HomepagePastorSection; actual text content is no longer hardcoded. |
| Settings structural overrides | Rarely changes; properly a developer/product decision |

### 18.2 Moved to admin (justified)

| Moved to admin | Reason |
|----------------|--------|
| Sermons, Series, Events, Testimonials, Leadership, Academy | Regular cadence; non-dev owners; business value |
| GlobalSettings (contact/address/giving/social) | Must be correct; admin-owned |
| HomepageSettings (hero/scripture/CTA) | Seasonal changes without deploys |
| ChurchProfile (mission/vision/welcome/history) | Rare but should not require developer deploy |
| ServiceTimes, Beliefs, Values, FAQs, WhatToExpect | Rare but should not require developer deploy |
| Announcements | No current mechanism; high communication value |
| PrayerRequests (moderated) | Congregation-generated; needs review |
| HomepagePastorSection | Pastor changes should not require deployments |
| ContentBlock (general-purpose text) | Granular editing of page copy |

---

## 19. Audit Log Requirements

### 19.1 Fields

| Field | Purpose |
|-------|---------|
| `old_value` | JSON of prior state for rollback analysis |
| `new_value` | JSON of new state |
| `ip_address` | Traceability / security investigation |
| `user_agent` | Forensics |
| `action` | CREATE / UPDATE / DELETE / APPROVE / PUBLISH / ARCHIVE |
| `model_name` | Audited model |
| `object_id` | Audited instance |
| `performed_by` | FK to User |
| `performed_at` | Timestamp |

### 19.2 Scope
- All mutating admin endpoints must create an AuditLog entry.
- Transitions in the content workflow (state changes) must be explicitly logged.
- Sensitive singleton changes (GlobalSettings, ChurchProfile) must always log old/new values.

### 19.3 Future Considerations
- Partition AuditLog by year for performance.
- Provide admin export for compliance.

---

## 20. Data Migration Strategy

See companion document: `RP/docs/DATA_MIGRATION_STRATEGY.md`.

Key goals:
- Safely migrate from static JSON to managed content without data loss.
- Backfill `MediaAsset` from static images.
- Maintain Prisma as source of truth for legacy tables during transition.

---

## 21. Readiness Assessment for B2

This architecture review is complete. The following are approved for B2 implementation:

- Schema ownership strategy: legacy `managed=False`, new `managed=True`.
- Split site config into GlobalSettings, HomepageSettings, ChurchProfile.
- ContentBlock as primary low-frequency content architecture.
- Formal workflow: Draft → In Review → Approved → Published → Archived.
- Expanded MediaAsset with governance fields.
- Cache invalidation architecture (post_save/post_delete).
- Search architecture: PostgreSQL Full Text Search only.
- Homepage Pastor Section moved to managed content.
- HomepageSection toggles documented (future-ready).
- Announcement severity levels defined.
- Audit log fields specified.
- Data migration strategy documented in separate draft.

No further architectural discovery is required before B2. Implementation should follow the roadmap in §17.