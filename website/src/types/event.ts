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

export interface EventView {
  id: string;
  slug: string;
  title: string;
  description: string;
  date: string;
  time: string;
  location: string;
  image: string;
  category: "service" | "special" | "outreach" | "training";
  registrationRequired: boolean;
  registrationUrl?: string;
  published: boolean;
  status: "upcoming" | "ongoing" | "past";
}