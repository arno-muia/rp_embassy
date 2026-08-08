"""Events domain models — mapped 1:1 to PostgreSQL.

Source of truth: apps/web/prisma/schema.prisma (ChurchEvent, EventRegistration).
All legacy models use managed = False and exact db_table names.
New Django-owned models use managed = True.
"""

import uuid

from django.db import models

from backend.apps.content.workflow import WorkflowStatus, Severity


# =============================================================================
# ENUMS
# =============================================================================


class ChurchEventType(models.TextChoices):
    SERVICE = 'SERVICE', 'Service'
    FELLOWSHIP = 'FELLOWSHIP', 'Fellowship'
    OUTREACH = 'OUTREACH', 'Outreach'
    CONFERENCE = 'CONFERENCE', 'Conference'
    FUNDRAISER = 'FUNDRAISER', 'Fundraiser'
    OTHER = 'OTHER', 'Other'


class ChurchEventStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PUBLISHED = 'PUBLISHED', 'Published'
    CANCELLED = 'CANCELLED', 'Cancelled'
    COMPLETED = 'COMPLETED', 'Completed'


class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PAID = 'PAID', 'Paid'
    WAIVED = 'WAIVED', 'Waived'


# =============================================================================
# LEGACY PRISMA-OWNED MODELS (managed=False)
# =============================================================================


class ChurchEvent(models.Model):
    """Maps to Prisma model ChurchEvent -> table 'ChurchEvent'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=20, choices=ChurchEventType.choices)
    start_date_time = models.DateTimeField(db_column='startDateTime')
    end_date_time = models.DateTimeField(null=True, blank=True, db_column='endDateTime')
    location = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.CharField(max_length=512, null=True, blank=True, db_column='imageUrl')
    gallery_url = models.CharField(max_length=512, null=True, blank=True, db_column='galleryUrl')
    registration_required = models.BooleanField(default=False, db_column='registrationRequired')
    max_attendees = models.IntegerField(null=True, blank=True, db_column='maxAttendees')
    cost_cents = models.IntegerField(null=True, blank=True, db_column='costCents')
    registration_open_date = models.DateTimeField(null=True, blank=True, db_column='registrationOpenDate')
    status = models.CharField(
        max_length=20, choices=ChurchEventStatus.choices, default=ChurchEventStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
    created_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='createdById',
        db_constraint=False,
        related_name='created_events',
    )

    class Meta:
        managed = True
        db_table = 'ChurchEvent'
        indexes = [
            models.Index(fields=['start_date_time'], name='event_start_idx'),
            models.Index(fields=['status'], name='event_status_idx'),
            models.Index(fields=['type'], name='event_type_idx'),
        ]

    def __str__(self) -> str:
        return self.title


class HomepageUpcomingEvent(ChurchEvent):
    """Proxy model for homepage-filtered event management.

    Uses the same ``ChurchEvent`` table — no duplicate storage.
    The admin for this model filters to PUBLISHED events only,
    matching the homepage API/frontend logic.
    """

    class Meta:
        proxy = True
        verbose_name = 'Upcoming Event'
        verbose_name_plural = 'Upcoming Events'


class EventRegistration(models.Model):
    """Maps to Prisma model EventRegistration -> table 'EventRegistration'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        'members.Member',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='memberId',
        db_constraint=False,
        related_name='event_registrations',
    )
    event = models.ForeignKey(
        'events.ChurchEvent',
        on_delete=models.DO_NOTHING,
        db_column='eventId',
        db_constraint=False,
        related_name='registrations',
    )
    walk_in_name = models.CharField(max_length=255, null=True, blank=True, db_column='walkInName')
    walk_in_phone = models.CharField(max_length=64, null=True, blank=True, db_column='walkInPhone')
    walk_in_email = models.CharField(max_length=255, null=True, blank=True, db_column='walkInEmail')
    registration_date = models.DateTimeField(auto_now_add=True, db_column='registrationDate')
    attended = models.BooleanField(null=True, blank=True)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, null=True, blank=True, db_column='paymentStatus'
    )
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')

    class Meta:
        managed = True
        db_table = 'EventRegistration'
        indexes = [
            models.Index(fields=['event'], name='reg_event_idx'),
            models.Index(fields=['member'], name='reg_member_idx'),
            models.Index(fields=['registration_date'], name='reg_regdate_idx'),
        ]

    def __str__(self) -> str:
        return f'Registration {self.id}'


# =============================================================================
# DJANGO-OWNED CMS MODELS (managed=True)
# =============================================================================


class Announcement(models.Model):
    """Time-windowed, audience-targeted homepage banners with severity levels."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    body = models.TextField(null=True, blank=True)
    severity = models.CharField(
        max_length=10, choices=Severity.choices, default=Severity.INFO
    )
    workflow_status = models.CharField(
        max_length=20,
        choices=WorkflowStatus.choices,
        default=WorkflowStatus.DRAFT,
    )
    display_from = models.DateTimeField(null=True, blank=True)
    display_until = models.DateTimeField(null=True, blank=True)
    link_url = models.URLField(max_length=512, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        indexes = [
            models.Index(fields=['is_active', 'display_from'], name='announce_active_idx'),
            models.Index(fields=['severity'], name='announce_severity_idx'),
        ]

    def __str__(self) -> str:
        return self.title