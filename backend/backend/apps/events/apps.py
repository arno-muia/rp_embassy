from django.apps import AppConfig


class EventsConfig(AppConfig):
    default = True
    name = 'backend.apps.events'
    label = 'events'
    verbose_name = 'Events & Calendar'