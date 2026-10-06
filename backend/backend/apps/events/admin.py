from django.contrib import admin

from backend.apps.media.widgets import RealtimeImageUploadWidget
from .models import ChurchEvent, HomepageUpcomingEvent, EventRegistration, Announcement


@admin.register(ChurchEvent)
class ChurchEventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'type', 'status', 'start_date_time', 'end_date_time',
        'location', 'registration_required', 'created_by', 'updated_at'
    )
    search_fields = ('title', 'description', 'location')
    list_filter = ('type', 'status', 'registration_required', 'start_date_time')
    list_editable = ('status', 'registration_required')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-start_date_time', '-updated_at')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image_url':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='events')
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'type', 'status', 'location', 'image_url', 'gallery_url')
        }),
        ('Schedule', {
            'fields': ('start_date_time', 'end_date_time', 'registration_open_date')
        }),
        ('Registration', {
            'fields': ('registration_required', 'max_attendees', 'cost_cents')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# =============================================================================
# Homepage Upcoming Events — read-only filtered view of homepage-eligible events
# =============================================================================


@admin.register(HomepageUpcomingEvent)
class HomepageUpcomingEventsAdmin(admin.ModelAdmin):
    """Read-only admin showing only events eligible for homepage rendering.

    Uses the same filtering logic as the homepage API/frontend:
    - status='PUBLISHED'
    - ordered by start_date_time ascending

    This is a presentation-layer filter only.  No data is moved, no
    duplicate table is created.
    """
    model = ChurchEvent
    list_display = (
        'title', 'type', 'start_date_time', 'end_date_time',
        'location', 'updated_at'
    )
    search_fields = ('title', 'description', 'location')
    list_filter = ('type', 'start_date_time')
    readonly_fields = (
        'title', 'description', 'type', 'status', 'start_date_time',
        'end_date_time', 'location', 'image_url', 'registration_required',
        'max_attendees', 'cost_cents', 'registration_open_date',
        'created_by', 'created_at', 'updated_at',
    )
    ordering = ('start_date_time',)

    def get_queryset(self, request):
        """Return only PUBLISHED events — same filter as EventRepository.published_upcoming()."""
        qs = super().get_queryset(request)
        return qs.filter(status='PUBLISHED').order_by('start_date_time')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True  # Read-only but still viewable

    def get_actions(self, request):
        return []  # Remove all action checkboxes


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