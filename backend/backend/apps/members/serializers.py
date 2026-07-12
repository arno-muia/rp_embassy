"""Serializers for the members domain (read + write)."""

from rest_framework import serializers

from .models import Household, HouseholdMember, Member


class MemberReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone', 'gender',
            'date_of_birth', 'marital_status', 'membership_date', 'baptism_date',
            'discipleship_level', 'spiritual_gifts', 'ministry_teams', 'visitor',
            'status', 'household', 'user', 'consent_given', 'consent_date',
            'consent_version', 'profile_image_url', 'created_at', 'updated_at',
            'deleted_at',
        )
        read_only_fields = fields


class MemberWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone', 'gender',
            'date_of_birth', 'marital_status', 'membership_date', 'baptism_date',
            'discipleship_level', 'spiritual_gifts', 'ministry_teams', 'visitor',
            'status', 'household', 'user', 'consent_given', 'consent_date',
            'consent_version', 'profile_image_url',
        )
        read_only_fields = ('id',)


class HouseholdReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = (
            'id', 'household_name', 'address', 'phone', 'email',
            'anniversary_date', 'status', 'created_at', 'updated_at', 'deleted_at',
        )
        read_only_fields = fields


class HouseholdWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = (
            'id', 'household_name', 'address', 'phone', 'email',
            'anniversary_date', 'status',
        )
        read_only_fields = ('id',)


class HouseholdMemberReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdMember
        fields = ('member_id', 'household', 'role', 'can_pick_up', 'is_primary_contact', 'joined_at')
        read_only_fields = fields


class HouseholdMemberWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdMember
        fields = ('member_id', 'household', 'role', 'can_pick_up', 'is_primary_contact')
        read_only_fields = ('member_id',)