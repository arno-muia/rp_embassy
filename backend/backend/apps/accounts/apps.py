from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default = True
    name = 'backend.apps.accounts'
    label = 'accounts'
    verbose_name = 'Accounts & Identity'