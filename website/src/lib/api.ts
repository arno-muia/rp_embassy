import type {
  Sermon,
  SermonSeries,
  Event,
  Leader,
  Testimonial,
  AcademyModule,
} from "../types";
import type {
  SermonView,
  SeriesView,
  EventView,
  LeaderView,
  TestimonialView,
  AcademyModuleView,
  ServiceTime,
} from "../types";
import { EVENT_CATEGORY_LABELS } from "../types";

const API_BASE_URL =
  import.meta.env.PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

/** Endpoint definitions — all pointed at the Django backend. */
export const API_ENDPOINTS = {
  sermons: `${API_BASE_URL}/api/sermons`,
  sermon: (slug: string) => `${API_BASE_URL}/api/sermons/${slug}`,
  series: `${API_BASE_URL}/api/series`,
  seriesDetail: (slug: string) => `${API_BASE_URL}/api/series/${slug}`,
  events: `${API_BASE_URL}/api/events`,
  event: (id: string) => `${API_BASE_URL}/api/events/${id}`,
  leaders: `${API_BASE_URL}/api/leaders`,
  testimonials: `${API_BASE_URL}/api/testimonials`,
  academy: `${API_BASE_URL}/api/academy`,
  siteConfig: `${API_BASE_URL}/api/site-config`,
  homepage: `${API_BASE_URL}/api/homepage`,
  contact: `${API_BASE_URL}/api/contact`,
  prayer: `${API_BASE_URL}/api/prayer`,
  rsvp: `${API_BASE_URL}/api/rsvp`,
  health: `${API_BASE_URL}/api/health`,
  login: `${API_BASE_URL}/api/auth/login`,
  logout: `${API_BASE_URL}/api/auth/logout`,
  me: `${API_BASE_URL}/api/auth/me`,
  changePassword: `${API_BASE_URL}/api/auth/change-password`,
  csrfToken: `${API_BASE_URL}/api/auth/csrf-token`,
} as const;

async function getJson<T>(
  path: string,
  cookieHeader?: string,
): Promise<T> {
  const res = await fetch(path, {
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(cookieHeader ? { Cookie: cookieHeader } : {}),
    },
    redirect: "follow",
  });
  if (!res.ok) {
    throw new Error(`API request failed: ${path} (${res.status})`);
  }
  return (await res.json()) as T;
}

/* ---------- Mappers: Django snake_case → frontend camelCase views ---------- */

export function toSermonView(s: Sermon): SermonView {
  return {
    id: s.id,
    slug: s.slug,
    title: s.title,
    description: s.description,
    series: s.series_title || s.series,
    seriesSlug: s.series_slug,
    scripture: s.scripture,
    speaker: s.speaker,
    date: s.date,
    videoUrl: s.video_url,
    audioUrl: s.audio_url,
    notesUrl: s.notes_url,
    thumbnail: s.thumbnail_url,
    duration: s.duration,
    tags: s.tags ?? [],
    published: s.is_published,
  };
}

export function toSeriesView(s: SermonSeries): SeriesView {
  return {
    id: s.id,
    slug: s.slug,
    title: s.title,
    description: s.description,
    image: s.image_url,
    sermonCount: s.sermon_count,
  };
}

export function toEventView(e: Event): EventView {
  const start = new Date(e.start_date_time);
  const status =
    e.status === "COMPLETED"
      ? "past"
      : e.status === "PUBLISHED" && start.getTime() > Date.now()
        ? "upcoming"
        : e.status === "PUBLISHED"
          ? "ongoing"
          : "past";

  let endDate: string | undefined;
  let endTime: string | undefined;
  if (e.end_date_time) {
    const end = new Date(e.end_date_time);
    endDate = end.toISOString().split("T")[0];
    endTime = end.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  return {
    id: e.id,
    slug: e.id,
    title: e.title,
    description: e.description ?? "",
    date: start.toISOString().split("T")[0],
    time: start.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    }),
    endDate,
    endTime,
    location: e.location ?? "Thika, Kenya",
    image: e.image_url ?? "/images/posters/kingdom-formation.jpeg",
    category: e.type || "OTHER",
    categoryLabel: EVENT_CATEGORY_LABELS[e.type] || "Special Event",
    registrationRequired: e.registration_required,
    registrationUrl: e.registration_required
      ? `/visit#rsvp`
      : undefined,
    published: true,
    status,
  };
}

