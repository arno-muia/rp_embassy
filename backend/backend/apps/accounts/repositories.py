"""Repository layer for the accounts domain.

Repository pattern only — query abstraction, no business logic.
"""

from django.db import models

from .models import AuditLog, User


class UserRepository:
    """Query abstraction for the User table."""

    model = User

    @classmethod
    def get_queryset(cls) -> models.QuerySet:
        return User.objects.all()

    @classmethod
    def get_by_id(cls, user_id) -> User | None:
        return User.objects.filter(id=user_id).first()

    @classmethod
    def get_by_email(cls, email: str) -> User | None:
        return User.objects.filter(email__iexact=email).first()

    @classmethod
    def list_active(cls) -> models.QuerySet:
        return User.objects.filter(is_active=True)

    @classmethod
    def list_by_role(cls, role: str) -> models.QuerySet:
        return User.objects.filter(role=role)


class AuditLogRepository:
    """Query abstraction for the AuditLog table."""

    model = AuditLog

    @classmethod
    def get_queryset(cls) -> models.QuerySet:
        return AuditLog.objects.select_related('user').all()

    @classmethod
    def get_by_id(cls, log_id) -> AuditLog | None:
        return AuditLog.objects.filter(id=log_id).select_related('user').first()

    @classmethod
    def list_by_user(cls, user_id) -> models.QuerySet:
        return AuditLog.objects.filter(user_id=user_id).select_related('user')

    @classmethod
    def list_by_action(cls, action: str) -> models.QuerySet:
        return AuditLog.objects.filter(action=action).select_related('user')