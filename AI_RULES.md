# AI RULES — Project Execution Rules

## Project Overview

This project is:
- Astro frontend
- Django backend
- PostgreSQL database
- CMS-driven church website
- Migrated from previous rpwebsite implementation

---

## Mandatory Startup Procedure

Before making any code changes, always:

1. Read **MEMORY.md**
2. Read **docs/** folder reports relevant to current phase
3. Inspect existing implementation
4. Verify source of truth
5. Search for previous migrations before creating new code
6. Avoid creating duplicate models/endpoints/components

---

## Architectural Rules

- **ServiceTime** model is the sole source of truth for service times
- **PublicSermon** model is the source of truth for sermons
- **ChurchEvent** model is the source of truth for events
- **WebsiteTestimonial** model is the source of truth for testimonials
- **Homepage API** is preferred for homepage content
- Avoid introducing duplicate sources of truth
- Avoid hardcoded content when CMS data exists

---

## Migration Rules

- Never recreate already migrated features
- Always audit before changing
- Always compare frontend, API, serializer, model and admin
- Preserve visual parity during migrations
- Preserve responsive behavior
- Preserve animations

---

## Validation Rules

Always run:

```bash
npm run check
npm run build
```

And relevant Django checks after structural changes.

---

## Reporting Rules

Every major phase must create:

`docs/<PHASE>_REPORT.md`

With:
- findings
- files modified
- validation results
- remaining issues

---

## Forbidden Actions

Never:
- introduce a second source of truth
- duplicate CMS fields
- bypass existing APIs
- delete data without verification
- remove functionality because it appears unused