export interface Leader {
  id: string;
  name: string;
  role: string;
  bio: string;
  photo_url?: string;
  sort_order: number;
  social?: {
    facebook?: string;
    instagram?: string;
  };
  is_published: boolean;
}

export interface LeaderView {
  id: string;
  name: string;
  role: string;
  bio: string;
  photo?: string;
  order: number;
  social?: {
    facebook?: string;
    instagram?: string;
  };
}