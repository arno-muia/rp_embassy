# Data Migration Strategy: Static JSON → Managed Content

**Phase:** B1 — Architecture Review
**Status:** Design / Strategy Only (no implementation yet)
**Date:** 2026-07-20
**Author:** Backend Architecture Review
**Related:** `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md`, `RP/docs/adr/ADR-001-CONTENT-MANAGEMENT-ARCHITECTURE.md`

---

## 1. Overview

This document defines the strategy for migrating the RP public website from its current static JSON content layer to the new managed Django CMS architecture. The migration must:

1. Preserve all existing content without data loss.
2. Maintain Prisma schema ownership for legacy tables (`managed = False`).
3. Populate new Django-owned tables (`managed = True`) with transformed/staged data.
4. Support rollback to the static JSON layer at any point during B2/B7.
5. Be executable in phases to minimize downtime.

### Source Files (static JSON)
- `site.json` — Global settings, beliefs, values, FAQs, service times, welcome message, theme
- `sermons.json` — Sermon entries
- `series.json` — Sermon series
- `events.json` — Church events
- `testimonials.json` — Testimonial entries
- `leadership.json` — Church leaders
- `academy-modules.json` — Academy modules

### Strategy Principles
- **Prisma is source of truth for legacy tables**: Do not overwrite Prisma-owned tables during migration. Read from Prisma/JSON; populate Django-owned tables only.
- **Idempotent migrations**: Scripts can be safely re-run without creating duplicates.
- **Validation-first**: Each migration step includes validation against expected counts and data integrity checks.
- **Feature-flagged cutover**: The frontend reads from managed endpoints only after explicit cutover; before that, static JSON remains fallback.

---

## 2. Migration Phases

| Phase | Activity | Target |
|-------|----------|--------|
| **M1** | Read-only validation | Audit existing JSON/Prisma data counts and integrity |
| **M2** | Backfill `MediaAsset` | Migrate static images to managed uploads |
| **M3** | Seed `GlobalSettings` / `HomepageSettings` / `ChurchProfile` | Extract singleton config from `site.json` |
| **M4** | Seed `ContentBlock` | Extract beliefs, values, FAQs, what-to-expect, theme, service times, page copy |
| **M5** | Seed legacy content into Prisma (if needed) | Ensure Prisma tables are fully populated; Django reads them |
| **M6** | Seed new CMS models | `Announcement` (initial empty), `PrayerRequest` (initial empty) |
| **M7** | Frontend feature-flag switch | Enable managed endpoints; disable static JSON fallback |
| **M8** | Archive static JSON | Move to `content/archive/` after validation |

---

## 3. Per-Source Migration Plans

### 3.1 `site.json`

#### Source
- Path: `apps/web/content/site.json`
- Structure: Single `SystemConfig` key `site` containing church-wide configuration.

#### Destination
| Destination Model | Path in `site.json` |
|-------------------|---------------------|
| `GlobalSettings` | `churchName`, `shortName`, `tagline`, `address`, `email`, `phone`, `whatsapp`, `socialLinks`, `mpesaTill`, `mpesaAccountName`, `academyUrl` |
| `HomepageSettings` | `homepageScriptureRef`, `homepageScriptureText`, `homepageTagline`, `ctaText`, `ctaLinkUrl` |
| `ChurchProfile` | `missionText`, `visionText`, `welcomeMessage`, `churchHistory`, `pastorBioTitle`, `pastorBioSubtitle`, `pastorBioBody`, `pastorCtaText`, `pastorCtaLinkUrl`, `pastorImage` |
| `ServiceTime` | `serviceTimes[]` |
| `ContentBlock` (BELIEF) | `beliefs[]` |
| `ContentBlock` (VALUE) | `values[]` |
| `ContentBlock` (FAQ) | `faqs[]` |
| `ContentBlock` (EXPECTATION) | `whatToExpect[]` |
| `ContentBlock` (THEME) | `theme2026.title`, `theme2026.scriptureRef`, `theme2026.scriptureText` |

