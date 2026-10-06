from django import forms
from django.utils.safestring import mark_safe


class RealtimeImageUploadWidget(forms.TextInput):
    """
    Drag-and-drop real-time image upload widget for Django Admin text fields.
    Renders an interactive dropzone area, live thumbnail preview, and hidden file input.
    Uploading immediately updates the underlying text input with the media URL.
    """
    class Media:
        css = {
            'all': ('admin/css/realtime_upload.css',)
        }
        js = ('admin/js/realtime_upload.js',)

    def __init__(self, folder='general', attrs=None):
        self.folder = folder
        super().__init__(attrs=attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # Render standard text input
        text_input_html = super().render(name, value, attrs, renderer)
        val = value or ''

        # Initial preview display style
        preview_style = "display: flex;" if val else "display: none;"

        html = f"""
        <div class="realtime-upload-field" data-folder="{self.folder}">
            {text_input_html}
            <input type="file" class="realtime-upload-fileinput" accept="image/*" style="display: none;" />
            <div class="realtime-upload-dropzone">
                <svg class="realtime-upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <p class="realtime-upload-text"><strong>Click to browse</strong> or drag and drop image here</p>
                <span class="realtime-upload-subtext">JPG, PNG, WebP, AVIF up to 10MB</span>
                <div class="realtime-upload-progress">
                    <div class="realtime-upload-progress-bar"></div>
                </div>
            </div>
            <div class="realtime-upload-error"></div>
            <div class="realtime-upload-preview-container" style="{preview_style}">
                <img class="realtime-upload-preview-img" src="{val}" alt="Preview" />
                <div class="realtime-upload-preview-info">
                    <strong>Selected Image:</strong>
                    <span class="realtime-upload-preview-url">{val}</span>
                </div>
            </div>
        </div>
        """
        return mark_safe(html)
