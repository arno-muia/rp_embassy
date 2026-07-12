"""API views for the events domain."""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import ChurchEvent
from .repositories import EventRepository
from .serializers import ChurchEventReadSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventRepository.published_upcoming()
    serializer_class = ChurchEventReadSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]