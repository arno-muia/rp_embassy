"""Serializers for the prayer domain (read + write)."""

from rest_framework import serializers

from .models import PrayerSubmission


class PrayerSubmissionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerSubmission
        fields = ('id', 'name', 'request', 'anonymous', 'created_at')
        read_only_fields = fields


class PrayerSubmissionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerSubmission
        fields = ('id', 'name', 'request', 'anonymous')
        read_only_fields = ('id',)