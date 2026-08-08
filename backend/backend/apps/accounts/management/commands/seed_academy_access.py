"""Management command to seed AcademyAccess grants.

Initial population grants AcademyAccess to users linked to ACTIVE members.
This is a one-time seeding step — the Academy authorization logic itself does
NOT hardcode Member.status checks.  Future grants for Students, Teachers,
Leaders, Pastors, or Administrators can be added via admin or future commands
without changing the authorization logic.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from backend.apps.accounts.academy_access import AcademyAccess
from backend.apps.accounts.models import User
from backend.apps.members.models import Member, MemberStatus


class Command(BaseCommand):
    help = (
        'Seed AcademyAccess grants for users linked to ACTIVE members. '
        'This is a one-time initial population; future grants can be added '
        'without changing Academy authorization logic.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without writing to the database.',
        )
        parser.add_argument(
            '--note',
            type=str,
            default='Initial seed: active member',
            help='Note to attach to each seeded AcademyAccess record.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        note = options['note']

        # Find users linked to ACTIVE members.
        active_member_users = User.objects.filter(
            member__status=MemberStatus.ACTIVE,
            is_active=True,
        ).distinct()

        created_count = 0
        skipped_count = 0

        for user in active_member_users:
            exists = AcademyAccess.objects.filter(
                user_id=user.id, is_active=True
            ).exists()
            if exists:
                skipped_count += 1
                continue
            if not dry_run:
                AcademyAccess.objects.create(
                    user_id=user.id,
                    note=note,
                )
            created_count += 1

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no records written.'))
        self.stdout.write(self.style.SUCCESS(
            f'AcademyAccess seed complete: {created_count} created, '
            f'{skipped_count} already had access.'
        ))