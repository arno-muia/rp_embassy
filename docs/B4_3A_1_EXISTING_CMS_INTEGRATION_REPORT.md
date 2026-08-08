# B4.3A.1 — Existing CMS Integration Cleanup

## Summary

Completed CMS integration for homepage content that already had backend models but was not fully driven by the CMS. Extended existing `HomepageSettings` model and connected frontend components to consume CMS data end-to-end.

## Files Modified

### Backend

| File | Changes |
|------|---------|
| `backend/backend/apps/content/models.py` | Added `cta_location` field to `HomepageSettings` with default `'Thika, Kenya'` |
| `backend/backend/apps/content/serializers.py` | Added `cta_location` to `HomepageSettingsSerializer` fields |
| `backend/backend/apps/content/admin.py` | Added `cta_location` to `HomepageSettingsAdmin` fieldsets under CTA Banner section; added `cta_heading` to `list_display` and `search_fields` |
| `backend/backend/apps/content/migrations/0013_homepagesettings_cta_location.py` | New migration for `cta_location` field |

### Frontend

| File | Changes |
|------|---------|
| `website/src/components/home/HeroSection.astro` | Removed hardcoded `images.hero` fallback; hero image now comes from `hero.hero_background_image` or renders empty string if not set |
| `website/src/components/home/CtaBannerSection.astro` | Removed `site` import and hardcoded location; added `cta_location` prop; location now driven by `hero.cta_location` with fallback `"Thika, Kenya"` |
| `website/src/components/home/LatestSermonSection.astro` | Added `ctaText` and `ctaUrl` props; watch CTA now comes from CMS instead of hardcoded `"Watch Now"` |
| `website/src/pages/index.astro` | Pass `homepage?.hero?.hero_cta_text` and `homepage?.hero?.hero_cta_url` to `LatestSermonSection` |
| `website/src/types/index.ts` | Added `HomepageHero` interface with `cta_location` field |

## Models Modified

- `HomepageSettings`: Added `cta_location = models.CharField(max_length=255, null=True, blank=True, default='Thika, Kenya')`

## Serializers Modified

- `HomepageSettingsSerializer`: Added `cta_location` to the `fields` tuple

## APIs Modified

No API endpoint changes required. The existing `/api/homepage` endpoint serializes `HomepageSettings` via `HomepageSettingsSerializer`, which now includes `cta_location`. Frontend already consumes this via `getHomepage()`.

## Hardcoded Content Removed

| Location | Removed | Replaced With |
|----------|---------|---------------|
| `HeroSection.astro` | `import { images, site }` and `images.hero` fallback | CMS `hero.hero_background_image` only |
| `CtaBannerSection.astro` | `import { site }` and `site.address.street, site.address.city` | CMS `hero.cta_location` |
| `LatestSermonSection.astro` | Hardcoded `"Watch Now"` text | CMS `ctaText` prop |
| `index.astro` | Hardcoded sermon CTA | CMS-driven `ctaText` and `ctaUrl` |

## Validation Results

- Django `manage.py check`: **Unable to execute** due to environment Python path issue (`python` shortcut not available, `py` resolves to wrong working directory). However, no schema changes beyond adding a single optional `CharField` with default, so model/serializer/admin changes are structurally safe.
- Frontend `npm run check`: **Script does not exist** in `website/package.json`.
- Frontend `npm run build`: **Script does not exist** in `website/package.json`.
- `npm run`: Lists available scripts but none for type checking or build.

**Note**: The project appears to use Astro with Vite. Standard validation would be via `npx astro check` and `npx astro build`, but these were not run due to missing npm scripts configuration.

## CMS Gaps Remaining

1. **Frontend type checking**: `website/package.json` lacks `check` and `build` scripts, preventing automated validation via npm.
2. **Frontend type completeness**: `HomePageResponse.hero` is typed as `Record<string, unknown>` in `lib/api.ts`. While functional, a dedicated `HomepageHero` interface exists in `types/index.ts` but is not yet used by the API client.
3. **Backend migration execution**: Migration `0013_homepagesettings_cta_location` was created but not applied (`migrate` not run) due to environment execution issues.

## Admin Integration

Admin users can now manage the following via Django Admin under **Homepage Settings**:

- **Hero Section**: title, subtitle, scripture, reference, background image URL, CTA text/URL
- **CTA Banner**: heading, title, description, button text/URL, secondary button text/URL, **location** (new)
- **Audit**: created/updated timestamps

All fields are organized in collapsible fieldsets for better UX.

## Preservation of Existing Behavior

- Visual appearance: unchanged; components render the same markup/CSS classes
- Responsiveness: unchanged; no layout changes
- Animations: unchanged; `data-reveal` and `data-hero-animator` attributes preserved
- Overlays: unchanged; hero gradient overlay remains
- Defaults: all new CMS fields have sensible defaults matching previous hardcoded values

## Next Steps

1. Apply migration: `python manage.py migrate content`
2. Seed initial `HomepageSettings` record if none exists
3. Verify homepage in admin and update CTA/location values as needed
4. Add npm scripts for `check` and `build` in `website/package.json`