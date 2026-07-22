from django.contrib import admin

from .models import (
    GlobalSettings,
    HomepageSettings,
    ChurchProfile,
    ContentBlock,
    ServiceTime,
    HomepageSection,
    SystemConfig,
    SermonSeries,
    PublicSermon,
    WebsiteLeader,
    WebsiteTestimonial,
    WebsiteAcademyModule,
    ContactSubmission,
    VisitRsvp,
)


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'email', 'phone', 'updated_at')
    search_fields = ('church_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)


@admin.register(HomepageSettings)
class HomepageSettingsAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'hero_cta_text', 'updated_at')
    search_fields = ('hero_title', 'hero_subtitle')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)


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
    list_display = ('day', 'time', 'label', 'display_order', 'updated_at')
    search_fields = ('day', 'label')
    list_filter = ('day',)
    list_editable = ('display_order',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('display_order', 'day')


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

    # Exclude non-existent created_at from readonly_fields
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields


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
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date', '-updated_at')


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


@admin.register(VisitRsvp)
class VisitRsvpAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'party_size', 'visit_date', 'status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'notes')
    list_filter = ('status', 'first_visit', 'created_at')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
