"""Repository layer for the content domain.

Repository pattern only — query abstraction, no business logic.
"""

from django.db import models

from .models import (
    ContactSubmission,
    PublicSermon,
    SermonSeries,
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