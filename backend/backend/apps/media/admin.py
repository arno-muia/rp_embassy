from django.contrib import admin

from .models import MediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'mime_type', 'file_size', 'is_public',
        'usage_count', 'uploaded_at', 'created_at'
    )
    search_fields = ('title', 'alt_text', 'file_path', 'checksum')
    list_filter = ('mime_type', 'is_public', 'uploaded_at')
    list_editable = ('is_public',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
