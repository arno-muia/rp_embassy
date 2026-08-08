# B4.3 Preparation Report

## Date

2026-07-25

## Phase

B4.3 — Homepage CMS Completeness Migration (Preparation)

## Objective

Create project-level AI context files to prevent repeated rediscovery of architecture, completed migrations, and known constraints.

---

## Files Created

- `RP/AI_RULES.md`
- `RP/MEMORY.md`

---

## Contents Summary

### AI_RULES.md

Mandatory execution rules for future AI-assisted development:

- Project overview (Astro, Django, PostgreSQL, CMS-driven, migrated)
- Mandatory startup procedure (read MEMORY.md, read docs, inspect code, verify source of truth, search prior migrations)
- Architectural rules (source-of-truth models, API preference, CMS-first)
- Migration rules (don't recreate, audit first, preserve parity)
- Validation rules (`npm run check`, `npm run build`, Django checks)
- Reporting rules (per-phase `docs/<PHASE>_REPORT.md`)
- Forbidden actions (no duplicate sources of truth, no bypass, no unsafe deletion)

### MEMORY.md

Persistent project memory:

- Current architecture state
- Completed migrations (B4.2.7, B4.2.8, B4.2.9)
- Known architecture decisions
- Current phase (B4.3) with pending items
- Future rule for appending completed summaries

---

## Validation Results

- `RP/AI_RULES.md` exists.
- `RP/MEMORY.md` exists.
- Both files are valid Markdown.
- No application code was modified in this phase.

---

## Remaining Issues

None. Preparation complete. Proceed with B4.3 migration tasks.