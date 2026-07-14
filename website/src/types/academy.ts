export interface AcademyModule {
  id: string;
  title: string;
  description: string;
  instructor: string;
  lessons_count: number;
  duration: string;
  sort_order: number;
  is_published: boolean;
}

export interface AcademyModuleView {
  id: string;
  title: string;
  description: string;
  instructor: string;
  lessonsCount: number;
  duration: string;
  order: number;
}