"""Content (public website CMS) domain models — mapped 1:1 to PostgreSQL.

Source of truth: apps/web/prisma/schema.prisma (SystemConfig, SermonSeries,
PublicSermon, WebsiteLeader, WebsiteTestimonial, WebsiteAcademyModule,
ContactSubmission, VisitRsvp). All legacy models use managed = False and
exact db_table names.
"""

import uuid

from django.db import models

from .workflow import WorkflowStatus


# =============================================================================
# LEGACY PRISMA-OWNED MODELS (managed=False)
# =============================================================================


class SystemConfig(models.Model):
    """Maps to Prisma model SystemConfig -> table 'SystemConfig'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField()
    description = models.CharField(max_length=2000, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
    updated_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='updatedById',
        db_constraint=False,
        related_name='system_configs',
    )

    class Meta:
        managed = True
        db_table = 'SystemConfig'
        indexes = [
            models.Index(fields=['key'], name='syscfg_key_idx'),
        ]

    def __str__(self) -> str:
        return self.key


class HeroSectionConfig(SystemConfig):
    """Proxy model for homepage hero content management.

    Filters SystemConfig to the 'site' key only — the actual source
    of hero scripture, tagline, description, and background image
    consumed by the homepage HeroSection component.

    Uses the same ``SystemConfig`` table — no duplicate storage.
    """

    class Meta:
        proxy = True
        verbose_name = 'Hero Section'
        verbose_name_plural = 'Hero Section'

    def __str__(self) -> str:
        return 'Hero Section Configuration'


# =============================================================================
# ABOUT PAGE SECTION CONTENT — DEDICATED MODELS (B5.5, admin-managed)
# =============================================================================
# Replaces the B5.4 JSON proxies (AboutIntroConfig / AboutValuesConfig /
# AboutThemeConfig): every component rendered by the About page's intro,
# values and 2026 theme sections is now a first-class, admin-editable field.
# The legacy SystemConfig 'site' subkeys (welcomeMessage / values / theme2026)
# remain in the database untouched but no longer drive the About page.


class AboutWelcome(models.Model):
    """About intro — 'Welcome, Vision & Mission' (admin: About group)."""

    eyebrow = models.CharField(
        max_length=128,
        default='1 Peter 2:9',
        help_text='Small label above the heading, e.g. a scripture reference.',
    )
    title = models.CharField(max_length=255, default='Welcome to the Embassy')
    vision_label = models.CharField(
        max_length=64,
        default='our Vision',
        help_text='Rendered after an em dash under the vision quote.',
    )
    vision_text = models.TextField()
    mission_label = models.CharField(
        max_length=64,
        default='Our Mission',
        help_text='Rendered after an em dash under the mission quote.',
    )
    mission_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Welcome, Vision & Mission'
        verbose_name_plural = 'Welcome, Vision & Mission'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title or 'Welcome, Vision & Mission'


class AboutValuesSection(models.Model):
    """'Our Values' section shell — heading + subtitle (cards are AboutValue)."""

    heading = models.CharField(max_length=128, default='Our Values')
    subtitle = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Our Values'
        verbose_name_plural = 'Our Values'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.heading or 'Our Values'


class AboutValue(models.Model):
    """One 'Our Values' card (managed inline under the Our Values section)."""

    section = models.ForeignKey(
        AboutValuesSection,
        on_delete=models.CASCADE,
        related_name='values',
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    sort_order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('sort_order', 'id')
        verbose_name = 'Value'
        verbose_name_plural = 'Values'

    def __str__(self) -> str:
        return self.title


class AboutTheme(models.Model):
    """'2026 Theme' section content (admin: About group)."""

    eyebrow = models.CharField(max_length=128, default='2026 Theme')
    title = models.CharField(max_length=255)
    scripture = models.CharField(
        max_length=255,
        help_text='Scripture reference, e.g. "Zechariah 10:1".',
    )
    scripture_text = models.TextField()
    image = models.CharField(
        max_length=512,
        blank=True,
        help_text='Image path or URL, e.g. /images/posters/theme-2026-latter-rain.jpeg',
    )
    button_label = models.CharField(max_length=64, default='Join Us')
    button_url = models.CharField(max_length=512, default='/visit')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '2026 Theme'
        verbose_name_plural = '2026 Theme'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title


class SermonSeries(models.Model):
    """Maps to Prisma model SermonSeries -> table 'SermonSeries'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.CharField(max_length=512, db_column='imageUrl')
    sermon_count = models.IntegerField(default=0, db_column='sermonCount')
    sort_order = models.IntegerField(default=0, db_column='sortOrder')
    is_published = models.BooleanField(default=True, db_column='isPublished')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')

    class Meta:
        managed = True
        db_table = 'SermonSeries'
        indexes = [
            models.Index(fields=['is_published'], name='series_ispub_idx'),
            models.Index(fields=['sort_order'], name='series_sort_idx'),
        ]

    def __str__(self) -> str:
        return self.title


