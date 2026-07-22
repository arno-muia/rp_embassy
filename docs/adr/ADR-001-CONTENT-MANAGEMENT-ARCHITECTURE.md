# ADR-001: Content Management Architecture

| Field | Value |
|-------|-------|
| **Title** | Content Management Architecture for the RP Public Website |
| **Status** | Approved — With Required Revisions (B1 Architecture Review) |
| **Date** | 2026-07-17 |
| **Revised** | 2026-07-20 |
| **Deciders** | Backend Architecture Review |
| **Related** | `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md`, `RP/docs/DATA_MIGRATION_STRATEGY.md` |

---

## Context

The RP platform's public website is currently driven by a **static JSON content layer** (`apps/web/content/*.json`) that was hand-edited by developers and redeployed. The new Django backend re-mirrors that same content as `managed = False`, read-only models (`content.*`, `events.*`) exposing `ReadOnlyModelViewSet` endpoints to an Astro frontend.

We must decide **how content should be managed going forward** before writing any models. Specific pressures:

1. **No admin editing** — every copy change requires a developer and a redeploy.
2. **One giant JSON blob** (`SystemConfig` key `site`) holds beliefs, values, FAQs, service times, welcome message, and theme. A single typo breaks the whole site config; nothing is editable granularly.
3. **No media management** — images are hardcoded `/public/images/*` paths; no upload, optimization, CDN, or alt text.
4. **No publishing lifecycle** — testimonials go stale with no expiry/archive; events have a status enum the frontend ignores (it derives its own past/upcoming/ongoing); there is no announcement/banner mechanism at all.
5. **Read-only backend** — no write path, no admin, no role enforcement beyond `AllowAny` reads.
6. **Future growth** — must scale from 1 church → multiple campuses → potentially a denomination network, without a rewrite.

The decision must specify which content becomes admin-editable, which stays code-configured, what models/apps/media/permissions/API/publishing design to adopt, and why — without over-administering structural constants.

---

## Decision

Adopt a **Django-admin-backed, role-gated content management layer** with these concrete decisions:

### Schema Ownership Strategy

Existing Prisma-backed legacy content models retain `managed = False`. Django owns newly introduced CMS infrastructure with `managed = True`.

**Prisma remains the historical schema owner** for legacy public content tables (PublicSermon, SermonSeries, WebsiteLeader, WebsiteTestimonial, WebsiteAcademyModule, ChurchEvent, EventRegistration). This reduces migration risk and avoids permanently coupling future schema evolution to Django for tables that were originally defined in Prisma.

**Django owns** newly introduced CMS infrastructure: Announcement, MediaAsset, GlobalSettings, HomepageSettings, ChurchProfile, ContentBlock, Audit extensions, and future CMS-specific entities.

This hybrid approach reduces migration risk by deferring full schema ownership conversion. Future migration to full Django ownership remains possible but is intentionally deferred until data stability is proven.

1. **Legacy content/event models remain `managed = False`** (Prisma-owned schema): PublicSermon, SermonSeries, WebsiteLeader, WebsiteTestimonial, WebsiteAcademyModule, ChurchEvent, EventRegistration. They gain Django lifecycle fields and admin interfaces but the database schema remains managed by Prisma migrations.

2. **Split site configuration** — Replace the proposed singleton `SiteSettings` with three focused models:
   - `GlobalSettings`: church_name, contact information, address, social links, giving information, academy links
   - `HomepageSettings`: hero text, homepage scripture, homepage tagline, CTA text, homepage-specific configuration
   - `ChurchProfile`: mission, vision, welcome message, church history, church profile content. Includes pastor biography fields for the homepage pastor section, moving this content from hardcoded `.astro` files into managed content.

3. **Introduce a `ContentBlock` model** with categories (BELIEF, VALUE, FAQ, EXPECTATION, PAGE_SECTION, THEME) as the primary architecture for low-frequency content areas. Dedicated models (`Belief`, `Value`, `FaqItem`, `WhatToExpectItem`, `AnnualTheme`) may be introduced later if requirements become more complex.

4. **Introduce a `media` app** with a `MediaAsset` model; all image fields migrate from `CharField` URL strings to managed uploads (FK to `MediaAsset` or served CDN URL) with required `alt_text`. The `MediaAsset` model includes governance fields: `file_size`, `checksum`, `focal_point_x`, `focal_point_y`, `is_public`, `usage_count` — enabling duplicate detection, responsive cropping, cleanup jobs, media governance, and future CDN optimization.

