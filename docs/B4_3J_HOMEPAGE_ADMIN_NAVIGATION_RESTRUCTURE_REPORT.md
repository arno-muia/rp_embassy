# B4.3J — Homepage Admin Navigation Restructure Report

## 1. Previous Admin Structure

Before this phase, the Django admin sidebar was organized by application (developer-oriented):

```
Public Website Content          ← backend.apps.content
├── Global Settings
├── Homepage Settings
├── Church Profile
├── Content Blocks
├── Service Times
├── Homepage Sections
├── System Config
├── Sermon Series
├── Public Sermons
├── Website Leaders
├── Website Testimonials
├── Website Academy Modules
├── Contact Submissions
├── Pastor Profiles
├── Visit RSVPs

Events & Calendar               ← backend.apps.events
├── Church Events
├── Event Registrations
├── Announcements

Prayer Requests                 ← backend.apps.prayer
├── Prayer Requests
├── Prayer Submissions

Media Assets                    ← backend.apps.media
├── Media Assets
```

**Problem:** Homepage-related content was scattered across multiple sections. A content editor had to navigate through developer-oriented app groupings to find homepage settings.

---

## 2. New Admin Structure

After this phase, the admin sidebar presents a dedicated **Homepage** section at the top:

```
Homepage                        ← synthetic group (presentation only)
├── Hero Settings
├── Homepage Sections
├── Church Profile
├── Pastor Profile
├── Service Times
├── Homepage Events
├── Homepage Sermons
├── Homepage Testimonials

Public Website Content          ← remaining content models
├── Global Settings
├── Content Blocks
├── System Config
├── Website Leaders
├── Website Academy Modules
├── Contact Submissions
├── Visit RSVPs

Events & Calendar               ← remaining event models
├── Event Registrations
├── Announcements

Prayer Requests                 ← unchanged
├── Prayer Requests
├── Prayer Submissions

Media Assets                    ← unchanged
├── Media Assets
```

---

## 3. Homepage Models Grouped

| Display Name | Model | Original App | Original Label |
|---|---|---|---|
| Hero Settings | `HomepageSettings` | content | Homepage Settings |
| Homepage Sections | `HomepageSection` | content | Homepage Sections |
| Church Profile | `ChurchProfile` | content | Church Profile |
| Pastor Profile | `PastorProfile` | content | Pastor Profiles |
| Service Times | `ServiceTime` | content | Service Times |
| Homepage Events | `ChurchEvent` | events | Church Events |
| Homepage Sermons | `PublicSermon`, `SermonSeries` | content | Public Sermons, Sermon Series |
| Homepage Testimonials | `WebsiteTestimonial` | content | Website Testimonials |

---

## 4. Files Modified

| File | Change |
|---|---|
| `backend/backend/apps/content/admin.py` | Added `HomepageAwareAdminSite` class that overrides `get_app_list()` to inject a synthetic "Homepage" section at the top of admin navigation. Replaced `admin.site.__class__` with the custom class. Added editor-friendly labels and descriptions for each homepage group. |
| `backend/backend/settings.py` | Added `BASE_DIR / 'templates'` to `TEMPLATES[0]['DIRS']` to enable custom admin template overrides. |
| `backend/templates/admin/index.html` | Created custom admin index template that extends the default. When `homepage_dashboard` context variable is set, renders a visual dashboard card with quick-link cards to all homepage content sections. |

---

## 5. Validation Results

```
$ python manage.py check
System check identified no issues (0 silenced).
```

- **No admin registration conflicts** — all models remain registered with the default `admin.site`.
- **No duplicate model registration** — each model appears once in the registry.
- **No URL conflicts** — URL configuration unchanged (`admin/` still points to `admin.site.urls`).
- **No import errors** — all imports resolve correctly.
- **No database migrations created** — this is a presentation-layer change only.

---

## 6. Screenshots / Notes

**How it works:**

The `HomepageAwareAdminSite` class extends Django's `AdminSite` and overrides the `get_app_list()` method. This method:

1. Calls the parent `get_app_list()` to get the default app grouping.
2. Builds a lookup dictionary mapping `(app_label, model_name)` → model dict.
3. Iterates through the `HOMEPAGE_GROUP` configuration to build a synthetic "Homepage" app section with editor-friendly names and descriptions.
4. Filters out homepage models from their original app groups.
5. Returns the homepage section first, followed by remaining apps.

**Key design decisions:**

- **No database changes** — models stay in their original apps and tables.
- **No model modifications** — `verbose_name`, `Meta`, and `db_table` are untouched.
- **No URL changes** — the admin still lives at `/admin/`.
- **All existing registrations preserved** — every model remains registered with `admin.site`.
- **Editor-friendly labels** — e.g., `WebsiteTestimonial` → "Homepage Testimonials", `ChurchEvent` → "Homepage Events".
- **Section descriptions** — each homepage group has a clear description explaining its purpose.
- **Homepage dashboard** — the admin index page shows a visual dashboard with quick-link cards to all homepage content sections.

---

## 7. Remaining Work Before Jazzmin

| Item | Status |
|---|---|
| Homepage appears as dedicated admin navigation section | ✅ Complete |
| Homepage-related content grouped together | ✅ Complete |
| Labels are editor-friendly | ✅ Complete |
| No database migrations created | ✅ Complete |
| Admin validation passes | ✅ Complete |
| Report created | ✅ Complete |
| Install Jazzmin (B4.3K) | ⏸️ **STOP — do not proceed** |