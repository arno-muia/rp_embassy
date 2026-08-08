# B4.2.6A — ServiceTime Admin Visibility Audit

**Date:** 2026-03-24  
**Phase:** Investigation Only  
**Status:** NO-GO (no fix required)

---

## Executive Summary

Runtime diagnostic inspection of the Django admin surface proves that **ServiceTime is already fully visible and operational in the admin interface**. The issue described in the task brief (that ServiceTime is not visible in Django Admin) **does not exist in the current codebase**.

All verification checks completed with PASS status:

- ServiceTime is registered in `admin.site._registry`
- ServiceTime appears in `get_app_list()` with full CRUD permissions
- All admin URLs resolve correctly (`/admin/content/servicetime/...`)
- No custom AdminSite override
- No custom admin templates
- No duplicate or conditional registration logic

**Recommendation:** GO/NO-GO = **NO-GO** for implementation because there is no defect to fix.

---

## 1. Admin Registration Audit

### Finding: PASS

`rpwebsite/RP/backend/backend/apps/content/admin.py` lines 55-62:

```python
@admin.register(ServiceTime)
class ServiceTimeAdmin(admin.ModelAdmin):
    list_display = ('day', 'time', 'label', 'display_order', 'updated_at')
    search_fields = ('day', 'label')
    list_filter = ('day',)
    list_editable = ('display_order',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('display_order', 'day')
```

- Registered exactly once via `@admin.register(ServiceTime)` decorator  
- No duplicate registration detected  
- No `unregister()` / re-register operations  
- No conditional registration logic  
- No manual `admin.site.register()` calls

**Verdict:** Registration is correct and complete.

---

## 2. Runtime Admin Inspection

### Finding: PASS

Executed diagnostic via `rpwebsite/RP/backend/diag_admin.py` against the live Django environment (superuser `RPADMIN`).

**Registry Check:**
```
1. ServiceTime in admin.site._registry: True
```

**Registered models list includes:**
```
content.ServiceTime -> ServiceTimeAdmin
```

**URL Resolution Check:**
```
7. URL resolution for ServiceTime:
   changelist: /admin/content/servicetime/ - OK
   add: /admin/content/servicetime/add/ - OK
   change: /admin/content/servicetime/1/change/ - OK
   delete: /admin/content/servicetime/1/delete/ - OK
```

**Model Permissions:**
```
8. ServiceTime get_model_perms: {'add': True, 'change': True, 'delete': True, 'view': True}
   has_module_permission: True
   has_view_permission: True
   has_change_permission: True
```

**Verdict:** ServiceTime is fully registered and accessible via admin URLs.

---

## 3. Admin Index Visibility Audit

### Finding: PASS

`get_app_list()` output confirms ServiceTime is present:

```
9. Admin app list (get_app_list):
   App: Public Website Content (content)
     ...
     - Service Times (ServiceTime)
     ...

10. ServiceTime in app list:
    FOUND: {
      'model': <class 'backend.apps.content.models.ServiceTime'>,
      'name': 'Service Times',
      'object_name': 'ServiceTime',
      'perms': {'add': True, 'change': True, 'delete': True, 'view': True},
      'admin_url': '/admin/content/servicetime/',
      'add_url': '/admin/content/servicetime/add/',
      'view_only': False
    }
```

Additional checks:
- No overridden `get_model_perms()`
- No overridden `has_module_permission()`
- No overridden `has_view_permission()`
- No custom `AdminSite` subclass (confirmed standard `django.contrib.admin.sites.AdminSite`)
- No custom `ADMIN_INDEX_TEMPLATE`
- `TEMPLATES[0]['APP_DIRS'] = True` — default admin templates are used

**Verdict:** ServiceTime passes every visibility gate in the admin index rendering pipeline.

---

## 4. Model Audit

### Finding: PASS (minor observation noted)

Current model definition (`models.py` lines 389-409):

