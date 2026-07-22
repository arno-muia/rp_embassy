# B2.3 — PostgreSQL Full Text Search Architecture Validation

**Phase:** B2.3 — PostgreSQL Full Text Search Foundation  
**Date:** 2026-07-21  
**Status:** In Progress  
**Governed By:** ADR-001, BACKEND_CONTENT_MANAGEMENT_DESIGN, B1_MODEL_OWNERSHIP_MATRIX

---

## 1 — Search Architecture Overview

### 1.1 PostgreSQL Full Text Search Components

Per ADR-001 section 93-112 and BACKEND_CONTENT_MANAGEMENT_DESIGN section 12, the following components are used:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `SearchVector` | Computed field for full-text indexing | Django `django.contrib.postgres.search.SearchVector` |
| `SearchQuery` | Query parser for search terms | Django `django.contrib.postgres.search.SearchQuery` |
| `SearchRank` | Relevance ranking | Django `django.contrib.postgres.search.SearchRank` |
| `GIN Index` | Fast lookup for tsvector columns | PostgreSQL GIN index on generated search vectors |

### 1.2 Explicit Exclusions

Per ADR-001 section 109-111, the following are explicitly NOT implemented:

| Service | Reason for Exclusion |
|---------|---------------------|
| Elasticsearch | Unnecessary operational complexity |
| OpenSearch | Unnecessary operational complexity |
| Meilisearch | Unnecessary operational complexity |
| Algolia | External dependency / cost |

**Justification:** PostgreSQL FTS is sufficient for the expected content volume and avoids maintaining a separate search service.

---

## 2 — Model Evaluation Matrix

### 2.1 Target Models (Task Specification)

| Model | App | Owner | Managed | Included? | Rationale |
|-------|-----|-------|---------|-----------|-----------|
| ContentBlock | content | Django | True | ✅ | Content searchable fields (title, content) |
| Announcement | events | Django | True | ✅ | Title and body are searchable |
| ChurchProfile | content | Django | True | ✅ | Mission, vision, welcome searchable |
| HomepageSettings | content | Django | True | ❌ | Not content-searchable (UI config only) |
| GlobalSettings | content | Django | True | ❌ | Operational settings, not content |
| PrayerRequest | prayer | Django | True | ✅ | Title and content searchable for moderation |

### 2.2 Prisma-Owned Models (Reference Only)

Per ADR-001 section 105-108, search applies to these models. However, since they are `managed = False`, GIN indexes must be added via Prisma migrations:

| Model | Owner | Managed | Search Fields | Status |
|-------|-------|---------|---------------|--------|
| PublicSermon | Prisma | False | title, description, speaker, scripture, transcript | ⚠️ Requires Prisma migration for GIN index |
| SermonSeries | Prisma | False | title, description | ⚠️ Requires Prisma migration for GIN index |
| ChurchEvent | Prisma | False | title, description, location | ⚠️ Requires Prisma migration for GIN index |

**Note:** B2.3 implements search for Django-owned models only. Prisma-owned models require coordinated Prisma migrations.

---

## 3 — Searchable Fields and Weighting

### 3.1 Weighting Strategy

Per ADR-001 section 100-101, weighted search uses:

| Weight | Field Type | Examples |
|--------|------------|----------|
| A | Titles, Names | sermon.title, series.title, leader.name |
| B | Summaries | sermon.description, announcement.title |
| C | Body content | sermon.notes, content_block.content, prayer_request.content |

### 3.2 ContentBlock

| Field | Weight | Searchable | Notes |
|-------|--------|------------|-------|
| key | - | ❌ | Identifier, not content |
| title | A | ✅ | Primary title |
| content | C | ✅ | Body content |
| content_type | - | ❌ | Filter field, not full-text |

### 3.3 Announcement

| Field | Weight | Searchable | Notes |
|-------|--------|------------|-------|
| title | A | ✅ | Primary title |
| body | C | ✅ | Announcement message body |
| severity | - | ❌ | Enum filter |
| workflow_status | - | ❌ | Workflow field |

### 3.4 ChurchProfile

| Field | Weight | Searchable | Notes |
|-------|--------|------------|-------|
| mission | C | ✅ | Church mission statement |
| vision | C | ✅ | Church vision statement |
| welcome_message | C | ✅ | Welcome text |
| pastor_message | C | ✅ | Pastor message |
| about_text | C | ✅ | About section |

### 3.5 PrayerRequest

| Field | Weight | Searchable | Notes |
|-------|--------|------------|-------|
| title | A | ✅ | Prayer request title/summary |
| content | C | ✅ | Full prayer request text |
| category | - | ❌ | Filter field |
| is_public | - | ❌ | Visibility filter |

---

## 4 — Ranking Strategy

### 4.1 Rank Formula

```python
SearchRank(
    vector=SearchVector(...),
    ranking=ts_rank_cd,  # Cover Density ranking
    normalization=20      # Rank + 1 for positive values
)
```

### 4.2 Weight Normalization

Per PostgreSQL documentation, weights are normalized to 4 decimal places:

| Weight | Normalization Factor |
|--------|---------------------|
| A | 1.0 |
| B | 0.4 |
| C | 0.1 |

This ensures titles rank higher than body content while maintaining relevance.

---

## 5 — Indexing Strategy

### 5.1 GIN Indexes

GIN indexes are created on computed `tsvector` columns. Two approaches:

| Approach | Pros | Cons |
|----------|------|------|
| Expression Index | No schema changes, always current | Computed on every query |
| Materialized Column | Faster queries | Requires triggers for updates |

**Decision:** Use expression indexes for simplicity. GIN indexes on `(title, content)` expressions.

### 5.2 Django Implementation

For `managed = True` models, GIN indexes are added via Django migrations using `SearchVectorField` or expression indexes.

---

## 6 — Search Service API

### 6.1 Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `build_search_vector()` | `(model, fields, weights)` | Construct SearchVector for model |
| `build_search_query()` | `(query_string)` | Construct SearchQuery |
| `execute_search()` | `(queryset, vector, query)` | Apply search with ranking |
| `rank_results()` | `(queryset, vector, query)` | Order by relevance |
| `paginate_results()` | `(queryset, page, page_size)` | Paginate results |

### 6.2 Future Expansion

The search service is designed to expand to include:
- Multi-model search
- Search filters by type/category
- Search result deduplication
- Highlight matching terms

---

## 7 — Ownership Compliance

| Check | Status |
|-------|--------|
| Prisma remains authoritative for Prisma-owned models | ✅ |
| Django remains authoritative for Django-owned models | ✅ |
| No ownership conversions performed | ✅ |
| No destructive schema changes | ✅ |

---

*End of B2.3 Search Architecture Validation*