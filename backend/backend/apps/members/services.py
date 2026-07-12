"""Service layer for the members domain.

Business logic only. Must use repositories — no direct ORM access, no API/serializer logic.
"""

from .repositories import HouseholdMemberRepository, HouseholdRepository, MemberRepository


class MemberService:
    @staticmethod
    def active_members():
        return MemberRepository.list_active()

    @staticmethod
    def household_members(household_id):
        return MemberRepository.list_by_household(household_id)


class HouseholdService:
    @staticmethod
    def active_households():
        return HouseholdRepository.list_active()

    @staticmethod
    def members_of(household_id):
        return HouseholdMemberRepository.list_by_household(household_id)