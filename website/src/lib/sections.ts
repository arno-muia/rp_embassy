/**
 * Section visibility flags (B5_1 / R1).
 *
 * GET /api/sections returns { page: { key: boolean } }.
 * Fail-open contract: any fetch failure, missing page, or missing key
 * renders the section (enabled) — an API hiccup never blanks the site.
 */
import { API_ENDPOINTS } from "./api";

export type SectionFlags = Record<string, Record<string, boolean>>;

export async function getSections(): Promise<SectionFlags> {
  try {
    const res = await fetch(API_ENDPOINTS.sections, { credentials: "include" });
    if (!res.ok) return {};
    return (await res.json()) as SectionFlags;
  } catch {
    return {};
  }
}

export function isEnabled(
  flags: SectionFlags | undefined,
  page: string,
  key: string,
): boolean {
  return flags?.[page]?.[key] ?? true;
}