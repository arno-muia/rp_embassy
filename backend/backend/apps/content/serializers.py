"""Serializers for the content domain (read + write)."""

from rest_framework import serializers

from .models import (
    ContactSubmission,
    PublicSermon,
    SermonSeries,
    SystemConfig,
    VisitRsvp,
    WebsiteAcademyModule,
    WebsiteLeader,
    WebsiteTestimonial,
)


class SystemConfigReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ('id', 'key', 'value', 'description', 'updated_at', 'updated_by')
        read_only_fields = fields


class SystemConfigWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ('id', 'key', 'value', 'description')
        read_only_fields = ('id',)


class SermonSeriesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SermonSeries
        fields = (
            'id', 'slug', 'title', 'description', 'image_url', 'sermon_count',
            'sort_order', 'is_published', 'created_at', 'updated_at',
        )
        read_only_fields = fields


class SermonSeriesWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SermonSeries
        fields = ('id', 'slug', 'title', 'description', 'image_url', 'sermon_count', 'sort_order', 'is_published')
        read_only_fields = ('id',)


class PublicSermonReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicSermon
        fields = (
            'id', 'slug', 'title', 'description', 'series', 'series_slug', 'series_title',
            'scripture', 'speaker', 'date', 'video_url', 'audio_url', 'notes_url',
            'thumbnail_url', 'duration', 'tags', 'is_published', 'created_at', 'updated_at',
        )
        read_only_fields = fields


class PublicSermonWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicSermon
        fields = (
            'id', 'slug', 'title', 'description', 'series', 'series_slug', 'series_title',
            'scripture', 'speaker', 'date', 'video_url', 'audio_url', 'notes_url',
            'thumbnail_url', 'duration', 'tags', 'is_published',
        )
        read_only_fields = ('id',)


class WebsiteLeaderReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteLeader
        fields = ('id', 'name', 'role', 'bio', 'photo_url', 'sort_order', 'social', 'is_published', 'created_at', 'updated_at')
        read_only_fields = fields


class WebsiteLeaderWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteLeader
        fields = ('id', 'name', 'role', 'bio', 'photo_url', 'sort_order', 'social', 'is_published')
        read_only_fields = ('id',)


class WebsiteTestimonialReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteTestimonial
        fields = ('id', 'quote', 'name', 'role', 'photo_url', 'sort_order', 'is_published', 'created_at', 'updated_at')
        read_only_fields = fields


class WebsiteTestimonialWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteTestimonial
        fields = ('id', 'quote', 'name', 'role', 'photo_url', 'sort_order', 'is_published')
        read_only_fields = ('id',)


class WebsiteAcademyModuleReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteAcademyModule
        fields = ('id', 'title', 'description', 'instructor', 'lessons_count', 'duration', 'sort_order', 'is_published', 'created_at', 'updated_at')
        read_only_fields = fields


class WebsiteAcademyModuleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteAcademyModule
        fields = ('id', 'title', 'description', 'instructor', 'lessons_count', 'duration', 'sort_order', 'is_published')
        read_only_fields = ('id',)


class ContactSubmissionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = ('id', 'name', 'email', 'phone', 'message', 'created_at')
        read_only_fields = fields


class ContactSubmissionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = ('id', 'name', 'email', 'phone', 'message')
        read_only_fields = ('id',)


class VisitRsvpReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitRsvp
        fields = ('id', 'name', 'phone', 'email', 'party_size', 'first_visit', 'visit_date', 'notes', 'status', 'created_at')
        read_only_fields = fields


class VisitRsvpWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitRsvp
        fields = ('id', 'name', 'phone', 'email', 'party_size', 'first_visit', 'visit_date', 'notes', 'status')
        read_only_fields = ('id',)