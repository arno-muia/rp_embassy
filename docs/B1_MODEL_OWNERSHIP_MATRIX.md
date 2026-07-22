# B1 Model Ownership Matrix

**Phase:** B1.5 — Final Architecture Validation
**Date:** 2026-07-20
**Status:** Approved
**Related:** `RP/docs/adr/ADR-001-CONTENT-MANAGEMENT-ARCHITECTURE.md`, `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md`

---

## Purpose

This matrix eliminates ownership ambiguity for every content-related model before B2 implementation. It specifies:

- Source of truth
- Migration strategy
- Whether Django migrations control schema
- Whether Prisma remains authoritative
- Future ownership considerations

---

## Ownership Definitions

| Ownership | Description |
|-----------|-------------|
| **Prisma Owned** | Schema defined and migrated by Prisma. Django reads/writes but does not manage schema. `managed = False`. |
| **Django Owned** | Schema defined and migrated by Django. `managed = True`. |
| **Shared** | Both systems can read/write; schema changes require coordinated migration. |

---

## Model Ownership Matrix

### Legacy Prisma-Owned Models

| Model | Prisma Owned | Django Owned | Managed | Source of Truth | Migration Strategy | Future Ownership |
|-------|-------------|--------------|---------|-----------------|-------------------|------------------|
| `PublicSermon` | YES | NO | `False` | Prisma schema + seed | Prisma migrations only. Django extends with lifecycle fields (status, featured, etc.) via ALTER TABLE or Prisma migration. Possible Django ownership after B7 cutover. |
| `SermonSeries` | YES | NO | `False` | Prisma schema + seed | Prisma migrations only. Django adds `is_featured` via Prisma extension. Possible Django ownership after B7. |
| `WebsiteLeader` | YES | NO | `False` | Prisma schema + seed | Prisma migrations only. Django adds `is_archived`, photo FK via Prisma extension. Possible Django ownership after B7. |
| `WebsiteTestimonial` | YES | NO | `False` | Prisma schema + seed | Prisma migrations only. Django adds lifecycle fields (expiration, featured, etc.) via Prisma extension. Possible Django ownership after B7. |
| `WebsiteAcademyModule` | YES | NO | `False` | Prisma schema + seed | Prisma migrations only. Django adds image FK via Prisma extension. Possible Django ownership after B7. |
| `ChurchEvent` | YES | NO | `False` | Prisma schema + seed | Prisma migrations only. Django adds category, featured, rsvp_enabled via Prisma extension. Possible Django ownership after B7. |
| `EventRegistration` | YES | NO | `False` | Prisma schema + seed | Prisma migrations only. No Django extensions planned. Possible Django ownership after B7. |

### New Django-Owned Models

| Model | Prisma Owned | Django Owned | Managed | Source of Truth | Migration Strategy | Future Ownership |
|-------|-------------|--------------|---------|-----------------|-------------------|------------------|
| `GlobalSettings` | NO | YES | `True` | Django seed from `site.json` | Django migration. Singleton; seeded once in B7. Remains Django-owned. |
| `HomepageSettings` | NO | YES | `True` | Django seed from `site.json` | Django migration. Singleton; seeded once in B7. Remains Django-owned. |
| `ChurchProfile` | NO | YES | `True` | Django seed from `site.json` | Django migration. Singleton; seeded once in B7. Remains Django-owned. |
| `ContentBlock` | NO | YES | `True` | Django seed from `site.json` arrays | Django migration. Seeded in B7. Remains Django-owned. May be extended with dedicated models later if complexity demands. |
| `ServiceTime` | NO | YES | `True` | Django seed from `site.json` `serviceTimes[]` | Django migration. Seeded in B7. Remains Django-owned. |
| `Announcement` | NO | YES | `True` | Admin UI after B3 | Django migration. No seed data. Remains Django-owned. |
| `MediaAsset` | NO | YES | `True` | Backfill from static images (B7 M2) | Django migration. Backfilled once. Remains Django-owned. |
| `PrayerRequest` | NO | YES | `True` | Congregation submissions (post-B3) | Django migration. No seed data. Remains Django-owned. |
| `AuditLog` | NO | YES | `True` | Mutating operations | Django migration. Remains Django-owned. |
| `HomepageSection` | NO | YES | `True` | Admin UI (future B3+) | Django migration. Seeded with defaults. Remains Django-owned. |
| `HomepagePastorSection` | NO | YES | `True` | Django seed from `site.json` pastor fields | Django migration. Seeded in B7. Could be merged into `ChurchProfile` fields; keep separate for clarity. Remains Django-owned. |

---

## Ownership Transition Path

### Current State (B1)
- Prisma owns: PublicSermon, SermonSeries, WebsiteLeader, WebsiteTestimonial, WebsiteAcademyModule, ChurchEvent, EventRegistration
- Django owns: none (only reads Prisma tables)

### Target State (B2–B7)
- Prisma continues to own legacy tables.
- Django owns all new CMS tables.
- Legacy tables gain Django-side extensions (fields, FKs) via Prisma migrations coordinated with B2.

### Future Consideration (Post-B7)
- Full Django ownership of legacy tables is possible but **deferred**.
- Trigger for conversion: if Prisma schema changes become rare and Django-side extensions become frequent.
- Conversion would require: Django migration to claim tables (`managed = True`), data verification, cutover.

---

## Critical Ownership Rules

1. **Never modify Prisma schema without coordination** during B2/B3. Any field additions to legacy tables must be done via Prisma migrations and reflected in Django models.
2. **Django migration commands must not touch `managed = False` tables.** Django migrations should only create/alter Django-owned tables.
3. **Data seeding**: Django-owned tables are seeded by Django management commands or migration `RunPython`. Prisma-owned tables are seeded by Prisma seed scripts.
4. **Rollback**: Django-owned table data can be deleted without affecting Prisma. Prisma-owned data must never be deleted by Django.
5. **Backup**: Prisma tables are backed up via Prisma/Database backup. Django tables are backed up via Django management command or database dump.

---

## Ambiguity Resolution

| Ambiguity | Resolution |
|-----------|------------|
| Who adds `is_featured` to `SermonSeries`? | Prisma migration adds column; Django model reads it. |
| Who creates `MediaAsset` table? | Django migration creates table; backfill script populates. |
| Who seeds `GlobalSettings`? | Django seed script (migration `RunPython`). |
| Who defines `category` enum on `ChurchEvent`? | Prisma migration adds column; Django model reads it. |
| Who drops legacy JSON files? | Archive script (B7 M8); both systems should ignore them. |
| Who migrates `site.json` → `GlobalSettings`? | Django management command reads JSON, writes to Django-owned table. |