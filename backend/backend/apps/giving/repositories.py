"""Repository layer for the giving domain.

Repository pattern only — query abstraction, no business logic.
"""

from django.db import models

from .models import GivingTransaction


class GivingTransactionRepository:
    model = GivingTransaction

    @classmethod
    def get_queryset(cls):
        return GivingTransaction.objects.select_related('member', 'household', 'created_by').all()

    @classmethod
    def get_by_id(cls, transaction_id):
        return GivingTransaction.objects.filter(id=transaction_id).first()

    @classmethod
    def by_member(cls, member_id):
        return GivingTransaction.objects.filter(member_id=member_id).select_related('member', 'household')

    @classmethod
    def by_household(cls, household_id):
        return GivingTransaction.objects.filter(household_id=household_id).select_related('member', 'household')

    @classmethod
    def completed(cls):
        return GivingTransaction.objects.filter(status='COMPLETED')