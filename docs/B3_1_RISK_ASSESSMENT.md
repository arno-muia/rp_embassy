# B3.1 Risk Assessment

**Phase:** B3.1 — Risk Assessment  
**Date:** 2026-07-21  
**Status:** Complete  
**Related:** `RP/docs/B3_1_OWNERSHIP_CONVERSION_AUDIT.md`, `RP/docs/B3_1_CONVERSION_STRATEGY.md`

---

## Executive Summary

This document evaluates risks associated with converting Prisma-owned tables to Django ownership. Risk assessment covers data loss, migration, downtime, serializer, API contract, and admin integration risks.

---

## 1. Data Loss Risk

### 1.1 Risk Assessment Matrix

| Model | Data Loss Risk | Justification | Mitigation |
|-------|----------------|-------------|------------|
| WebsiteAcademyModule | LOW | Simple table, no FKs, read-only | Backup before migration |
| WebsiteTestimonial | LOW | Simple table, no FKs, read-only | Backup before migration |
| ContactSubmission | LOW | Append-only submissions | Backup before migration |
| VisitRsvp | LOW | Append-only submissions | Backup before migration |
| PrayerSubmission | LOW | Append-only submissions | Backup before migration |
| SermonSeries | LOW-MEDIUM | Has FK from PublicSermon | Maintain FK constraint |
| PublicSermon | MEDIUM | Media-rich content, FTS enabled | Backup + verify GIN indexes |
| ChurchEvent | MEDIUM | Event registrations linked | Backup + verify relationship |
| SystemConfig | LOW | Singleton config data | Backup singleton record |
| User | HIGH | Authentication credentials | Critical backup + test auth |
| AuditLog | MEDIUM | Immutable audit trail | Verify write behavior |
| Household | MEDIUM | Family unit definitions | Backup + foreign key deps |
| Member | HIGH | Member records with PII | Critical backup + privacy |
| HouseholdMember | MEDIUM | Bridge table data | Backup + verify relationships |
| GivingTransaction | HIGH | Financial records | Critical backup + verify |
| EventRegistration | MEDIUM | Registration payments | Backup + verify relationships |

### 1.2 Data Loss Mitigation Strategies

1. **Full Database Backup**: Run `pg_dump` before Phase 3
   ```bash
   pg_dump -h localhost -U postgres -t RP > rp_backup_pre_migration.sql
   ```

2. **Point-in-Time Recovery**: Enable WAL archiving if not already active

3. **Verification Queries**: After each conversion, run checksum queries
   ```sql
   SELECT COUNT(*), SUM(hashtext(title::text)) FROM "PublicSermon";
   ```

---

## 2. Migration Risk

### 2.1 Migration Complexity Risk

| Risk Level | Models | Concerns |
|------------|--------|----------|
| LOW | AcademyModule, Testimonial, ContactSubmission, VisitRsvp, PrayerSubmission | No FK constraints, simple schema |
| MEDIUM | SermonSeries, PublicSermon, ChurchEvent, SystemConfig | FK constraints with db_constraint=False |
| HIGH | User, Member, Household, HouseholdMember, GivingTransaction | Auth/financial critical, multiple FK dependencies |

### 2.2 Migration Risk Factors

1. **Schema Mismatch Risk**: Django may generate slightly different DDL than Prisma
   - **Impact**: Migration failure or constraint mismatches
   - **Mitigation**: Review all generated migrations before applying

2. **Index Ownership Risk**: GIN indexes created in B2.3 may conflict
   - **Impact**: Duplicate indexes or missing search functionality
   - **Mitigation**: Document existing indexes, verify post-migration

3. **Sequence/Serial Risk**: UUID defaults using `gen_random_uuid()`
   - **Impact**: Migration tries to set default
   - **Mitigation**: Verify UUID columns use correct defaults

### 2.3 Migration Commands Safety

