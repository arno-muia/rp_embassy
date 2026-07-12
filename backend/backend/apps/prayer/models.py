"""Prayer domain models — mapped 1:1 to PostgreSQL.

Source of truth: apps/web/prisma/schema.prisma (PrayerSubmission).
All models use managed = False and exact db_table names.
Note: PrayerRequest is a P2 (deferred) model and is intentionally not implemented here.
"""

import uuid

from django.db import models


class PrayerSubmission(models.Model):
    """Maps to Prisma model PrayerSubmission -> table 'PrayerSubmission'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    request = models.TextField()
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')

    class Meta:
        managed = False
        db_table = 'PrayerSubmission'
        indexes = [
            models.Index(fields=['created_at'], name='prayer_created_idx'),
        ]

    def __str__(self) -> str:
        return f'Prayer from {self.name or "Anonymous"}'