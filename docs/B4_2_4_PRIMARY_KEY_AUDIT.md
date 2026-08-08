# B4.2.4 — Primary Key Type Audit

## Phase 1 — Audit Results

### Methodology
Queried PostgreSQL `information_schema.columns` for all tables in the public schema, comparing Django model PK declarations against actual PostgreSQL column types.

### Django-Owned Models (Correct — managed=True, no Prisma legacy)

| Model | Django PK Field | PostgreSQL PK Type | Match? |
|---|---|---|---|
| HomepageSettings | AutoField (BigAutoField default) | bigint | ✅ |
| ChurchProfile | AutoField (BigAutoField default) | bigint | ✅ |
| ContentBlock | AutoField (BigAutoField default) | bigint | ✅ |
| ServiceTime | AutoField (BigAutoField default) | bigint | ✅ |
| HomepageSection | AutoField (BigAutoField default) | bigint | ✅ |
| GlobalSettings | AutoField (BigAutoField default) | bigint | ✅ |
| Announcement | UUIDField (default=uuid4) | uuid | ✅ |
| PrayerRequest | UUIDField (default=uuid4) | uuid | ✅ |
| MediaAsset | UUIDField (pk field named `uuid`) | N/A | ✅ |

### Prisma-Legacy Models (MISMATCH — managed=True, restructured tables)

| Model | Django PK Field | PostgreSQL PK Type | Match? |
|---|---|---|---|
| **SystemConfig** | UUIDField | **TEXT** | ❌ MISMATCH |
| **SermonSeries** | UUIDField | **TEXT** | ❌ MISMATCH |
| **PublicSermon** | UUIDField | **TEXT** | ❌ MISMATCH |
| **WebsiteLeader** | UUIDField | **TEXT** | ❌ MISMATCH |
| **WebsiteTestimonial** | UUIDField | **TEXT** | ❌ MISMATCH |
| **WebsiteAcademyModule** | UUIDField | **TEXT** | ❌ MISMATCH |
| **ContactSubmission** | UUIDField | **TEXT** | ❌ MISMATCH |
| **VisitRsvp** | UUIDField | **TEXT** | ❌ MISMATCH |
| **ChurchEvent** | UUIDField | **TEXT** | ❌ MISMATCH |
| **EventRegistration** | UUIDField | **TEXT** | ❌ MISMATCH |
| **PrayerSubmission** | UUIDField | **TEXT** | ❌ MISMATCH |

### Foreign Key Columns Affected
All FK columns referencing the tables above also store UUIDs as TEXT. Examples:
- `seriesId` in PublicSermon
- `eventId` in EventRegistration
- `createdById` in multiple tables
- `updatedById` in SystemConfig

## Phase 2 — Root Cause Analysis

### Cause
The original database was created and managed by Prisma ORM. Prisma stored UUID values in TEXT columns by default. When the ownership was converted to Django (Phase B3.2), the Django models were declared with `UUIDField(primary_key=True, default=uuid.uuid4)` but the existing PostgreSQL columns remained as TEXT type. Django migrations were not generated to alter the column types because `managed=True` was set on already-existing tables, and no migration explicitly cast the column types.

### Affected Admin Pages
Admin views for these models are broken with:
```
ProgrammingError: operator does not exist: text = uuid
```
This affects admin change/detail views for:
- WebsiteTestimonial (confirmed broken)
- WebsiteLeader
- WebsiteAcademyModule
- PublicSermon
- SermonSeries
- ChurchEvent
- EventRegistration
- ContactSubmission
- VisitRsvp
- PrayerSubmission
- SystemConfig

### UUID Validity Check
All UUID values stored in TEXT columns were validated. **100% of stored values are valid UUIDs.** No invalid or non-UUID strings exist. This makes PostgreSQL column type conversion safe.

## Summary
- **12 tables** affected
- **100% of UUID values are valid**
- **Root cause:** Prisma-originated TEXT columns not converted to UUID during Django ownership conversion