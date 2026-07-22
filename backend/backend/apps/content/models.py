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

    hero_title = models.CharField(max_length=255, null=True, blank=True)
    hero_subtitle = models.CharField(max_length=512, null=True, blank=True)
    hero_scripture = models.TextField(null=True, blank=True)
    hero_scripture_reference = models.CharField(max_length=128, null=True, blank=True)
    hero_background_image = models.URLField(max_length=512, null=True, blank=True)
    hero_cta_text = models.CharField(max_length=128, null=True, blank=True)
    hero_cta_url = models.URLField(max_length=512, null=True, blank=True)
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


class DayOfWeek(models.TextChoices):
    MONDAY = 'MONDAY', 'Monday'
    TUESDAY = 'TUESDAY', 'Tuesday'
    WEDNESDAY = 'WEDNESDAY', 'Wednesday'
    THURSDAY = 'THURSDAY', 'Thursday'
    FRIDAY = 'FRIDAY', 'Friday'
    SATURDAY = 'SATURDAY', 'Saturday'
    SUNDAY = 'SUNDAY', 'Sunday'


class ServiceTime(models.Model):
    """Service time entries with display ordering."""

    day = models.CharField(max_length=12, choices=DayOfWeek.choices)
    time = models.TimeField()
    label = models.CharField(max_length=128)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Service Time'
        verbose_name_plural = 'Service Times'
        indexes = [
            models.Index(fields=['display_order'], name='servicetime_order_idx'),
            models.Index(fields=['day'], name='servicetime_day_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.get_day_display()} {self.time} — {self.label}'