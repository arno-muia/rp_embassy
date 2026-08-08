"""Serializers for the accounts domain (read + write + auth)."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import AuditLog, User


# =============================================================================
# Auth serializers
# =============================================================================


class LoginSerializer(serializers.Serializer):
    """Accepts email + password for the login endpoint."""

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )


class AuthUserSerializer(serializers.ModelSerializer):
    """Public user fields returned after login / me endpoints."""

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'role',
            'is_active',
            'must_change_password',
            'last_login',
        )
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    """Accepts old + new password for the change-password endpoint."""

    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password],
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {'old_password': 'Current password is incorrect.'}
            )
        return value


# =============================================================================
# CRUD serializers (for admin / existing endpoints)
# =============================================================================


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'role',
            'is_active',
            'is_staff',
            'is_superuser',
            'must_change_password',
            'failed_login_attempts',
            'locked_until',
            'last_login',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class UserWriteSerializer(serializers.ModelSerializer):
    """Write serializer — password is write-only (never returned)."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'name',
            'role',
            'is_active',
            'is_staff',
            'must_change_password',
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# =============================================================================
# AuditLog serializers (unchanged)
# =============================================================================


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