export function toLeaderView(l: Leader): LeaderView {
  return {
    id: l.id,
    name: l.name,
    role: l.role,
    bio: l.bio,
    photo: l.photo_url,
    order: l.sort_order,
    social: l.social,
  };
}

export function toTestimonialView(t: Testimonial): TestimonialView {
  return {
    id: t.id,
    quote: t.quote,
    name: t.name,
    role: t.role,
    photo: t.photo_url,
  };
}

export function toAcademyModuleView(m: AcademyModule): AcademyModuleView {
  return {
    id: m.id,
    title: m.title,
    description: m.description,
    instructor: m.instructor,
    lessonsCount: m.lessons_count,
    duration: m.duration,
    order: m.sort_order,
  };
}

/* ---------- Typed fetch helpers (server-side usage in Astro frontmatter) ---------- */

export async function getSermons(): Promise<SermonView[]> {
  const data = await getJson<Sermon[]>(API_ENDPOINTS.sermons);
  return data.map(toSermonView);
}

export async function getSermonBySlug(
  slug: string,
): Promise<SermonView | undefined> {
  try {
    const s = await getJson<Sermon>(API_ENDPOINTS.sermon(slug));
    return toSermonView(s);
  } catch {
    return undefined;
  }
}

export async function getSeries(): Promise<SeriesView[]> {
  const data = await getJson<SermonSeries[]>(API_ENDPOINTS.series);
  return data.map(toSeriesView);
}

export async function getSeriesBySlug(
  slug: string,
): Promise<SeriesView | undefined> {
  try {
    const s = await getJson<SermonSeries>(API_ENDPOINTS.seriesDetail(slug));
    return toSeriesView(s);
  } catch {
    return undefined;
  }
}

export async function getSermonsBySeries(
  seriesSlug: string,
): Promise<SermonView[]> {
  const all = await getSermons();
  return all.filter((s) => s.seriesSlug === seriesSlug);
}

export async function getRelatedSermons(
  sermon: SermonView,
  limit = 3,
): Promise<SermonView[]> {
  const all = await getSermons();
  return all
    .filter((s) => s.slug !== sermon.slug && s.seriesSlug === sermon.seriesSlug)
    .slice(0, limit);
}

export async function getLatestSermon(): Promise<SermonView | undefined> {
  const all = await getSermons();
  const sorted = [...all].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime(),
  );
  return sorted[0];
}

