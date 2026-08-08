from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    GlobalSettings,
    HomepageSettings,
    ChurchProfile,
    ContentBlock,
    ServiceTime,
    HomepageSection,
    SystemConfig,
    HeroSectionConfig,
    SermonSeries,
    PublicSermon,
    HomepageLatestSermon,
    WebsiteLeader,
    WebsiteTestimonial,
    WebsiteAcademyModule,
    ContactSubmission,
    VisitRsvp,
    PastorProfile,
)


# =============================================================================
# Custom AdminSite — Homepage section grouping
# =============================================================================


class HomepageGroupedAdminSite(AdminSite):
    """AdminSite that groups homepage-related models under a 'Homepage' section.

    This preserves the standard Django admin interface while providing
    a logical grouping for homepage content models. No models are moved,
    no database tables are altered, and no migrations are created.
    """

    site_header = 'RP Ministries Administration'
    site_title = 'RP Admin'
    index_title = 'Dashboard'

    # Homepage model registry — order determines display order in the section
    HOMEPAGE_GROUP = [
        ('HeroSectionConfig', 'content'),
        ('ServiceTime', 'content'),
        ('HomepageUpcomingEvent', 'events'),
        ('HomepageLatestSermon', 'content'),
        ('WebsiteTestimonial', 'content'),
        ('PastorProfile', 'content'),
    ]

    def get_app_list(self, request):
        """Return app list with grouped 'Homepage' section."""
        original = list(super().get_app_list(request))

        # Build lookup: (app_label, model_name) -> model_dict
        model_lookup = {}
        for app in original:
            app_label = app['app_label']
            for model in app['models']:
                key = (app_label, model['object_name'])
                model_lookup[key] = model

        # Extract homepage models in defined order
        homepage_models = []
        seen_keys = set()

        for model_name, app_label in self.HOMEPAGE_GROUP:
            key = (app_label, model_name)
            if key in model_lookup and key not in seen_keys:
                model_entry = dict(model_lookup[key])  # shallow copy
                # Use the model's verbose name or a readable title
                model_entry['name'] = model_entry.get('name', model_name)
                homepage_models.append(model_entry)
                seen_keys.add(key)

        # Build synthetic Homepage app
        homepage_app = {
            'name': 'Homepage',
            'app_label': 'homepage',
            'app_url': reverse('admin:index'),
            'has_module_perms': True,
            'models': homepage_models,
        }

        # Build remaining apps, filtering out models shown in Homepage
        remaining = []
        for app in original:
            filtered_models = [
                m for m in app['models']
                if (app['app_label'], m['object_name']) not in seen_keys
            ]
            if filtered_models:
                remaining.append({
                    'name': app['name'],
                    'app_label': app['app_label'],
                    'app_url': app.get('app_url', '#'),
                    'has_module_perms': app.get('has_module_perms', True),
                    'models': filtered_models,
                })

        # Insert Homepage section at the beginning (before Authentication)
        result = [homepage_app] + list(remaining)

        return result


# Replace the default admin site with our grouped version
admin.site.__class__ = HomepageGroupedAdminSite


