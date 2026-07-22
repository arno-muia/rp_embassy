# B2.2 Schema Drift Audit

**Phase:** B2.2 — Schema Drift Resolution  
**Date:** 2026-07-20  
**Status:** Complete  
**Related:** `RP/docs/B1_MODEL_OWNERSHIP_MATRIX.md`, `RP/apps/web/prisma/schema.prisma`

---

## Executive Summary

A full schema drift audit was conducted across all 8 Prisma-owned models. **One critical mismatch** was identified in the `WebsiteLeader` Django model. The database schema and Prisma schema are in agreement; the drift exists solely in the Django model definition.

### Drift Summary

| Model | Django Fields | DB Columns | Prisma Fields | Mismatches | Severity |
|-------|---------------|------------|---------------|------------|----------|
| SystemConfig | 6 | 6 | 6 | 0 | — |
| SermonSeries | 9 | 9 | 9 | 0 | — |
| PublicSermon | 17 | 17 | 17 | 0 | — |
| **WebsiteLeader** | **10** | **9** | **9** | **1** | **CRITICAL** |
| WebsiteTestimonial | 10 | 10 | 10 | 0 | — |
| WebsiteAcademyModule | 9 | 9 | 9 | 0 | — |
| ContactSubmission | 5 | 5 | 5 | 0 | — |
| VisitRsvp | 9 | 9 | 9 | 0 | — |

---

## Detailed Mismatch Report

### 1. WebsiteLeader — Extra Django Field

| Attribute | Value |
|-----------|-------|
| **Model** | `WebsiteLeader` |
| **Django field** | `is_archived = models.BooleanField(default=False, db_column='isArchived')` |
| **Database column** | `isArchived` — **DOES NOT EXIST** |
| **Prisma column** | `isPublished` only (no `isArchived`) |
| **Severity** | **CRITICAL** |
| **Affected endpoint** | `GET /api/leaders/` (`LeaderViewSet`) |
| **Error pattern** | `psycopg2.errors.UndefinedColumn: column WebsiteLeader.isArchived does not exist` |
| **Evidence** | PostgreSQL column inspection confirms `WebsiteLeader` contains: `id`, `name`, `role`, `bio`, `photoUrl`, `sortOrder`, `social`, `isPublished`, `createdAt`, `updatedAt` — no `isArchived` |

### Root Cause

The Django `WebsiteLeader` model contains a field from an earlier design iteration (`is_archived`) that was never reflected in the Prisma schema or database migration. Because `managed = False`, Django does not own the table schema, yet the model still declares the field, causing runtime query failures when Django ORM attempts to SELECT the non-existent column.

---

## Source of Truth Determination

Per `RP/docs/B1_MODEL_OWNERSHIP_MATRIX.md`:

- **Ownership:** Prisma Owned (`managed = False`)
- **Source of Truth:** Prisma schema + seed
- **Migration Strategy:** Prisma migrations only

**Conclusion:** The Prisma schema is authoritative. The Django model must be trimmed to match the Prisma schema and database exactly. No Django migration should be created. No ownership conversion is authorized.

---

## Audit Methodology

1. **Django model fields** extracted from `RP/backend/backend/apps/content/models.py`
2. **Prisma schema fields** extracted from `RP/apps/web/prisma/schema.prisma`
3. **Database columns** verified via direct PostgreSQL query against `information_schema.columns` for all 8 legacy tables
4. **API endpoints** traced from `RP/backend/backend/apps/content/urls.py`