export async function getEvents(): Promise<EventView[]> {
  const data = await getJson<Event[]>(API_ENDPOINTS.events);
  const mapped = data.map(toEventView);
  // Sort: upcoming/ongoing first (soonest), then past (most recent)
  return mapped.sort((a, b) => {
    const aPast = a.status === "past" ? 1 : 0;
    const bPast = b.status === "past" ? 1 : 0;
    if (aPast !== bPast) return aPast - bPast;
    return (
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  });
}

export async function getUpcomingEvents(
  limit?: number,
): Promise<EventView[]> {
  const events = await getEvents();
  const upcoming = events.filter(
    (e) => e.status === "upcoming" || e.status === "ongoing",
  );
  return limit ? upcoming.slice(0, limit) : upcoming;
}

export async function getEventById(
  id: string,
): Promise<EventView | undefined> {
  try {
    const e = await getJson<Event>(API_ENDPOINTS.event(id));
    return toEventView(e);
  } catch {
    return undefined;
  }
}

export async function getLeaders(): Promise<LeaderView[]> {
  const data = await getJson<Leader[]>(API_ENDPOINTS.leaders);
  return data.map(toLeaderView).sort((a, b) => a.order - b.order);
}

export async function getTestimonials(): Promise<TestimonialView[]> {
  const data = await getJson<Testimonial[]>(API_ENDPOINTS.testimonials);
  return data.map(toTestimonialView);
}

export async function getAcademyModules(
  cookieHeader?: string,
): Promise<AcademyModuleView[]> {
  // A1: Forward the browser's Cookie header when called server-side (SSR).
  // Without this, Django returns 403 because the Node fetch has no session.
  try {
    const data = await getJson<AcademyModule[]>(
      API_ENDPOINTS.academy,
      cookieHeader,
    );
    return data.map(toAcademyModuleView).sort((a, b) => a.order - b.order);
  } catch {
    // If the user is authenticated but not authorized to view academy modules
    // (403), or any other failure occurs, return an empty list so the page
    // can render gracefully instead of crashing SSR.
    return [];
  }
}

/* ---------- CSRF helpers ---------- */

/**
 * Read the ``csrftoken`` cookie value.
 *
 * This is the single source of truth for the CSRF token.  The backend
 * ``/api/auth/csrf-token`` endpoint sets this cookie; we read it directly
 * rather than trusting any JSON payload that could get out of sync if the
 * endpoint is called multiple times before a POST.
 */
export function getCsrfTokenFromCookie(): string | null {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

/* ---------- Auth helpers (A1.5) ---------- */

export async function getMe(
  cookieHeader?: string,
): Promise<AuthUser | null> {
  try {
    const res = await fetch(API_ENDPOINTS.me, {
      credentials: "include",
      headers: {
        Accept: "application/json",
        ...(cookieHeader ? { Cookie: cookieHeader } : {}),
      },
    });
    if (!res.ok) return null;
    return (await res.json()) as AuthUser;
  } catch {
    return null;
  }
}

export async function logout(): Promise<boolean> {
  try {
    const res = await fetch(API_ENDPOINTS.logout, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });
    return res.ok;
  } catch {
    return false;
  }
}

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  must_change_password: boolean;
  last_login: string | null;
}

export interface SiteConfig {
  name: string;
  shortName: string;
  tagline: string;
  scripture: string;
  description: string;
  address: {
    street: string;
    city: string;
    country: string;
    mapsUrl: string;
  };
  contact: { email: string; whatsapp?: string };
  social: { instagram: string; facebook: string; youtube: string };
  giving: { mpesaTill: string; accountName: string };
  academyUrl: string;
  welcomeMessage?: { title: string; message: string; author?: string };
  whatToExpect?: { title: string; description: string; icon: string }[];
  beliefs?: { id: string; title: string; description: string }[];
  values?: { id: string; title: string; description: string }[];
  visitFaqs?: { question: string; answer: string }[];
  theme2026?: {
    title: string;
    scripture: string;
    scriptureText: string;
    image?: string;
  };
}

export async function getSiteConfig(): Promise<SiteConfig | undefined> {
  try {
    return await getJson<SiteConfig>(API_ENDPOINTS.siteConfig);
  } catch {
    return undefined;
  }
}

export interface HomePageResponse {
  hero: Record<string, unknown>;
  churchProfile: Record<string, unknown>;
  serviceTimes: ServiceTime[];
  values: Array<Record<string, unknown>>;
  beliefs: Array<Record<string, unknown>>;
  faqs: Array<Record<string, unknown>>;
  whatToExpect: Array<Record<string, unknown>>;
  sections: Array<Record<string, unknown>>;
  latestSermon: Record<string, unknown> | null;
  events: EventView[];
  testimonials: TestimonialView[];
  leaders: LeaderView[];
}

export { ServiceTime };

export async function getHomepage(): Promise<HomePageResponse | undefined> {
  try {
    return await getJson<HomePageResponse>(API_ENDPOINTS.homepage);
  } catch {
    return undefined;
  }
}

/* ---------- POST helpers ---------- */

export async function postContact(payload: Record<string, unknown>) {
  const res = await fetch(API_ENDPOINTS.contact, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    redirect: "follow",
  });
  if (!res.ok) throw new Error("Failed to send contact message");
  return res.json();
}

export async function postPrayer(payload: Record<string, unknown>) {
  const res = await fetch(API_ENDPOINTS.prayer, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    redirect: "follow",
  });
  if (!res.ok) throw new Error("Failed to submit prayer request");
  return res.json();
}

export async function postRsvp(payload: Record<string, unknown>) {
  const res = await fetch(API_ENDPOINTS.rsvp, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    redirect: "follow",
  });
  if (!res.ok) throw new Error("Failed to submit RSVP");
  return res.json();
}