# =============================================================================
# ModelAdmin registrations
# =============================================================================


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'email', 'phone', 'updated_at')
    search_fields = ('church_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)


@admin.register(HomepageSettings)
class HomepageSettingsAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'hero_cta_text', 'cta_heading', 'updated_at')
    search_fields = ('hero_title', 'hero_subtitle', 'cta_heading')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Hero Section', {
            'fields': (
                'hero_title', 'hero_subtitle',
                'hero_scripture', 'hero_scripture_reference',
                'hero_background_image',
                'hero_cta_text', 'hero_cta_url',
                'hero_secondary_cta_text', 'hero_secondary_cta_url',
            ),
            'description': 'Homepage hero banner content — all fields are CMS editable',
        }),
        ('CTA Banner', {
            'fields': (
                'cta_heading', 'cta_title', 'cta_description',
                'cta_button_text', 'cta_button_url',
                'cta_secondary_button_text', 'cta_secondary_button_url',
                'cta_location',
            ),
            'description': 'Call-to-action banner section content',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ChurchProfile)
class ChurchProfileAdmin(admin.ModelAdmin):
    list_display = ('mission', 'updated_at')
    search_fields = ('mission', 'vision', 'pastor_message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('key', 'title', 'content_type', 'display_order', 'is_active', 'updated_at')
    search_fields = ('key', 'title', 'content')
    list_filter = ('content_type', 'is_active', 'is_rich_text')
    list_editable = ('display_order', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('content_type', 'display_order')


@admin.register(ServiceTime)
class ServiceTimeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'day', 'time', 'platform', 'is_published', 'display_order', 'updated_at',
    )
    list_display_links = ('name',)
    search_fields = ('name', 'day', 'location', 'description')
    list_filter = ('day', 'platform', 'is_published')
    list_editable = ('display_order', 'is_published', 'platform')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('display_order', 'day')
    fieldsets = (
        ('Service Details', {
            'fields': ('name', 'day', 'time', 'platform'),
        }),
        ('Location & Link', {
            'fields': ('location', 'link'),
        }),
        ('Content', {
            'fields': ('description', 'image'),
        }),
        ('Ordering & Visibility', {
            'fields': ('display_order', 'is_published'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    list_display = ('section_name', 'enabled', 'display_order', 'updated_at')
    search_fields = ('section_name',)
    list_filter = ('enabled',)
    list_editable = ('enabled', 'display_order')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('display_order',)


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'updated_by', 'updated_at')
    search_fields = ('key', 'description', 'value')
    list_filter = ('updated_at',)
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'description')
        }),
        ('Audit', {
            'fields': ('updated_by', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    ordering = ('key',)

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields


@admin.register(HeroSectionConfig)
class HeroSectionConfigAdmin(admin.ModelAdmin):
    """Editor-friendly admin for homepage hero content.

    Filters SystemConfig to the 'site' key only — the actual source
    of hero scripture, tagline, description, and background image
    consumed by the homepage HeroSection component.
    """
    list_display = ('key', 'description', 'updated_by', 'updated_at')
    search_fields = ('key', 'description')
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Hero Content', {
            'fields': ('key', 'value', 'description'),
            'description': 'This is the actual source of hero banner content used by the homepage. Edit the JSON value to update scripture, tagline, description, and background image.',
        }),
        ('Audit', {
            'fields': ('updated_by', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Return only the 'site' config record — the hero content source."""
        qs = super().get_queryset(request)
        return qs.filter(key='site')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SermonSeries)
class SermonSeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'sort_order', 'sermon_count', 'updated_at')
    search_fields = ('title', 'slug', 'description')
    list_filter = ('is_published',)
    list_editable = ('is_published', 'sort_order')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', '-updated_at')


@admin.register(PublicSermon)
class PublicSermonAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'date', 'is_published', 'series', 'updated_at')
    search_fields = ('title', 'speaker', 'scripture', 'series_slug', 'series_title')
    list_filter = ('is_published', 'date', 'series')
    list_editable = ('is_published',)
    readonly_fields = ('created_at', 'updated_at', 'homepage_display_note')
    ordering = ('-date', '-updated_at')
    fieldsets = (
        (None, {
            'fields': ('homepage_display_note',),
        }),
        ('Sermon Details', {
            'fields': (
                'title', 'slug', 'speaker', 'date', 'scripture',
                'description', 'video_url', 'audio_url', 'thumbnail_url',
                'series', 'series_slug', 'series_title',
            ),
        }),
        ('Publication', {
            'fields': ('is_published',),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def homepage_display_note(self, obj):
        """Display a prominent note about homepage sermon behavior."""
        return format_html(
            '<div style="padding:12px 16px;background:#fff3cd;border:1px solid #ffc107;'
            'border-radius:4px;margin-bottom:8px;">'
            '<strong>Homepage Display:</strong> '
            'The homepage renders only the single most recently published sermon '
            '(ordered by <code>date</code> descending, filtered to '
            '<code>is_published=True</code>).<br>'
            'SermonSeries is <strong>not</strong> consumed by the homepage — '
            'it is only used on sermon detail pages.<br><br>'
            'To update what appears on the homepage, edit a sermon\'s '
            '<code>date</code> field or use <code>is_published</code>.'
            '</div>'
        )
    homepage_display_note.short_description = ''


@admin.register(HomepageLatestSermon)
class HomepageLatestSermonAdmin(PublicSermonAdmin):
    """Admin for the homepage's latest sermon — filtered to a single record.

    Uses the same PublicSermon table via proxy model — no duplicate storage.
    The queryset is filtered to only the most recently published sermon,
    matching the homepage API/frontend logic.
    """

    def get_queryset(self, request):
        """Return only the latest published sermon — matching homepage logic."""
        qs = super().get_queryset(request)
        latest = qs.filter(is_published=True).order_by('-date').first()
        if latest:
            return qs.filter(pk=latest.pk)
        return qs.none()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(WebsiteLeader)
class WebsiteLeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'sort_order', 'is_published', 'updated_at')
    search_fields = ('name', 'role')
    list_filter = ('is_published',)
    list_editable = ('sort_order', 'is_published')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', '-updated_at')


@admin.register(WebsiteTestimonial)
class WebsiteTestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'sort_order', 'is_published', 'updated_at')
    search_fields = ('name', 'role', 'quote')
    list_filter = ('is_published',)
    list_editable = ('sort_order', 'is_published')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', '-updated_at')


@admin.register(WebsiteAcademyModule)
class WebsiteAcademyModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'lessons_count', 'duration', 'sort_order', 'is_published', 'updated_at')
    search_fields = ('title', 'instructor', 'description')
    list_filter = ('is_published',)
    list_editable = ('sort_order', 'is_published')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', '-updated_at')


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(PastorProfile)
class PastorProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'display_order', 'is_active', 'updated_at')
    search_fields = ('name', 'title', 'biography')
    list_filter = ('is_active',)
    list_editable = ('display_order', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    ordering = ('display_order', '-is_active', 'name')
    fieldsets = (
        ('Profile', {
            'fields': ('name', 'title', 'image', 'image_preview', 'biography'),
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_url'),
        }),
        ('Ordering & Status', {
            'fields': ('display_order', 'is_active'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px;max-width:300px;" />', obj.image)
        return '(No image)'
    image_preview.short_description = 'Image Preview'


@admin.register(VisitRsvp)
class VisitRsvpAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'party_size', 'visit_date', 'status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'notes')
    list_filter = ('status', 'first_visit', 'created_at')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)