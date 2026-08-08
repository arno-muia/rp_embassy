"""API views for the public content domain."""

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..accounts.permissions import IsAcademyAuthorized

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
    ChurchProfileRepository,
    ContactSubmissionRepository,
    ContentBlockRepository,
    HomepageSectionRepository,
    HomepageSettingsRepository,
    PastorProfileRepository,
    SermonRepository,
    SeriesRepository,
    ServiceTimeRepository,
    SystemConfigRepository,
    VisitRsvpRepository,
    WebsiteAcademyModuleRepository,
    WebsiteLeaderRepository,
    WebsiteTestimonialRepository,
)
from .serializers import (
    ChurchProfileSerializer,
    ContactSubmissionWriteSerializer,
    ContentBlockSerializer,
    HomepageSectionSerializer,
    HomepageSettingsSerializer,
    PastorProfileSerializer,
    PublicSermonReadSerializer,
    SermonSeriesReadSerializer,
    ServiceTimeSerializer,
    SystemConfigReadSerializer,
    VisitRsvpWriteSerializer,
    WebsiteAcademyModuleReadSerializer,
    WebsiteLeaderReadSerializer,
    WebsiteTestimonialReadSerializer,
)
from ..events.repositories import EventRepository
from ..events.serializers import ChurchEventReadSerializer
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
    permission_classes = [IsAuthenticated, IsAcademyAuthorized]


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


# =============================================================================
# Homepage Aggregation Endpoint
# =============================================================================


@api_view(['GET'])
@permission_classes([AllowAny])
def homepage(request):
    """
    Aggregate homepage content from CMS models.

    Returns:
        hero: HomepageSettings hero configuration
        churchProfile: ChurchProfile mission/vision/messages
        serviceTimes: ServiceTime entries
        values: ContentBlock entries with type=VALUE
        beliefs: ContentBlock entries with type=BELIEF
        faqs: ContentBlock entries with type=FAQ
        sections: HomepageSection visibility control
        latestSermon: Most recent published sermon
        events: Upcoming published events (limited)
        testimonials: Published testimonials
        leaders: Published leaders
    """
    # Aggregate hero settings
    hero_settings = HomepageSettingsRepository.get_solo()
    hero_data = HomepageSettingsSerializer(hero_settings).data if hero_settings else {}

    # Aggregate church profile
    church_profile = ChurchProfileRepository.get_solo()
    church_profile_data = ChurchProfileSerializer(church_profile).data if church_profile else {}

    # Aggregate service times
    service_times = ServiceTimeSerializer(ServiceTimeRepository.all_ordered(), many=True).data

    # Aggregate content blocks by type
    values = ContentBlockSerializer(ContentBlockRepository.by_type('VALUE'), many=True).data
    beliefs = ContentBlockSerializer(ContentBlockRepository.by_type('BELIEF'), many=True).data
    faqs = ContentBlockSerializer(ContentBlockRepository.by_type('FAQ'), many=True).data
    expectations = ContentBlockSerializer(ContentBlockRepository.by_type('EXPECTATION'), many=True).data

    # Aggregate homepage sections
    sections = HomepageSectionSerializer(HomepageSectionRepository.all_ordered(), many=True).data

    # Aggregate latest sermon
    latest_sermon = SermonRepository.published()[:1]
    latest_sermon_data = PublicSermonReadSerializer(latest_sermon[0]).data if latest_sermon else None

    # Aggregate upcoming events
    events = ChurchEventReadSerializer(EventRepository.published_upcoming()[:5], many=True).data

    # Aggregate testimonials
    testimonials = WebsiteTestimonialReadSerializer(WebsiteTestimonialRepository.published(), many=True).data

    # Aggregate leaders
    leaders = WebsiteLeaderReadSerializer(WebsiteLeaderRepository.published(), many=True).data

    # Aggregate pastor profile
    pastor_profile = PastorProfileRepository.get_active()
    pastor_profile_data = PastorProfileSerializer(pastor_profile).data if pastor_profile else None

    return Response({
        'hero': hero_data,
        'churchProfile': church_profile_data,
        'serviceTimes': service_times,
        'values': values,
        'beliefs': beliefs,
        'faqs': faqs,
        'whatToExpect': expectations,
        'sections': sections,
        'latestSermon': latest_sermon_data,
        'events': events,
        'testimonials': testimonials,
        'leaders': leaders,
        'pastorProfile': pastor_profile_data,
    })
