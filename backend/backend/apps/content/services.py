"""Service layer for the content domain.

Business logic only. Must use repositories — no direct ORM access, no API/serializer logic.
"""

from .repositories import (
    ContactSubmissionRepository,
    SeriesRepository,
    SermonRepository,
    SystemConfigRepository,
    VisitRsvpRepository,
    WebsiteAcademyModuleRepository,
    WebsiteLeaderRepository,
    WebsiteTestimonialRepository,
)


class ContentService:
    @staticmethod
    def published_sermons():
        return SermonRepository.published()

    @staticmethod
    def sermon_by_slug(slug: str):
        return SermonRepository.get_by_slug(slug)

    @staticmethod
    def published_series():
        return SeriesRepository.published()

    @staticmethod
    def published_leaders():
        return WebsiteLeaderRepository.published()

    @staticmethod
    def published_testimonials():
        return WebsiteTestimonialRepository.published()

    @staticmethod
    def published_academy_modules():
        return WebsiteAcademyModuleRepository.published()

    @staticmethod
    def config_value(key: str, default=None):
        cfg = SystemConfigRepository.get_by_key(key)
        return cfg.value if cfg else default


class CaptureService:
    @staticmethod
    def pending_visits():
        return VisitRsvpRepository.pending()

    @staticmethod
    def all_contacts():
        return ContactSubmissionRepository.get_queryset()