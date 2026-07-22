# B2.3A — Search Implementation Plan

**Phase:** B2.3A — Architecture Validation & Readiness Review  
**Date:** 2026-07-21  
**Status:** Design Ready (Implementation in B2.3B)  
**Depends On:** B2_3A_SEARCH_ARCHITECTURE_VALIDATION.md, B2_3A_SEARCH_INDEX_DESIGN.md

---

## 1 — Service Architecture Design

### 1.1 File Location

```
backend/apps/content/services/search_service.py
```

**Note:** The service currently exists at `backend/apps/content/search_service.py`. The design anticipates potential relocation to the services directory in B2.3B (no code changes in B2.3A).

### 1.2 Responsibilities

| Responsibility | Description | Implementation Level |
|----------------|-------------|----------------------|
| Search vector construction | Build SearchVector from model fields with weights | SearchVector composition |
| Query parsing | Convert user input to SearchQuery | SearchQuery with type selection |
| Rank computation | Calculate relevance scores | SearchRank with ts_rank_cd |
| Result filtering | Filter queryset by rank threshold | queryset.filter(rank__gt=0) |
| Result ordering | Order results by relevance | queryset.order_by('-rank') |
| Pagination | Page-based result slicing | Offset/limit calculation |
| Model-specific search | Dedicated functions per model | search_* functions |
| Unified search | Combined search across models | unified_search() function |

### 1.3 Interfaces

#### Core Helper Functions

```python
def build_search_vector(fields: List[Tuple[str, str]]) -> SearchVector
def build_weighted_search_vector(fields: List[Tuple[str, str]]) -> SearchVector
def build_search_query(query_string: str, search_type: str = 'plain') -> SearchQuery
def execute_search(queryset: QuerySet, search_vector: SearchVector, search_query: SearchQuery) -> QuerySet
def paginate_results(queryset: QuerySet, page: int, page_size: int) -> QuerySet
```

#### Model-Specific Search Functions

| Function | Model | Returns | Notes |
|----------|-------|---------|-------|
| `search_content_blocks(query, page, page_size)` | ContentBlock | Tuple[QuerySet, float] | Uses CONTENT_BLOCK_SEARCH config |
| `search_announcements(query, page, page_size)` | Announcement | Tuple[QuerySet, float] | Uses ANNOUNCEMENT_SEARCH config |
| `search_church_profile(query, page, page_size)` | ChurchProfile | Tuple[QuerySet, float] | Uses CHURCH_PROFILE_SEARCH config |
| `search_prayer_requests(query, page, page_size)` | PrayerRequest | Tuple[QuerySet, float] | Uses PRAYER_REQUEST_SEARCH config |

#### Unified Search Function

```python
def unified_search(
    query: str,
    page: int = 1,
    page_size: int = 12,
    include_content_blocks: bool = True,
    include_announcements: bool = True,
    include_church_profile: bool = False,
    include_prayer_requests: bool = True,
) -> dict
```

**Returns:** Dictionary with keys `'content_blocks'`, `'announcements'`, `'church_profile'`, `'prayer_requests'` containing paginated querysets.

---

## 2 — Methods Design

### 2.1 Core Search Pipeline

```
User Query Input
      ↓
build_search_query() → SearchQuery object
      ↓
build_weighted_search_vector() → SearchVector object
      ↓
Model QuerySet.all()
      ↓
execute_search() → Annotated & filtered queryset
      ↓
paginate_results() → Paginated slice
      ↓
Return (results, total_count)
```

### 2.2 Weight Configuration Modules

| Module Variable | Fields | Weights |
|-----------------|--------|---------|
| `CONTENT_BLOCK_SEARCH` | 'title', 'content' | A, C |
| `ANNOUNCEMENT_SEARCH` | 'title', 'body' | A, C |
| `CHURCH_PROFILE_SEARCH` | 'mission', 'vision', 'welcome_message', 'pastor_message', 'about_text' | C (all) |
| `PRAYER_REQUEST_SEARCH` | 'title', 'content' | A, C |

