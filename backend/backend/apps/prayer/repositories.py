"""Repository layer for the prayer domain.

Repository pattern only — query abstraction, no business logic.
"""

from django.db import models

from .models import PrayerSubmission


class PrayerSubmissionRepository:
    model = PrayerSubmission

    @classmethod
    def get_queryset(cls):
        return PrayerSubmission.objects.all()

    @classmethod
    def get_by_id(cls, submission_id):
        return PrayerSubmission.objects.filter(id=submission_id).first()

    @classmethod
    def public(cls):
        return PrayerSubmission.objects.filter(anonymous=False)