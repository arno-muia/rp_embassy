"""Custom DRF permissions for the academy authorization layer."""

from rest_framework import permissions

from .academy_access import AcademyAccess


class IsAcademyAuthorized(permissions.BasePermission):
    """Allows access only to authenticated users with an active AcademyAccess grant.

    This permission decouples academy access from Member.status, User.role,
    or DiscipleshipLevel.  Future role expansions (Student, Teacher, Leader,
    Pastor, Administrator) are supported by simply creating AcademyAccess
    records for those users.
    """

    message = 'You do not have authorized access to the Academy.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return AcademyAccess.objects.filter(
            user_id=user.id, is_active=True
        ).exists()