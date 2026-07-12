"""Repository layer for the events domain.

Repository pattern only — query abstraction, no business logic.
"""

from django.db import models

from .models import ChurchEvent, EventRegistration


class EventRepository:
    model = ChurchEvent

    @classmethod
    def get_queryset(cls):
        return ChurchEvent.objects.select_related('created_by').all()

    @classmethod
    def get_by_id(cls, event_id):
        return ChurchEvent.objects.filter(id=event_id).first()

    @classmethod
    def published_upcoming(cls):
        return ChurchEvent.objects.filter(
            status='PUBLISHED'
        ).order_by('start_date_time')

    @classmethod
    def registrations(cls, event_id):
        return EventRegistration.objects.filter(event_id=event_id).select_related('member')


class EventRegistrationRepository:
    model = EventRegistration

    @classmethod
    def get_queryset(cls):
        return EventRegistration.objects.select_related('member', 'event').all()

    @classmethod
    def by_member(cls, member_id):
        return EventRegistration.objects.filter(member_id=member_id).select_related('event')