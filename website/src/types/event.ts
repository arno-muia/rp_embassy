export interface Event {
  id: string;
  title: string;
  description: string;
  type: string;
  start_date_time: string;
  end_date_time?: string;
  location?: string;
  image_url?: string;
  video_url?: string;
  gallery_url?: string;
  registration_required: boolean;
  max_attendees?: number;
  cost_cents?: number;
  registration_open_date?: string;
  status: string;
}

export const EVENT_CATEGORY_LABELS: Record<string, string> = {
  SERVICE: "Worship Service",
  FELLOWSHIP: "Fellowship",
  OUTREACH: "Outreach",
  CONFERENCE: "Conference",
  FUNDRAISER: "Fundraiser",
  OTHER: "Special Event",
};

export interface EventView {
  id: string;
  slug: string;
  title: string;
  description: string;
  date: string;
  time: string;
  endDate?: string;
  endTime?: string;
  location: string;
  image: string;
  category: string;
  categoryLabel: string;
  registrationRequired: boolean;
  registrationUrl?: string;
  published: boolean;
  status: "upcoming" | "ongoing" | "past";
}