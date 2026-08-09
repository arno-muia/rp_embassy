/**
 * Astro middleware — Academy route protection.
 *
 * A1.3/A1.4: Protects /academy and /academy/* routes.
 *
 * Strategy:
 *   1. Forward the incoming Cookie header to Django's /api/auth/me.
 *   2. If /api/auth/me returns 200 → session is valid → allow through.
 *   3. If /api/auth/me returns 401 → no valid session → redirect to login.
 *
 * The middleware does NOT treat the mere presence of a sessionid cookie
 * as proof of authentication. A stale, expired, or invalidated session
 * cookie must not grant access.
 *
 * The Academy page frontmatter will still call /api/auth/me and /api/academy
 * to verify authentication + AcademyAccess and render the appropriate state.
 *
 * Future /academy/* routes (dashboard, courses, lessons, etc.) are
 * automatically protected by the pathname prefix check.
 */

import { defineMiddleware } from "astro:middleware";

const ACADEMY_PREFIX = "/academy";

const API_BASE_URL =
  import.meta.env.PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";
const ME_ENDPOINT = `${API_BASE_URL}/api/auth/me`;

export const onRequest = defineMiddleware(async (context, next) => {
  const { pathname } = context.url;

  // Only protect /academy and /academy/* routes
  if (pathname === ACADEMY_PREFIX || pathname.startsWith(ACADEMY_PREFIX + "/")) {
    // Forward the browser's Cookie header to Django so Node.js fetch
    // sends the sessionid cookie cross-origin.
    const cookieHeader = context.request.headers.get("cookie") || undefined;

    let authenticated = false;
    try {
      const res = await fetch(ME_ENDPOINT, {
        credentials: "include",
        headers: {
          Accept: "application/json",
          ...(cookieHeader ? { Cookie: cookieHeader } : {}),
        },
      });
      authenticated = res.ok;
    } catch {
      authenticated = false;
    }

    if (!authenticated) {
      // Not authenticated — redirect to login with return path
      const loginUrl = new URL("/login", context.url.origin);
      loginUrl.searchParams.set("redirect", pathname);
      return context.redirect(loginUrl.pathname + loginUrl.search);
    }

    // Session is valid — allow through.
    const response = await next();

    // Prevent caching of authenticated Academy pages so that
    // browser back/forward navigation cannot show protected content
    // after logout.
    response.headers.set("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0");
    response.headers.set("Pragma", "no-cache");
    response.headers.set("Expires", "0");

    return response;
  }

  return next();
});
