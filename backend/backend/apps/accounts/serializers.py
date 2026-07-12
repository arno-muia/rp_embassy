"""Serializers for the accounts domain (read + write)."""

from rest_framework import serializers

from .models import AuditLog, User


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'role',
            'is_active',
            'must_change_password',
            'failed_login_attempts',
            'locked_until',
            'last_login',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class UserWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password_hash',
            'name',
            'role',
            'is_active',
            'must_change_password',
        )
        read_only_fields = ('id',)


class AuditLogReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = (
            'id',
            'user',
            'action',
            'entity_type',
            'entity_id',
            'details',
            'ip_address',
            'user_agent',
            'timestamp',
        )
        read_only_fields = fields


class AuditLogWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = (
            'id',
            'user',
            'action',
            'entity_type',
            'entity_id',
            'details',
            'ip_address',
            'user_agent',
            'timestamp',
        )
        read_only_fields = ('id',)