"""Serializers for the content domain (read + write)."""

from rest_framework import serializers

from .models import (
    ChurchProfile,
    ContactSubmission,
    ContentBlock,
    HomepageSection,
    HomepageSettings,
    PastorProfile,
    PublicSermon,
    SermonSeries,
    ServiceTime,
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


# =============================================================================
# CMS Model Serializers (managed=True)
# =============================================================================


class HomepageSettingsSerializer(serializers.ModelSerializer):
    """Serializer for HomepageSettings (hero + CTA configuration)."""

    class Meta:
        model = HomepageSettings
        fields = (
            'hero_title',
            'hero_subtitle',
            'hero_scripture',
            'hero_scripture_reference',
            'hero_background_image',
            'hero_cta_text',
            'hero_cta_url',
            'hero_secondary_cta_text',
            'hero_secondary_cta_url',
            'cta_heading',
            'cta_title',
            'cta_description',
            'cta_button_text',
            'cta_button_url',
            'cta_secondary_button_text',
            'cta_secondary_button_url',
            'cta_location',
        )
        read_only_fields = fields


class ChurchProfileSerializer(serializers.ModelSerializer):
    """Serializer for ChurchProfile (mission, vision, messages)."""

    class Meta:
        model = ChurchProfile
        fields = ('mission', 'vision', 'welcome_message', 'pastor_message', 'about_text')
        read_only_fields = fields


class ServiceTimeSerializer(serializers.ModelSerializer):
    """Serializer for ServiceTime — exposes every field required by the Service Times UI."""

    # Return the human-readable day name (e.g. "Sunday") instead of the raw
    # choice value (e.g. "SUNDAY") so the frontend can use it directly.
    day = serializers.CharField(source='get_day_display', read_only=True)

    class Meta:
        model = ServiceTime
        fields = (
            'id',
            'name',
            'day',
            'time',
            'platform',
            'location',
            'link',
            'description',
            'image',
            'is_published',
            'display_order',
        )
        read_only_fields = fields


class ContentBlockSerializer(serializers.ModelSerializer):
    """Serializer for ContentBlock (beliefs, values, FAQs, expectations)."""

    class Meta:
        model = ContentBlock
        fields = ('id', 'key', 'title', 'content', 'content_type', 'display_order', 'is_active')
        read_only_fields = fields


class PastorProfileSerializer(serializers.ModelSerializer):
    """Serializer for PastorProfile."""

    class Meta:
        model = PastorProfile
        fields = (
            'id', 'name', 'title', 'image', 'biography',
            'cta_text', 'cta_url', 'is_active',
        )
        read_only_fields = fields


class HomepageSectionSerializer(serializers.ModelSerializer):
    """Serializer for HomepageSection (visibility control)."""

    class Meta:
        model = HomepageSection
        fields = ('section_name', 'enabled', 'display_order')
        read_only_fields = fields