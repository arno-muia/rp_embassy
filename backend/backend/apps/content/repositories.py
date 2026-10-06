"""Repository layer for the content domain.

Repository pattern only — query abstraction, no business logic.
"""

from django.db import models

from .models import (
    AboutTheme,
    ContactDetailsSection,
    ContactFormSection,
    ContactHero,
    ContactSocialLink,
    GiveAllocationItem,
    GiveAllocationSection,
    GiveHero,
    GiveMpesaSection,
    GiveWhySection,
    AboutValue,
    AboutValuesSection,
    AboutWelcome,
    ChurchProfile,
    ContactSubmission,
    ContentBlock,
    HomepageSection,
    HomepageSettings,
    PastorProfile,
    PublicSermon,
    SermonDetailCopy,
    SermonSeries,
    SermonsBrowseSection,
    SermonsGridSection,
    SermonsHero,
    SermonsRelatedSection,
    ServiceTime,
    SystemConfig,
    VisitComingSunday,
    VisitExpectSection,
    VisitExpectStep,
    VisitFaq,
    VisitFaqSection,
    VisitHero,
    VisitLocation,
    VisitRsvp,
    VisitRsvpSection,
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

    @classmethod
    def published(cls):
        """Get published service times ordered for public display."""
        return cls.model.objects.filter(
            is_published=True
        ).order_by('display_order', 'day')


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


# =============================================================================
# About page section content (B5.5 — dedicated models)
# =============================================================================


class AboutContentRepository:
    """Repository for the About page's admin-managed section content.

    Each section (intro / values / theme) is stored in its own model; the
    public endpoint returns the most recently updated record so the page
    always reflects the latest admin edit.
    """

    @classmethod
    def welcome(cls) -> AboutWelcome | None:
        """Latest 'Welcome, Vision & Mission' record (None when not set up)."""
        return AboutWelcome.objects.order_by('-updated_at').first()

    @classmethod
    def values_section(cls) -> AboutValuesSection | None:
        """Latest 'Our Values' section record (None when not set up)."""
        return AboutValuesSection.objects.order_by('-updated_at').first()

    @classmethod
    def published_values(cls, section: AboutValuesSection):
        """Published value cards for a section, in display order."""
        return AboutValue.objects.filter(
            section=section,
            is_published=True,
        ).order_by('sort_order', 'id')

    @classmethod
    def theme(cls) -> AboutTheme | None:
        """Latest '2026 Theme' record (None when not set up)."""
        return AboutTheme.objects.order_by('-updated_at').first()


# =============================================================================
# Visit page section content (dedicated models)
# =============================================================================


class VisitContentRepository:
    """Repository for the Visit page's admin-managed section content.

    Each singleton section returns the most recently updated record so the
    page always reflects the latest admin edit (B5.5 About precedent).
    """

    @classmethod
    def hero(cls) -> VisitHero | None:
        """Latest 'Page Hero' record (None when not set up)."""
        return VisitHero.objects.order_by('-updated_at').first()

    @classmethod
    def location(cls) -> VisitLocation | None:
        """Latest 'Location & Map' record (None when not set up)."""
        return VisitLocation.objects.order_by('-updated_at').first()

    @classmethod
    def expect_section(cls) -> VisitExpectSection | None:
        """Latest 'What to Expect' section record (None when not set up)."""
        return VisitExpectSection.objects.order_by('-updated_at').first()

    @classmethod
    def published_steps(cls, section: VisitExpectSection):
        """Published expect cards for a section, in display order."""
        return VisitExpectStep.objects.filter(
            section=section,
            is_published=True,
        ).order_by('sort_order', 'id')

    @classmethod
    def faq_section(cls) -> VisitFaqSection | None:
        """Latest 'FAQs' section record (None when not set up)."""
        return VisitFaqSection.objects.order_by('-updated_at').first()

    @classmethod
    def published_faqs(cls, section: VisitFaqSection):
        """Published FAQ rows for a section, in display order."""
        return VisitFaq.objects.filter(
            section=section,
            is_published=True,
        ).order_by('sort_order', 'id')

    @classmethod
    def rsvp_section(cls) -> VisitRsvpSection | None:
        """Latest 'RSVP Form Copy' record (None when not set up)."""
        return VisitRsvpSection.objects.order_by('-updated_at').first()

    @classmethod
    def coming_sunday(cls) -> VisitComingSunday | None:
        """Latest 'I Am Coming This Sunday' record (None when not set up)."""
        return VisitComingSunday.objects.order_by('-updated_at').first()


# =============================================================================
# Sermons page section content (dedicated models)
# =============================================================================


class SermonsContentRepository:
    """Repository for the Sermons page's admin-managed section content.

    Singleton sections return the most recently updated record (B5.7 Visit
    precedent) so the page always reflects the latest admin edit.
    """

    @classmethod
    def hero(cls) -> SermonsHero | None:
        """Latest 'Page Hero' record (None when not set up)."""
        return SermonsHero.objects.order_by('-updated_at').first()

    @classmethod
    def browse_section(cls) -> SermonsBrowseSection | None:
        """Latest 'Browse by Series' record (None when not set up)."""
        return SermonsBrowseSection.objects.order_by('-updated_at').first()

    @classmethod
    def grid_section(cls) -> SermonsGridSection | None:
        """Latest 'All Sermons' record (None when not set up)."""
        return SermonsGridSection.objects.order_by('-updated_at').first()

    @classmethod
    def detail_copy(cls) -> SermonDetailCopy | None:
        """Latest 'Sermon Detail Copy' record (None when not set up)."""
        return SermonDetailCopy.objects.order_by('-updated_at').first()

    @classmethod
    def related_section(cls) -> SermonsRelatedSection | None:
        """Latest 'Related Sermons' record (None when not set up)."""
        return SermonsRelatedSection.objects.order_by('-updated_at').first()


# =============================================================================
# Partner (Give) page section content (dedicated models)
# =============================================================================


class GiveContentRepository:
    """Repository for the Partner (Give) page's admin-managed section content.

    Singleton sections return the most recently updated record (Visit B5.7 /
    Sermons B5.8 precedent) so the page always reflects the latest admin edit.
    GiveMpesaSection is the canonical till/account source for /give; the
    legacy GlobalSettings.mpesa_till / SystemConfig 'site'.giving keys are
    left untouched.
    """

    @classmethod
    def hero(cls) -> GiveHero | None:
        """Latest 'Page Hero' record (None when not set up)."""
        return GiveHero.objects.order_by('-updated_at').first()

    @classmethod
    def why(cls) -> GiveWhySection | None:
        """Latest 'Why We Give' record (None when not set up)."""
        return GiveWhySection.objects.order_by('-updated_at').first()

    @classmethod
    def mpesa(cls) -> GiveMpesaSection | None:
        """Latest 'M-Pesa Giving' record (None when not set up)."""
        return GiveMpesaSection.objects.order_by('-updated_at').first()

    @classmethod
    def allocation_section(cls) -> GiveAllocationSection | None:
        """Latest 'Where Your Giving Goes' record (None when not set up)."""
        return GiveAllocationSection.objects.order_by('-updated_at').first()

    @classmethod
    def published_allocations(cls, section: GiveAllocationSection):
        """Published allocation cards for a section, in display order."""
        return GiveAllocationItem.objects.filter(
            section=section,
            is_published=True,
        ).order_by('sort_order', 'id')


# =============================================================================
# Contact page section content (dedicated models)
# =============================================================================


class ContactContentRepository:
    """Repository for the Contact page's admin-managed section content.

    Singleton sections return the most recently updated record (Visit B5.7 /
    Sermons B5.8 / Give B5.9 precedent) so the page always reflects the latest
    admin edit.
    """

    @classmethod
    def hero(cls) -> ContactHero | None:
        """Latest 'Page Hero' record (None when not set up)."""
        return ContactHero.objects.order_by('-updated_at').first()

    @classmethod
    def details(cls) -> ContactDetailsSection | None:
        """Latest 'Contact Details' record (None when not set up)."""
        return ContactDetailsSection.objects.order_by('-updated_at').first()

    @classmethod
    def published_socials(cls, section: ContactDetailsSection):
        """Published social links for a details section, in display order."""
        return ContactSocialLink.objects.filter(
            section=section,
            is_published=True,
        ).order_by('sort_order', 'id')

    @classmethod
    def form(cls) -> ContactFormSection | None:
        """Latest 'Contact Form' record (None when not set up)."""
        return ContactFormSection.objects.order_by('-updated_at').first()
