export interface SermonSeries {
  id: string;
  slug: string;
  title: string;
  description: string;
  image_url: string;
  sermon_count: number;
  sort_order: number;
  is_published: boolean;
}

export interface SeriesView {
  id: string;
  slug: string;
  title: string;
  description: string;
  image: string;
  sermonCount: number;
}