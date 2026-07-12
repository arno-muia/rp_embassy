"""Service layer for the accounts domain.

Business logic only. Must use repositories — no direct ORM access, no API/serializer logic.
"""

from .repositories import AuditLogRepository, UserRepository


class UserService:
    """Member-facing business logic for accounts."""

    @staticmethod
    def get_active_users():
        return UserRepository.list_active()

    @staticmethod
    def get_users_by_role(role: str):
        return UserRepository.list_by_role(role)

    @staticmethod
    def is_locked(user) -> bool:
        if not user:
            return False
        if user.locked_until is None:
            return False
        from django.utils import timezone

        return user.locked_until > timezone.now()

    @staticmethod
    def requires_password_change(user) -> bool:
        return bool(user and user.must_change_password)


class AuditService:
    """Business logic for audit-trail reads."""

    @staticmethod
    def recent_for_user(user_id, limit: int = 50):
        return AuditLogRepository.list_by_user(user_id)[:limit]

    @staticmethod
    def recent_for_action(action: str, limit: int = 50):
        return AuditLogRepository.list_by_action(action)[:limit]