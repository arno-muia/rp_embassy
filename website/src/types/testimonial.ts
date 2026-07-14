export interface Testimonial {
  id: string;
  quote: string;
  name: string;
  role?: string;
  photo_url?: string;
  sort_order: number;
  is_published: boolean;
}

export interface TestimonialView {
  id: string;
  quote: string;
  name: string;
  role?: string;
  photo?: string;
}