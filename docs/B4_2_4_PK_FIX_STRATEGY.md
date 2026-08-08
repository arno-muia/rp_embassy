# B4.2.4 — Primary Key Type Fix Strategy

## Option Evaluation

### Option A: Change Django Models to CharField

Change all Django UUIDField declarations to CharField to match PostgreSQL TEXT columns.

**Pros:**
- No database migration needed
- No risk of data corruption
- Simple to implement

**Cons:**
- Perpetuates incorrect schema design
- Django Admin will still work, but will treat IDs as strings
- Serializers and API responses will return strings instead of UUID objects
- Future team members will inherit a confusing schema
- Performance implications (TEXT comparison is slower than UUID)
- Breaks clean UUID validation at the model layer

### Option B: Convert PostgreSQL Columns to UUID Type (RECOMMENDED) ✅

Alter PostgreSQL column types from TEXT to UUID using `ALTER COLUMN ... TYPE uuid USING ...::uuid`.

**Pros:**
- Correct schema matches Django model declarations exactly
- Django Admin will work with proper UUID type comparisons
- Serializers/APIs return proper UUID objects
- Better database performance (UUID type is more efficient than TEXT)
- Clean schema for future development
- Proper UUID validation enforced at database level

**Cons:**
- Requires a database migration
- Need to validate all existing UUIDs first (already done - 100% valid)
- FK columns must also be converted
- Migration is not trivially reversible (but data is preserved)

## Recommendation: Option B

### Justification

1. **All existing UUIDs are valid** — 0 invalid values across all 12 tables
2. **Django models already declare UUIDField** — the database should match
3. **Admin compatibility** — the root cause of the bug is TEXT != UUID comparison
4. **Long-term maintenance** — correct schema prevents future confusion
5. **Reversible** — column values are preserved, conversion can be rolled back by re-running the reverse ALTER

### Implementation Plan

#### Step 1: Create a single data migration
Use `RunSQL` to execute ALTER TABLE statements that convert id columns from TEXT to UUID.

#### Step 2: Tables to convert

1. SystemConfig
2. SermonSeries
3. PublicSermon
4. WebsiteLeader
5. WebsiteTestimonial
6. WebsiteAcademyModule
7. ContactSubmission
8. VisitRsvp
9. ChurchEvent
10. EventRegistration
11. PrayerSubmission

#### Step 3: Validation
- Run `python manage.py check`
- Run `python manage.py makemigrations --check`
- Verify admin pages load for affected models
- Verify `GET /api/homepage` still returns HTTP 200

## Risk Assessment

| Risk | Probability | Mitigation |
|---|---|---|
| Data loss | None | ALTER TABLE preserves data; all UUIDs pre-validated |
| Broken API | Low | UUID types are compatible with DRF serializers |
| Broken migrations | Low | Single migration with dependencies on previous migrations |
| Reversibility | High | Use `ALTER COLUMN ... TYPE text` to revert |