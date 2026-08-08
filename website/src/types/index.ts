export * from "./sermon";
export * from "./series";
export * from "./event";
export * from "./leader";
export * from "./testimonial";
export * from "./academy";
export * from "./servicetime";

export interface ContactSubmission {
  id: string;
  name: string;
  email: string;
  phone?: string;
  message: string;
  createdAt: string;
}

export interface PrayerSubmission {
  id: string;
  name?: string;
  request: string;
  anonymous: boolean;
  createdAt: string;
}

export interface VisitRsvp {
  id: string;
  name: string;
  phone: string;
  email?: string;
  partySize: number;
  firstVisit: boolean;
  visitDate?: string;
  notes?: string;
  status?: string;
  createdAt: string;
}

export interface HomepageHero {
  hero_title?: string;
  hero_subtitle?: string;
  hero_scripture?: string;
  hero_scripture_reference?: string;
  hero_background_image?: string;
  hero_cta_text?: string;
  hero_cta_url?: string;
  cta_heading?: string;
  cta_title?: string;
  cta_description?: string;
  cta_button_text?: string;
  cta_button_url?: string;
  cta_secondary_button_text?: string;
  cta_secondary_button_url?: string;
  cta_location?: string;
}