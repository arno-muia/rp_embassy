"""Accounts domain models.

The User model is a proper Django authentication model extending
AbstractBaseUser + PermissionsMixin.  It maps to the existing PostgreSQL
"User" table (previously Prisma-owned) using db_column aliases so no
schema rename is required.

AuditLog remains Prisma-owned (managed=False).
"""

import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


# =============================================================================
# Choices
# =============================================================================


class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    HOSPITALITY = 'HOSPITALITY', 'Hospitality'
    LEADERSHIP = 'LEADERSHIP', 'Leadership'
    CELL_LEADER = 'CELL_LEADER', 'Cell Leader'
    MEMBER = 'MEMBER', 'Member'


class AuditAction(models.TextChoices):
    LOGIN = 'LOGIN', 'Login'
    LOGOUT = 'LOGOUT', 'Logout'
    PASSWORD_CHANGE = 'PASSWORD_CHANGE', 'Password Change'
    ACCOUNT_LOCKED = 'ACCOUNT_LOCKED', 'Account Locked'
    ACCOUNT_UNLOCKED = 'ACCOUNT_UNLOCKED', 'Account Unlocked'
    MEMBER_CREATE = 'MEMBER_CREATE', 'Member Create'
    MEMBER_UPDATE = 'MEMBER_UPDATE', 'Member Update'
    MEMBER_DELETE = 'MEMBER_DELETE', 'Member Delete'
    MEMBER_RESTORE = 'MEMBER_RESTORE', 'Member Restore'
    HOUSEHOLD_CREATE = 'HOUSEHOLD_CREATE', 'Household Create'
    HOUSEHOLD_UPDATE = 'HOUSEHOLD_UPDATE', 'Household Update'
    ATTENDANCE_CHECKIN = 'ATTENDANCE_CHECKIN', 'Attendance Check-in'
    SESSION_OPEN = 'SESSION_OPEN', 'Session Open'
    SESSION_CLOSE = 'SESSION_CLOSE', 'Session Close'
    GIVING_RECORD = 'GIVING_RECORD', 'Giving Record'
    GIVING_UPDATE = 'GIVING_UPDATE', 'Giving Update'
    GIVING_DELETE = 'GIVING_DELETE', 'Giving Delete'
    FUND_CREATE = 'FUND_CREATE', 'Fund Create'
    FUND_UPDATE = 'FUND_UPDATE', 'Fund Update'
    EVENT_CREATE = 'EVENT_CREATE', 'Event Create'
    EVENT_UPDATE = 'EVENT_UPDATE', 'Event Update'
    EVENT_DELETE = 'EVENT_DELETE', 'Event Delete'
    ANNOUNCEMENT_CREATE = 'ANNOUNCEMENT_CREATE', 'Announcement Create'
    ANNOUNCEMENT_UPDATE = 'ANNOUNCEMENT_UPDATE', 'Announcement Update'
    ROLE_ASSIGN = 'ROLE_ASSIGN', 'Role Assign'
    USER_INVITE = 'USER_INVITE', 'User Invite'
    USER_ACTIVATE = 'USER_ACTIVATE', 'User Activate'
    USER_DEACTIVATE = 'USER_DEACTIVATE', 'User Deactivate'
    SETTINGS_CHANGE = 'SETTINGS_CHANGE', 'Settings Change'
    EXPORT_DATA = 'EXPORT_DATA', 'Export Data'
    IMPORT_DATA = 'IMPORT_DATA', 'Import Data'
    CONSENT_COLLECTED = 'CONSENT_COLLECTED', 'Consent Collected'
    CARE_CASE_CREATE = 'CARE_CASE_CREATE', 'Care Case Create'
    CARE_CASE_UPDATE = 'CARE_CASE_UPDATE', 'Care Case Update'
    CARE_NOTE_CREATE = 'CARE_NOTE_CREATE', 'Care Note Create'
    VOLUNTEER_ASSIGN = 'VOLUNTEER_ASSIGN', 'Volunteer Assign'
    PRAYER_REQUEST_CREATE = 'PRAYER_REQUEST_CREATE', 'Prayer Request Create'
    PRAYER_REQUEST_ANSWERED = 'PRAYER_REQUEST_ANSWERED', 'Prayer Request Answered'
    COMMUNICATION_SENT = 'COMMUNICATION_SENT', 'Communication Sent'


# =============================================================================
# Manager
# =============================================================================


class UserManager(BaseUserManager):
    """Custom manager for the User model using email as the username."""

    def create_user(self, email, name, password=None, **extra_fields):
        """Create and save a regular user with email and password."""
        if not email:
            raise ValueError('Users must have an email address.')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        """Create and save a superuser with email and password."""
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        extra_fields.setdefault('must_change_password', False)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)


# =============================================================================
# User model
# =============================================================================


class User(AbstractBaseUser, PermissionsMixin):
    """Django authentication user model.

    Maps to the existing PostgreSQL ``"User"`` table using db_column
    aliases.  The ``password`` field maps to the ``passwordHash`` column
    and uses Django's built-in password hashing (PBKDF2 / bcrypt / argon2).
    """

    id = models.CharField(primary_key=True, max_length=36, editable=False)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, db_column='passwordHash')
    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.MEMBER
    )
    is_active = models.BooleanField(default=True, db_column='isActive')
    is_staff = models.BooleanField(default=False)
    must_change_password = models.BooleanField(
        default=True, db_column='mustChangePassword'
    )
    failed_login_attempts = models.IntegerField(
        default=0, db_column='failedLoginAttempts'
    )
    locked_until = models.DateTimeField(
        null=True, blank=True, db_column='lockedUntil'
    )
    last_login = models.DateTimeField(
        null=True, blank=True, db_column='lastLogin'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        managed = True
        db_table = 'User'
        indexes = [
            models.Index(fields=['role'], name='user_role_idx'),
        ]

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return self.name

    def get_short_name(self) -> str:
        return self.name


# =============================================================================
# AcademyAccess authorization model
# =============================================================================


from .academy_access import AcademyAccess  # noqa: F401


# =============================================================================
# AuditLog (Prisma-owned, unchanged)
# =============================================================================


class AuditLog(models.Model):
    """Maps to Prisma model AuditLog -> table 'AuditLog'."""

    id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='userId',
        db_constraint=False,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=40, choices=AuditAction.choices)
    entity_type = models.CharField(max_length=100, db_column='entityType')
    entity_id = models.CharField(
        max_length=255, null=True, blank=True, db_column='entityId'
    )
    details = models.JSONField(null=True, blank=True)
    ip_address = models.CharField(
        max_length=64, null=True, blank=True, db_column='ipAddress'
    )
    user_agent = models.CharField(
        max_length=512, null=True, blank=True, db_column='userAgent'
    )
    timestamp = models.DateTimeField(db_column='timestamp')

    class Meta:
        managed = False
        db_table = 'AuditLog'
        indexes = [
            models.Index(fields=['user'], name='auditlog_user_idx'),
            models.Index(fields=['action'], name='auditlog_action_idx'),
            models.Index(fields=['entity_type'], name='auditlog_entitytype_idx'),
            models.Index(fields=['timestamp'], name='auditlog_timestamp_idx'),
            models.Index(fields=['entity_id'], name='auditlog_entityid_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.action} @ {self.timestamp}'