"""Update the existing RPADMIN superuser with email and Django password."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Set email + password on the RPADMIN superuser'

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            name='RPADMIN',
            defaults={
                'email': 'muiaarnold12@gmail.com',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'role': 'ADMIN',
                'must_change_password': False,
            },
        )
        user.email = 'muiaarnold12@gmail.com'
        user.set_password('RP@2026!')
        user.save()
        self.stdout.write(
            self.style.SUCCESS(
                f'Superuser updated: muiaarnold12@gmail.com / RP@2026! '
                f'({"created" if created else "updated"})'
            )
        )