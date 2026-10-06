"""Serializers for the content domain (read + write)."""

from rest_framework import serializers

from .models import (
    AboutTheme,
    ContactDetailsSection,
    ContactFormSection,
    ContactHero,
    ContactSocialLink,
    GiveAllocationItem,
    GiveWhySection,
    GiveMpesaSection,
    GiveHero,
    GiveAllocationSection,
    AboutValue,
    AboutValuesSection,
    AboutWelcome,
    ChurchProfile,
    ContactSubmission,
    ContentBlock,
    HomepageSection,
    HomepageSettings,
    PastorProfile,
    PublicSermon,
    SermonDetailCopy,
    SermonSeries,
    SermonsBrowseSection,
    SermonsGridSection,
    SermonsHero,
    SermonsRelatedSection,
    ServiceTime,
    SystemConfig,
    VisitComingSunday,
    VisitExpectSection,
    VisitExpectStep,
    VisitFaq,
    VisitFaqSection,
    VisitHero,
    VisitLocation,
    VisitRsvp,
    VisitRsvpSection,
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


# =============================================================================
# About page section content (B5.5 — dedicated models)
# =============================================================================


class AboutWelcomeReadSerializer(serializers.ModelSerializer):
    """'Welcome, Vision & Mission' (About intro) — every rendered component."""

    class Meta:
        model = AboutWelcome
        fields = (
            'eyebrow', 'title',
            'vision_label', 'vision_text',
            'mission_label', 'mission_text',
        )
        read_only_fields = fields


class AboutValueReadSerializer(serializers.ModelSerializer):
    """One 'Our Values' card."""

    class Meta:
        model = AboutValue
        fields = ('id', 'title', 'description', 'sort_order')
        read_only_fields = fields


class AboutThemeReadSerializer(serializers.ModelSerializer):
    """'2026 Theme' — every rendered component."""

    class Meta:
        model = AboutTheme
        fields = (
            'eyebrow', 'title', 'scripture', 'scripture_text',
            'image', 'button_label', 'button_url',
        )
        read_only_fields = fields


# =============================================================================
# Visit page section content (dedicated models)
# =============================================================================


class VisitHeroReadSerializer(serializers.ModelSerializer):
    """'Page Hero' — every rendered component."""

    class Meta:
        model = VisitHero
        fields = ('title', 'subtitle', 'scripture', 'variant')
        read_only_fields = fields


class VisitLocationReadSerializer(serializers.ModelSerializer):
    """'Location & Map' — every rendered component."""

    class Meta:
        model = VisitLocation
        fields = (
            'eyebrow', 'title', 'description',
            'button_label', 'button_url',
            'map_embed_url', 'map_title',
        )
        read_only_fields = fields


class VisitExpectStepReadSerializer(serializers.ModelSerializer):
    """One 'What to Expect' card."""

    class Meta:
        model = VisitExpectStep
        fields = ('id', 'step', 'description', 'icon', 'sort_order')
        read_only_fields = fields


class VisitFaqReadSerializer(serializers.ModelSerializer):
    """One FAQ row."""

    class Meta:
        model = VisitFaq
        fields = ('id', 'question', 'answer', 'sort_order')
        read_only_fields = fields


class VisitRsvpSectionReadSerializer(serializers.ModelSerializer):
    """RSVP form copy — every rendered component."""

    class Meta:
        model = VisitRsvpSection
        fields = (
            'heading', 'subheading', 'submit_label',
            'success_title', 'success_message',
        )
        read_only_fields = fields


class VisitComingSundayReadSerializer(serializers.ModelSerializer):
    """'I Am Coming This Sunday' — every rendered component."""

    class Meta:
        model = VisitComingSunday
        fields = ('title', 'description', 'button_label', 'button_url')
        read_only_fields = fields


# =============================================================================
# Sermons page section content (dedicated models)
# =============================================================================


class SermonsHeroReadSerializer(serializers.ModelSerializer):
    """Sermons 'Page Hero' — every rendered component."""

    class Meta:
        model = SermonsHero
        fields = (
            'image', 'image_alt', 'label', 'preacher', 'title',
            'button_label', 'button_url', 'register',
        )
        read_only_fields = fields


class SermonsBrowseSectionReadSerializer(serializers.ModelSerializer):
    """'Browse by Series' heading."""

    class Meta:
        model = SermonsBrowseSection
        fields = ('heading',)
        read_only_fields = fields


class SermonsGridSectionReadSerializer(serializers.ModelSerializer):
    """'All Sermons' grid heading + empty state."""

    class Meta:
        model = SermonsGridSection
        fields = ('heading', 'empty_text')
        read_only_fields = fields


class SermonDetailCopyReadSerializer(serializers.ModelSerializer):
    """Shared copy on /sermons/[slug] — every rendered component."""

    class Meta:
        model = SermonDetailCopy
        fields = (
            'video_note', 'watch_button_label',
            'secondary_button_label', 'secondary_button_url',
        )
        read_only_fields = fields


class SermonsRelatedSectionReadSerializer(serializers.ModelSerializer):
    """'Related Sermons' heading on sermon detail pages."""

    class Meta:
        model = SermonsRelatedSection
        fields = ('heading',)
        read_only_fields = fields


# =============================================================================
# Partner (Give) page section content (dedicated models)
# =============================================================================


class GiveHeroReadSerializer(serializers.ModelSerializer):
    """Give 'Page Hero' — every rendered component."""

    class Meta:
        model = GiveHero
        fields = ('title', 'subtitle', 'scripture', 'register', 'image', 'image_alt')
        read_only_fields = fields


class GiveWhySectionReadSerializer(serializers.ModelSerializer):
    """'Why We Give' copy — every rendered component."""

    class Meta:
        model = GiveWhySection
        fields = ('eyebrow', 'heading', 'body')
        read_only_fields = fields


class GiveMpesaSectionReadSerializer(serializers.ModelSerializer):
    """'M-Pesa Giving' card — every rendered component."""

    class Meta:
        model = GiveMpesaSection
        fields = (
            'eyebrow', 'till_number', 'till_caption', 'account_name',
            'instructions', 'button_label', 'button_url',
        )
        read_only_fields = fields


class GiveAllocationItemReadSerializer(serializers.ModelSerializer):
    """One 'Where Your Giving Goes' card."""

    class Meta:
        model = GiveAllocationItem
        fields = ('id', 'title', 'percentage', 'description', 'image', 'image_alt', 'sort_order')
        read_only_fields = fields


# =============================================================================
# Contact page section content (dedicated models)
# =============================================================================


class ContactHeroReadSerializer(serializers.ModelSerializer):
    """Contact 'Page Hero' — every rendered component."""

    class Meta:
        model = ContactHero
        fields = ('title', 'subtitle', 'scripture', 'register', 'image', 'image_alt')
        read_only_fields = fields


class ContactDetailsSectionReadSerializer(serializers.ModelSerializer):
    """'Contact Details' left-column copy — every rendered component."""

    class Meta:
        model = ContactDetailsSection
        fields = (
            'email_heading', 'email_address', 'location_heading', 'street',
            'city', 'country', 'maps_url', 'directions_label', 'social_heading',
        )
        read_only_fields = fields


class ContactSocialLinkReadSerializer(serializers.ModelSerializer):
    """One 'Contact Details' social link."""

    class Meta:
        model = ContactSocialLink
        fields = ('id', 'network', 'label', 'url', 'sort_order')
        read_only_fields = fields


class ContactFormSectionReadSerializer(serializers.ModelSerializer):
    """'Send a Message' form copy — every rendered string."""

    class Meta:
        model = ContactFormSection
        fields = (
            'heading', 'name_label', 'email_label', 'phone_label',
            'message_label', 'submit_label', 'sending_label',
            'success_message', 'error_message',
        )
        read_only_fields = fields