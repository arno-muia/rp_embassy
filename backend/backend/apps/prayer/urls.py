"""URL routing for the prayer API."""

from django.urls import path

from . import views

urlpatterns = [
    path('prayer', views.prayer_submit, name='prayer-submit'),
]