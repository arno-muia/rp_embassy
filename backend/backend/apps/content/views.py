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
    SiteSection,
    SystemConfig,
    VisitRsvp,
    WebsiteAcademyModule,
    WebsiteLeader,
    WebsiteTestimonial,
)
from .sections_registry import ensure_registered
from .repositories import (
    AboutContentRepository,
    ContactContentRepository,
    GiveContentRepository,
    ChurchProfileRepository,
    ContactSubmissionRepository,
    ContentBlockRepository,
    HomepageSectionRepository,
    HomepageSettingsRepository,
    PastorProfileRepository,
    SermonRepository,
    SeriesRepository,
    ServiceTimeRepository,
    SermonsContentRepository,
    SystemConfigRepository,
    VisitContentRepository,
    VisitRsvpRepository,
    WebsiteAcademyModuleRepository,
    WebsiteLeaderRepository,
    WebsiteTestimonialRepository,
)
from .serializers import (
    AboutThemeReadSerializer,
    ContactDetailsSectionReadSerializer,
    ContactFormSectionReadSerializer,
    ContactHeroReadSerializer,
    ContactSocialLinkReadSerializer,
    GiveAllocationItemReadSerializer,
    GiveHeroReadSerializer,
    GiveMpesaSectionReadSerializer,
    GiveWhySectionReadSerializer,
    AboutValueReadSerializer,
    AboutWelcomeReadSerializer,
    ChurchProfileSerializer,
    ContactSubmissionWriteSerializer,
    ContentBlockSerializer,
    HomepageSectionSerializer,
    HomepageSettingsSerializer,
    PastorProfileSerializer,
    PublicSermonReadSerializer,
    SermonSeriesReadSerializer,
    SermonsBrowseSectionReadSerializer,
    SermonsGridSectionReadSerializer,
    SermonsHeroReadSerializer,
    SermonsRelatedSectionReadSerializer,
    SermonDetailCopyReadSerializer,
    ServiceTimeSerializer,
    SystemConfigReadSerializer,
    VisitComingSundayReadSerializer,
    VisitExpectStepReadSerializer,
    VisitFaqReadSerializer,
    VisitHeroReadSerializer,
    VisitLocationReadSerializer,
    VisitRsvpSectionReadSerializer,
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


@api_view(['GET'])
@permission_classes([AllowAny])
def about_page(request):
    """About page section content (B5.5 — dedicated models).

    Returns one key per About content section, each managed from its own
    admin entry under the About group:

        intro:  'Welcome, Vision & Mission' — every rendered component
        values: 'Our Values' heading/subtitle + published cards in order
        theme:  '2026 Theme' — every rendered component

    A key is null when its record has not been created, and the client keeps
    its fallback copy. Section on/off remains /api/sections (About group).
    """
    welcome = AboutContentRepository.welcome()
    values_section = AboutContentRepository.values_section()
    theme = AboutContentRepository.theme()

    values_payload = None
    if values_section is not None:
        values = AboutContentRepository.published_values(values_section)
        values_payload = {
            'heading': values_section.heading,
            'subtitle': values_section.subtitle,
            'items': AboutValueReadSerializer(values, many=True).data,
        }

    return Response({
        'intro': AboutWelcomeReadSerializer(welcome).data if welcome else None,
        'values': values_payload,
        'theme': AboutThemeReadSerializer(theme).data if theme else None,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def visit_page(request):
    """Visit page section content (dedicated models).

    Returns one key per Visit content section, each managed from its own
    admin entry under the Visit group:

        hero:         'Page Hero' — every rendered component
        location:     'Location & Map' — every rendered component
        expect:       'What to Expect' eyebrow/title + published cards in order
        faqs:         'FAQs' heading + published rows in order
        rsvp:         'RSVP Form Copy' — every rendered component
        comingSunday: 'I Am Coming This Sunday' — every rendered component

    A key is null when its record has not been created, and the client keeps
    its fallback copy. Section on/off remains /api/sections (Visit group).
    Service times stay shared via /api/homepage (no duplicate).
    """
    hero = VisitContentRepository.hero()
    location = VisitContentRepository.location()
    expect_section = VisitContentRepository.expect_section()
    faq_section = VisitContentRepository.faq_section()
    rsvp = VisitContentRepository.rsvp_section()
    coming_sunday = VisitContentRepository.coming_sunday()

    expect_payload = None
    if expect_section is not None:
        steps = VisitContentRepository.published_steps(expect_section)
        expect_payload = {
            'eyebrow': expect_section.eyebrow,
            'title': expect_section.title,
            'items': VisitExpectStepReadSerializer(steps, many=True).data,
        }

    faqs_payload = None
    if faq_section is not None:
        faqs = VisitContentRepository.published_faqs(faq_section)
        faqs_payload = {
            'title': faq_section.title,
            'items': VisitFaqReadSerializer(faqs, many=True).data,
        }

    return Response({
        'hero': VisitHeroReadSerializer(hero).data if hero else None,
        'location': VisitLocationReadSerializer(location).data if location else None,
        'expect': expect_payload,
        'faqs': faqs_payload,
        'rsvp': VisitRsvpSectionReadSerializer(rsvp).data if rsvp else None,
        'comingSunday': VisitComingSundayReadSerializer(coming_sunday).data if coming_sunday else None,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def sermons_page(request):
    """Sermons page section content (dedicated models, B5.8).

    Returns one key per Sermons content section, each managed from its own
    admin entry under the Sermons group:

        hero:    'Page Hero' — every rendered component
        browse:  'Browse by Series' heading
        grid:    'All Sermons' heading + empty state
        detail:  'Sermon Detail Copy' — shared copy on /sermons/[slug]
        related: 'Related Sermons' heading on /sermons/[slug]

    A key is null when its record has not been created, and the client keeps
    its fallback copy. Section on/off remains /api/sections (Sermons group).
    Sermon/series records stay on /api/sermons and /api/series (no change).
    """
    hero = SermonsContentRepository.hero()
    browse = SermonsContentRepository.browse_section()
    grid = SermonsContentRepository.grid_section()
    detail = SermonsContentRepository.detail_copy()
    related = SermonsContentRepository.related_section()

    return Response({
        'hero': SermonsHeroReadSerializer(hero).data if hero else None,
        'browse': SermonsBrowseSectionReadSerializer(browse).data if browse else None,
        'grid': SermonsGridSectionReadSerializer(grid).data if grid else None,
        'detail': SermonDetailCopyReadSerializer(detail).data if detail else None,
        'related': SermonsRelatedSectionReadSerializer(related).data if related else None,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def give_page(request):
    """Partner (Give) page section content (dedicated models).

    Returns one key per Give content section, each managed from its own
    admin entry under the Partner group:

        hero:       'Page Hero' — every rendered component
        why:        'Why We Give' — every rendered component
        mpesa:      'M-Pesa Giving' — every rendered component (canonical
                    till/account source; legacy GlobalSettings.mpesa_till and
                    SystemConfig 'site'.giving are left untouched)
        allocation: 'Where Giving Goes' heading/subtitle + published cards

    A key is null when its record has not been created, and the client keeps
    its fallback copy. Section on/off remains /api/sections (Partner group).
    """
    hero = GiveContentRepository.hero()
    why = GiveContentRepository.why()
    mpesa = GiveContentRepository.mpesa()
    allocation_section = GiveContentRepository.allocation_section()

    allocation_payload = None
    if allocation_section is not None:
        items = GiveContentRepository.published_allocations(allocation_section)
        allocation_payload = {
            'heading': allocation_section.heading,
            'subtitle': allocation_section.subtitle,
            'items': GiveAllocationItemReadSerializer(items, many=True).data,
        }

    return Response({
        'hero': GiveHeroReadSerializer(hero).data if hero else None,
        'why': GiveWhySectionReadSerializer(why).data if why else None,
        'mpesa': GiveMpesaSectionReadSerializer(mpesa).data if mpesa else None,
        'allocation': allocation_payload,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def contact_page(request):
    """Contact page section content (dedicated models).

    Returns one key per Contact content section, each managed from its own
    admin entry under the Contact group:

        hero:    'Page Hero' — every rendered component
        details: 'Contact Details' copy + published social links in order
        form:    'Contact Form' — every rendered string

    A key is null when its record has not been created, and the client keeps
    its fallback copy. Section on/off remains /api/sections (Contact group).
    POST /api/contact (form submissions) is unchanged.
    """
    hero = ContactContentRepository.hero()
    details = ContactContentRepository.details()
    form = ContactContentRepository.form()

    details_payload = None
    if details is not None:
        socials = ContactContentRepository.published_socials(details)
        details_payload = {
            **ContactDetailsSectionReadSerializer(details).data,
            'social_links': ContactSocialLinkReadSerializer(socials, many=True).data,
        }

    return Response({
        'hero': ContactHeroReadSerializer(hero).data if hero else None,
        'details': details_payload,
        'form': ContactFormSectionReadSerializer(form).data if form else None,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def sections(request):
    """
    Section visibility flags for the public site (B5_1 / R1).

    Returns:
        { "<page>": { "<section-key>": <bool>, ... }, ... }

    Missing/unknown keys on the client are treated as enabled (fail-open),
    so an unregistered section renders exactly as before.
    """
    ensure_registered()
    data: dict = {}
    for page, key, enabled in SiteSection.objects.values_list('page', 'key', 'enabled'):
        data.setdefault(page, {})[key] = enabled
    return Response(data)


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

    # Aggregate published service times (unpublished entries are hidden from the public site)
    service_times = ServiceTimeSerializer(ServiceTimeRepository.published(), many=True).data

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
