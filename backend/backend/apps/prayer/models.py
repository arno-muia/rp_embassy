"""Prayer domain models — mapped 1:1 to PostgreSQL.

Source of truth: apps/web/prisma/schema.prisma (PrayerSubmission).
All legacy models use managed = False and exact db_table names.
New Django-owned models use managed = True.
"""

import uuid

from django.db import models

from backend.apps.content.workflow import WorkflowStatus


# =============================================================================
# LEGACY PRISMA-OWNED MODELS (managed=False)
# =============================================================================


class PrayerSubmission(models.Model):
    """Maps to Prisma model PrayerSubmission -> table 'PrayerSubmission'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    request = models.TextField()
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')

    class Meta:
        managed = True
        db_table = 'PrayerSubmission'
        indexes = [
            models.Index(fields=['created_at'], name='prayer_created_idx'),
        ]

    def __str__(self) -> str:
        return f'Prayer from {self.name or "Anonymous"}'


# =============================================================================
# DJANGO-OWNED CMS MODELS (managed=True)
# =============================================================================


class PrayerRequestCategory(models.TextChoices):
    GENERAL = 'GENERAL', 'General'
    HEALING = 'HEALING', 'Healing'
    THANKSGIVING = 'THANKSGIVING', 'Thanksgiving'
    FINANCE = 'FINANCE', 'Finance'
    FAMILY = 'FAMILY', 'Family'
    SALVATION = 'SALVATION', 'Salvation'
    OTHER = 'OTHER', 'Other'


class PrayerRequestWorkflow(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    ANSWERED = 'ANSWERED', 'Answered'
    CLOSED = 'CLOSED', 'Closed'


class PrayerRequest(models.Model):
    """Moderated public prayer request. Created via admin moderation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(
        max_length=20, choices=PrayerRequestCategory.choices, default=PrayerRequestCategory.GENERAL
    )
    is_public = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    workflow_status = models.CharField(
        max_length=20,
        choices=WorkflowStatus.choices,
        default=WorkflowStatus.DRAFT,
    )
    status = models.CharField(
        max_length=20, choices=PrayerRequestWorkflow.choices, default=PrayerRequestWorkflow.ACTIVE
    )
    prayer_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Prayer Request'
        verbose_name_plural = 'Prayer Requests'
        indexes = [
            models.Index(fields=['workflow_status'], name='prayreq_wf_idx'),
            models.Index(fields=['is_public'], name='prayreq_public_idx'),
        ]

    def __str__(self) -> str:
        return self.title