```bash
# Always review before applying
python manage.py makemigrations --dry-run

# Check SQL output
python manage.py sqlmigrate content 0003

# Apply with transaction
python manage.py migrate --atomic
```

---

## 3. Downtime Risk

### 3.1 Downtime Requirements

| Phase | Models | Downtime Required | Window |
|-------|--------|-------------------|--------|
| Phase 1 | 6 models | ❌ No | - |
| Phase 2 | 3 models | ⚠️ Minimal | Brief |
| Phase 3 | 7 models | ✅ Yes | 2-4 hours |

### 3.2 Downtime Scenarios

| Scenario | Duration | Rollback Time |
|----------|----------|---------------|
| Phase 1 failure | < 5 min | < 1 min |
| Phase 2 failure | < 10 min | < 5 min |
| Phase 3 failure | 15-30 min | 30-60 min |

### 3.3 Minimizing Downtime

1. **Staged Rollout**: Deploy migrations to staging first
2. **Blue-Green Deployment**: If available, use parallel infrastructure
3. **Read Replicas**: For read-only verification during migration

---

## 4. Serializer Risk

### 4.1 Serializer Compatibility Risk

All serializers are in read-only mode currently. Upon conversion:

| Model | Read Serializer Risk | Write Serializer Risk | Action |
|-------|---------------------|---------------------|--------|
| All models | LOW | LOW | Both serializers exist, API stable |

### 4.2 Serializer Verification

```bash
# Verify serializer outputs match
curl -s http://localhost:8000/api/sermons | python -m json.tool
# Compare output before/after migration
```

### 4.3 Serializer Risks on Conversion

1. **JSON Field Handling**: Ensure `JSONField` serializes correctly
2. **DateTime Formatting**: Verify timezone handling unchanged
3. **Nested Serialization**: FK relationships may need explicit handling

---

## 5. API Contract Risk

### 5.1 API Endpoint Stability

| Endpoint | Risk | Current State |
|----------|------|---------------|
| GET /api/sermons | LOW | Read-only ViewSet |
| GET /api/sermons/:slug | LOW | Lookup by slug |
| GET /api/series | LOW | Read-only ViewSet |
| GET /api/series/:slug | LOW | Lookup by slug |
| GET /api/events | LOW | Read-only ViewSet |
| GET /api/events/:id | LOW | Lookup by UUID |
| GET /api/leaders | LOW | Read-only ViewSet |
| GET /api/testimonials | LOW | Read-only ViewSet |
| GET /api/academy | LOW | Read-only ViewSet |
| GET /api/site-config | LOW | Function view returns JSON |
| POST /api/contact | LOW | Function view |
| POST /api/rsvp | LOW | Function view |
| POST /api/prayer | LOW | Function view |

### 5.2 API Contract Verification

```bash
# Test all endpoints return valid JSON
for endpoint in /api/sermons /api/series /api/events /api/leaders /api/testimonials /api/academy; do
  curl -sf "http://localhost:8000$endpoint" | jq . > /dev/null || echo "FAIL: $endpoint"
done
```

### 5.3 API Risk Mitigations

1. **Contract Testing**: Run full API test suite post-migration
2. **Frontend Verification**: Smoke test all Astro pages
3. **CORS Verification**: Confirm CORS headers unchanged

---

## 6. Admin Integration Risk

### 6.1 Current Admin Status

None of the Prisma-owned models are currently registered in Django admin. All models require admin registration post-conversion.

### 6.2 Admin Registration Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| Model not visible | Forgetting to register model | Create admin.py for each app |
| Write access broken | Missing admin form handling | Use ModelAdmin with serializer validation |
| Search not working | GIN indexes not exposed | Add search_fields to ModelAdmin |

### 6.3 Required Admin Actions

