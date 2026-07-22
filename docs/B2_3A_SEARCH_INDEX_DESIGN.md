# B2.3A — Search Index Design

**Phase:** B2.3A — Architecture Validation & Readiness Review  
**Date:** 2026-07-21  
**Status:** Design Complete (No Implementation)  
**Depends On:** B2_3A_SEARCH_ARCHITECTURE_VALIDATION.md

---

## 1 — SearchVector Usage

### 1.1 Design Overview

PostgreSQL Full Text Search uses `tsvector` (text search vector) to represent documents for search. Django's `SearchVector` class creates these vectors dynamically.

**Decision:** Use expression-based `SearchVector` computed at query time rather than materialized columns.

**Rationale:** Expression vectors simplify implementation and ensure data consistency. No trigger maintenance required.

### 1.2 Per-Model SearchVector Definitions

#### ContentBlock
```
SearchVector('title', weight='A') 
+ SearchVector('content', weight='C')
```

**Search Fields:** `title` (A), `content` (C)  
**Excluded Fields:** `key`, `content_type`, `display_order`, `is_active`, `is_rich_text`, timestamps

**Justification:** Title is the primary identifier; content contains the searchable body text. Category and status fields are filters, not full-text search terms.

#### Announcement
```
SearchVector('title', weight='A') 
+ SearchVector('body', weight='C')
```

**Search Fields:** `title` (A), `body` (C)  
**Excluded Fields:** `severity`, `workflow_status`, `display_from`, `display_until`, `link_url`, `is_active`, `priority`, timestamps

**Justification:** Title/body are editorial content presented to users. Severity, dates, and active flags control visibility and ordering, not search relevance.

#### ChurchProfile
```
SearchVector('mission', weight='C') 
+ SearchVector('vision', weight='C') 
+ SearchVector('welcome_message', weight='C') 
+ SearchVector('pastor_message', weight='C') 
+ SearchVector('about_text', weight='C')
```

**Search Fields:** All text fields at weight C  
**Excluded Fields:** timestamps

**Justification:** ChurchProfile is a singleton with no title field. All text fields contribute equally to search as they represent church identity content.

#### PrayerRequest
```
SearchVector('title', weight='A') 
+ SearchVector('content', weight='C')
```

**Search Fields:** `title` (A), `content` (C)  
**Excluded Fields:** `category`, `is_public`, `is_anonymous`, `workflow_status`, `status`, `prayer_count`, timestamps

**Justification:** Title provides context for prayer requests; content contains the full request. Category and status fields are used for filtering by moderators/admins.

#### GlobalSettings & HomepageSettings
**Status:** NOT INDEXED

**Justification:** Operational settings and UI configuration are not searchable content. These are administrative data accessed via direct key lookup, not full-text search.

#### HomepageSection
**Status:** NOT INDEXED

**Justification:** `HomepageSection` provides feature toggles for visibility. It has no content fields—only `section_name`, `enabled`, and `display_order`.

---

## 2 — SearchQuery Usage

### 2.1 Query Types

| Type | Usage | Example |
|------|-------|---------|
| plain | Default, tokenizes input | `SearchQuery('faith')` |
| phrase | Exact phrase match | `SearchQuery('"faith like potatoes"', search_type='phrase')` |
| raw | PostgreSQL tsquery syntax | `SearchQuery('faith & hope', search_type='raw')` |

**Default:** `search_type='plain'` for standard user search

### 2.2 Search Query Normalization

Per PostgreSQL FTS behavior:
- Input is tokenized into lexemes
- Stop words (common words like "the", "and") are removed
- Stemming occurs for supported languages
- **Language:** Default 'simple' (English-compatible, no stemming)

---

## 3 — SearchRank Usage

### 3.1 Rank Calculation

```
SearchRank(
    vector=SearchVector(...),
    query=SearchQuery(...),
    ranking=ts_rank_cd,  # Cover Density algorithm
)
```

**Ranking Function:** `ts_rank_cd` (Cover Density)  
**Normalization:** 20 (1-based rank for positive values, no division)