class PublicSermon(models.Model):
    """Maps to Prisma model PublicSermon -> table 'PublicSermon'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    series = models.ForeignKey(
        'content.SermonSeries',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='seriesId',
        db_constraint=False,
        related_name='sermons',
    )
    series_slug = models.CharField(max_length=255, db_column='seriesSlug')
    series_title = models.CharField(max_length=255, db_column='seriesTitle')
    scripture = models.CharField(max_length=255, null=True, blank=True)
    speaker = models.CharField(max_length=255)
    date = models.DateTimeField()
    video_url = models.CharField(max_length=512, db_column='videoUrl')
    audio_url = models.CharField(max_length=512, null=True, blank=True, db_column='audioUrl')
    notes_url = models.CharField(max_length=512, null=True, blank=True, db_column='notesUrl')
    thumbnail_url = models.CharField(max_length=512, db_column='thumbnailUrl')
    duration = models.CharField(max_length=64, null=True, blank=True)
    tags = models.JSONField(default=list)
    is_published = models.BooleanField(default=True, db_column='isPublished')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')

    class Meta:
        managed = True
        db_table = 'PublicSermon'
        indexes = [
            models.Index(fields=['series_slug'], name='sermon_serislug_idx'),
            models.Index(fields=['is_published'], name='sermon_ispub_idx'),
            models.Index(fields=['date'], name='sermon_date_idx'),
        ]

    def __str__(self) -> str:
        return self.title


class WebsiteLeader(models.Model):
    """Maps to Prisma model WebsiteLeader -> table 'WebsiteLeader'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    bio = models.TextField()
    photo_url = models.CharField(max_length=512, db_column='photoUrl')
    sort_order = models.IntegerField(default=0, db_column='sortOrder')
    social = models.JSONField(null=True, blank=True)
    is_published = models.BooleanField(default=True, db_column='isPublished')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')

    class Meta:
        managed = True
        db_table = 'WebsiteLeader'
        indexes = [
            models.Index(fields=['sort_order'], name='leader_sort_idx'),
        ]

    def __str__(self) -> str:
        return self.name


class WebsiteTestimonial(models.Model):
    """Maps to Prisma model WebsiteTestimonial -> table 'WebsiteTestimonial'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.TextField()
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, null=True, blank=True)
    photo_url = models.CharField(max_length=512, null=True, blank=True, db_column='photoUrl')
    sort_order = models.IntegerField(default=0, db_column='sortOrder')
    is_published = models.BooleanField(default=True, db_column='isPublished')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')

    class Meta:
        managed = True
        db_table = 'WebsiteTestimonial'
        indexes = [
            models.Index(fields=['sort_order'], name='testi_sort_idx'),
        ]

    def __str__(self) -> str:
        return self.name


class WebsiteAcademyModule(models.Model):
    """Maps to Prisma model WebsiteAcademyModule -> table 'WebsiteAcademyModule'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.CharField(max_length=255)
    lessons_count = models.IntegerField(db_column='lessonsCount')
    duration = models.CharField(max_length=64)
    sort_order = models.IntegerField(default=0, db_column='sortOrder')
    is_published = models.BooleanField(default=True, db_column='isPublished')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')

    class Meta:
        managed = True
        db_table = 'WebsiteAcademyModule'
        indexes = [
            models.Index(fields=['sort_order'], name='academy_sort_idx'),
        ]

    def __str__(self) -> str:
        return self.title


class ContactSubmission(models.Model):
    """Maps to Prisma model ContactSubmission -> table 'ContactSubmission'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=64, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')

    class Meta:
        managed = True
        db_table = 'ContactSubmission'
        indexes = [
            models.Index(fields=['created_at'], name='contactsub_creat_idx'),
        ]

    def __str__(self) -> str:
        return f'Contact from {self.name}'


class VisitRsvp(models.Model):
    """Maps to Prisma model VisitRsvp -> table 'VisitRsvp'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=64)
    email = models.CharField(max_length=255, null=True, blank=True)
    party_size = models.IntegerField(default=1, db_column='partySize')
    first_visit = models.BooleanField(default=True, db_column='firstVisit')
    visit_date = models.DateTimeField(null=True, blank=True, db_column='visitDate')
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=32, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')

    class Meta:
        managed = True
        db_table = 'VisitRsvp'
        indexes = [
            models.Index(fields=['created_at'], name='rsvp_created_idx'),
            models.Index(fields=['status'], name='rsvp_status_idx'),
        ]

    def __str__(self) -> str:
        return f'RSVP {self.name}'


# =============================================================================
# DJANGO-OWNED CMS MODELS (managed=True)
# =============================================================================


