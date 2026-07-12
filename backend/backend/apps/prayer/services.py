"""Service layer for the prayer domain.

Business logic only. Must use repositories — no direct ORM access, no API/serializer logic.
"""

from .repositories import PrayerSubmissionRepository


class PrayerService:
    @staticmethod
    def all_submissions():
        return PrayerSubmissionRepository.get_queryset()

    @staticmethod
    def public_submissions():
        return PrayerSubmissionRepository.public()