"""Admin configuration for the accounts (authentication) domain.

Registers the email-based ``User`` model so a superadmin can add additional
admin-panel members (email + password) through Django admin under the
"Authentication and Authorization" card.

Passwords are stored hashed via Django's built-in password hashing — never
plain text.  Added members log in at ``/admin/`` (and ``/api/auth/login``)
with the email/password the superadmin created.
"""

import uuid

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import AuditAction, AuditLog, User


# =============================================================================
# Forms
# =============================================================================


class CustomUserCreationForm(UserCreationForm):
    """Creation form for admin-added users — email is the identifier."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'name', 'role', 'is_staff', 'must_change_password')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _('A user with this email already exists.')
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Change form for editing existing users in the admin.

    The password field shows the stored hash only; raw passwords are managed
    through the ``/api/auth/change-password`` endpoint rather than the admin.
    """

    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            'email',
            'name',
            'role',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )
# =============================================================================
# ModelAdmin
# =============================================================================


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin for the email-based ``User`` model.

    The add form lets a superadmin create a new staff member with email +
    password.  The change form lets an admin adjust role / active / staff /
    superuser flags.
    """

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    # --- list view ---------------------------------------------------------
    list_display = (
        'email',
        'name',
        'role',
        'is_staff',
        'is_active',
        'last_login',
    )
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)
    readonly_fields = ('last_login', 'created_at', 'updated_at')
    filter_horizontal = ('groups', 'user_permissions')

    # --- change form fieldsets ---------------------------------------------
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'role')}),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (
            'Audit',
            {
                'fields': ('last_login', 'created_at', 'updated_at'),
                'classes': ('collapse',),
            },
        ),
    )

    # --- add form fieldsets -------------------------------------------------
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'name',
                    'password1',
                    'password2',
                    'role',
                    'is_staff',
                    'must_change_password',
                ),
            },
        ),
    )

    # --- behaviour ----------------------------------------------------------
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Non-superusers cannot escalate privileges (staff / superuser / groups / perms).
        if not request.user.is_superuser:
            for field in (
                'is_superuser',
                'is_staff',
                'groups',
                'user_permissions',
            ):
                if field in form.base_fields:
                    form.base_fields[field].disabled = True
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Non-superusers can only see non-superuser accounts.
        return qs.exclude(is_superuser=True)

    def has_delete_permission(self, request, obj=None):
        # A user cannot delete themselves.
        if obj is not None and obj == request.user:
            return False
        return super().has_delete_permission(request, obj)

    def has_module_permission(self, request):
        # Only staff can see the Authentication and Authorization card.
        return bool(
            request.user
            and request.user.is_active
            and request.user.is_staff
        )

    def save_model(self, request, obj, form, change):
        if not change:
            # Generate a UUID primary key if the manager did not supply one.
            if not obj.pk:
                obj.pk = str(uuid.uuid4())
            # Admin-created users are staff so they can reach /admin/.
            obj.is_staff = True
            super().save_model(request, obj, form, change)
            # Audit trail — USER_INVITE.
            AuditLog.objects.create(
                id=str(uuid.uuid4()),
                user=request.user,
                action=AuditAction.USER_INVITE,
                entity_type='User',
                entity_id=str(obj.id),
                details={
                    'email': obj.email,
                    'role': obj.role,
                    'created_by': request.user.email,
                },
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                timestamp=timezone.now(),
            )
        else:
            super().save_model(request, obj, form, change)