### 3.2 Weight Influence on Rank

| Weight | Factor | Effect |
|--------|--------|--------|
| A | 1.0 | Title matches dominate score |
| C | 0.1 | Body content contributes minimally |
| B | 0.4 | Not currently used |
| D | 0.01 | Not currently used |

### 3.3 Rank Filtering

**Minimum Rank Threshold:** `rank__gt=0`  
Only documents with at least one matching term are returned.

---

## 4 — GIN Index Strategy

### 4.1 Index Approach

**Decision:** Expression GIN indexes

**Rationale:** 
- No schema changes required
- Always current with data
- Simpler than materialized column + triggers

**Alternative Considered:** Materialized `tsvector` column with triggers — Rejected to avoid trigger maintenance overhead.

### 4.2 Per-Model Index Designs

#### ContentBlock GIN Index
```sql
CREATE INDEX idx_contentblock_search 
ON content_contentblock 
USING GIN (
    (setweight(to_tsvector('simple', COALESCE(title, '')), 'A') 
    || setweight(to_tsvector('simple', COALESCE(content, '')), 'C'))
);
```

**Expected Migration:** `content/migrations/0002_gin_search_index.py`  
**Operation:** Add index only; no model changes.

#### Announcement GIN Index
```sql
CREATE INDEX idx_announcement_search 
ON events_announcement 
USING GIN (
    (setweight(to_tsvector('simple', COALESCE(title, '')), 'A') 
    || setweight(to_tsvector('simple', COALESCE(body, '')), 'C'))
);
```

**Expected Migration:** `events/migrations/0002_gin_search_index.py`  
**Operation:** Add index only; no model changes.

#### ChurchProfile GIN Index
```sql
CREATE INDEX idx_churchprofile_search 
ON content_churchprofile 
USING GIN (
    (setweight(to_tsvector('simple', COALESCE(mission, '')), 'C') 
    || setweight(to_tsvector('simple', COALESCE(vision, '')), 'C') 
    || setweight(to_tsvector('simple', COALESCE(welcome_message, '')), 'C') 
    || setweight(to_tsvector('simple', COALESCE(pastor_message, '')), 'C') 
    || setweight(to_tsvector('simple', COALESCE(about_text, '')), 'C'))
);
```

**Expected Migration:** `content/migrations/0002_gin_churchprofile_search.py`  
**Operation:** Add index only; no model changes.

#### PrayerRequest GIN Index
```sql
CREATE INDEX idx_prayerrequest_search 
ON prayer_prayerrequest 
USING GIN (
    (setweight(to_tsvector('simple', COALESCE(title, '')), 'A') 
    || setweight(to_tsvector('simple', COALESCE(content, '')), 'C'))
);
```

**Expected Migration:** `prayer/migrations/0002_gin_search_index.py`  
**Operation:** Add index only; no model changes.

---

## 5 — Expected Migrations

### 5.1 Migration Files (Not Created in B2.3A)

| File | App | Purpose | Status |
|------|-----|---------|--------|
| `content/migrations/0002_gin_contentblock_idx.py` | content | GIN index on ContentBlock | 📋 PLANNED |
| `content/migrations/0003_gin_churchprofile_idx.py` | content | GIN index on ChurchProfile | 📋 PLANNED |
| `events/migrations/0002_gin_announcement_idx.py` | events | GIN index on Announcement | 📋 PLANNED |
| `prayer/migrations/0002_gin_prayerrequest_idx.py` | prayer | GIN index on PrayerRequest | 📋 PLANNED |

### 5.2 Migration Constraints

**Critical Rule:** No migration may target `managed = False` models.

Per B1_MODEL_OWNERSHIP_MATRIX and B2_DATABASE_IMPLEMENTATION_PLAN:
- `PublicSermon`, `SermonSeries`, `ChurchEvent` are `managed = False`
- GIN indexes for these require Prisma migrations (future coordination)

---

## 6 — Expected Files to Change

