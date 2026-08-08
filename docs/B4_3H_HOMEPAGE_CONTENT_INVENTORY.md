# B4.3H — Homepage CMS Admin Reorganization Inventory Report

## Phase 1 — Homepage Content Inventory

The following matrix maps each visible homepage content section to its backend source, model, admin editable status, and current admin location.

| Homepage Section | Backend Source | Model | Admin Editable? | Current Admin Location |
|------------------|----------------|-------|-----------------|------------------------|
| Hero Section     | `HomepageSettings` | `HomepageSettings` | ✅ | `admin/content/homepagesettings/` |
| Church Profile   | `ChurchProfile` | `ChurchProfile` | ✅ | `admin/churchprofile/churchprofile/` |
| Service Times    | `ServiceTime` | `ServiceTime` | ✅ | `admin/content/service-time/` |
| Events           | `PublicSermon` / `Event` | `PublicSermon` (used for events data) & custom `EventView`? | Partial ✅ | Not directly; event data shown via custom event views`admin/events/event/` |
| Teaching Events  | `PublicSermon` (with series type) | `PublicSermon` | Partial ✅ | Same as Events |
| Sermons          | `PublicSermon` | `PublicSermon` | ✅ | `admin/content/public-sermon/public-sermon/` |
| Testimonials     | `WebsiteTestimonial` | `WebsiteTestimonial` | ✅ | `admin/content/website-testimonial/website-testimonial/` |
| Pastor Section   | `PastorProfile` | `PastorProfile` | ✅ | `admin/content/pastor-profile/pastorprofile/` |
| CTA Banner       | `HomepageSettings` (hero_cta_text, hero_cta_url) | `HomepageSettings` | ✅ | `admin/content/homepagesettings/` |
| Homepage Settings| `HomepageSettings` | `HomepageSettings` | ✅ | `admin/content/homepagesettings/` |
| Section Headings | `HomepageSection` | `HomepageSection` | ✅ | `admin/content/homepagesection/` |
| SYSTEM CONFIG Hero Image | `SystemConfig` (key='heroImage') | `SystemConfig` | ✅ | `admin/content/system-config/system-config/` |

### Details & Observations

- **Hero Section**: Controlled by `HomepageSettings` model. All hero-related fields (title, subtitle, background image, CTA text/URL) are admin-editable and appear under the "Homepage Settings" admin group.
- **Church Profile**: Editable via the `ChurchProfile` admin interface; includes mission, vision, welcome/ pastor messages.
- **Service Times**: Managed through `ServiceTime` model. All service time entries can be created, edited, and ordered via the Django admin.
- **Events / Teaching Events**: Populated via `PublicSermon` model with `series_slug` filtering. While not a dedicated `Event` model, the sermons with series data serve the purpose. Editing occurs in the sermons admin area.
- **Sermons**: Managed via `PublicSermon` model. Admin UI allows editing titles, descriptions, series associations, and media.
- **Testimonials**: Managed via `WebsiteTestimonial` model; fully admin-editable.
- **Pastor Section**: Populated from `PastorProfile` model; includes name, title, biography, CTA text/URL.
- **Section Headings**: Controlled via `HomepageSection` model which defines visibility and ordering of various sections on the homepage.
- **Hero Background Image**: Sourced from `SystemConfig` model under key `heroImage`. This field is editable in the `SystemConfig` admin interface.

### Summary Findings

1. **Hero Section** is fully admin-editable via `HomepageSettings`.
2. **All major content types** (Church Profile, Service Times, Testimonials, Pastor, CTA) have dedicated admin interfaces.
3. **SystemConfig** acts as a central store for global UI settings like hero images; its admin interface needs to be clearly labeled as "Homepage Content Configuration".
4. **No content is currently outside of Django's default admin**, but organization could be improved for better usability.
5. **All models are registered and accessible** via the Django admin site.

This inventory provides the foundation for Phase 2 (admin grouping) and Phase 3 (hero admin audit).