class GlobalSettings(models.Model):
    """Church-wide operational settings. Singleton pattern enforced at app level."""

    church_name = models.CharField(max_length=255)
    church_short_name = models.CharField(max_length=64, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=64, null=True, blank=True)
    whatsapp = models.CharField(max_length=64, null=True, blank=True)
    address = models.CharField(max_length=512, null=True, blank=True)
    city = models.CharField(max_length=128, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)
    mpesa_till = models.CharField(max_length=32, null=True, blank=True)
    mpesa_paybill = models.CharField(max_length=32, null=True, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    academy_url = models.URLField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Global Settings'
        verbose_name_plural = 'Global Settings'

    def __str__(self) -> str:
        return self.church_name


class HomepageSettings(models.Model):
    """Homepage hero configuration. Singleton pattern enforced at app level."""

    hero_title = models.CharField(max_length=255, null=True, blank=True, help_text='Main hero heading text')
    hero_subtitle = models.CharField(max_length=512, null=True, blank=True, help_text='Hero subtitle beneath the heading')
    hero_scripture = models.TextField(null=True, blank=True, help_text='Hero scripture verse text')
    hero_scripture_reference = models.CharField(max_length=128, null=True, blank=True, help_text='Scripture reference (e.g. 1 Peter 2:9)')
    hero_background_image = models.URLField(max_length=512, null=True, blank=True, help_text='URL or path to hero background image')
    hero_cta_text = models.CharField(max_length=128, null=True, blank=True, help_text='Primary CTA button text')
    hero_cta_url = models.URLField(max_length=512, null=True, blank=True, help_text='Primary CTA button URL')
    hero_secondary_cta_text = models.CharField(max_length=128, null=True, blank=True, default='Watch a Sermon', help_text='Secondary CTA button text')
    hero_secondary_cta_url = models.URLField(max_length=512, null=True, blank=True, default='/sermons', help_text='Secondary CTA button URL')
    cta_heading = models.CharField(max_length=255, null=True, blank=True, default='Join Us This Sunday', help_text='CTA banner heading')
    cta_title = models.CharField(max_length=255, null=True, blank=True, default="You're Invited", help_text='CTA banner title')
    cta_description = models.TextField(null=True, blank=True, help_text='CTA banner description text')
    cta_button_text = models.CharField(max_length=128, null=True, blank=True, default='Plan Your Visit', help_text='CTA primary button text')
    cta_button_url = models.URLField(max_length=512, null=True, blank=True, default='/visit', help_text='CTA primary button URL')
    cta_secondary_button_text = models.CharField(max_length=128, null=True, blank=True, default='Watch a Sermon', help_text='CTA secondary button text')
    cta_secondary_button_url = models.URLField(max_length=512, null=True, blank=True, default='/sermons', help_text='CTA secondary button URL')
    cta_location = models.CharField(max_length=255, null=True, blank=True, default='Thika, Kenya', help_text='Church location for CTA banner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Homepage Settings'
        verbose_name_plural = 'Homepage Settings'

    def __str__(self) -> str:
        return 'Homepage Settings'


class ChurchProfile(models.Model):
    """Church identity and narrative. Singleton pattern enforced at app level."""

    mission = models.TextField(null=True, blank=True)
    vision = models.TextField(null=True, blank=True)
    welcome_message = models.TextField(null=True, blank=True)
    pastor_message = models.TextField(null=True, blank=True)
    about_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Church Profile'
        verbose_name_plural = 'Church Profile'

    def __str__(self) -> str:
        return 'Church Profile'


class ContentType(models.TextChoices):
    """ContentBlock category choices for low-frequency content."""
    BELIEF = 'BELIEF', 'Belief'
    VALUE = 'VALUE', 'Value'
    FAQ = 'FAQ', 'Frequently Asked Question'
    EXPECTATION = 'EXPECTATION', 'What to Expect'
    PAGE_SECTION = 'PAGE_SECTION', 'Page Section Copy'
    THEME = 'THEME', 'Annual Theme'


class ContentBlock(models.Model):
    """Replace excessive low-frequency models with categorized content blocks."""

    key = models.CharField(max_length=128, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    content_type = models.CharField(
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.PAGE_SECTION,
        db_index=True,
    )
    display_order = models.IntegerField(default=0)
    is_rich_text = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Content Block'
        verbose_name_plural = 'Content Blocks'
        indexes = [
            models.Index(fields=['key'], name='contentblock_key_idx'),
            models.Index(fields=['content_type'], name='contentblock_type_idx'),
            models.Index(fields=['display_order'], name='contentblock_order_idx'),
        ]

    def __str__(self) -> str:
        return self.key


class HomepageSection(models.Model):
    """Future-ready homepage section visibility and ordering control."""

    section_name = models.CharField(max_length=128, unique=True)
    enabled = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Homepage Section'
        verbose_name_plural = 'Homepage Sections'
        indexes = [
            models.Index(fields=['display_order'], name='homesection_order_idx'),
            models.Index(fields=['enabled'], name='homesection_enabled_idx'),
        ]

    def __str__(self) -> str:
        return self.section_name


class HomepageLatestSermon(PublicSermon):
    """Proxy model for homepage latest sermon management.

    Uses the same ``PublicSermon`` table — no duplicate storage.
    The admin for this model filters to only the single most recently
    published sermon (by date descending), matching the homepage
    API/frontend logic.
    """

    class Meta:
        proxy = True
        verbose_name = 'Latest Sermon'
        verbose_name_plural = 'Latest Sermon'


class PastorProfile(models.Model):
    """CMS-managed pastor profile for the homepage Pastor Section."""

    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    image = models.CharField(max_length=512)
    biography = models.TextField()
    cta_text = models.CharField(max_length=255, blank=True, default='Learn More')
    cta_url = models.CharField(max_length=512, blank=True, default='/about')
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Pastor Profile'
        verbose_name_plural = 'Pastor Profiles'
        indexes = [
            models.Index(fields=['is_active'], name='pastor_active_idx'),
            models.Index(fields=['display_order'], name='pastor_order_idx'),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self):
        """Enforce only one active pastor profile at a time."""
        from django.core.exceptions import ValidationError
        if self.is_active:
            # Check if there's another active profile
            active_profiles = PastorProfile.objects.filter(is_active=True)
            if self.pk:
                active_profiles = active_profiles.exclude(pk=self.pk)
            if active_profiles.exists():
                raise ValidationError('Only one PastorProfile can be active at a time.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class DayOfWeek(models.TextChoices):
    MONDAY = 'MONDAY', 'Monday'
    TUESDAY = 'TUESDAY', 'Tuesday'
    WEDNESDAY = 'WEDNESDAY', 'Wednesday'
    THURSDAY = 'THURSDAY', 'Thursday'
    FRIDAY = 'FRIDAY', 'Friday'
    SATURDAY = 'SATURDAY', 'Saturday'
    SUNDAY = 'SUNDAY', 'Sunday'


class PlatformChoices(models.TextChoices):
    PHYSICAL = 'physical', 'Physical'
    ONLINE = 'online', 'Online'


class ServiceTime(models.Model):
    """Service time entries -- single authoritative source for Service Times UI."""

    name = models.CharField(max_length=128, help_text="Display name, e.g. 'Sunday Online Service'")
    day = models.CharField(max_length=12, choices=DayOfWeek.choices)
    time = models.CharField(
        max_length=64,
        help_text="Display string, e.g. '6:00 AM - 8:00 AM' or 'TBD'",
    )
    platform = models.CharField(
        max_length=12,
        choices=PlatformChoices.choices,
        default=PlatformChoices.PHYSICAL,
    )
    location = models.CharField(max_length=512, null=True, blank=True)
    link = models.URLField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=512, null=True, blank=True, help_text='Image path or URL')
    is_published = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Legacy field -- kept for backward compatibility, not used by the UI
    label = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        managed = True
        verbose_name = 'Service Time'
        verbose_name_plural = 'Service Times'
        indexes = [
            models.Index(fields=['display_order'], name='servicetime_order_idx'),
            models.Index(fields=['day'], name='servicetime_day_idx'),
            models.Index(fields=['is_published'], name='servicetime_published_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.name} - {self.get_day_display()} {self.time}'


class SectionPage(models.TextChoices):
    """Public site pages that own renderable sections."""
    HOMEPAGE = 'homepage', 'Home'
    ABOUT = 'about', 'About'
    EVENTS = 'events', 'Events'
    VISIT = 'visit', 'Visit'
    SERMONS = 'sermons', 'Sermons'
    SERIES = 'series', 'Series'
    GIVE = 'give', 'Give'
    PRAYER = 'prayer', 'Prayer'
    CONTACT = 'contact', 'Contact'


class SiteSection(models.Model):
    """Admin visibility toggle for one rendered section on one page.

    Rows are auto-created from ``content.sections_registry.SECTION_REGISTRY``
    (``ensure_registered``). This model controls visibility ONLY — page layout
    order remains code-owned. Disabling hides the section from the public site;
    nothing is deleted and re-enabling restores it.
    """
    page = models.CharField(
        max_length=32,
        choices=SectionPage.choices,
        default=SectionPage.HOMEPAGE,
    )
    key = models.SlugField(
        max_length=64,
        help_text="Section identifier, e.g. 'hero' (registry-controlled)",
    )
    title = models.CharField(max_length=128, help_text='Admin label, e.g. "Hero Section"')
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        unique_together = (('page', 'key'),)
        ordering = ('page', 'id')  # registry seed order = admin list order
        verbose_name = 'Page Section'
        verbose_name_plural = 'Page Sections'

    def __str__(self) -> str:
        return f'{self.get_page_display()} - {self.title}'


# ---------------------------------------------------------------------------
# Per-page admin proxies (D3): state-only, same SiteSection table.
# Each proxy's toggles are grouped under that page's admin card — mirroring
# the HomepageLatestSermon/HomepageUpcomingEvent proxy precedent.
# ---------------------------------------------------------------------------

class HomepageSections(SiteSection):
    """Homepage section toggles (admin presentation proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'


class AboutSections(SiteSection):
    """About page section toggles (admin presentation proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'


class EventsSections(SiteSection):
    """Events page section toggles (admin presentation proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'


# =============================================================================
# VISIT PAGE SECTION CONTENT — DEDICATED MODELS (admin-managed)
# =============================================================================
# Mirrors the B5.5 About pattern: one admin entry per Visit section (page
# order), each holding the section's full component set. The public API
# renders the most recently updated record, so the latest admin edit is
# always what the site shows. Section on/off remains the VisitSections
# toggles (/api/sections) — no duplicate switches.


class VisitHeroVariant(models.TextChoices):
    WARM = 'warm', 'Warm'
    CELESTIAL = 'celestial', 'Celestial'
    PARCHMENT = 'parchment', 'Parchment'


class VisitHero(models.Model):
    """Visit 'Page Hero' section content (admin: Visit group)."""

    title = models.CharField(max_length=255, default="You're Welcome Here")
    subtitle = models.TextField(
        blank=True,
        default='Everything you need to know for your first visit to Royal Priesthood Embassy in Thika, Kenya.',
    )
    scripture = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Small label above the heading. Leave blank to hide.',
    )
    variant = models.CharField(
        max_length=16,
        choices=VisitHeroVariant.choices,
        default=VisitHeroVariant.WARM,
        help_text='Background register. Warm matches the current page.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Page Hero'
        verbose_name_plural = 'Page Hero'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title or 'Page Hero'


class VisitLocation(models.Model):
    """Visit 'Location & Map' section content (admin: Visit group)."""

    eyebrow = models.CharField(max_length=128, default='Find Us')
    title = models.CharField(max_length=255, default='Visit Us in Thika')
    description = models.TextField(
        default='We meet at Voice of Grace, behind Spoonzoom in Thika. '
                'Look for the hospitality team at the entrance — they will '
                'guide you to parking and seating.',
    )
    button_label = models.CharField(max_length=64, default='Get Directions')
    button_url = models.CharField(
        max_length=512,
        default='https://maps.app.goo.gl/PLHU6uvwqJHPG9PD6',
    )
    map_embed_url = models.CharField(
        max_length=1024,
        default='https://maps.google.com/maps?q=Voice+of+Grace+Behind+Spoonzoom+Thika+Kenya&output=embed',
        help_text='iframe src for the embedded Google map.',
    )
    map_title = models.CharField(
        max_length=255,
        default='Royal Priesthood Embassy location map',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Location & Map'
        verbose_name_plural = 'Location & Map'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title or 'Location & Map'


class VisitExpectSection(models.Model):
    """'What to Expect' section shell — eyebrow + title (cards are VisitExpectStep)."""

    eyebrow = models.CharField(max_length=128, default='First Visit?')
    title = models.CharField(max_length=255, default='What to Expect')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'What to Expect'
        verbose_name_plural = 'What to Expect'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title or 'What to Expect'


class VisitExpectStepIcon(models.TextChoices):
    MUSIC = 'music', 'Music (worship note)'
    BOOK_OPEN = 'book-open', 'Book (teaching)'
    USERS = 'users', 'Users (community)'
    TRENDING_UP = 'trending-up', 'Trending Up (growth)'


class VisitExpectStep(models.Model):
    """One 'What to Expect' card (managed inline under the section)."""

    section = models.ForeignKey(
        VisitExpectSection,
        on_delete=models.CASCADE,
        related_name='steps',
    )
    step = models.CharField(max_length=128, help_text='Card title, e.g. Arrive.')
    description = models.TextField()
    icon = models.CharField(
        max_length=16,
        choices=VisitExpectStepIcon.choices,
        default=VisitExpectStepIcon.USERS,
    )
    sort_order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('sort_order', 'id')
        verbose_name = 'Expect Step'
        verbose_name_plural = 'Expect Steps'

    def __str__(self) -> str:
        return self.step


class VisitFaqSection(models.Model):
    """'Frequently Asked Questions' section shell — heading (rows are VisitFaq)."""

    title = models.CharField(max_length=255, default='Frequently Asked Questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FAQs'
        verbose_name_plural = 'FAQs'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title or 'FAQs'


class VisitFaq(models.Model):
    """One FAQ row (managed inline under the section)."""

    section = models.ForeignKey(
        VisitFaqSection,
        on_delete=models.CASCADE,
        related_name='faqs',
    )
    question = models.CharField(max_length=512)
    answer = models.TextField()
    sort_order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('sort_order', 'id')
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self) -> str:
        return self.question


class VisitRsvpSection(models.Model):
    """RSVP form copy (admin: Visit group). Submissions stay in VisitRsvp."""

    heading = models.CharField(max_length=255, default='RSVP for Your Visit')
    subheading = models.TextField(
        blank=True,
        default="Let us know you're coming so our hospitality team can greet you personally.",
    )
    submit_label = models.CharField(max_length=64, default='Confirm RSVP')
    success_title = models.CharField(max_length=255, default="You're on the list!")
    success_message = models.TextField(
        blank=True,
        default='Our hospitality team has received your RSVP and will prepare a warm welcome for you.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'RSVP Form Copy'
        verbose_name_plural = 'RSVP Form Copy'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.heading or 'RSVP Form Copy'


class VisitComingSunday(models.Model):
    """'I Am Coming This Sunday' CTA banner (admin: Visit group)."""

    title = models.CharField(max_length=255, default='I Am Coming This Sunday')
    description = models.TextField(
        blank=True,
        default="Questions before you visit? Reach out — we're happy to help.",
    )
    button_label = models.CharField(max_length=64, default='Contact Us')
    button_url = models.CharField(max_length=512, default='#rsvp')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'I Am Coming This Sunday'
        verbose_name_plural = 'I Am Coming This Sunday'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title or 'I Am Coming This Sunday'


class VisitSections(SiteSection):
    """Visit page section toggles (admin presentation proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'


class SermonsSections(SiteSection):
    """Sermons page section toggles (admin presentation proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'


# =============================================================================
# SERMONS PAGE SECTION CONTENT — DEDICATED MODELS (admin-managed)
# =============================================================================
# B5.8 — mirrors the B5.7 Visit pattern: one admin entry per Sermons section
# (page order), each holding the section's full component set. Singletons are
# rendered latest-record-wins; section on/off stays on the SermonsSections
# toggles (/api/sections) — no duplicate switches.


class SermonsHeroRegister(models.TextChoices):
    WARM = 'warm', 'Warm'
    CELESTIAL = 'celestial', 'Celestial'
    PARCHMENT = 'parchment', 'Parchment'


class SermonsHero(models.Model):
    """Sermons 'Page Hero' image banner (admin: Sermons group)."""

    image = models.CharField(
        max_length=512,
        default='/images/Thumbnail_final.jpg',
        help_text='Banner image path or URL, e.g. /images/Thumbnail_final.jpg',
    )
    image_alt = models.CharField(max_length=255, default='Latest Teaching')
    label = models.CharField(
        max_length=64,
        default='Latest sermon',
        help_text='Large label on the left of the banner.',
    )
    preacher = models.CharField(max_length=255, default='Pst Charles Muchemi')
    title = models.CharField(max_length=255, default='Emotional Intelligence')
    button_label = models.CharField(max_length=64, default='Watch Sermon →')
    button_url = models.CharField(max_length=512, default='/sermons')
    register = models.CharField(
        max_length=16,
        choices=SermonsHeroRegister.choices,
        default=SermonsHeroRegister.CELESTIAL,
        help_text='Background register. Celestial matches the current page.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Page Hero'
        verbose_name_plural = 'Page Hero'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title or 'Page Hero'


class SermonsBrowseSection(models.Model):
    """'Browse by Series' heading (pills stay data-driven from /api/series)."""

    heading = models.CharField(max_length=255, default='Browse by Series')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Browse by Series'
        verbose_name_plural = 'Browse by Series'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.heading or 'Browse by Series'


class SermonsGridSection(models.Model):
    """'All Sermons' grid heading + empty state (admin: Sermons group)."""

    heading = models.CharField(max_length=255, default='All Sermons')
    empty_text = models.CharField(
        max_length=255,
        default='No sermons available yet.',
        help_text='Shown when no sermons are published.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'All Sermons'
        verbose_name_plural = 'All Sermons'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.heading or 'All Sermons'


class SermonDetailCopy(models.Model):
    """Shared copy on every /sermons/[slug] detail page (admin: Sermons group).

    Per-sermon data (title, speaker, description, video URL) stays on
    PublicSermon — this record only holds the fixed labels around it.
    """

    video_note = models.CharField(
        max_length=255,
        default='Watch this teaching on our YouTube channel',
        help_text='Note inside the video placeholder.',
    )
    watch_button_label = models.CharField(
        max_length=64,
        default='Watch on YouTube',
        help_text='Primary button label (rendered under the video and in the buttons row).',
    )
    secondary_button_label = models.CharField(
        max_length=64,
        default='Kingdom Formation',
        help_text='Secondary button label next to Watch on YouTube.',
    )
    secondary_button_url = models.CharField(max_length=512, default='/academy')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sermon Detail Copy'
        verbose_name_plural = 'Sermon Detail Copy'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.video_note or 'Sermon Detail Copy'


class SermonsRelatedSection(models.Model):
    """'Related Sermons' heading on sermon detail pages (admin: Sermons group)."""

    heading = models.CharField(max_length=255, default='Related Sermons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Related Sermons'
        verbose_name_plural = 'Related Sermons'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.heading or 'Related Sermons'


# =============================================================================
# PARTNER (GIVE) PAGE SECTION CONTENT — DEDICATED MODELS (admin-managed)
# =============================================================================
# Every component rendered by /give is a first-class, admin-editable field.
# Page key stays 'give'; the admin card label is 'Partner' (see GiveSections
# and HomepageGroupedAdminSite.PARTNER_MODELS). Singleton sections return the
# most recently updated record (About B5.5 / Visit B5.7 / Sermons B5.8
# precedent) so the page always reflects the latest admin edit.
#
# GiveMpesaSection (till_number / account_name) is the canonical source for
# the /give page. The legacy GlobalSettings.mpesa_till and SystemConfig
# 'site'.giving keys remain in the database untouched for backwards
# compatibility but no longer drive the Partner page.


class GiveHeroRegister(models.TextChoices):
    WARM = 'warm', 'Warm'
    CELESTIAL = 'celestial', 'Celestial'
    PARCHMENT = 'parchment', 'Parchment'


class GiveHero(models.Model):
    """'Page Hero' — every rendered component of the give page-hero section."""

    title = models.CharField(max_length=255, default='Give')
    subtitle = models.TextField(
        blank=True,
        default='Your generosity fuels community outreach, global missions, and the daily work of the Kingdom Embassy.',
    )
    scripture = models.CharField(
        max_length=255,
        blank=True,
        default='2 Corinthians 9:7',
        help_text='Small label above the heading. Leave blank to hide.',
    )
    register = models.CharField(
        max_length=16,
        choices=GiveHeroRegister.choices,
        default=GiveHeroRegister.WARM,
        help_text='Background register. Warm matches the current page.',
    )
    image = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text='Optional banner image path or URL. Leave blank for no image.',
    )
    image_alt = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Page Hero'
        verbose_name_plural = 'Page Hero'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title or 'Page Hero'


class GiveWhySection(models.Model):
    """'Why We Give' intro copy (admin: Partner group)."""

    eyebrow = models.CharField(
        max_length=128,
        blank=True,
        default='',
        help_text='Small label above the heading. Leave blank to hide.',
    )
    heading = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Section heading. Leave blank to hide.',
    )
    body = models.TextField(
        default='We give because God first gave — generously, sacrificially, '
        'and with joy. Your giving is an act of worship and partnership in '
        'advancing the Gospel. Every contribution, whether large or small, '
        'makes a Kingdom impact in Thika and beyond.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Why We Give'
        verbose_name_plural = 'Why We Give'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.heading or 'Why We Give'


class GiveMpesaSection(models.Model):
    """'M-Pesa Giving' card — canonical till/account source for /give."""

    eyebrow = models.CharField(max_length=128, default='M-Pesa Giving')
    till_number = models.CharField(
        max_length=32,
        default='8598004',
        help_text='M-Pesa Till number shown in large type.',
    )
    till_caption = models.CharField(max_length=64, default='Till Number')
    account_name = models.CharField(max_length=255, default='Salome Njuguna Waruguru')
    instructions = models.TextField(
        blank=True,
        default='Go to M-Pesa → Lipa na M-Pesa → Buy Goods and Services → Enter Till Number',
    )
    button_label = models.CharField(max_length=64, default='Need Help Giving?')
    button_url = models.CharField(max_length=512, default='/contact')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'M-Pesa Giving'
        verbose_name_plural = 'M-Pesa Giving'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return f'{self.eyebrow} — {self.till_number}'


class GiveAllocationSection(models.Model):
    """'Where Your Giving Goes' heading (cards stay data-driven)."""

    heading = models.CharField(max_length=255, default='Where Your Giving Goes')
    subtitle = models.TextField(
        blank=True,
        default='',
        help_text='Optional subheading. Leave blank to hide (matches current page).',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Where Giving Goes'
        verbose_name_plural = 'Where Giving Goes'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.heading or 'Where Giving Goes'


class GiveAllocationItem(models.Model):
    """One 'Where Your Giving Goes' card."""

    section = models.ForeignKey(
        GiveAllocationSection,
        on_delete=models.CASCADE,
        related_name='items',
    )
    title = models.CharField(max_length=128, help_text='Card title, e.g. Community Programs.')
    percentage = models.CharField(
        max_length=16,
        default='',
        blank=True,
        help_text='Share label, e.g. 35%. Leave blank to hide.',
    )
    description = models.TextField()
    image = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text='Optional card image path or URL. Leave blank for no image.',
    )
    image_alt = models.CharField(max_length=255, blank=True, default='')
    sort_order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Allocation Item'
        verbose_name_plural = 'Allocation Items'
        ordering = ('sort_order', 'id')

    def __str__(self) -> str:
        return f'{self.title} ({self.percentage})' if self.percentage else self.title


# =============================================================================
# Contact page section content (dedicated models)
# =============================================================================


class ContactHeroRegister(models.TextChoices):
    WARM = 'warm', 'Warm'
    CELESTIAL = 'celestial', 'Celestial'
    PARCHMENT = 'parchment', 'Parchment'


class ContactHero(models.Model):
    """'Page Hero' — every rendered component of the contact page-hero section."""

    title = models.CharField(max_length=255, default='Contact Us')
    subtitle = models.TextField(
        blank=True,
        default="We'd love to hear from you. Reach out with questions, "
        'prayer requests, or to plan your visit.',
    )
    scripture = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Small label above the heading. Leave blank to hide.',
    )
    register = models.CharField(
        max_length=16,
        choices=ContactHeroRegister.choices,
        default=ContactHeroRegister.PARCHMENT,
        help_text='Background register. Parchment matches the current page.',
    )
    image = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text='Optional banner image path or URL. Leave blank for no image.',
    )
    image_alt = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Page Hero'
        verbose_name_plural = 'Page Hero'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.title or 'Page Hero'


class ContactDetailsSection(models.Model):
    """'Contact Details' left-column copy (admin: Contact group).

    Blank address/email fields fall back to the canonical ``SystemConfig``
    ``site`` keys (``site.contact.email`` / ``site.address.*``) so existing
    content keeps rendering until an override is saved here.
    """

    email_heading = models.CharField(max_length=64, default='Email')
    email_address = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Contact email. Leave blank to use the site default.',
    )
    location_heading = models.CharField(max_length=64, default='Location')
    street = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Street line. Leave blank to use the site default.',
    )
    city = models.CharField(
        max_length=128,
        blank=True,
        default='',
        help_text='City. Leave blank to use the site default.',
    )
    country = models.CharField(
        max_length=128,
        blank=True,
        default='',
        help_text='Country. Leave blank to use the site default.',
    )
    maps_url = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text='Get Directions URL. Leave blank to use the site default.',
    )
    directions_label = models.CharField(max_length=64, default='Get Directions →')
    social_heading = models.CharField(max_length=64, default='Social Media')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Details'
        verbose_name_plural = 'Contact Details'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.email_heading or 'Contact Details'


class ContactSocialLink(models.Model):
    """One published social link under 'Contact Details'."""

    section = models.ForeignKey(
        ContactDetailsSection,
        on_delete=models.CASCADE,
        related_name='social_links',
    )
    network = models.CharField(
        max_length=64,
        help_text='Network key, e.g. instagram, facebook, youtube.',
    )
    label = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text='Display label. Leave blank to use the capitalized network.',
    )
    url = models.CharField(max_length=512)
    sort_order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Social Link'
        verbose_name_plural = 'Social Links'
        ordering = ('sort_order', 'id')

    def __str__(self) -> str:
        return f'{self.network} — {self.url}'


class ContactFormSection(models.Model):
    """'Send a Message' form copy — every rendered string (admin: Contact group)."""

    heading = models.CharField(max_length=255, default='Send a Message')
    name_label = models.CharField(max_length=64, default='Name')
    email_label = models.CharField(max_length=64, default='Email')
    phone_label = models.CharField(max_length=64, default='Phone (optional)')
    message_label = models.CharField(max_length=64, default='Message')
    submit_label = models.CharField(max_length=64, default='Send Message')
    sending_label = models.CharField(max_length=64, default='Sending…')
    success_message = models.TextField(default="Message sent! We'll be in touch soon.")
    error_message = models.TextField(
        default='Something went wrong. Please email us directly.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Form'
        verbose_name_plural = 'Contact Form'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.heading or 'Contact Form'


class SeriesSections(SiteSection):
    """Series page section toggles (admin presentation proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'


class GiveSections(SiteSection):
    """Partner page section toggles (admin presentation proxy, page key 'give').

    Visible label is 'Partner' (matching the public site nav) while the stored
    page key stays 'give' — a display-only alias, so no migration is required.
    """

    class Meta:
        proxy = True
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'

    def get_page_display(self) -> str:
        """Admin-facing page label; stored key remains 'give' (no migration)."""
        return 'Partner'


class PrayerSections(SiteSection):
    """Prayer page section toggles (admin presentation proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'


class ContactSections(SiteSection):
    """Contact page section toggles (admin presentation proxy)."""

    class Meta:
        proxy = True
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
