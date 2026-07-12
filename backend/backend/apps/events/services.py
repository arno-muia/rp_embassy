"""Service layer for the events domain.

Business logic only. Must use repositories — no direct ORM access, no API/serializer logic.
"""

from .repositories import EventRegistrationRepository, EventRepository


class EventService:
    @staticmethod
    def upcoming_events():
        return EventRepository.published_upcoming()

    @staticmethod
    def event_registrations(event_id):
        return EventRepository.registrations(event_id)


class RegistrationService:
    @staticmethod
    def registrations_for_member(member_id):
        return EventRegistrationRepository.by_member(member_id)