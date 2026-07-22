from django.contrib import admin

from .models import ChurchEvent, EventRegistration, Announcement


@admin.register(ChurchEvent)
class ChurchEventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'type', 'status', 'start_date_time', 'end_date_time',
        'location', 'registration_required', 'created_by', 'updated_at'
    )
    search_fields = ('title', 'description', 'location', 'speaker', 'agenda')
    list_filter = ('type', 'status', 'registration_required', 'start_date_time')
    list_editable = ('status', 'registration_required')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-start_date_time', '-updated_at')
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'type', 'status', 'location', 'image_url', 'agenda')
        }),
        ('Schedule', {
            'fields': ('start_date_time', 'end_date_time', 'registration_open_date', 'expiry_date')
        }),
        ('Registration', {
            'fields': ('registration_required', 'max_attendees', 'cost_cents', 'payment_details')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'event', 'member', 'walk_in_name', 'registration_date',
        'attended', 'payment_status', 'updated_at'
    )
    search_fields = (
        'event__title', 'member__first_name', 'member__last_name',
        'walk_in_name', 'walk_in_email', 'walk_in_phone'
    )
    list_filter = ('payment_status', 'attended', 'registration_date', 'event__type')
    list_editable = ('attended', 'payment_status')
    readonly_fields = ('registration_date', 'created_at', 'updated_at')
    ordering = ('-registration_date',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'severity', 'workflow_status', 'is_active',
        'priority', 'display_from', 'display_until', 'updated_at'
    )
    search_fields = ('title', 'body')
    list_filter = ('severity', 'workflow_status', 'is_active', 'display_from')
    list_editable = ('is_active', 'priority')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Announcement Details', {
            'fields': ('title', 'body', 'severity', 'workflow_status', 'link_url')
        }),
        ('Display Settings', {
            'fields': ('display_from', 'display_until', 'priority', 'is_active')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    ordering = ('-priority', '-display_from')
