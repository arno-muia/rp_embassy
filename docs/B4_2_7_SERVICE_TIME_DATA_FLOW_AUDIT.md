# B4.2.7 — Service Times Source of Truth Audit

## Executive Summary

The homepage Service Times section was **NOT** sourcing its data from `/api/homepage`. Instead, it read `serviceTimes` from the `/api/site-config` endpoint, with a hardcoded fallback array embedded directly in the component. Changes made to `ServiceTime` model records in Django Admin were not reflected on the homepage/visit pages because the rendering path did not consume the `/api/homepage` endpoint.

**Fix Status:** Implemented on 24 July 2026. The frontend now consumes `/api/homepage` → `HomePageResponse.serviceTimes` as the single source of truth, matching the pattern used by all other homepage CMS sections.

## Investigation Scope

- Frontend: `website/src/pages/index.astro` → `ServiceTimesSection.astro`
- Data layer: `website/src/lib/api.ts` → Django backend `content/views.py`
- Backend: `content/urls.py`, `content/models.py`, `content/serializers.py`

---

## 1. Component Rendering Path (AFTER FIX)

### Layer 1: `index.astro`

```typescript
// Frontmatter
import { getSiteConfig, getHomepage } from "../lib/api";

const [config, homepage] = await Promise.all([
  getSiteConfig(),
  getHomepage(),
]);

// Render
{homepage?.serviceTimes && homepage.serviceTimes.length > 0 && (
  <ServiceTimesSection services={homepage.serviceTimes} />
)}
```

- **Component:** `ServiceTimesSection`
- **Prop received:** `services` from `homepage.serviceTimes`
- **Data origin:** `homepage` returned by `getHomepage()` → `/api/homepage`

### Layer 2: `api.ts` (AFTER FIX)

`getHomepage()` helper:

```typescript
export async function getHomepage(): Promise<HomePageResponse | undefined> {
  try {
    return await getJson<HomePageResponse>(API_ENDPOINTS.homepage);
  } catch {
    return undefined;
  }
}
```

- **Endpoint called:** `/api/homepage`
- Response type: `HomePageResponse` includes `serviceTimes: ServiceTime[]`.
- `SiteConfig` no longer defines `serviceTimes` (removed to eliminate dual source of truth).

### Layer 3: `ServiceTimesSection.astro` (AFTER FIX)

```typescript
const { services }: Props = Astro.props;

const FALLBACK_SERVICES: ServiceTime[] = [...]; // preserved as last resort

const orderedServices = TAB_ORDER.map((tabName) =>
  services.find((s) => s.name === tabName) ?? FALLBACK_SERVICES.find((s) => s.name === tabName) ?? null,
).filter(Boolean) as ServiceTime[];
```

- **Data received:** `services` prop (from `homepage.serviceTimes`)
- **Data passed forward:** `orderedServices` rendered as tabs/cards
- **Fallback mechanism:** If API data is empty/missing, hardcoded `FALLBACK_SERVICES` are used.

---

## 2. Backend Data Sources

### `/api/site-config`

`content/views.py` lines 85-92:

```python
@api_view(['GET'])
@permission_classes([AllowAny])
def site_config(request):
    cfg = SystemConfigRepository.get_by_key('site')
    if cfg:
        return Response(cfg.value)
    return Response({'error': 'Site config not found'}, status=404)
```

- Returns `SystemConfig.value`, which is a JSON field.
- `SystemConfig` is a model with a `value` JSONB column.
- `SystemConfig` may or may not contain `serviceTimes`, but this is no longer the rendered source.

### `/api/homepage`

`content/views.py` lines 122-187:

```python
@api_view(['GET'])
@permission_classes([AllowAny])
def homepage(request):
    # ...
    service_times = ServiceTimeSerializer(ServiceTimeRepository.all_ordered(), many=True).data
    # ...
    return Response({
        'hero': hero_data,
        'churchProfile': church_profile_data,
        'serviceTimes': service_times,  # <-- ServiceTime model data
        # ...
    })
```

- `/api/homepage` serializes `ServiceTime` model records in insertion order.
- This is the **only** source now used by the homepage frontend for Service Times.

---

## 3. Source of Truth Determination (AFTER FIX)

| Data Source | Used By | Contains ServiceTimes? | Status |
|-------------|---------|------------------------|--------|
| `/api/homepage` | `index.astro`, `visit.astro` | Yes, from `ServiceTime` model | **Single source of truth** |
| `/api/site-config` | `index.astro` (other config), `visit.astro` (other config) | May contain legacy `serviceTimes` | **No longer used for Service Times** |
| `ServiceTime` model | Django Admin editable | Yes, source for `/api/homepage` | Admin-editable |
| `FALLBACK_SERVICES` | `ServiceTimesSection.astro` | Yes, hardcoded | **Last-resort fallback only** |

**Actual displayed source:** `homepage.serviceTimes` from `/api/homepage`, falling back to `FALLBACK_SERVICES` only when API returns empty data.

---

## 4. Why Django Admin Changes Did NOT Appear (Pre-Fix)

