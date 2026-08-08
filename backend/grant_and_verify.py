"""Grant AcademyAccess to existing users and verify."""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from backend.apps.accounts.academy_access import AcademyAccess
from backend.apps.accounts.models import User

users = User.objects.filter(is_active=True)
created = 0
skipped = 0

for user in users:
    exists = AcademyAccess.objects.filter(
        user_id=user.id, is_active=True
    ).exists()
    if exists:
        skipped += 1
        continue
    AcademyAccess.objects.create(
        user_id=user.id,
        note='Direct grant: existing user (no Member record yet)',
    )
    created += 1
    print(f"  Granted AcademyAccess to: {user.email} (id={user.id})")

print(f"\nDone: {created} created, {skipped} already had access.")

# Verify
print("\n=== Verification ===")
access_records = AcademyAccess.objects.filter(is_active=True)
print(f"Active AcademyAccess records: {access_records.count()}")
for a in access_records:
    print(f"  user_id={a.user_id}, note={a.note}, is_active={a.is_active}")