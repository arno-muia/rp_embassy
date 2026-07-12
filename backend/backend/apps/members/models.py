"""Members domain models — mapped 1:1 to the existing PostgreSQL schema.

Source of truth: apps/web/prisma/schema.prisma (Member, Household, HouseholdMember).
All models use managed = False and exact db_table names.
"""

import uuid

from django.db import models


class Gender(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'


class MaritalStatus(models.TextChoices):
    SINGLE = 'SINGLE', 'Single'
    MARRIED = 'MARRIED', 'Married'
    DIVORCED = 'DIVORCED', 'Divorced'
    WIDOWED = 'WIDOWED', 'Widowed'


class DiscipleshipLevel(models.TextChoices):
    SEEKER = 'SEEKER', 'Seeker'
    NEW_BELIEVER = 'NEW_BELIEVER', 'New Believer'
    DISCIPLE = 'DISCIPLE', 'Disciple'
    LEADER = 'LEADER', 'Leader'
    MINISTER = 'MINISTER', 'Minister'


class MemberStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    TRANSFERRED = 'TRANSFERRED', 'Transferred'
    DECEASED = 'DECEASED', 'Deceased'


class HouseholdRole(models.TextChoices):
    HEAD = 'HEAD', 'Head'
    SPOUSE = 'SPOUSE', 'Spouse'
    CHILD = 'CHILD', 'Child'
    EXTENDED = 'EXTENDED', 'Extended'


class HouseholdStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'


class Member(models.Model):
    """Maps to Prisma model Member -> table 'Member'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255, db_column='firstName')
    last_name = models.CharField(max_length=255, db_column='lastName')
    email = models.CharField(max_length=255, null=True, blank=True, unique=True)
    phone = models.CharField(max_length=64, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    date_of_birth = models.DateTimeField(null=True, blank=True, db_column='dateOfBirth')
    marital_status = models.CharField(
        max_length=20, choices=MaritalStatus.choices, null=True, blank=True, db_column='maritalStatus'
    )
    membership_date = models.DateTimeField(null=True, blank=True, db_column='membershipDate')
    baptism_date = models.DateTimeField(null=True, blank=True, db_column='baptismDate')
    discipleship_level = models.CharField(
        max_length=20,
        choices=DiscipleshipLevel.choices,
        default=DiscipleshipLevel.SEEKER,
        db_column='discipleshipLevel',
    )
    spiritual_gifts = models.CharField(max_length=2000, null=True, blank=True, default='', db_column='spiritualGifts')
    ministry_teams = models.CharField(max_length=2000, null=True, blank=True, default='', db_column='ministryTeams')
    visitor = models.BooleanField(default=False, db_column='visitor')
    status = models.CharField(
        max_length=20, choices=MemberStatus.choices, default=MemberStatus.ACTIVE, db_column='status'
    )
    household = models.ForeignKey(
        'members.Household',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='householdId',
        db_constraint=False,
        related_name='members',
    )
    user = models.OneToOneField(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='userId',
        db_constraint=False,
        related_name='member',
        unique=True,
    )
    consent_given = models.BooleanField(default=False, db_column='consentGiven')
    consent_date = models.DateTimeField(null=True, blank=True, db_column='consentDate')
    consent_version = models.CharField(max_length=50, null=True, blank=True, db_column='consentVersion')
    profile_image_url = models.CharField(max_length=512, null=True, blank=True, db_column='profileImageUrl')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
    deleted_at = models.DateTimeField(null=True, blank=True, db_column='deletedAt')
    created_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='createdById',
        db_constraint=False,
        related_name='created_members',
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='updatedById',
        db_constraint=False,
        related_name='updated_members',
    )

    class Meta:
        managed = False
        db_table = 'Member'
        indexes = [
            models.Index(fields=['household'], name='member_house_idx'),
            models.Index(fields=['email'], name='member_email_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'


class Household(models.Model):
    """Maps to Prisma model Household -> table 'Household'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household_name = models.CharField(max_length=255, null=True, blank=True, db_column='householdName')
    address = models.JSONField(null=True, blank=True)
    phone = models.CharField(max_length=64, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    anniversary_date = models.DateTimeField(null=True, blank=True, db_column='anniversaryDate')
    status = models.CharField(
        max_length=20, choices=HouseholdStatus.choices, default=HouseholdStatus.ACTIVE, db_column='status'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
    deleted_at = models.DateTimeField(null=True, blank=True, db_column='deletedAt')
    created_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='createdById',
        db_constraint=False,
        related_name='created_households',
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='updatedById',
        db_constraint=False,
        related_name='updated_households',
    )

    class Meta:
        managed = False
        db_table = 'Household'
        indexes = [
            models.Index(fields=['status'], name='household_status_idx'),
        ]

    def __str__(self) -> str:
        return self.household_name or str(self.id)


class HouseholdMember(models.Model):
    """Maps to Prisma model HouseholdMember -> table 'HouseholdMember'.

    memberId is @unique in Prisma, so it is used as the Django primary key.
    """

    member_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='memberId')
    household = models.ForeignKey(
        'members.Household',
        on_delete=models.DO_NOTHING,
        db_column='householdId',
        db_constraint=False,
        related_name='household_members',
    )
    role = models.CharField(
        max_length=20, choices=HouseholdRole.choices, default=HouseholdRole.EXTENDED
    )
    can_pick_up = models.BooleanField(default=False, db_column='canPickUp')
    is_primary_contact = models.BooleanField(default=False, db_column='isPrimaryContact')
    joined_at = models.DateTimeField(auto_now_add=True, db_column='joinedAt')

    class Meta:
        managed = False
        db_table = 'HouseholdMember'
        indexes = [
            models.Index(fields=['member_id'], name='hmember_member_idx'),
            models.Index(fields=['household'], name='hmember_house_idx'),
        ]

    def __str__(self) -> str:
        return f'HouseholdMember {self.member_id}'