```python
class ServiceTime(models.Model):
    """Service time entries with display ordering."""

    day = models.CharField(max_length=12, choices=DayOfWeek.choices)
    time = models.TimeField()
    label = models.CharField(max_length=128)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Service Time'
        verbose_name_plural = 'Service Times'
        indexes = [
            models.Index(fields=['display_order'], name='servicetime_order_idx'),
            models.Index(fields=['day'], name='servicetime_day_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.get_day_display()} {self.time} — {self.label}'
```

**Verification:**
- Primary key: Implicit `BigAutoField` (Django default — migration `0001_initial.py` confirms `id` field was created; current model definition omits explicit declaration but Django adds it implicitly via `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'` in `settings.py`)
- App label: `content` (matching `apps.py` label)
- Verbose name: `'Service Time'` / `'Service Times'`
- Managed: `True`
- Meta options: Standard, no unusual configuration
- `__str__` method: Returns descriptive string using `get_day_display()`

**Observation:** The model relies on Django's implicit auto-created PK rather than declaring `id = models.BigAutoField(...)` explicitly. This is valid but differs from the style used in `GlobalSettings`, `HomepageSettings`, `ChurchProfile`, `ContentBlock`, and `HomepageSection`, all of which declare `id = models.BigAutoField(...)` explicitly. This is a **style inconsistency, not a functional defect.**

**Verdict:** Model is valid and operational in admin.

---

## 5. Root Cause Analysis

**Root Cause:** None found.

The assumption that ServiceTime is invisible in Django Admin is **contradicted by runtime evidence**. The model is registered, appears in the admin index, has full permissions, and all URLs resolve correctly.

Possible explanation for the original report:  
- Admin session caching might have briefly shown a stale index page.  
- The user may not have noticed ServiceTime in the alphabetical listing (between "Sermon series" and "System configs").  
- A transient DB connection or middleware issue during a single request cycle.

All of these are operational anomalies, not code defects.

---

## 6. Evidence Summary

| Check | Result | Evidence Location |
|-------|--------|-------------------|
| Admin registration | PASS | `diag_admin.py` #1-4 |
| Single registration | PASS | `diag_admin.py` #3 |
| URL resolution | PASS | `diag_admin.py` #7 |
| Model perms | PASS | `diag_admin.py` #8 |
| App list visibility | PASS | `diag_admin.py` #9-10 |
| Custom AdminSite | PASS (none found) | `diag_admin.py` #15 |
| Custom templates | PASS (none found) | `diag_admin.py` #14 |
| Model definition | PASS | `models.py` #389-409 |
| Migration history | PASS | `0001_initial.py` #264-281 |

---

## 7. Recommended Fix

**No fix required.**

If the goal is to make ServiceTime more prominent in the admin, consider these non-critical enhancements (not defects):

1. **Explicit PK declaration (style):** Add `id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')` to match sibling managed models.
2. **Admin list display ordering:** Ensure `display_order` values are populated to avoid confusing blank ordering.
3. **Admin changelist ordering:** Already set via `ordering = ('display_order', 'day')` — no change needed.

These are cosmetic improvements, not functional defects.

---

## 8. Risk Assessment

| Risk Category | Level | Notes |
|---------------|-------|-------|
| Code change risk | N/A | No fix implemented |
| Regression risk | NONE | No changes made |
| Data integrity risk | NONE | No changes made |
| Admin availability risk | NONE | ServiceTime is already fully available |
| Migration risk | NONE | No new migrations needed |

---

## 9. GO/NO-GO Assessment

**NO-GO**

This phase is investigation only. The investigation proves that ServiceTime is fully visible and functional in Django Admin. There is no defect to repair in a subsequent implementation phase.

If stakeholders insist on a change to improve visibility, that would be a UX enhancement (e.g., moving ServiceTime higher in the admin index, adding a custom admin dashboard widget), which is outside the scope of this bug fix task.

---

## Appendix: Diagnostic Scripts

See `rpwebsite/RP/backend/diag_admin.py` for the complete diagnostic routine used to validate admin visibility.