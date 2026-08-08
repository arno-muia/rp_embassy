"""Academy authorization model.

AcademyAccess is a dedicated authorization mechanism that decouples academy
access from Member.status, User.role, or DiscipleshipLevel.  Future access
grants for Students, Teachers, Leaders, Pastors, or Administrators can be
added without changing the academy authorization logic — simply create an
AcademyAccess record for the relevant User.

The ``user_id`` and ``granted_by_id`` fields are CharField(36) to match the
Prisma-owned ``User.id`` column (text type).  This avoids FK type mismatches
while still providing efficient lookups via indexes.
"""

from django.db import models


class AcademyAccess(models.Model):
    """Grants a user access to the Academy learning portal.

    Attributes:
        user_id: The authenticated user's id (CharField(36), matches User.id).
        granted_at: Timestamp when access was granted.
        granted_by_id: Admin/user id who granted the access (nullable).
        note: Optional reason or context for the grant.
        is_active: Soft flag to revoke access without deleting the record.
    """

    user_id = models.CharField(max_length=36, db_index=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by_id = models.CharField(max_length=36, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'AcademyAccess'
        indexes = [
            models.Index(fields=['user_id', 'is_active'], name='academyaccess_user_active_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user_id'],
                condition=models.Q(is_active=True),
                name='unique_active_academy_access_per_user',
            ),
        ]

    def __str__(self) -> str:
        return f'AcademyAccess(user={self.user_id}, active={self.is_active})'