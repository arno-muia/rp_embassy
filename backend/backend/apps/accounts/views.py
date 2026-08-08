"""API views for authentication (login, logout, me, change-password).

Uses Django's built-in session framework via ``django.contrib.auth.login``
and ``django.contrib.auth.logout``.  DRF ``SessionAuthentication`` reads
the session cookie on subsequent requests.
"""

import logging
import uuid

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import connection
from django.middleware.csrf import get_token
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import AuditAction, AuditLog, User
from .serializers import (
    AuthUserSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
)

logger = logging.getLogger(__name__)


def _write_audit(user, action, request):
    """Write an AuditLog entry for the given user + action."""
    AuditLog.objects.create(
        id=str(uuid.uuid4()),
        user=user,
        action=action,
        entity_type='User',
        entity_id=str(user.id) if user else None,
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        timestamp=timezone.now(),
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """POST /api/auth/login — authenticate and create a session."""
    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("=== LOGIN VIEW CALLED ===")
    logger.info("AUTH_USER_MODEL: %s", settings.AUTH_USER_MODEL)
    logger.info("AUTHENTICATION_BACKENDS: %s", settings.AUTHENTICATION_BACKENDS)
    logger.info("Database: %s", connection.settings_dict.get("NAME"))
    # END TEMP

    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("Incoming email: %s", email)
    user_exists = User.objects.filter(email=email).exists()
    logger.info("User.objects.filter(email=email).exists(): %s", user_exists)
    if user_exists:
        temp_user = User.objects.filter(email=email).first()
        logger.info("User PK if found: %s", temp_user.id if temp_user else None)
    # END TEMP

    user = authenticate(request, username=email, password=password)
    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("authenticate() result: %s", user)
    # END TEMP

    if user is None:
        # TEMP: Runtime trace logging — remove after diagnosis
        logger.info("Response: 401 UNAUTHORIZED")
        logger.info("=== LOGIN VIEW END ===")
        # END TEMP
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        # TEMP: Runtime trace logging — remove after diagnosis
        logger.info("Response: 403 FORBIDDEN (inactive)")
        logger.info("=== LOGIN VIEW END ===")
        # END TEMP
        return Response(
            {'error': 'This account is inactive.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    login(request, user)
    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("login(request, user) executed for user pk=%s", user.id)
    # END TEMP

    # Update last_login and reset failed attempts
    user.last_login = timezone.now()
    user.failed_login_attempts = 0
    user.save(update_fields=['last_login', 'failed_login_attempts'])

    _write_audit(user, AuditAction.LOGIN, request)

    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("Response: 200 OK")
    logger.info("=== LOGIN VIEW END ===")
    # END TEMP
    return Response(AuthUserSerializer(user).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """POST /api/auth/logout — destroy the current session."""
    user = request.user
    _write_audit(user, AuditAction.LOGOUT, request)
    logout(request)
    return Response({'success': True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """GET /api/auth/me — return the currently authenticated user."""
    return Response(AuthUserSerializer(request.user).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """POST /api/auth/change-password — change the current user's password."""
    serializer = ChangePasswordSerializer(
        data=request.data, context={'request': request}
    )
    serializer.is_valid(raise_exception=True)

    user = request.user
    user.set_password(serializer.validated_data['new_password'])
    user.must_change_password = False
    user.save(update_fields=['password', 'must_change_password'])

    _write_audit(user, AuditAction.PASSWORD_CHANGE, request)

    return Response({'success': True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    """GET /api/auth/csrf-token — ensure CSRF cookie is set and return its value.

    A1.8: The Astro frontend (port 4321) cannot read the Django CSRF cookie
    directly due to cross-origin restrictions.  This endpoint ensures the
    ``csrftoken`` cookie is set (via ``get_token``) and returns the value
    from that cookie so the frontend can echo it back in the
    ``X-CSRFToken`` header for subsequent POST requests.

    IMPORTANT: The cookie is the single source of truth.  We return
    ``request.COOKIES['csrftoken']`` rather than the ``get_token`` return
    value to guarantee the JSON body and the cookie always agree, even if
    this endpoint is called multiple times before a POST.
    """
    # get_token() ensures the csrftoken cookie is set in the response
    get_token(request)
    # Read the canonical value from the cookie (set by get_token above or
    # a previous call). This guarantees csrftoken cookie === X-CSRFToken.
    token = request.COOKIES.get('csrftoken', '')
    return Response(
        {'csrfToken': token},
        status=status.HTTP_200_OK,
    )