#### Transformation Rules
- Flatten nested JSON fields into Django model fields.
- `socialLinks` JSON → `JSONField` on `GlobalSettings`.
- `serviceTimes[]` array → individual `ServiceTime` rows with `display_order`.
- `beliefs[]`, `values[]`, `faqs[]`, `whatToExpect[]` → `ContentBlock` rows with `category` set accordingly; preserve existing order.
- `theme2026` → `ContentBlock` with category `THEME`; any `theme2026.image` path becomes a `MediaAsset` reference (after M2).
- `pastorImage` path → `MediaAsset` reference after M2.
- If field is missing in source, leave destination field blank/null.

#### Validation Steps
- Count records in destination and compare to source arrays.
- Validate singleton rows (`GlobalSettings`, `HomepageSettings`, `ChurchProfile`) exist exactly once.
- Validate all `ContentBlock` rows have non-empty `title` and `category`.
- Verify `serviceTimes` order preserved.

#### Rollback Strategy
- Delete seeded rows by model (respecting `managed=True` so Django migrations handle schema).
- Do **not** modify `site.json` or Prisma tables during this migration.
- Subsequent frontend cutover is feature-flagged; rollback means flipping the flag.

---

### 3.2 `sermons.json`

#### Source
- Path: `apps/web/content/sermons.json`
- Structure: Array of sermon objects with slug, title, date, speaker, description, series, audio/video URLs, thumbnail.

#### Destination
| Destination Model | Notes |
|-------------------|-------|
| `PublicSermon` (leg Prisma, `managed=False`) | Django does not own schema, but reads/writes data. Ensure Prisma has all rows. |
| `MediaAsset` (Django, `managed=True`) | Thumbnail image, optional audio/video poster. |

#### Transformation Rules
- Ensure Prisma tables are fully populated (if not already) — possibly via Prisma seed or direct INSERT. Django migration step M5 ensures Prisma is populated.
- For each sermon, map thumbnail path → `MediaAsset` (upload/copy in M2).
- `series` field: If series name exists in `series.json`, populate `series` FK via slug or title. If not, leave FK null.
- Convert audio/video URL strings; no upload required (external URLs).

#### Validation Steps
- Count sermons in Prisma vs. JSON. Must match.
- Verify every sermon with a thumbnail has a corresponding `MediaAsset`.
- Verify slugs are unique.

#### Rollback Strategy
- Prisma tables are source of truth. Do not delete Prisma rows. If Django-populated FK references cause issues, nullify FKs.

---

### 3.3 `series.json`

#### Source
- Path: `apps/web/content/series.json`
- Structure: Array of series objects with slug, title, description, image.

#### Destination
| Destination Model | Notes |
|-------------------|-------|
| `SermonSeries` (legacy Prisma, `managed=False`) | Ensure Prisma table populated. |
| `MediaAsset` (Django) | Artwork image. |

#### Transformation Rules
- Ensure Prisma table populated.
- `image` path → `MediaAsset` (M2).
- `slug` preserved.

#### Validation Steps
- Count series in Prisma vs. JSON.
- Every series with an image must have a `MediaAsset` reference.

#### Rollback Strategy
- Prisma is authoritative. No deletion of Prisma rows.

---

### 3.4 `events.json`

#### Source
- Path: `apps/web/content/events.json`
- Structure: Array of event objects with id, title, date, time, location, description, category, image, status.

#### Destination
| Destination Model | Notes |
|-------------------|-------|
| `ChurchEvent` (legacy Prisma, `managed=False`) | Ensure Prisma table populated. |
| `MediaAsset` (Django) | Event poster image. |

#### Transformation Rules
- Ensure Prisma table populated, preserving `id` and `status`.
- `category` field: Ensure it exists and maps to frontend enum. If source has inconsistent values, normalize (e.g., "special" → default category).
- `image` path → `MediaAsset` (M2).
- `start_date_time` and `end_date_time` derived from `date` and `time`.

#### Validation Steps
- Count events in Prisma vs. JSON.
- Verify all events have valid `status`.
- Verify every event with image has a `MediaAsset`.

#### Rollback Strategy
- Prisma authoritative. No deletion.

---

### 3.5 `testimonials.json`

#### Source
- Path: `apps/web/content/testimonials.json`
- Structure: Array of testimonial objects with name, quote, photo, role, date.

#### Destination
| Destination Model | Notes |
|-------------------|-------|
| `WebsiteTestimonial` (legacy Prisma, `managed=False`) | Ensure Prisma table populated. |
| `MediaAsset` (Django) | Photo image. |

