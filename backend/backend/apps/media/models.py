"""Media domain models — schema only, no upload logic, no storage integration.

All image/asset references across the platform point to MediaAsset.
"""

import uuid

from django.db import models


class MediaAsset(models.Model):
    """Centralized managed media asset. Schema only — no upload logic."""

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=1024, null=True, blank=True)
    alt_text = models.CharField(max_length=512, blank=True, default='')
    mime_type = models.CharField(max_length=128, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    checksum = models.CharField(max_length=64, null=True, blank=True)
    focal_point_x = models.FloatField(default=0.5)
    focal_point_y = models.FloatField(default=0.5)
    is_public = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = 'Media Asset'
        verbose_name_plural = 'Media Assets'
        indexes = [
            models.Index(fields=['mime_type'], name='media_mime_idx'),
            models.Index(fields=['checksum'], name='media_checksum_idx'),
            models.Index(fields=['is_public'], name='media_public_idx'),
        ]

    def __str__(self) -> str:
        return self.title