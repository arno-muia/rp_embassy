from django.apps import AppConfig


class ContentConfig(AppConfig):
    default = True
    name = 'backend.apps.content'
    label = 'content'
    verbose_name = 'Public Website Content'