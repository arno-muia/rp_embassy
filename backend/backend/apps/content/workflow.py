"""Shared workflow enums for the content management system.

Defined once here and imported by all apps to ensure consistency.
"""

from django.db import models


class WorkflowStatus(models.TextChoices):
    """Architecture-approved content workflow states.

    Draft → In Review → Approved → Published → Archived
    """
    DRAFT = 'DRAFT', 'Draft'
    IN_REVIEW = 'IN_REVIEW', 'In Review'
    APPROVED = 'APPROVED', 'Approved'
    PUBLISHED = 'PUBLISHED', 'Published'
    ARCHIVED = 'ARCHIVED', 'Archived'


class Severity(models.TextChoices):
    """Announcement severity levels."""
    INFO = 'INFO', 'Info'
    SUCCESS = 'SUCCESS', 'Success'
    WARNING = 'WARNING', 'Warning'
    URGENT = 'URGENT', 'Urgent'