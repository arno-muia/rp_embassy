# MEMORY.md — Persistent Project Memory

---

## Project State

Current architecture:
- Astro frontend
- Django backend
- PostgreSQL database
- CMS-driven church website
- Migrated from previous rpwebsite implementation

---

## Completed Work

### B4.2.7 — ServiceTime Source of Truth Migration

**Summary:**
Homepage and visit pages now consume serviceTimes from `/api/homepage`.

---

### B4.2.8 — ServiceTime CMS Migration

**Summary:**
ServiceTime expanded with:
- name
- platform
- location
- link
- description
- image
- is_published

**Removed:**
- frontend fallback source-of-truth behavior
- name matching reconstruction

**Result:**
Admin → ServiceTime → API → UI

---

### B4.2.9 — SystemConfig Admin Repair

**Summary:**
User.password_hash mapped to:
- db_column="passwordHash"

Admin crash resolved.

---

## Known Architecture Decisions

- ServiceTime ordering controlled by `display_order`.
- Homepage API is preferred for homepage content.
- CMS-first architecture.
- Avoid SystemConfig when dedicated models already exist.

---

## Current Phase

**B4.3 — Homepage CMS Completeness Migration**

**Pending items:**
- Pastor section CMS
- Hero image CMS integration
- CTA CMS migration
- Section heading CMS migration
- Hardcoded URL migration

---

## Future Rule

Whenever a new phase completes:
- append summary to this file