### 2.3 Future Extensibility

| Extension Point | Description | Implementation |
|-----------------|-------------|----------------|
| Custom ranking | Different ranking algorithms | Add `ranking` parameter to SearchRank |
| Search language | Language-specific search | Add `config` parameter to SearchVector |
| Highlight matching | Return highlighted snippets | Use `SearchHeadline` (PostgreSQL 14+ / Django 4.2+) |
| Similarity search | Fuzzy matching | Use `TrigramSimilarity` with GIN index |
| Vector search | Embedding-based search | Future external service integration |

---

## 3 — GIN Index Implementation Design (B2.3B)

### 3.1 Migration Structure

Each Django app will receive a `0002_*` migration adding GIN indexes:

```
content/migrations/
├── 0001_initial.py (existing - B2.1)
├── 0002_gin_contentblock_search.py
└── 0003_gin_churchprofile_search.py

events/migrations/
├── 0001_initial.py (existing - B2.1)
└── 0002_gin_announcement_search.py

prayer/migrations/
├── 0001_initial.py (existing - B2.1)
└── 0002_gin_prayerrequest_search.py
```

### 3.2 Django Migration Pattern

```python
# migrations/0002_gin_contentblock_search.py
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='contentblock',
            index=GinIndex(
                name='idx_contentblock_search',
                fields=['title', 'content'],  # Expression handled in SQL
                opclasses=['gin', 'gin'],
            ),
        ),
    ]
```

**Note:** Actual GIN indexes may require `RunSQL` for weighted expression indexes.

---

## 4 — Search Workflow Integration Plan

### 4.1 Current Workflow Status (from workflow.py)

| Status | Value | Applicable Models |
|--------|-------|-------------------|
| DRAFT | 'DRAFT' | ContentBlock, Announcement, PrayerRequest |
| IN_REVIEW | 'IN_REVIEW' | ContentBlock, Announcement, PrayerRequest |
| APPROVED | 'APPROVED' | ContentBlock, Announcement, PrayerRequest |
| PUBLISHED | 'PUBLISHED' | All searchable models |
| ARCHIVED | 'ARCHIVED' | All searchable models |

### 4.2 Search Integration Points

| Model | Search Filter | Notes |
|-------|---------------|-------|
| ContentBlock | `is_active=True` | Active content only |
| Announcement | `is_active=True` AND `display_from/until` | Time-bound announcements |
| ChurchProfile | No filter | Singleton; always available |
| PrayerRequest | `is_public=True` | Public requests only; moderation filter |

---

## 5 — Implementation Phases

### 5.1 Phase B2.3B — GIN Index Generation

**Goal:** Create migration files with GIN index definitions.

| Step | Action | Command | Validation |
|------|--------|---------|------------|
| 1 | Review existing migrations | `ls content/migrations/` | Confirm 0001 exists |
| 2 | Create GIN index migrations | Manual migration creation | Follow pattern above |
| 3 | Validate migration content | Code review | No managed=False changes |
| 4 | Run migration dry-run | `python manage.py sqlmigrate content 0002` | SQL review only |

### 5.2 Phase B2.3B — Service Layer Enhancement

**Goal:** Enhance search_service.py with additional features.

| Step | Action | Dependencies |
|------|--------|--------------|
| 1 | Add missing search models to unified_search | PrayerRequest already present |
| 2 | Add search type selection | UI integration |
| 3 | Add highlight support | PostgreSQL 14+ requirement |
| 4 | Add filtering by category/type | Search endpoint enhancement |

---

## 6 — API Integration Design (Future)

### 6.1 Search Endpoint Pattern

```
GET /api/search?q={query}&page=1&page_size=12&models=content_blocks,announcements
```

### 6.2 Response Structure

```json
{
  "results": {
    "content_blocks": [...],
    "announcements": [...],
    "prayer_requests": [...]
  },
  "pagination": {
    "page": 1,
    "page_size": 12,
    "total": 42
  }
}
```