5. **Add an `Announcement` model** (already present in Prisma but missing in Django) for time-windowed, audience-targeted homepage banners with severity levels (INFO, SUCCESS, WARNING, URGENT). Severity drives frontend color, icon, and dismissibility behavior.

6. **Keep navigation, footer, logo/favicons, CSS tokens, and default per-page SEO titles code-configured** — they are structural/product decisions, not editorial content.

7. **Enforce publishing workflow**: Draft → In Review → Approved → Published → Archived. Content Editors create/edit drafts. Pastors approve. Administrators publish. Super Admins perform all transitions. Apply to: Sermons, Events, Testimonials, Announcements, Beliefs, Values.

8. **Enforce 5 personas** (Church Administrator, Media Team, Pastor, Content Editor, Super Admin) via Django roles/groups + DRF `IsAuthenticated` on all write routes; public reads stay `AllowAny` + cached.

9. **Scale by designing multi-campus-forward**: `campus` FK on `ServiceTime`/`ChurchEvent`/`Announcement` (nullable = all); `organization` FK left nullable-ready for future tenancy.

10. **API**: separate public `ReadOnlyModelViewSet` (cached, filtered, paginated, searchable) from admin `ModelViewSet` (auth + role). Add `/api/announcements/active` and a structured `/api/site-config`.

11. **Homepage Configuration Architecture**: Introduce `HomepageSection` model with fields `section_name`, `enabled`, `display_order`. Purpose: future control of homepage section visibility, ordering, and feature toggles without introducing a page-builder system. Document as future-ready architecture.

12. **Audit Log**: Expand the existing AuditLog model with fields for `old_value`, `new_value`, `ip_address`, `user_agent`. Scope: all mutating admin endpoints, content workflow transitions, and singleton changes (GlobalSettings, ChurchProfile). Purpose: traceability, rollback analysis, security investigations.

---

### Cache Invalidation Strategy

When content changes, the following caches must be invalidated:

| Content Change | Cache Invalidated |
|----------------|-------------------|
| Sermon created/updated/deleted | sermon list, sermon detail, series sermon counts |
| Event created/updated/deleted | event list, event detail |
| Announcement created/updated/deleted | active announcement cache |
| Homepage / GlobalSettings / HomepageSettings / ChurchProfile changes | homepage cache, `/api/site-config` |
| MediaAsset updated/deleted | any cached references to the media URL |

Implementation mechanism:
- `post_save` and `post_delete` Django signals (or model `save()` overrides) trigger cache key deletion.
- Cache keys follow a namespaced convention: `cache:{content_type}:{identifier}`.
- No cache warming required; first request after invalidation repopulates cache.

---

### Search Architecture

**Phase B2/B3 — PostgreSQL Full Text Search**

Use PostgreSQL Full Text Search via Django `SearchVector`, `SearchRank`, and GIN indexes. No dedicated search engine at this stage.

Components:
- `SearchVector` — computed field indexing title, description, speaker, scripture_ref.
- `SearchRank` — orders results by relevance.
- GIN index — on the `SearchVector` field for fast lookup.

Applies to:
- `PublicSermon` — title, description, speaker, scripture_ref, transcript
- `SermonSeries` — title, description
- `ChurchEvent` — title, description, location

Explicit exclusion: Do NOT introduce Elasticsearch/OpenSearch/Meilisearch at this stage. Reason: unnecessary operational complexity for a read-heavy, moderate-content site. PostgreSQL FTS is sufficient for the expected content volume and avoids maintaining a separate search service.

---

## Alternatives Considered

### A. Keep the static JSON + redeploy workflow
- *Pros:* Zero backend work; familiar.
- *Cons:* Every edit needs a developer and a deploy; no governance, no media, no lifecycle; directly contradicts the business need for non-dev content owners. **Rejected.**

### B. Headless CMS (Strapi / Sanity / Contentful)
- *Pros:* Instant admin UI, media CDN, publishing workflows out of the box.
- *Cons:* External dependency & cost; duplicates the existing Django/Postgres stack; auth/roles must be bridged; the Prisma→Django domain (members, giving, prayer) already lives in Django, splitting CMS across two systems fractures the data model. **Rejected** for now; could be revisited if admin UX becomes a bottleneck.

### C. Keep `managed = False` and just add write serializers
- *Pros:* Minimal migration risk; schema owned by Prisma.
- *Cons:* Django cannot evolve the schema (new fields, new models like `Announcement`, `MediaAsset`); blocks the roadmap. **Accepted for legacy tables only** — legacy Prisma-backed tables remain `managed = False`, while new CMS models are `managed = True`.

