# B4.2.5 — Foreign Key UUID Consistency Repair Implementation

## Problem

After B4.2.4 converted Prisma-legacy TEXT primary keys to UUID, foreign key columns
remained TEXT. This caused PostgreSQL join errors:

```
operator does not exist: text = uuid
Example: JOIN "SermonSeries" ON "PublicSermon"."seriesId" = "SermonSeries"."id"
```

## Affected Columns

| Model | Column | Referenced PK |
|--------|---------|----------------|
| PublicSermon | seriesId | SermonSeries.id (uuid) |
| SystemConfig | updatedById | auth_user.id (uuid) |
| EventRegistration | eventId | ChurchEvent.id (uuid) |
| EventRegistration | memberId | Member.id (uuid) |

## Repair Migrations

### content/0009_convert_publicsermon_seriesid_to_uuid.py

Converts `PublicSermon.seriesId` from TEXT to UUID.

```sql
ALTER TABLE "PublicSermon"
ALTER COLUMN "seriesId" TYPE uuid
USING "seriesId"::uuid;
```

### content/0010_convert_systemconfig_updatedbyid_to_uuid.py

Converts `SystemConfig.updatedById` from TEXT to UUID.

```sql
ALTER TABLE "SystemConfig"
ALTER COLUMN "updatedById" TYPE uuid
USING "updatedById"::uuid;
```

### events/0008_convert_eventregistration_eventid_to_uuid.py

Converts `EventRegistration.eventId`, `memberId`, and ensures `ChurchEvent.id` and
`EventRegistration.id` are UUID. Drops lingering FK constraints before conversion.

```sql
-- Drop constraints that block type conversion
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'EventRegistration_eventId_fkey') THEN
        ALTER TABLE "EventRegistration" DROP CONSTRAINT "EventRegistration_eventId_fkey";
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'EventRegistration_memberId_fkey') THEN
        ALTER TABLE "EventRegistration" DROP CONSTRAINT "EventRegistration_memberId_fkey";
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ChurchEvent_createdById_fkey') THEN
        ALTER TABLE "ChurchEvent" DROP CONSTRAINT "ChurchEvent_createdById_fkey";
    END IF;
END $$;

-- Convert PK columns
ALTER TABLE "ChurchEvent" ALTER COLUMN id TYPE uuid USING id::uuid;
ALTER TABLE "EventRegistration" ALTER COLUMN id TYPE uuid USING id::uuid;

-- Convert FK columns
ALTER TABLE "EventRegistration" ALTER COLUMN "eventId" TYPE uuid USING "eventId"::uuid;
ALTER TABLE "EventRegistration" ALTER COLUMN "memberId" TYPE uuid USING "memberId"::uuid;
```

## Data Preservation

All migrations use `USING ...::uuid` to preserve existing data. No rows are dropped.

## Notes

- Django ForeignKey declarations use `db_constraint=False`, so PostgreSQL did not enforce
  referential integrity. The mismatch surfaced only at ORM join time.
- Constraints are dropped before conversion and not recreated because Django manages
  relationships at the application level.