---

## 7 — Testing Strategy

### 7.1 Unit Tests

| Test Case | Model | Expected |
|-----------|-------|----------|
| Empty query returns empty | All | Empty queryset |
| Title matches rank higher | ContentBlock | Weight A > Weight C |
| No results for unmatched term | All | Empty queryset |
| Pagination boundary handling | All | Correct slicing |

### 7.2 Integration Tests

| Test Case | Description |
|-----------|-------------|
| Search with special characters | Apostrophes, quotes handled |
| Stop word handling | Common words excluded |
| Multi-term search | All terms required (AND semantics) |
| Phrase search option | Exact phrase matching |

---

## 8 — Monitoring Considerations

### 8.1 Metrics to Track

| Metric | Purpose | Tooling |
|--------|---------|---------|
| Query duration | Performance monitoring | Django debug toolbar |
| Index hit rate | Index effectiveness | PostgreSQL stats |
| Average rank score | Result quality | Application logs |
| Zero-result queries | Search gap analysis | Application logs |

### 8.2 Index Maintenance

| Task | Frequency | Owner |
|------|-----------|-------|
| Index bloat analysis | Monthly | DBA |
| VACUUM ANALYZE | Weekly | Automated |
| Query plan review | Quarterly | Developer |

---

## 9 — Risk Assessment

### 9.1 Identified Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GIN index on large text | Low | High | ContentBlock content is moderate length |
| Concurrent schema changes | Low | Medium | B2.2 signoff confirms no drift |
| Missing migration order | Low | High | Follow B2.1 migration order (content → events → prayer) |
| Search performance degradation | Low | Medium | Monitor query duration; add composite indexes if needed |

### 9.2 Rollback Plan

| Migration | Rollback Command |
|-----------|------------------|
| content 0002 | `python manage.py migrate content 0001` |
| events 0002 | `python manage.py migrate events 0001` |
| prayer 0002 | `python manage.py migrate prayer 0001` |

---

## 10 — Deliverables Checklist

### 10.1 B2.3A Deliverables (This Phase)

- [x] RP/docs/B2_3A_SEARCH_ARCHITECTURE_VALIDATION.md
- [x] RP/docs/B2_3A_SEARCH_INDEX_DESIGN.md
- [x] RP/docs/B2_3A_IMPLEMENTATION_PLAN.md

### 10.2 B2.3B Deliverables (Next Phase)

- [ ] GIN index migration files (content 0002, events 0002, prayer 0002)
- [ ] Search API endpoint
- [ ] Search filters integration
- [ ] Performance benchmarking report

---

## 11 — GO Recommendation

**RECOMMENDATION:** ✅ **PROCEED TO B2.3B**

### 11.1 Readiness Checklist

| Criterion | Status | Notes |
|-----------|--------|-------|
| Architecture validated | ✅ Verified | B2_3A_SEARCH_ARCHITECTURE_VALIDATION.md complete |
| Index design documented | ✅ Verified | B2_3A_SEARCH_INDEX_DESIGN.md complete |
| Service design documented | ✅ Verified | Implementation plan complete |
| No code changes in B2.3A | ✅ Verified | Documentation only phase |
| No migrations in B2.3A | ✅ Verified | Documentation only phase |
| Ownership verified | ✅ Verified | All searchable models are Django-owned `managed=True` |

---

## 12 — References

- `RP/docs/adr/ADR-001-CONTENT-MANAGEMENT-ARCHITECTURE.md` (§93-112)
- `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md` (§12)
- `RP/docs/B1_MODEL_OWNERSHIP_MATRIX.md`
- `RP/docs/B2_DATABASE_IMPLEMENTATION_PLAN.md`
- `RP/docs/B2_2_FINAL_SIGNOFF.md`
- `backend/apps/content/search_service.py`
- `backend/apps/content/workflow.py`
- `backend/apps/content/models.py`
- `backend/apps/events/models.py`
- `backend/apps/prayer/models.py`

---

*End of B2.3A Implementation Plan*