### D. Put everything (including nav, footer, SEO, brand) into the admin
- *Pros:* Maximally flexible.
- *Cons:* Admins can break site structure; larger attack surface; unnecessary governance overhead. **Rejected** — only editorial/content earns admin access (see §4 / design doc §13).

### E. Full multi-tenant from day one
- *Pros:* Future-proof.
- *Cons:* Premature complexity (per-schema migrations, row-level isolation, routing) for a single church today. **Rejected** — design tenancy-ready (nullable `organization` FK) but defer activation.

---

## Consequences

### Positive
- Non-developers (Pastor, Content Editor, Media Team, Administrator) can own their content without deploys.
- Granular editing: a bad FAQ edit can't break service times.
- Real media management: upload, reuse, CDN, accessibility alt text.
- Lifecycle governance: testimonials auto-expire; events auto-complete; announcements schedule themselves with severity levels.
- Audit trail on every mutation satisfies accountability ("who changed what") with full field-level data for rollback analysis.
- Caching + pagination on a read-heavy site keeps the Astro frontend fast. Cache invalidation via signals ensures stale content is never served.
- Campus/tenant fields are ready, so growth is additive, not a rewrite.
- Reduced migration risk: legacy Prisma schema owners remain untouched; Django only owns new tables.
- Pastor homepage content is managed: pastor changes no longer require deployments.
- PostgreSQL Full Text Search provides adequate search without operational overhead of a separate search engine.
- HomepageSection enables future control of homepage layout without a page builder.

### Negative / Trade-offs
- Mixed schema ownership (Prisma + Django) adds operational complexity during transition.
- More models = more admin polish work (B2/B3).
- Media pipeline adds storage/CDN configuration.
- Role enforcement must be implemented and tested; misconfiguration could either block editors or leak writes.
- Some duplication risk between Django `GlobalSettings`/`HomepageSettings`/`ChurchProfile` and the frontend `site.ts` fallback — mitigated by making `site.ts` a pure fallback and sourcing live from `/api/site-config`.
- ContentBlock categorization adds model complexity; must be documented and admin-filtered.
- Cache invalidation via signals requires careful naming and testing to ensure all relevant keys are invalidated.

### Neutral
- `Announcement` and `MediaAsset` are net-new; `PrayerRequest` public model is net-new.
- Prisma schema remains the historical reference for legacy tables; Django becomes authoritative for new CMS tables post-cutover.

---

## Rationale

The single deciding factor is **business value per edit frequency vs. risk**. Content that changes weekly/monthly and is owned by non-engineers (sermons, events, testimonials, leaders, academy, service times, announcements, beliefs/values, site settings) earns admin management because the cost of developer-gated edits is recurring and high. Content that is structural or brand-constant (nav, footer, logo, CSS tokens, default SEO) stays in code because editing it is rare, risky, and properly a developer/product decision. Media must be managed because hardcoded paths don't scale and harm performance/accessibility. The lifecycle fields exist because stale content (testimonials, events) is a real, observed defect in the current site.

Schema ownership follows the same principle: legacy Prisma-backed tables were defined, migrated, and maintained in Prisma. Converting them to `managed = True` introduces migration risk and permanently couples their evolution to Django's migration system. Retaining `managed = False` preserves the existing Prisma schema owner while still allowing Django to manage the data and provide admin/API access.

Cache invalidation, search strategy, and HomepageSection architecture are documented to ensure the design is complete and no architectural surprises arise during implementation.

---

## Future Evolution

- **B2:** Model hardening (legacy `managed=False`, new `managed=True`, new fields/models). Implement PostgreSQL FTS indexes.
- **B3:** Admin registration + role permissions + AuditLog wiring + workflow enforcement.
- **B4:** Media pipeline (storage, optimization, alt text).
- **B5:** Admin write API + filtering/pagination/caching + announcements endpoint + cache invalidation hooks.
- **B6:** Frontend contract update (`api.ts` mappers, live `GlobalSettings`/`HomepageSettings`/`ChurchProfile`, announcement banner, HomepageSection toggles).
- **B7:** Data migration/seed from JSON + Prisma; cutover.
- **Later:** Activate `campus` FK; introduce `organization` tenancy; optional headless-CMS bridge if admin UX lags; django-reversion for SiteSettings/Beliefs versioning if needed.

This ADR is the authoritative architectural decision for B1; the companion design doc provides the implementation-level detail (models, fields, endpoints, personas) required to begin B2 without further discovery.