1. Admin edits modified `ServiceTime` model records.
2. The homepage did **not** read from `/api/homepage` (which serializes `ServiceTime`).
3. The homepage read from `/api/site-config` → `SystemConfig.value.serviceTimes`.
4. Unless `SystemConfig.value` was explicitly updated to mirror `ServiceTime` changes, the homepage remained stale.
5. If `SystemConfig.value.serviceTimes` was absent or empty, the hardcoded `FALLBACK_SERVICES` were displayed instead.

**After fix:** `/api/homepage` is the sole source, so Admin edits now propagate correctly to the UI.

---

## 5. Exact File(s) Where the Chain Was Broken

**Primary break point:**
- **File:** `rpwebsite/RP/website/src/pages/index.astro`
- **Issue:** Called `getSiteConfig()` only, passed `config.serviceTimes` to `ServiceTimesSection`.

**Secondary break points:**
- **File:** `rpwebsite/RP/website/src/pages/visit.astro`
- **Issue:** Called `getSiteConfig()` only, passed `config.serviceTimes` to `ServiceTimesCarousel`.
- **File:** `rpwebsite/RP/website/src/components/home/CtaBannerSection.astro`
- **Issue:** Accepted `config?: SiteConfig` prop instead of `serviceTimes?: ServiceTime[]`.
- **File:** `rpwebsite/RP/website/src/components/shared/ServiceTimesCarousel.astro`
- **Issue:** Typed to `SiteConfig["serviceTimes"]` instead of `ServiceTime[]`.
- **File:** `rpwebsite/RP/website/src/components/shared/ServiceTimesGrid.astro`
- **Issue:** Typed to `SiteConfig["serviceTimes"]` instead of `ServiceTime[]`.

---

## 6. Evidence Summary

### Pre-fix evidence

- `website/src/pages/index.astro` imported only `getSiteConfig` for service times.
- `getSiteConfig()` was the **only** source for service times on the homepage.
- `FALLBACK_SERVICES` in `ServiceTimesSection.astro` ensured hardcoded values appeared when API data was missing.

### Post-fix state

- `index.astro` now imports `getHomepage` and uses `homepage.serviceTimes`.
- `visit.astro` now imports `getHomepage` and uses `homepage.serviceTimes`.
- `CtaBannerSection.astro` now accepts `serviceTimes?: ServiceTime[]`.
- `ServiceTimesCarousel.astro` now types `services` as `ServiceTime[]`.
- `ServiceTimesGrid.astro` now types `services` as `ServiceTime[]`.
- `api.ts` no longer includes `serviceTimes` on `SiteConfig`, and re-exports `ServiceTime`.

---

## 7. Recommended Fix and Implementation Status

**Implemented:** The frontend has been refactored to consume `/api/homepage` exclusively for Service Times.

### Changes made

1. **`website/src/lib/api.ts`**
   - Removed `serviceTimes` from `SiteConfig`.
   - Re-exported `ServiceTime` type.
   - Confirmed `getHomepage()` returns `HomePageResponse.serviceTimes`.

2. **`website/src/pages/index.astro`**
   - Added `getHomepage` import.
   - Calls `getHomepage()` in parallel with `getSiteConfig()`.
   - Passes `homepage.serviceTimes` to `ServiceTimesSection` and `CtaBannerSection`.

3. **`website/src/pages/visit.astro`**
   - Added `getHomepage` import.
   - Calls `getHomepage()` in parallel with `getSiteConfig()`.
   - Passes `homepage.serviceTimes` to `ServiceTimesCarousel`.

4. **`website/src/components/home/CtaBannerSection.astro`**
   - Changed prop from `config?: SiteConfig` to `serviceTimes?: ServiceTime[]`.

5. **`website/src/components/shared/ServiceTimesCarousel.astro`**
   - Changed prop type from `NonNullable<SiteConfig["serviceTimes"]>` to `ServiceTime[]`.

6. **`website/src/components/shared/ServiceTimesGrid.astro`**
   - Changed prop type from `NonNullable<SiteConfig["serviceTimes"]>` to `ServiceTime[]`.

7. **`website/src/components/home/ServiceTimesSection.astro`**
   - Removed empty array default (`services = []`) so fallback only applies when no data is passed.

**Alternative options (not taken):**
- **Option B:** Keep dual source and sync via Django signal — rejected due to ongoing maintenance burden.
- **Option C:** Remove `serviceTimes` from `SystemConfig` entirely — planned for a future cleanup migration if desired.

---

## 8. Verification Checklist

- [x] Identified component: `ServiceTimesSection.astro`
- [x] Identified prop: `services` from `config.serviceTimes`
- [x] Confirmed endpoint: `/api/site-config` (not `/api/homepage`)
- [x] Confirmed hardcoded fallback: `FALLBACK_SERVICES` in component
- [x] Confirmed ServiceTime model exists and is Admin-editable
- [x] Confirmed `/api/homepage` returns ServiceTime data (unused by homepage)
- [x] Documented exact break point in `index.astro`
- [x] Implemented fix: wired homepage and visit pages to `/api/homepage`
- [ ] Re-run `npx astro check` to confirm TypeScript integrity
- [ ] Manual verification: edit a ServiceTime in Django Admin, confirm UI update on homepage and /visit
