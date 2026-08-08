# B4.2.5 — Foreign Key UUID Consistency Audit

## Objective

After B4.2.4 converted Prisma-legacy TEXT primary keys to UUID, foreign key columns
were not updated. This caused PostgreSQL join errors:

```
operator does not exist: text = uuid
Example: JOIN "SermonSeries" ON "PublicSermon"."seriesId" = "SermonSeries"."id"
```

## Scope

Django-owned models inspected:

- `backend/apps/content/models.py`
- `backend/apps/events/models.py`
- `backend/apps/prayer/models.py`
- `backend/apps/media/models.py`

## Audit Methodology

1. Read relationship fields in each model to determine referenced PK types.
2. Query PostgreSQL `information_schema.columns` to determine actual column types.
3. Flag every mismatch where FK column is `text` and referenced PK is `uuid`.

## Results

### Mismatches Identified

| Model | Column | Django Type | PostgreSQL Type (before repair) | Referenced PK Type | Status |
|--------|---------|-------------|----------------------------------|---------------------|--------|
| PublicSermon | seriesId | ForeignKey(SermonSeries) | text | uuid (SermonSeries.id) | MISMATCH |
| SystemConfig | updatedById | ForeignKey(User) | text | uuid (auth_user.id) | MISMATCH |
| EventRegistration | eventId | ForeignKey(ChurchEvent) | text | uuid (ChurchEvent.id) | MISMATCH |
| EventRegistration | memberId | ForeignKey(Member) | text | uuid (Member.id) | MISMATCH |

### Matches Verified

| Model | Column | Django Type | PostgreSQL Type | Referenced PK Type | Status |
|--------|---------|-------------|------------------|---------------------|--------|
| PublicSermon | id | UUIDField | uuid | uuid | OK |
| SermonSeries | id | UUIDField | uuid | uuid | OK |
| WebsiteLeader | id | UUIDField | uuid | uuid | OK |
| WebsiteTestimonial | id | UUIDField | uuid | uuid | OK |
| WebsiteAcademyModule | id | UUIDField | uuid | uuid | OK |
| ContactSubmission | id | UUIDField | uuid | uuid | OK |
| VisitRsvp | id | UUIDField | uuid | uuid | OK |
| ChurchEvent | id | UUIDField | uuid | uuid | OK |
| EventRegistration | id | UUIDField | uuid | uuid | OK |

## Notes

- All Django ForeignKey declarations use `db_constraint=False`, so PostgreSQL did not
  enforce referential integrity. The mismatch therefore surfaced only at ORM join time.
- B4.2.4 migration `0007_convert_text_pk_to_uuid` (events) and `0008_convert_text_pk_to_uuid`
  (content) converted PKs but intentionally did not alter FK columns.
- This audit isolates the exact FK columns requiring repair.