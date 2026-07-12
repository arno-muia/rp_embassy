"""Service layer for the giving domain.

Business logic only. Must use repositories — no direct ORM access, no API/serializer logic.
"""

from django.db.models import Sum

from .repositories import GivingTransactionRepository


class GivingService:
    @staticmethod
    def member_giving(member_id):
        return GivingTransactionRepository.by_member(member_id)

    @staticmethod
    def household_giving(household_id):
        return GivingTransactionRepository.by_household(household_id)

    @staticmethod
    def total_for_member(member_id) -> int:
        agg = GivingTransactionRepository.by_member(member_id).filter(
            status='COMPLETED'
        ).aggregate(total=Sum('amount_cents'))
        return agg.get('total') or 0

    @staticmethod
    def total_for_household(household_id) -> int:
        agg = GivingTransactionRepository.by_household(household_id).filter(
            status='COMPLETED'
        ).aggregate(total=Sum('amount_cents'))
        return agg.get('total') or 0