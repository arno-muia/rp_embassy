from django.apps import AppConfig


class GivingConfig(AppConfig):
    default = True
    name = 'backend.apps.giving'
    label = 'giving'
    verbose_name = 'Giving & Donations'