#### Transformation Rules
- Ensure Prisma table populated with quote, name, role.
- `photo` path → `MediaAsset` (M2).
- `publish_date`, `expiration_date`, `is_featured`, `display_order` need to be set:
  - `publish_date` = source `date` or today if absent.
  - `expiration_date` = `publish_date` + 1 year (configurable).
  - `is_featured` = false by default.
  - `display_order` = 0.
- `is_archived` = false.

#### Validation Steps
- Count testimonials in Prisma vs. JSON.
- Verify every testimonial with a photo has a `MediaAsset`.

#### Rollback Strategy
- Prisma authoritative. No deletion.

---

### 3.6 `leadership.json`

#### Source
- Path: `apps/web/content/leadership.json`
- Structure: Array of leader objects with name, role, photo, bio.

#### Destination
| Destination Model | Notes |
|-------------------|-------|
| `WebsiteLeader` (legacy Prisma, `managed=False`) | Ensure Prisma table populated. |
| `MediaAsset` (Django) | Photo image. |

#### Transformation Rules
- Ensure Prisma table populated.
- `photo` path → `MediaAsset` (M2).
- `is_archived` = false initially.
- `sort_order` = derived from role order if defined.

#### Validation Steps
- Count leaders in Prisma vs. JSON.
- Verify every leader with a photo has a `MediaAsset`.

#### Rollback Strategy
- Prisma authoritative. No deletion.

---

### 3.7 `academy-modules.json`

#### Source
- Path: `apps/web/content/academy-modules.json`
- Structure: Array of module objects with title, description, image, instructor.

#### Destination
| Destination Model | Notes |
|-------------------|-------|
| `WebsiteAcademyModule` (legacy Prisma, `managed=False`) | Ensure Prisma table populated. |
| `MediaAsset` (Django) | Optional image. |

#### Transformation Rules
- Ensure Prisma table populated.
- `image` path → `MediaAsset` (M2) if image exists.
- `instructor` stored as text.

#### Validation Steps
- Count modules in Prisma vs. JSON.
- For modules with image, verify `MediaAsset` reference exists.

#### Rollback Strategy
- Prisma authoritative. No deletion.

---

## 4. Media Backfill Migration (M2)

### Source
- Static image assets in `apps/web/public/images/*` and `RP/website/public/*`.
- Image paths referenced by JSON/Prisma content.

### Destination
- `MediaAsset` table (Django, `managed=True`).

### Process
1. **Scan references**: Extract all unique image paths from:
   - JSON content files.
   - Prisma model fields (e.g., `thumbnail`, `image`, `photo`).
2. **Copy files**: For each unique path, copy file to Django `MEDIA_ROOT` structured by content type (e.g., `sermons/`, `events/`, `leaders/`).
3. **Create MediaAsset records**:
   - `title` = filename.
   - `file` = relative path in `MEDIA_ROOT`.
   - `alt_text` = derived from filename or set blank.
   - `file_size` = file size on disk.
   - `checksum` = MD5 hash (duplicate detection).
   - `mime_type` = derived from extension.
   - `width`, `height` = image dimensions.
   - `focal_point_x` = 0.5 (center, until optimized).
   - `focal_point_y` = 0.5.
   - `is_public` = true.
   - `usage_count` = increment each time the asset is referenced.
4. **Update references**:
   - For Prisma-managed tables, update the Prisma row to store the CDN URL or a reference to the `MediaAsset` (depending on integration design).
   - For new Django models, store `MediaAsset` FK or generated URL.

### Validation
- Count: number of `MediaAsset` records equals number of unique source image files.
- Spot-check: a sample of images loads correctly via Django media serving.
- Checksums match source files.

### Rollback
- `MediaAsset` is a new table; deletion does not affect legacy data.
- Prisma fields referencing CDN URLs can be reverted to old paths if necessary.

---

## 5. GlobalSingleton Migration (M3)

### Models
- `GlobalSettings`
- `HomepageSettings`
- `ChurchProfile`

### Process
1. Parse `site.json` and extract relevant sections.
2. Create or update singletons.
3. Validate exactly one row exists per model.

