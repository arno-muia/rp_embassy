"""Giving domain models — mapped 1:1 to PostgreSQL.

Source of truth: apps/web/prisma/schema.prisma (GivingTransaction).
All models use managed = False and exact db_table names.
Note: GivingCampaign is a P2 (deferred) model and is intentionally not implemented here.
"""

import uuid

from django.db import models


class GivingMethod(models.TextChoices):
    M_PESA = 'M_PESA', 'M-PESA'
    BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
    CASH = 'CASH', 'Cash'
    CHEQUE = 'CHEQUE', 'Cheque'
    CARD = 'CARD', 'Card'
    OTHER = 'OTHER', 'Other'


class GivingFund(models.TextChoices):
    TITHE = 'TITHE', 'Tithe'
    OFFERING = 'OFFERING', 'Offering'
    MISSIONS = 'MISSIONS', 'Missions'
    BUILDING = 'BUILDING', 'Building'
    SPECIAL = 'SPECIAL', 'Special'
    SEED = 'SEED', 'Seed'


class TransactionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    REFUNDED = 'REFUNDED', 'Refunded'


class RecurringFrequency(models.TextChoices):
    WEEKLY = 'WEEKLY', 'Weekly'
    MONTHLY = 'MONTHLY', 'Monthly'


class GivingTransaction(models.Model):
    """Maps to Prisma model GivingTransaction -> table 'GivingTransaction'."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        'members.Member',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='memberId',
        db_constraint=False,
        related_name='giving_transactions',
    )
    household = models.ForeignKey(
        'members.Household',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='householdId',
        db_constraint=False,
        related_name='giving_transactions',
    )
    amount_cents = models.IntegerField(db_column='amountCents')
    currency = models.CharField(max_length=8, default='KES')
    method = models.CharField(max_length=20, choices=GivingMethod.choices)
    fund = models.CharField(max_length=20, choices=GivingFund.choices)
    reference = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING
    )
    mpesa_request_id = models.CharField(max_length=255, null=True, blank=True, db_column='mpesaRequestId')
    mpesa_callback_data = models.JSONField(null=True, blank=True, db_column='mpesaCallbackData')
    failure_reason = models.TextField(null=True, blank=True, db_column='failureReason')
    is_recurring = models.BooleanField(default=False, db_column='isRecurring')
    recurring_frequency = models.CharField(
        max_length=20, choices=RecurringFrequency.choices, null=True, blank=True, db_column='recurringFrequency'
    )
    recurring_end_date = models.DateTimeField(null=True, blank=True, db_column='recurringEndDate')
    completed_at = models.DateTimeField(null=True, blank=True, db_column='completedAt')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
    created_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_column='createdById',
        db_constraint=False,
        related_name='created_transactions',
    )

    class Meta:
        managed = False
        db_table = 'GivingTransaction'
        indexes = [
            models.Index(fields=['member'], name='gtx_member_idx'),
            models.Index(fields=['household'], name='gtx_house_idx'),
            models.Index(fields=['status'], name='gtx_status_idx'),
            models.Index(fields=['fund'], name='gtx_fund_idx'),
            models.Index(fields=['created_at'], name='gtx_created_idx'),
            models.Index(fields=['mpesa_request_id'], name='gtx_mpesa_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.fund} {self.amount_cents/100:.2f} {self.currency}'