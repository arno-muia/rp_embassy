# B2.1 Schema Audit — Current Ownership vs Intended Architecture

**Phase:** B2.1 — Model Hardening & Schema Foundation
**Date:** 2026-07-20
**Related:** `B1_MODEL_OWNERSHIP_MATRIX.md`, `BACKEND_CONTENT_MANAGEMENT_DESIGN.md`

---

## 1. Content App (`content` models)

| Model | Current Owner | Managed | Intended Owner | Managed | Changes Required |
|-------|--------------|---------|----------------|---------|------------------|
| `SystemConfig` | Prisma | `False` | Prisma (legacy) | `False` | None (will be deprecated by GlobalSettings) |
| `SermonSeries` | Prisma | `False` | Prisma (legacy) | `False` | Add `is_featured`, `published_at` fields |
| `PublicSermon` | Prisma | `False` | Prisma (legacy) | `False` | Add `workflow_status`, `is_featured`, `published_at`, `archived_at` |
| `WebsiteLeader` | Prisma | `False` | Prisma (legacy) | `False` | Add `display_order` (exists), `is_archived` |
| `WebsiteTestimonial` | Prisma | `False` | Prisma (legacy) | `False` | Add `display_order` (exists), `is_featured`, `expiration_date`, `archived_at` |
| `WebsiteAcademyModule` | Prisma | `False` | Prisma (legacy) | `False` | Add `display_order` (exists), `is_featured` |
| `ContactSubmission` | Prisma | `False` | Prisma (legacy) | `False` | None |
| `VisitRsvp` | Prisma | `False` | Prisma (legacy) | `False` | None |
| `GlobalSettings` | N/A | — | Django | `True` | New model — CREATE |
| `HomepageSettings` | N/A | — | Django | `True` | New model — CREATE |
| `ChurchProfile` | N/A | — | Django | `True` | New model — CREATE |
| `ContentBlock` | N/A | — | Django | `True` | New model — CREATE |

## 2. Events App (`events` models)

| Model | Current Owner | Managed | Intended Owner | Managed | Changes Required |
|-------|--------------|---------|----------------|---------|------------------|
| `ChurchEvent` | Prisma | `False` | Prisma (legacy) | `False` | Add `category`, `workflow_status`, `is_featured`, `published_at`, `archived_at`, `rsvp_enabled` |
| `EventRegistration` | Prisma | `False` | Prisma (legacy) | `False` | None |
| `Announcement` | N/A | — | Django | `True` | New model — CREATE |

## 3. Prayer App (`prayer` models)

| Model | Current Owner | Managed | Intended Owner | Managed | Changes Required |
|-------|--------------|---------|----------------|---------|------------------|
| `PrayerSubmission` | Prisma | `False` | Prisma (legacy) | `False` | None |
| `PrayerRequest` | N/A | — | Django | `True` | New model — CREATE |

## 4. Media App (`media` models)

| Model | Current Owner | Managed | Intended Owner | Managed | Changes Required |
|-------|--------------|---------|----------------|---------|------------------|
| `MediaAsset` | N/A | — | Django | `True` | New app + model — CREATE |

## 5. Accounts App (`accounts` models)

| Model | Current Owner | Managed | Intended Owner | Managed | Changes Required |
|-------|--------------|---------|----------------|---------|------------------|
| `User` | Prisma | `False` | Prisma (legacy) | `False` | None |
| `AuditLog` | Prisma | `False` | Prisma (legacy) | `False` | None |

## 6. New Django-Owned Models Required

| Model | App | Managed |
|-------|-----|---------|
| `GlobalSettings` | `content` | `True` |
| `HomepageSettings` | `content` | `True` |
| `ChurchProfile` | `content` | `True` |
| `ContentBlock` | `content` | `True` |
| `Announcement` | `events` | `True` |
| `PrayerRequest` | `prayer` | `True` |
| `MediaAsset` | `media` (NEW) | `True` |

## Key Decisions

1. **No Prisma-owned models converted to `managed=True`.** All legacy content models remain `managed=False` per the architecture.
2. **New Django-owned models** all use `managed=True`.
3. **New `media` app** added to `INSTALLED_APPS` for `MediaAsset`.
4. **Workflow enums** extracted into a shared module in the `content` app for reuse.