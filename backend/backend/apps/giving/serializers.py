"""Serializers for the giving domain (read + write)."""

from rest_framework import serializers

from .models import GivingTransaction


class GivingTransactionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GivingTransaction
        fields = (
            'id', 'member', 'household', 'amount_cents', 'currency', 'method', 'fund',
            'reference', 'status', 'mpesa_request_id', 'mpesa_callback_data',
            'failure_reason', 'is_recurring', 'recurring_frequency', 'recurring_end_date',
            'completed_at', 'created_at', 'updated_at', 'created_by',
        )
        read_only_fields = fields


class GivingTransactionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GivingTransaction
        fields = (
            'id', 'member', 'household', 'amount_cents', 'currency', 'method', 'fund',
            'reference', 'status', 'mpesa_request_id', 'mpesa_callback_data',
            'failure_reason', 'is_recurring', 'recurring_frequency', 'recurring_end_date',
            'completed_at', 'created_by',
        )
        read_only_fields = ('id',)