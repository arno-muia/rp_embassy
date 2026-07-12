"""Serializers for the events domain (read + write)."""

from rest_framework import serializers

from .models import ChurchEvent, EventRegistration


class ChurchEventReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchEvent
        fields = (
            'id', 'title', 'description', 'type', 'start_date_time', 'end_date_time',
            'location', 'image_url', 'gallery_url', 'registration_required',
            'max_attendees', 'cost_cents', 'registration_open_date', 'status',
            'created_at', 'updated_at', 'created_by',
        )
        read_only_fields = fields


class ChurchEventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchEvent
        fields = (
            'id', 'title', 'description', 'type', 'start_date_time', 'end_date_time',
            'location', 'image_url', 'gallery_url', 'registration_required',
            'max_attendees', 'cost_cents', 'registration_open_date', 'status',
        )
        read_only_fields = ('id',)


class EventRegistrationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = (
            'id', 'member', 'event', 'walk_in_name', 'walk_in_phone', 'walk_in_email',
            'registration_date', 'attended', 'payment_status', 'notes',
            'created_at', 'updated_at',
        )
        read_only_fields = fields


class EventRegistrationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = (
            'id', 'member', 'event', 'walk_in_name', 'walk_in_phone', 'walk_in_email',
            'attended', 'payment_status', 'notes',
        )
        read_only_fields = ('id',)