/**
 * Astro middleware — lightweight Academy route protection.
 *
 * A1.3/A1.4: Protects /academy and /academy/* routes.
 *
 * Strategy (A1.4 — lightweight, no per-request API calls):
 *   1. Check for the Django session cookie ("sessionid") in the request.
 *   2. If no session cookie → redirect to /login?redirect=<original path>.
 *   3. If session cookie present → allow the request through.
 *      The Academy page frontmatter will call /api/auth/me and /api/academy
 *      to verify authentication + AcademyAccess and render the appropriate
 *      state (academy content, access denied, or redirect to login).
 *
 * This avoids unnecessary API calls and DB lookups for every request.
 * The middleware only inspects cookies — it does NOT call the backend.
 *
 * Future /academy/* routes (dashboard, courses, lessons, etc.) are
 * automatically protected by the pathname prefix check.
 */

import { defineMiddleware } from "astro:middleware";

const ACADEMY_PREFIX = "/academy";

export const onRequest = defineMiddleware(async (context, next) => {
  const { pathname } = context.url;

  // Only protect /academy and /academy/* routes
  if (pathname === ACADEMY_PREFIX || pathname.startsWith(ACADEMY_PREFIX + "/")) {
    // Lightweight session cookie check — no API call
    const cookies = context.cookies;
    const sessionCookie = cookies.get("sessionid");

    if (!sessionCookie) {
      // Not authenticated — redirect to login with return path
      const loginUrl = new URL("/login", context.url.origin);
      loginUrl.searchParams.set("redirect", pathname);
      return context.redirect(loginUrl.pathname + loginUrl.search);
    }

    // Session cookie present — allow through.
    // The page itself will verify auth + AcademyAccess via API.
    const response = await next();
    
    // A1.4: Prevent caching of authenticated Academy pages so that
    // browser back/forward navigation cannot show protected content
    // after logout.
    response.headers.set("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0");
    response.headers.set("Pragma", "no-cache");
    response.headers.set("Expires", "0");
    
    return response;
  }

  return next();
});
