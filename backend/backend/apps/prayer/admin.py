from django.contrib import admin

from .models import PrayerRequest, PrayerSubmission


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'is_public', 'workflow_status',
        'status', 'prayer_count', 'created_at'
    )
    search_fields = ('title', 'content')
    list_filter = ('category', 'is_public', 'workflow_status', 'status', 'created_at')
    list_editable = ('is_public', 'status')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(PrayerSubmission)
class PrayerSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'request', 'anonymous', 'created_at')
    search_fields = ('name', 'request')
    list_filter = ('anonymous', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
