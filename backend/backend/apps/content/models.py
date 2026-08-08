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