### 6.1 Files Requiring Modification (B2.3B Implementation)

| File | Change Type | Purpose |
|------|-------------|---------|
| `backend/apps/content/models.py` | None | No changes required (search via annotation) |
| `backend/apps/events/models.py` | None | No changes required (search via annotation) |
| `backend/apps/prayer/models.py` | None | No changes required (search via annotation) |
| `backend/apps/content/search_service.py` | Enhancement | Add missing search methods (already present) |
| `content/migrations/0002_*.py` | New | GIN index for ContentBlock |
| `events/migrations/0002_*.py` | New | GIN index for Announcement |
| `prayer/migrations/0002_*.py` | New | GIN index for PrayerRequest |
| `content/migrations/0003_*.py` | New | GIN index for ChurchProfile |

### 6.2 Files NOT to Change

| File | Reason |
|------|--------|
| `backend/apps/content/models.py` (search fields) | Search happens via queryset annotation, not model field |
| `backend/apps/events/models.py` (search fields) | Search happens via queryset annotation, not model field |
| `backend/apps/prayer/models.py` (search fields) | Search happens via queryset annotation, not model field |
| Any migration targeting `managed = False` models | Must use Prisma migrations |

---

## 7 — Performance Considerations

### 7.1 Index Size Estimation

| Model | Estimated Rows | Index Size | Notes |
|-------|----------------|------------|-------|
| ContentBlock | 20-50 | ~10KB | Low volume; infrequent updates |
| Announcement | 10-100 | ~20KB | Time-bound; archived over time |
| ChurchProfile | 1 | ~1KB | Singleton; essentially static |
| PrayerRequest | 100-1000 | ~50KB | Growing; may benefit from index |

### 7.2 Query Performance

- GIN indexes provide O(log n) lookup for full-text queries
- Expression indexes computed at query time add minimal overhead
- Rank computation O(1) per matched row
- Pagination applied after ranking for consistent results

---

## 8 — Multi-Model Search Architecture

### 8.1 Current Unified Search

The existing `unified_search()` function in `search_service.py` provides:
- Optional inclusion flags per model type
- Separate result groups (not merged ranking)
- Basic pagination

### 8.2 Future Enhancement (B2.3B+)

| Feature | Current Status | Future Status |
|---------|---------------|---------------|
| Combined ranking | ❌ Not implemented | ⚠️ Possible |
| Result highlighting | ❌ Not implemented | ⚠️ Possible |
| Search result truncation | ❌ Not implemented | ⚠️ Possible |
| Search term highlighting | ❌ Not implemented | ⚠️ Possible |

---

## 9 — GIN Index Design Summary

| Model | Indexed Fields | Weight A | Weight B | Weight C | Weight D | Status |
|-------|---------------|----------|----------|----------|----------|--------|
| ContentBlock | title, content | ✅ title | ❌ | ✅ content | ❌ | ✅ Designed |
| Announcement | title, body | ✅ title | ❌ | ✅ body | ❌ | ✅ Designed |
| ChurchProfile | mission, vision, welcome_message, pastor_message, about_text | ❌ | ❌ | ✅ all | ❌ | ✅ Designed |
| PrayerRequest | title, content | ✅ title | ❌ | ✅ content | ❌ | ✅ Designed |
| GlobalSettings | None | ❌ | ❌ | ❌ | ❌ | ✅ Excluded |
| HomepageSettings | None | ❌ | ❌ | ❌ | ❌ | ✅ Excluded |
| HomepageSection | None | ❌ | ❌ | ❌ | ❌ | ✅ Excluded |

---

## 10 — References

- `RP/docs/B2_3A_SEARCH_ARCHITECTURE_VALIDATION.md`
- PostgreSQL Documentation: [Full Text Search](https://www.postgresql.org/docs/current/datatype-textsearch.html)
- Django Documentation: [PostgreSQL Full Text Search](https://docs.djangoproject.com/en/stable/ref/contrib/postgres/search/)
- `backend/apps/content/search_service.py`

---

*End of B2.3A Search Index Design*