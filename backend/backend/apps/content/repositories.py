"""Repository layer for the content domain.

Repository pattern only — query abstraction, no business logic.
"""

from django.db import models

from .models import (
    ChurchProfile,
    ContactSubmission,
    ContentBlock,
    HomepageSection,
    HomepageSettings,
    PastorProfile,
    PublicSermon,
    SermonSeries,
    ServiceTime,
    SystemConfig,
    VisitRsvp,
    WebsiteAcademyModule,
    WebsiteLeader,
    WebsiteTestimonial,
)


class SystemConfigRepository:
    model = SystemConfig

    @classmethod
    def get_queryset(cls):
        return SystemConfig.objects.all()

    @classmethod
    def get_by_key(cls, key: str) -> SystemConfig | None:
        return SystemConfig.objects.filter(key=key).first()


class SermonRepository:
    model = PublicSermon

    @classmethod
    def get_queryset(cls):
        return PublicSermon.objects.select_related('series').all()

    @classmethod
    def published(cls):
        return PublicSermon.objects.filter(is_published=True).select_related('series').order_by('-date')

    @classmethod
    def get_by_slug(cls, slug: str) -> PublicSermon | None:
        return PublicSermon.objects.select_related('series').filter(slug=slug).first()

    @classmethod
    def by_series(cls, series_slug: str):
        return PublicSermon.objects.filter(series_slug=series_slug)


class SeriesRepository:
    model = SermonSeries

    @classmethod
    def published(cls):
        return SermonSeries.objects.filter(is_published=True).order_by('sort_order')

    @classmethod
    def get_by_slug(cls, slug: str) -> SermonSeries | None:
        return SermonSeries.objects.filter(slug=slug).first()


class EventRepository:
    """Reused for generic published-content helpers (sermons/events share read shape)."""

    model = PublicSermon

    @classmethod
    def latest(cls, limit: int = 1):
        return PublicSermon.objects.filter(is_published=True).order_by('-date')[:limit]


class WebsiteLeaderRepository:
    model = WebsiteLeader

    @classmethod
    def published(cls):
        return WebsiteLeader.objects.filter(is_published=True).order_by('sort_order')


class WebsiteTestimonialRepository:
    model = WebsiteTestimonial

    @classmethod
    def published(cls):
        return WebsiteTestimonial.objects.filter(is_published=True).order_by('sort_order')


class WebsiteAcademyModuleRepository:
    model = WebsiteAcademyModule

    @classmethod
    def published(cls):
        return WebsiteAcademyModule.objects.filter(is_published=True).order_by('sort_order')


class ContactSubmissionRepository:
    model = ContactSubmission

    @classmethod
    def get_queryset(cls):
        return ContactSubmission.objects.all()


class VisitRsvpRepository:
    model = VisitRsvp

    @classmethod
    def get_queryset(cls):
        return VisitRsvp.objects.all()

    @classmethod
    def pending(cls):
        return VisitRsvp.objects.filter(status='PENDING')


# =============================================================================
# CMS Model Repositories (managed=True)
# =============================================================================


class HomepageSettingsRepository:
    """Repository for HomepageSettings (singleton hero configuration)."""
    model = HomepageSettings

    @classmethod
    def get_solo(cls) -> HomepageSettings | None:
        """Get the singleton HomepageSettings instance."""
        return HomepageSettings.objects.first()


class ChurchProfileRepository:
    """Repository for ChurchProfile (singleton church identity)."""
    model = ChurchProfile

    @classmethod
    def get_solo(cls) -> ChurchProfile | None:
        """Get the singleton ChurchProfile instance."""
        return ChurchProfile.objects.first()


class ServiceTimeRepository:
    """Repository for ServiceTime entries."""
    model = ServiceTime

    @classmethod
    def all_ordered(cls):
        """Get all service times ordered by display_order."""
        return ServiceTime.objects.all().order_by('display_order', 'day')


class ContentBlockRepository:
    """Repository for ContentBlock entries."""
    model = ContentBlock

    @classmethod
    def by_type(cls, content_type: str):
        """Get content blocks by type, ordered by display_order."""
        return ContentBlock.objects.filter(
            content_type=content_type,
            is_active=True
        ).order_by('display_order')


class HomepageSectionRepository:
    """Repository for HomepageSection entries."""
    model = HomepageSection

    @classmethod
    def all_ordered(cls):
        """Get all homepage sections ordered by display_order."""
        return HomepageSection.objects.all().order_by('display_order')

    @classmethod
    def get_by_name(cls, section_name: str) -> HomepageSection | None:
        """Get a specific section by name."""
        return HomepageSection.objects.filter(section_name=section_name).first()


class PastorProfileRepository:
    """Repository for PastorProfile."""
    model = PastorProfile

    @classmethod
    def get_active(cls) -> PastorProfile | None:
        """Get the active pastor profile."""
        return PastorProfile.objects.filter(is_active=True).first()