```python
# Example admin.py for content app
from django.contrib import admin
from .models import SermonSeries, PublicSermon, WebsiteLeader

@admin.register(SermonSeries)
class SermonSeriesAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'sort_order']
    search_fields = ['title', 'description']
    
@admin.register(PublicSermon)
class PublicSermonAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'speaker', 'date', 'is_published']
    search_fields = ['title', 'description', 'speaker']
```

---

## 7. GIN Index Risk

### 7.1 Search Index Ownership

The GIN indexes created in B2.3 (`0002_gin_search_indexes.py`) create a special case:

| Table | Index Name | Risk |
|-------|------------|------|
| PublicSermon | gin indexes on FTS fields | MEDIUM |
| ChurchEvent | gin indexes on FTS fields | MEDIUM |
| PrayerSubmission | gin indexes on FTS fields | LOW |

### 7.2 Possible Issues

1. Django may try to recreate indexes on conversion
2. Index naming conflicts
3. Search vectors may need adjustment

### 7.3 GIN Index Verification

```sql
-- Pre-migration
SELECT indexname, indexdef FROM pg_indexes WHERE tablename IN ('PublicSermon', 'ChurchEvent', 'PrayerSubmission');

-- Post-migration
SELECT indexname FROM pg_indexes WHERE tablename = 'PublicSermon' AND indexname LIKE '%gin%';
```

---

## 8. Overall Risk Summary

### 8.1 Risk Matrix

| Category | Risk Level | Models Affected | Mitigation Status |
|----------|------------|-----------------|-------------------|
| Data Loss | HIGH | User, Member, GivingTransaction | Backup required |
| Migration | MEDIUM | All models | Review migrations |
| Downtime | HIGH | Phase 3 models | Schedule window |
| Serializer | LOW | All models | Test coverage exists |
| API Contract | LOW | All models | Verify endpoints |
| Admin | MEDIUM | All models | Register post-conversion |
| GIN Index | MEDIUM | PublicSermon, ChurchEvent | Document indexes |

### 8.2 Total Risk Assessment

| Metric | Value |
|--------|-------|
| High Risk Models | 4 (User, AuditLog, Member, GivingTransaction) |
| Medium Risk Models | 7 (PublicSermon, ChurchEvent, SystemConfig, Household, HouseholdMember, EventRegistration, AuditLog) |
| Low Risk Models | 6 (AcademyModule, Testimonial, ContactSubmission, VisitRsvp, PrayerSubmission, SermonSeries) |

---

## 9. Final Recommendation

### 9.1 GO/NO-GO Decision

**STATUS: GO WITH CONDITIONS**

### 9.2 Required Conditions

1. **Pre-requisites (Before B3.2)**:
   - ✅ Fix WebsiteLeader schema drift (remove `is_archived` field)
   - ✅ Complete full database backup
   - ✅ Document GIN index definitions
   - ✅ Schedule Phase 3 maintenance window

2. **During B3.2 Execution**:
   - ✅ Verify all API endpoints post-migration
   - ✅ Test frontend rendering after each phase
   - ✅ Register models in Django admin after conversion

3. **Post-B3.2 Verification**:
   - ✅ Run full regression test suite
   - ✅ Verify GIN search indexes functional
   - ✅ Confirm all admin write operations work

### 9.3 Acceptable Rollback Points

- **After Phase 1**: Full rollback possible, no downtime
- **After Phase 2**: Full rollback possible, minimal downtime
- **After Phase 3**: Requires database restore, significant downtime

### 9.4 Success Criteria

Migration is successful when:
1. All API endpoints return 200 OK
2. Frontend pages render without errors
3. Admin can view and edit all models
4. GIN search indexes are functional
5. No data loss verified by record counts
6. Authentication system functional (if User converted)

---

## 10. Sign-off

| Role | Name | Date | Decision |
|------|------|------|----------|
| Architect | - | - | GO WITH CONDITIONS |
| DBA | - | - | Pending backup verification |
| Lead Developer | - | - | Ready for Phase 1 |

**Next Phase:** B3.2 Ownership Conversion Implementation