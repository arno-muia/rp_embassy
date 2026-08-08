"""URL routing for the accounts (authentication) API.

All endpoints are mounted under ``api/auth/`` by the project URL conf.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('auth/login', views.login_view, name='auth-login'),
    path('auth/logout', views.logout_view, name='auth-logout'),
    path('auth/me', views.me_view, name='auth-me'),
    path(
        'auth/change-password',
        views.change_password_view,
        name='auth-change-password',
    ),
    path(
        'auth/csrf-token',
        views.csrf_token_view,
        name='auth-csrf-token',
    ),
]
