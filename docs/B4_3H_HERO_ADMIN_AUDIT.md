# B4.3H — Hero Admin Audit

## Objective
Audit the current administrative control over the Homepage Hero section to ensure all fields are properly CMS-managed.

## Audit Matrix

| Hero Field | Source Model | Admin Location | Editable? |
| :--- | :--- | :--- | :--- |
| **Title** | `HomepageSettings` | `admin/content/homepagesettings` | ✅ YES |
| **Subtitle** | `HomepageSettings` | `admin/content/homepagesettings` | ✅ YES |
| **Scripture** | `HomepageSettings` | `admin/content/homepagesettings` | ✅ YES |
| **Scripture Ref** | `HomepageSettings` | `admin/content/homepagesettings` | ✅ YES |
| **Background Image** | `HomepageSettings` | `admin/content/homepagesettings` | ✅ YES |
| **Primary CTA Label**| `HomepageSettings` | `admin/content/homepagesettings` | ✅ YES |
| **Primary CTA URL** | `HomepageSettings` | `admin/content/homepagesettings` | ✅ YES |
| **Secondary CTA Label**| `HomepageSettings` | *MISSING* | ❌ NO |
| **Secondary CTA URL** | `HomepageSettings` | *MISSING* | ❌ NO |

## Findings
1. All core Hero section content (Title, Subtitle, Scripture, Background Image, Primary CTA) is currently managed via `HomepageSettings` model, which is correctly exposed in the admin interface.
2. **Gap Identified**: The secondary CTA components (label and URL) are missing from the `HomepageSettings` admin fieldset and database structure, meaning they are likely hardcoded or not currently functional in the CMS.

## Recommendations
1. Update `HomepageSettings` model to include `secondary_cta_text` and `secondary_cta_url` fields.
2. Expose these new fields in `HomepageSettingsAdmin` fieldset under the "Hero Section" group.
3. Update API serializers and frontend `HeroSection.astro` to consume these fields.
4. Ensure all hero-related fields are treated as a single cohesive unit for content managers.

This audit confirms that while the primary Hero functionality is covered, the secondary CTA capacity is a clear gap that should be addressed to provide a complete hero management experience.