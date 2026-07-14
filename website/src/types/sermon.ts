export interface Sermon {
  id: string;
  slug: string;
  title: string;
  description: string;
  series: string;
  series_slug: string;
  series_title: string;
  scripture?: string;
  speaker: string;
  date: string;
  video_url: string;
  audio_url?: string;
  notes_url?: string;
  thumbnail_url: string;
  duration?: string;
  tags: string[];
  is_published: boolean;
}

/** Frontend-friendly view derived from the Django serializer. */
export interface SermonView {
  id: string;
  slug: string;
  title: string;
  description: string;
  series: string;
  seriesSlug: string;
  scripture?: string;
  speaker: string;
  date: string;
  videoUrl: string;
  audioUrl?: string;
  notesUrl?: string;
  thumbnail: string;
  duration?: string;
  tags: string[];
  published: boolean;
}