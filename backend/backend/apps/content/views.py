"""API views for the public content domain."""

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import (
    ContactSubmission,
    PublicSermon,
    SermonSeries,
    SystemConfig,
    VisitRsvp,
    WebsiteAcademyModule,
    WebsiteLeader,
    WebsiteTestimonial,
)
from .repositories import (
    ContactSubmissionRepository,
    SermonRepository,
    SeriesRepository,
    SystemConfigRepository,
    VisitRsvpRepository,
    WebsiteAcademyModuleRepository,
    WebsiteLeaderRepository,
    WebsiteTestimonialRepository,
)
from .serializers import (
    ContactSubmissionWriteSerializer,
    PublicSermonReadSerializer,
    SermonSeriesReadSerializer,
    SystemConfigReadSerializer,
    VisitRsvpWriteSerializer,
    WebsiteAcademyModuleReadSerializer,
    WebsiteLeaderReadSerializer,
    WebsiteTestimonialReadSerializer,
)
from ..prayer.serializers import PrayerSubmissionWriteSerializer


class SermonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SermonRepository.published()
    serializer_class = PublicSermonReadSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]


class SeriesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SeriesRepository.published()
    serializer_class = SermonSeriesReadSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]


class LeaderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebsiteLeaderRepository.published()
    serializer_class = WebsiteLeaderReadSerializer
    permission_classes = [AllowAny]


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebsiteTestimonialRepository.published()
    serializer_class = WebsiteTestimonialReadSerializer
    permission_classes = [AllowAny]


class AcademyModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebsiteAcademyModuleRepository.published()
    serializer_class = WebsiteAcademyModuleReadSerializer
    permission_classes = [AllowAny]


@api_view(['GET'])
@permission_classes([AllowAny])
def site_config(request):
    """Return the site configuration from SystemConfig."""
    cfg = SystemConfigRepository.get_by_key('site')
    if cfg:
        return Response(cfg.value)
    return Response({'error': 'Site config not found'}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def contact_submit(request):
    serializer = ContactSubmissionWriteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([AllowAny])
def rsvp_submit(request):
    serializer = VisitRsvpWriteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)