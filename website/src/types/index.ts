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