### Rollback
- Delete singleton rows.
- Frontend falls back to `site.ts` hardcoded values.

---

## 6. ContentBlock Migration (M4)

### Process
1. From `site.json`, extract arrays for beliefs, values, FAQs, what-to-expect, theme.
2. Also extract any page-specific copy (prayer page, contact page).
3. For each item, create a `ContentBlock`:
   - `key` = auto-generated slug (e.g., `belief-1`, `value-1`).
   - `category` = enum based on source section.
   - `title` = item title or question.
   - `body` = item description or answer.
   - `display_order` = original array index.
   - `is_active` = true.
4. Insert all in a single transaction per category.

### Validation
- Count rows per category matches source arrays.
- No duplicate keys.

### Rollback
- Delete seeded `ContentBlock` rows by category.

---

## 7. Legacy Content Validation (M5)

Even though Prisma is source of truth, B2 may need to extend Prisma schema with new fields (e.g., `status`, `is_featured`, `thumbnail` FK). This migration step ensures all legacy rows in Prisma:

1. Have default values for new fields.
2. Have valid foreign keys (e.g., `series` FK points to existing series).
3. Maintain referential integrity.

This step is executed as a Prisma migration, not a Django migration.

---

## 8. New CMS Models (M6)

- `Announcement`: Initially empty; no seed data required. Admins populate via B3+ admin UI.
- `PrayerRequest`: Initially empty; will be populated by congregation submissions via existing prayer form.

No migration needed; these are net-new tables.

---

## 9. Frontend Cutover (M7)

### Feature Flag
Introduce an environment variable `USE_MANAGED_CONTENT=true` (or similar). The frontend `api.ts` mappers respect this flag:

- `true` → fetch from `/api/...` managed endpoints.
- `false` → read from `site.ts` and static JSON (current behavior).

### Cutover Steps
1. Deploy B2/B3 backend with all endpoints enabled.
2. Deploy frontend with flag `false`. Verify managed endpoints return correct data.
3. Enable flag for a subset of traffic (canary).
4. Enable flag fully.
5. Monitor for 1–2 weeks.

### Rollback
- Flip flag to `false`. Frontend immediately reverts to static JSON.

---

## 10. Archive Static JSON (M8)

After successful validation and cutover:

1. Move `site.json`, `sermons.json`, `series.json`, `events.json`, `testimonials.json`, `leadership.json`, `academy-modules.json` to `apps/web/content/archive/`.
2. Update any build scripts to not rely on these files for runtime.
3. Keep archive for historical reference and rollback.

---

## 11. Rollback Matrix

| Failure Scenario | Rollback Action |
|-----------------|-----------------|
| Media backfill corrupt | Delete `MediaAsset` rows; revert Prisma URL fields to old paths. |
| Singleton seed wrong | Delete singleton rows; frontend falls back to `site.ts`. |
| ContentBlock duplicates | Delete seeded rows; JSON source unchanged. |
| Prisma extension fails | Revert Prisma migration; Django reads unchanged schema. |
| Frontend integration breaks | Flip `USE_MANAGED_CONTENT=false`. |
| Full cutover failure | Restore static JSON from archive; revert feature flag. |

---

## 12. Success Criteria

- All counts match: number of source JSON items == number of destination managed records.
- Zero data loss on rollback test (each migration phase independently reversible).
- Frontend renders identically with managed endpoints as with static JSON.
- `USE_MANAGED_CONTENT=true` stable for 7 days without incident.

---

## 13. Open Questions (Deferred to B2)

1. Should Prisma schema be extended before or after Django models are built?
   - Recommendation: Extend Prisma first (M5) so Django reads are valid.
2. How to handle `pastorImage` URL during transition?
   - Recommendation: Backfill `MediaAsset` first (M2), then seed `ChurchProfile` with FK.
3. Should announcements be seeded with sample data for B2 testing?
   - Recommendation: No, empty table is fine; admins will populate in B3+.

---

## 14. Bibliography / References

- `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md` — target model shapes and ownership.
- `RP/docs/adr/ADR-001-CONTENT-MANAGEMENT-ARCHITECTURE.md` — schema ownership decision.
- `prisma/schema.prisma` — legacy schema definition.
- `apps/web/content/*.json` — source files.