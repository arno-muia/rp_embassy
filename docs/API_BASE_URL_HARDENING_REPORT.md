# API Base URL Hardening Report

## PHASE C4D — API BASE URL HARDENING FOR ASTRO SSR

### Objective
Fix all Astro SSR runtime failures caused by relative API URLs such as `/api/testimonials`, `/api/sermons`, `/api/events`.

### Root Cause
Astro is executing `fetch()` during SSR (server-side rendering). Relative URLs work in browsers but fail in Node.js SSR because Node requires fully-qualified URLs.

---

## Summary of Changes

### Files Modified

1. **RP/website/.env** (Created)
   - Added `PUBLIC_API_URL=http://127.0.0.1:8000`

2. **RP/website/.env.example** (Created)
   - Added `PUBLIC_API_URL=http://127.0.0.1:8000`

3. **RP/website/src/env.d.ts** (Modified)
   - Changed `PUBLIC_API_BASE` to `PUBLIC_API_URL` in `ImportMetaEnv` interface

4. **RP/website/src/lib/api.ts** (Modified)
   - Added `API_BASE_URL` constant that reads from `import.meta.env.PUBLIC_API_URL` with fallback to `http://127.0.0.1:8000`
   - Updated all `API_ENDPOINTS` to use full absolute URLs with `${API_BASE_URL}/api/...`
   - Added `login` and `changePassword` endpoints for auth forms
   - Updated `postContact`, `postPrayer`, `postRsvp` functions to use already-computed full URLs

5. **RP/website/src/components/forms/ContactForm.astro** (Modified)
   - Added import for `API_ENDPOINTS`
   - Changed `data-endpoint="/api/contact"` to `data-endpoint={API_ENDPOINTS.contact}`

6. **RP/website/src/components/forms/PrayerForm.astro** (Modified)
   - Added import for `API_ENDPOINTS`
   - Changed `data-endpoint="/api/prayer"` to `data-endpoint={API_ENDPOINTS.prayer}`

7. **RP/website/src/components/forms/RsvpForm.astro** (Modified)
   - Added import for `API_ENDPOINTS`
   - Changed `data-endpoint="/api/rsvp"` to `data-endpoint={API_ENDPOINTS.rsvp}`

8. **RP/website/src/components/forms/LoginForm.astro** (Modified)
   - Added import for `API_ENDPOINTS`
   - Changed `data-endpoint="/api/auth/login"` to `data-endpoint={API_ENDPOINTS.login}`

9. **RP/website/src/components/forms/ChangePasswordForm.astro** (Modified)
   - Added import for `API_ENDPOINTS`
   - Changed `data-endpoint="/api/auth/change-password"` to `data-endpoint={API_ENDPOINTS.changePassword}`

---

## Relative URLs Found and Replaced

### In src/lib/api.ts (Server-side fetch calls)
| Before | After |
|--------|-------|
| `sermons: "/api/sermons"` | `sermons: "${API_BASE_URL}/api/sermons"` |
| `sermon: (slug: string) => \`/api/sermons/${slug}\`` | `sermon: (slug: string) => \`${API_BASE_URL}/api/sermons/${slug}\`` |
| `series: "/api/series"` | `series: "${API_BASE_URL}/api/series"` |
| `seriesDetail: (slug: string) => \`/api/series/${slug}\`` | `seriesDetail: (slug: string) => \`${API_BASE_URL}/api/series/${slug}\`` |
| `events: "/api/events"` | `events: "${API_BASE_URL}/api/events"` |
| `event: (id: string) => \`/api/events/${id}\`` | `event: (id: string) => \`${API_BASE_URL}/api/events/${id}\`` |
| `leaders: "/api/leaders"` | `leaders: "${API_BASE_URL}/api/leaders"` |
| `testimonials: "/api/testimonials"` | `testimonials: "${API_BASE_URL}/api/testimonials"` |
| `academy: "/api/academy"` | `academy: "${API_BASE_URL}/api/academy"` |
| `siteConfig: "/api/site-config"` | `siteConfig: "${API_BASE_URL}/api/site-config"` |
| `contact: "/api/contact"` | `contact: "${API_BASE_URL}/api/contact"` |
| `prayer: "/api/prayer"` | `prayer: "${API_BASE_URL}/api/prayer"` |
| `rsvp: "/api/rsvp"` | `rsvp: "${API_BASE_URL}/api/rsvp"` |
| `health: "/api/health"` | `health: "${API_BASE_URL}/api/health"` |

### In Form Components (Client-side fetch calls)
| Component | Before | After |
|---------|--------|-------|
| ContactForm.astro | `data-endpoint="/api/contact"` | `data-endpoint={API_ENDPOINTS.contact}` |
| PrayerForm.astro | `data-endpoint="/api/prayer"` | `data-endpoint={API_ENDPOINTS.prayer}` |
| RsvpForm.astro | `data-endpoint="/api/rsvp"` | `data-endpoint={API_ENDPOINTS.rsvp}` |
| LoginForm.astro | `data-endpoint="/api/auth/login"` | `data-endpoint={API_ENDPOINTS.login}` |
| ChangePasswordForm.astro | `data-endpoint="/api/auth/change-password"` | `data-endpoint={API_ENDPOINTS.changePassword}` |

---

## Environment Variables Added

```
PUBLIC_API_URL=http://127.0.0.1:8000
```

This can be overridden in production to point to the actual backend URL:
```
PUBLIC_API_URL=https://api.royalpriesthoodembassy.org
```

---

## Validation Status

### npm run check
- **Status**: Unable to run due to npm native binding issue (environment problem, not code issue)

### npm run build
- **Status**: Unable to run due to npm native binding issue (environment problem, not code issue)
- The npm cache has a corrupted rolldown native binding. This needs to be resolved with:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

---

## Remaining Issues

1. **npm environment issue**: The Node.js/npm environment has a corrupted native binding for rolldown. This is unrelated to the code changes and can be fixed by clearing the npm cache and reinstalling dependencies.

2. **No other API references found**: All hardcoded `/api/` URLs have been replaced with environment-aware URLs.

---

## How to Verify

After fixing the npm environment:

```bash
cd rpwebsite/RP/website
npm install  # Clean install
npm run check
npm run build
```

The Astro SSR should now work correctly because:
- All `fetch()` calls in server-side code (pages, api.ts) use full absolute URLs
- All form components use full absolute URLs via `API_ENDPOINTS`
- The `API_BASE_URL` environment variable defaults to `http://127.0.0.1:8000` but can be overridden

---

## Notes

- The changes ensure SSR compatibility while maintaining backward compatibility
- Relative URLs in client-side JavaScript (browser) would have worked, but using environment-aware URLs ensures consistency and allows the frontend to be hosted on a different domain from the backend
- The `API_ENDPOINTS` object is computed at module load time, ensuring the environment variable is read once during initialization