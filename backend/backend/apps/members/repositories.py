"""Repository layer for the members domain.

Repository pattern only — query abstraction, no business logic.
"""

from django.db import models

from .models import Household, HouseholdMember, Member


class MemberRepository:
    model = Member

    @classmethod
    def get_queryset(cls) -> models.QuerySet:
        return Member.objects.select_related('household', 'user').all()

    @classmethod
    def get_by_id(cls, member_id) -> Member | None:
        return Member.objects.select_related('household', 'user').filter(id=member_id).first()

    @classmethod
    def get_by_email(cls, email: str) -> Member | None:
        return Member.objects.filter(email__iexact=email).first()

    @classmethod
    def get_by_user(cls, user_id) -> Member | None:
        return Member.objects.filter(user_id=user_id).first()

    @classmethod
    def list_active(cls) -> models.QuerySet:
        return Member.objects.filter(status='ACTIVE')

    @classmethod
    def list_by_household(cls, household_id) -> models.QuerySet:
        return Member.objects.filter(household_id=household_id)


class HouseholdRepository:
    model = Household

    @classmethod
    def get_queryset(cls) -> models.QuerySet:
        return Household.objects.all()

    @classmethod
    def get_by_id(cls, household_id) -> Household | None:
        return Household.objects.filter(id=household_id).first()

    @classmethod
    def list_active(cls) -> models.QuerySet:
        return Household.objects.filter(status='ACTIVE')


class HouseholdMemberRepository:
    model = HouseholdMember

    @classmethod
    def get_queryset(cls) -> models.QuerySet:
        return HouseholdMember.objects.select_related('household', 'member').all()

    @classmethod
    def list_by_household(cls, household_id) -> models.QuerySet:
        return HouseholdMember.objects.filter(household_id=household_id).select_related('member')