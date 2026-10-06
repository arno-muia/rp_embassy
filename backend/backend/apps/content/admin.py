from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Case, IntegerField, Value, When
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    GlobalSettings,
    HomepageSettings,
    ChurchProfile,
    ContentBlock,
    ServiceTime,
    SystemConfig,
    HeroSectionConfig,
    AboutWelcome,
    AboutValuesSection,
    AboutValue,
    AboutTheme,
    SermonSeries,
    PublicSermon,
    HomepageLatestSermon,
    HomepageSections,
    AboutSections,
    EventsSections,
    VisitSections,
    VisitHero,
    VisitLocation,
    VisitExpectSection,
    VisitExpectStep,
    VisitFaqSection,
    VisitFaq,
    VisitRsvpSection,
    VisitComingSunday,
    SermonsSections,
    SermonsHero,
    SermonsBrowseSection,
    SermonsGridSection,
    SermonDetailCopy,
    SermonsRelatedSection,
    GiveHero,
    GiveWhySection,
    GiveMpesaSection,
    GiveAllocationSection,
    GiveAllocationItem,
    SeriesSections,
    GiveSections,
    PrayerSections,
    ContactHero,
    ContactDetailsSection,
    ContactSocialLink,
    ContactFormSection,
    ContactSections,
    WebsiteLeader,
    WebsiteTestimonial,
    WebsiteAcademyModule,
    ContactSubmission,
    VisitRsvp,
    PastorProfile,
)
from .sections_registry import SECTION_REGISTRY, ensure_registered
from backend.apps.media.widgets import RealtimeImageUploadWidget


# =============================================================================
# Custom AdminSite — Homepage section grouping
# =============================================================================


class HomepageGroupedAdminSite(AdminSite):
    """AdminSite that groups models into cards: the standard 'Homepage'
    card, plus per-page cards (About, Visit, ...) that hold each page's
    content components and its Sections visibility toggle.

    Display-layer grouping only — no models are moved and no database
    tables are altered by the grouping itself.
    """

    site_header = 'RP Ministries Administration'
    site_title = 'RP Admin'
    index_title = 'Dashboard'

    # Homepage model registry — order determines display order in the section
    HOMEPAGE_GROUP = [
        ('HeroSectionConfig', 'content'),
        ('ServiceTime', 'content'),
        ('HomepageUpcomingEvent', 'events'),
        ('HomepageLatestSermon', 'content'),
        ('WebsiteTestimonial', 'content'),
        ('PastorProfile', 'content'),
        # Section visibility toggles live inside their page's group (D3)
        ('HomepageSections', 'content'),
    ]

    # Per-page section toggles: (page_key, card_name, proxy_object_name, app_label).
    # Injected into an existing admin card when card_name matches (e.g. the
    # events app's 'Events & Calendar', the prayer app's 'Prayer'); otherwise
    # a synthetic page card (About, Visit, ...) is created (decision D3).
    PAGE_SECTION_GROUPS = [
        ('about', 'About', 'AboutSections', 'content'),
        ('events', 'Events & Calendar', 'EventsSections', 'content'),
        ('visit', 'Visit', 'VisitSections', 'content'),
        ('sermons', 'Sermons', 'SermonsSections', 'content'),
        ('series', 'Series', 'SeriesSections', 'content'),
        ('give', 'Partner', 'GiveSections', 'content'),
        ('prayer', 'Prayer', 'PrayerSections', 'content'),
        ('contact', 'Contact', 'ContactSections', 'content'),
    ]

    # Content components grouped into their page's card (B5.4 v2, updated in
    # B5.5 for About): extracted from their app cards (like HOMEPAGE_GROUP) and
    # listed before the page's Sections toggle — one entry per page section,
    # matching the Homepage and Prayer conventions.
    # (page_key, card_name, [(model, app_label), ...])
    # NOTE: ChurchProfile is intentionally NOT grouped — it stays in 'Public
    # Website Content' until the user removes it (user decision).
    PAGE_CONTENT_GROUPS = [
        ('about', 'About', [
            ('AboutWelcome', 'content'),        # section: intro
            ('AboutValuesSection', 'content'),  # section: values (cards inline)
            ('WebsiteLeader', 'content'),       # section: leadership
            ('AboutTheme', 'content'),          # section: theme-2026
        ]),
        ('visit', 'Visit', [
            ('VisitHero', 'content'),           # section: page-hero
            ('VisitLocation', 'content'),       # section: location
            ('VisitExpectSection', 'content'),  # section: what-to-expect (steps inline)
            ('VisitFaqSection', 'content'),     # section: faqs (rows inline)
            ('VisitRsvpSection', 'content'),    # section: rsvp (form copy)
            ('VisitRsvp', 'content'),           # section: rsvp (submissions)
            ('VisitComingSunday', 'content'),   # section: coming-sunday
        ]),
        ('sermons', 'Sermons', [
            ('SermonsHero', 'content'),           # section: page-hero
            ('SermonsBrowseSection', 'content'),  # section: browse-by-series
            ('SermonsGridSection', 'content'),    # section: sermons-grid
            ('PublicSermon', 'content'),          # section: sermons-grid (records)
            ('SermonSeries', 'content'),          # section: browse-by-series (records)
            ('SermonDetailCopy', 'content'),      # detail page: video/CTA copy
            ('SermonsRelatedSection', 'content'), # detail page: related heading
            # Roadmap (separate approvals): series → SermonSeries alias,
            # contact → ContactSubmission.
        ]),
        ('give', 'Partner', [
            ('GiveHero', 'content'),               # section: page-hero
            ('GiveWhySection', 'content'),         # section: why-we-give
            ('GiveMpesaSection', 'content'),       # section: mpesa-giving
            ('GiveAllocationSection', 'content'),  # section: where-giving-goes (cards inline)
        ]),
        ('contact', 'Contact', [
            ('ContactHero', 'content'),            # section: page-hero
            ('ContactDetailsSection', 'content'),  # section: contact-details (social links inline)
            ('ContactFormSection', 'content'),     # section: contact-details (form copy)
        ]),
    ]

    def get_app_list(self, request):
        """Return app list with grouped 'Homepage' and per-page sections."""
        original = list(super().get_app_list(request))

        # Build lookup: (app_label, model_name) -> model_dict
        model_lookup = {}
        for app in original:
            app_label = app['app_label']
            for model in app['models']:
                key = (app_label, model['object_name'])
                model_lookup[key] = model

        # Extract homepage models in defined order
        homepage_models = []
        seen_keys = set()

        for model_name, app_label in self.HOMEPAGE_GROUP:
            key = (app_label, model_name)
            if key in model_lookup and key not in seen_keys:
                model_entry = dict(model_lookup[key])  # shallow copy
                # Use the model's verbose name or a readable title
                model_entry['name'] = model_entry.get('name', model_name)
                homepage_models.append(model_entry)
                seen_keys.add(key)

        # Build synthetic Homepage app
        homepage_app = {
            'name': 'Homepage',
            'app_label': 'homepage',
            'app_url': reverse('admin:index'),
            'has_module_perms': True,
            'models': homepage_models,
        }

        # Extract page content components (B5.4 v2) before the toggles: they
        # are removed from their app cards and re-listed in their page card.
        page_content_entries = []  # (page_key, card_name, model_entry)
        for page_key, card_name, group_models in self.PAGE_CONTENT_GROUPS:
            for model_name, app_label in group_models:
                key = (app_label, model_name)
                if key in model_lookup and key not in seen_keys:
                    entry = dict(model_lookup[key])
                    entry['name'] = entry.get('name', model_name)
                    seen_keys.add(key)
                    page_content_entries.append((page_key, card_name, entry))

        # Extract per-page section toggles (D3) before building remaining
        page_section_entries = []  # (page_key, card_name, model_entry)
        for page_key, card_name, model_name, app_label in self.PAGE_SECTION_GROUPS:
            key = (app_label, model_name)
            if key in model_lookup and key not in seen_keys:
                entry = dict(model_lookup[key])
                entry['name'] = entry.get('name', model_name)
                seen_keys.add(key)
                page_section_entries.append((page_key, card_name, entry))

        # Build remaining apps, filtering out models shown in Homepage/page cards
        remaining = []
        for app in original:
            filtered_models = [
                m for m in app['models']
                if (app['app_label'], m['object_name']) not in seen_keys
            ]
            if filtered_models:
                remaining.append({
                    'name': app['name'],
                    'app_label': app['app_label'],
                    'app_url': app.get('app_url', '#'),
                    'has_module_perms': app.get('has_module_perms', True),
                    'models': filtered_models,
                })

        # Inject content components + section toggles into an existing card
        # of the same name (Events & Calendar, Prayer), or create a synthetic
        # page card (About, Visit, Sermons, Series, Partner, Contact).
        # Each card reads: content models first (page order), Sections toggle
        # last — matching the Homepage and Prayer conventions (B5.4 v2).
        content_by_page = {}
        for page_key, card_name, entry in page_content_entries:
            content_by_page.setdefault((page_key, card_name), []).append(entry)

        synthetic_page_apps = []
        for page_key, card_name, entry in page_section_entries:
            models = content_by_page.get((page_key, card_name), []) + [entry]
            target = next((a for a in remaining if a['name'] == card_name), None)
            if target is not None:
                target['models'].extend(models)
            else:
                synthetic_page_apps.append({
                    'name': card_name,
                    'app_label': f'page_{page_key}',
                    'app_url': reverse('admin:index'),
                    'has_module_perms': True,
                    'models': models,
                })

        # Safety net: a content group whose page has no toggle entry still
        # gets a card, so extracted models can never vanish from the admin.
        for (page_key, card_name), entries in content_by_page.items():
            if any(pk == page_key for pk, _, _ in page_section_entries):
                continue
            target = next((a for a in remaining if a['name'] == card_name), None)
            if target is not None:
                target['models'][:0] = entries
            else:
                synthetic_page_apps.append({
                    'name': card_name,
                    'app_label': f'page_{page_key}',
                    'app_url': reverse('admin:index'),
                    'has_module_perms': True,
                    'models': list(entries),
                })

        # Homepage card first, then existing apps, then new page cards
        result = [homepage_app] + list(remaining) + synthetic_page_apps

        return result


# Replace the default admin site with our grouped version
admin.site.__class__ = HomepageGroupedAdminSite


# =============================================================================
# ModelAdmin registrations
# =============================================================================


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'email', 'phone', 'updated_at')
    search_fields = ('church_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)


@admin.register(HomepageSettings)
class HomepageSettingsAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'hero_cta_text', 'cta_heading', 'updated_at')
    search_fields = ('hero_title', 'hero_subtitle', 'cta_heading')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'hero_background_image':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='hero')
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        ('Hero Section', {
            'fields': (
                'hero_title', 'hero_subtitle',
                'hero_scripture', 'hero_scripture_reference',
                'hero_background_image',
                'hero_cta_text', 'hero_cta_url',
                'hero_secondary_cta_text', 'hero_secondary_cta_url',
            ),
            'description': 'Homepage hero banner content — all fields are CMS editable',
        }),
        ('CTA Banner', {
            'fields': (
                'cta_heading', 'cta_title', 'cta_description',
                'cta_button_text', 'cta_button_url',
                'cta_secondary_button_text', 'cta_secondary_button_url',
                'cta_location',
            ),
            'description': 'Call-to-action banner section content',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ChurchProfile)
class ChurchProfileAdmin(admin.ModelAdmin):
    list_display = ('mission', 'updated_at')
    search_fields = ('mission', 'vision', 'pastor_message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('key', 'title', 'content_type', 'display_order', 'is_active', 'updated_at')
    search_fields = ('key', 'title', 'content')
    list_filter = ('content_type', 'is_active', 'is_rich_text')
    list_editable = ('display_order', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('content_type', 'display_order')


@admin.register(ServiceTime)
class ServiceTimeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'day', 'time', 'platform', 'is_published', 'display_order', 'updated_at',
    )
    list_display_links = ('name',)
    search_fields = ('name', 'day', 'location', 'description')
    list_filter = ('day', 'platform', 'is_published')
    list_editable = ('display_order', 'is_published', 'platform')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('display_order', 'day')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='services')
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        ('Service Details', {
            'fields': ('name', 'day', 'time', 'platform'),
        }),
        ('Location & Link', {
            'fields': ('location', 'link'),
        }),
        ('Content', {
            'fields': ('description', 'image'),
        }),
        ('Ordering & Visibility', {
            'fields': ('display_order', 'is_published'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# NOTE (B5_1 / decision D1b): HomepageSection is retired — its admin was
# unregistered on 2026-09-23. The model, its 5 seeded rows, and the legacy
# homepage.sections API payload remain dormant BY DECISION (no DropModel
# migration). SiteSection + its per-page proxies are the live
# section-visibility mechanism (see sections_registry.py).


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'updated_by', 'updated_at')
    search_fields = ('key', 'description', 'value')
    list_filter = ('updated_at',)
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'description'),
            'description': 'Raw escape hatch for every SystemConfig key. Note: '
                           'About page copy is managed from the About group '
                           '(Welcome, Vision &amp; Mission / Our Values / 2026 '
                           'Theme); its legacy <code>site</code> subkeys '
                           'welcomeMessage, values and theme2026 are kept for '
                           'reference only and no longer drive that page.',
        }),
        ('Audit', {
            'fields': ('updated_by', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    ordering = ('key',)

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields


@admin.register(HeroSectionConfig)
class HeroSectionConfigAdmin(admin.ModelAdmin):
    """Editor-friendly admin for homepage hero content.

    Filters SystemConfig to the 'site' key only — the actual source
    of hero scripture, tagline, description, and background image
    consumed by the homepage HeroSection component.
    """
    list_display = ('key', 'description', 'updated_by', 'updated_at')
    search_fields = ('key', 'description')
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Hero Content', {
            'fields': ('key', 'value', 'description'),
            'description': 'This is the actual source of hero banner content used by the homepage. Edit the JSON value to update scripture, tagline, description, and background image.',
        }),
        ('Audit', {
            'fields': ('updated_by', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Return only the 'site' config record — the hero content source."""
        qs = super().get_queryset(request)
        return qs.filter(key='site')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# =============================================================================
# About page section content — dedicated models (B5.5)
# =============================================================================
# One admin entry per About section (page order), each holding the section's
# full component set: AboutWelcome (intro), AboutValuesSection (+ inline
# AboutValue cards), WebsiteLeader, AboutTheme. No add/delete restrictions;
# the public API renders the most recently updated record, so the latest
# admin edit is always what the site shows.


@admin.register(AboutWelcome)
class AboutWelcomeAdmin(admin.ModelAdmin):
    """Admin for the About 'Welcome, Vision & Mission' intro section."""

    list_display = ('title', 'eyebrow', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Intro', {
            'fields': ('eyebrow', 'title'),
            'description': 'Rendered at the top of the About page.',
        }),
        ('Vision', {
            'fields': ('vision_label', 'vision_text'),
            'description': 'Quote with its label rendered after an em dash.',
        }),
        ('Mission', {
            'fields': ('mission_label', 'mission_text'),
            'description': 'Second quote, rendered below the vision quote.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


class AboutValueInline(admin.StackedInline):
    """'Our Values' cards managed inside their section's change form."""

    model = AboutValue
    extra = 0
    fields = ('title', 'description', 'sort_order', 'is_published')
    ordering = ('sort_order', 'id')


@admin.register(AboutValuesSection)
class AboutValuesSectionAdmin(admin.ModelAdmin):
    """Admin for the About 'Our Values' section (heading + inline cards)."""

    list_display = ('heading', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    inlines = (AboutValueInline,)
    fieldsets = (
        ('Section', {
            'fields': ('heading', 'subtitle'),
            'description': 'Section heading and the line beneath it. '
                           'The value cards are edited below.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(AboutTheme)
class AboutThemeAdmin(admin.ModelAdmin):
    """Admin for the About '2026 Theme' section."""

    list_display = ('title', 'scripture', 'updated_at')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    ordering = ('-updated_at',)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='theme')
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        ('Section', {
            'fields': ('eyebrow', 'title', 'scripture', 'scripture_text'),
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
            'description': 'Poster shown beneath the scripture text. '
                           'Leave blank to hide the image.',
        }),
        ('Button', {
            'fields': ('button_label', 'button_url'),
            'description': 'Call-to-action button below the section.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Image preview')
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-height:200px;max-width:300px;" />',
                obj.image,
            )
        return '(No image)'


# =============================================================================
# Visit page section content — dedicated models (B5.7)
# =============================================================================
# One admin entry per Visit section (page order), mirroring the About group.
# Singleton sections are rendered latest-record-wins; child rows (ExpectStep,
# Faq) are FK inlines with sort_order + is_published. Section on/off toggles
# stay on the VisitSections proxy (separate control panel).


@admin.register(VisitHero)
class VisitHeroAdmin(admin.ModelAdmin):
    """Admin for the Visit 'Page Hero' section."""

    list_display = ('title', 'variant', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Hero', {
            'fields': ('title', 'subtitle', 'scripture'),
            'description': 'Banner at the top of the Visit page.',
        }),
        ('Style', {
            'fields': ('variant',),
            'description': 'Controls the hero background treatment.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(VisitLocation)
class VisitLocationAdmin(admin.ModelAdmin):
    """Admin for the Visit 'Location & Map' section."""

    list_display = ('title', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Section', {
            'fields': ('eyebrow', 'title', 'description'),
        }),
        ('Button', {
            'fields': ('button_label', 'button_url'),
            'description': 'Call-to-action under the description.',
        }),
        ('Map', {
            'fields': ('map_embed_url', 'map_title'),
            'description': 'Google Maps embed URL and iframe title.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


class VisitExpectStepInline(admin.TabularInline):
    model = VisitExpectStep
    extra = 1
    fields = ('step', 'description', 'icon', 'sort_order', 'is_published')
    ordering = ('sort_order',)


@admin.register(VisitExpectSection)
class VisitExpectSectionAdmin(admin.ModelAdmin):
    """Admin for the Visit 'What to Expect' section (steps inline)."""

    list_display = ('title', 'eyebrow', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    inlines = [VisitExpectStepInline]
    fieldsets = (
        ('Section', {
            'fields': ('eyebrow', 'title'),
            'description': 'Heading above the expectation cards.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


class VisitFaqInline(admin.TabularInline):
    model = VisitFaq
    extra = 1
    fields = ('question', 'answer', 'sort_order', 'is_published')
    ordering = ('sort_order',)


@admin.register(VisitFaqSection)
class VisitFaqSectionAdmin(admin.ModelAdmin):
    """Admin for the Visit 'FAQs' section (rows inline)."""

    list_display = ('title', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    inlines = [VisitFaqInline]
    fieldsets = (
        ('Section', {
            'fields': ('title',),
            'description': 'Heading above the accordion.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(VisitRsvpSection)
class VisitRsvpSectionAdmin(admin.ModelAdmin):
    """Admin for the Visit RSVP form copy (labels only — not submissions)."""

    list_display = ('heading', 'submit_label', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Heading', {
            'fields': ('heading', 'subheading'),
        }),
        ('Form', {
            'fields': ('submit_label',),
            'description': 'Submit button label on the RSVP form.',
        }),
        ('Success Message', {
            'fields': ('success_title', 'success_message'),
            'description': 'Shown after a successful submission.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(VisitComingSunday)
class VisitComingSundayAdmin(admin.ModelAdmin):
    """Admin for the Visit 'I Am Coming This Sunday' CTA."""

    list_display = ('title', 'button_label', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('CTA', {
            'fields': ('title', 'description'),
        }),
        ('Button', {
            'fields': ('button_label', 'button_url'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# =============================================================================
# Sermons page section content — dedicated models (B5.8)
# =============================================================================
# One admin entry per Sermons section (page order), mirroring the Visit group.
# Singleton sections are rendered latest-record-wins. Section on/off toggles
# stay on the SermonsSections proxy (separate control panel).


@admin.register(SermonsHero)
class SermonsHeroAdmin(admin.ModelAdmin):
    """Admin for the Sermons 'Page Hero' image banner."""

    list_display = ('title', 'preacher', 'register', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='sermons-hero')
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        ('Banner Image', {
            'fields': ('image', 'image_alt'),
            'description': 'Background image of the hero banner.',
        }),
        ('Content', {
            'fields': ('label', 'preacher', 'title'),
            'description': 'Large label, preacher name and sermon title on the banner.',
        }),
        ('Button', {
            'fields': ('button_label', 'button_url'),
        }),
        ('Style', {
            'fields': ('register',),
            'description': 'Controls the hero background treatment.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(SermonsBrowseSection)
class SermonsBrowseSectionAdmin(admin.ModelAdmin):
    """Admin for the 'Browse by Series' heading (pills stay data-driven)."""

    list_display = ('heading', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Section', {
            'fields': ('heading',),
            'description': 'Heading above the series pill links.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(SermonsGridSection)
class SermonsGridSectionAdmin(admin.ModelAdmin):
    """Admin for the 'All Sermons' grid heading + empty state."""

    list_display = ('heading', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Section', {
            'fields': ('heading',),
            'description': 'Heading above the sermon card grid.',
        }),
        ('Empty State', {
            'fields': ('empty_text',),
            'description': 'Shown when no sermons are published.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(SermonDetailCopy)
class SermonDetailCopyAdmin(admin.ModelAdmin):
    """Admin for the shared copy on /sermons/[slug] detail pages."""

    list_display = ('video_note', 'watch_button_label', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Video Placeholder', {
            'fields': ('video_note',),
            'description': 'Note inside the video area on every sermon page.',
        }),
        ('Buttons', {
            'fields': (
                'watch_button_label',
                'secondary_button_label', 'secondary_button_url',
            ),
            'description': 'Primary and secondary call-to-action buttons.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(SermonsRelatedSection)
class SermonsRelatedSectionAdmin(admin.ModelAdmin):
    """Admin for the 'Related Sermons' heading on sermon detail pages."""

    list_display = ('heading', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Section', {
            'fields': ('heading',),
            'description': 'Heading above the related-sermons grid.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(GiveHero)
class GiveHeroAdmin(admin.ModelAdmin):
    """Admin for the Give 'Page Hero' section (Partner group)."""

    list_display = ('title', 'scripture', 'register', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'scripture', 'register'),
            'description': 'Hero heading, supporting copy and background register.',
        }),
        ('Banner Image (optional)', {
            'fields': ('image', 'image_alt'),
            'description': 'Optional banner image. Leave blank for no image.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='give')
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(GiveWhySection)
class GiveWhySectionAdmin(admin.ModelAdmin):
    """Admin for the 'Why We Give' section (Partner group)."""

    list_display = ('heading', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Content', {
            'fields': ('eyebrow', 'heading', 'body'),
            'description': 'Eyebrow and heading are optional (blank hides them, matching the current page).',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(GiveMpesaSection)
class GiveMpesaSectionAdmin(admin.ModelAdmin):
    """Admin for the 'M-Pesa Giving' card (Partner group).

    Canonical till/account source for /give. Legacy GlobalSettings.mpesa_till
    and SystemConfig 'site'.giving are left untouched.
    """

    list_display = ('eyebrow', 'till_number', 'account_name', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Card', {
            'fields': ('eyebrow', 'till_number', 'till_caption', 'account_name', 'instructions'),
            'description': 'M-Pesa Till card content.',
        }),
        ('Call to Action', {
            'fields': ('button_label', 'button_url'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


class GiveAllocationItemInline(admin.TabularInline):
    model = GiveAllocationItem
    extra = 0
    fields = ('title', 'percentage', 'description', 'image', 'sort_order', 'is_published')
    ordering = ('sort_order', 'id')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='give')
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(GiveAllocationSection)
class GiveAllocationSectionAdmin(admin.ModelAdmin):
    """Admin for the 'Where Your Giving Goes' section (Partner group)."""

    list_display = ('heading', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    inlines = [GiveAllocationItemInline]
    fieldsets = (
        ('Section', {
            'fields': ('heading', 'subtitle'),
            'description': 'Subtitle is optional (blank hides it, matching the current page).',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# =============================================================================
# Contact page section content (dedicated models)
# =============================================================================


@admin.register(ContactHero)
class ContactHeroAdmin(admin.ModelAdmin):
    """Admin for the Contact 'Page Hero' section (Contact group)."""

    list_display = ('title', 'scripture', 'register', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'scripture', 'register'),
            'description': 'Hero heading, supporting copy and background register.',
        }),
        ('Banner Image (optional)', {
            'fields': ('image', 'image_alt'),
            'description': 'Optional banner image. Leave blank for no image.',
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='contact')
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class ContactSocialLinkInline(admin.TabularInline):
    model = ContactSocialLink
    extra = 0
    fields = ('network', 'label', 'url', 'sort_order', 'is_published')
    ordering = ('sort_order', 'id')


@admin.register(ContactDetailsSection)
class ContactDetailsSectionAdmin(admin.ModelAdmin):
    """Admin for the 'Contact Details' left column (Contact group).

    Blank email/address fields fall back to the canonical SystemConfig 'site'
    keys so the page keeps rendering until an override is saved.
    """

    list_display = ('email_heading', 'location_heading', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    inlines = [ContactSocialLinkInline]
    fieldsets = (
        ('Email', {
            'fields': ('email_heading', 'email_address'),
            'description': 'Leave the address blank to use the site default.',
        }),
        ('Location', {
            'fields': (
                'location_heading', 'street', 'city', 'country',
                'maps_url', 'directions_label',
            ),
            'description': 'Blank fields use the site address defaults.',
        }),
        ('Social', {
            'fields': ('social_heading',),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ContactFormSection)
class ContactFormSectionAdmin(admin.ModelAdmin):
    """Admin for the 'Send a Message' form copy (Contact group)."""

    list_display = ('heading', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Heading', {
            'fields': ('heading',),
        }),
        ('Field Labels', {
            'fields': (
                'name_label', 'email_label', 'phone_label', 'message_label',
            ),
        }),
        ('Submit & Status', {
            'fields': (
                'submit_label', 'sending_label',
                'success_message', 'error_message',
            ),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(SermonSeries)
class SermonSeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'sort_order', 'sermon_count', 'updated_at')
    search_fields = ('title', 'slug', 'description')
    list_filter = ('is_published',)
    list_editable = ('is_published', 'sort_order')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', '-updated_at')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image_url':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='series')
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(PublicSermon)
class PublicSermonAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'date', 'is_published', 'series', 'updated_at')
    search_fields = ('title', 'speaker', 'scripture', 'series_slug', 'series_title')
    list_filter = ('is_published', 'date', 'series')
    list_editable = ('is_published',)
    readonly_fields = ('created_at', 'updated_at', 'homepage_display_note')
    ordering = ('-date', '-updated_at')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'thumbnail_url':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='sermons')
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        (None, {
            'fields': ('homepage_display_note',),
        }),
        ('Sermon Details', {
            'fields': (
                'title', 'slug', 'speaker', 'date', 'scripture',
                'description', 'video_url', 'audio_url', 'thumbnail_url',
                'series', 'series_slug', 'series_title',
            ),
        }),
        ('Publication', {
            'fields': ('is_published',),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def homepage_display_note(self, obj):
        """Display a prominent note about homepage sermon behavior."""
        return format_html(
            '<div style="padding:12px 16px;background:#fff3cd;border:1px solid #ffc107;'
            'border-radius:4px;margin-bottom:8px;">'
            '<strong>Homepage Display:</strong> '
            'The homepage renders only the single most recently published sermon '
            '(ordered by <code>date</code> descending, filtered to '
            '<code>is_published=True</code>).<br>'
            'SermonSeries is <strong>not</strong> consumed by the homepage — '
            'it is only used on sermon detail pages.<br><br>'
            'To update what appears on the homepage, edit a sermon\'s '
            '<code>date</code> field or use <code>is_published</code>.'
            '</div>'
        )
    homepage_display_note.short_description = ''


@admin.register(HomepageLatestSermon)
class HomepageLatestSermonAdmin(PublicSermonAdmin):
    """Admin for the homepage's latest sermon — filtered to a single record.

    Uses the same PublicSermon table via proxy model — no duplicate storage.
    The queryset is filtered to only the most recently published sermon,
    matching the homepage API/frontend logic.
    """

    def get_queryset(self, request):
        """Return only the latest published sermon — matching homepage logic."""
        qs = super().get_queryset(request)
        latest = qs.filter(is_published=True).order_by('-date').first()
        if latest:
            return qs.filter(pk=latest.pk)
        return qs.none()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(WebsiteLeader)
class WebsiteLeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'sort_order', 'is_published', 'updated_at')
    search_fields = ('name', 'role')
    list_filter = ('is_published',)
    list_editable = ('sort_order', 'is_published')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', '-updated_at')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'photo_url':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='leaders')
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(WebsiteTestimonial)
class WebsiteTestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'sort_order', 'is_published', 'updated_at')
    search_fields = ('name', 'role', 'quote')
    list_filter = ('is_published',)
    list_editable = ('sort_order', 'is_published')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', '-updated_at')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'photo_url':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='testimonials')
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(WebsiteAcademyModule)
class WebsiteAcademyModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'lessons_count', 'duration', 'sort_order', 'is_published', 'updated_at')
    search_fields = ('title', 'instructor', 'description')
    list_filter = ('is_published',)
    list_editable = ('sort_order', 'is_published')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', '-updated_at')


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(PastorProfile)
class PastorProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'display_order', 'is_active', 'updated_at')
    search_fields = ('name', 'title', 'biography')
    list_filter = ('is_active',)
    list_editable = ('display_order', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    ordering = ('display_order', '-is_active', 'name')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image':
            kwargs['widget'] = RealtimeImageUploadWidget(folder='pastor')
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        ('Profile', {
            'fields': ('name', 'title', 'image', 'image_preview', 'biography'),
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_url'),
        }),
        ('Ordering & Status', {
            'fields': ('display_order', 'is_active'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px;max-width:300px;" />', obj.image)
        return '(No image)'
    image_preview.short_description = 'Image Preview'


@admin.register(VisitRsvp)
class VisitRsvpAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'party_size', 'visit_date', 'status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'notes')
    list_filter = ('status', 'first_visit', 'created_at')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


# =============================================================================
# Page section visibility toggles (B5_1 / R1 — D3: grouped per page)
# =============================================================================


class BaseSectionsAdmin(admin.ModelAdmin):
    """Shared control panel for SiteSection visibility toggles.

    One proxy model per page lets each page's toggles live inside that
    page's admin group. Rows are registry-created (ensure_registered) —
    adding and deleting are disabled; the only admin action is toggling
    ``enabled``. Disabling hides the section on the public site; nothing
    is deleted and re-enabling restores it.
    """

    target_page: str = ''

    list_display = ('title', 'key', 'enabled', 'updated_at')
    list_display_links = ('title',)
    list_editable = ('enabled',)
    search_fields = ('title', 'key')
    list_filter = ('enabled',)
    readonly_fields = ('page_label', 'created_at', 'updated_at')
    fieldsets = (
        ('Section', {
            'fields': ('title', 'key'),
            'description': (
                'Disabling hides this section on the public site. '
                'Nothing is deleted - re-enabling restores it.'
            ),
        }),
        ('Visibility', {
            'fields': ('enabled',),
        }),
        ('Audit', {
            'fields': ('page_label', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(page=self.target_page)

    def get_ordering(self, request):
        """Display rows in registry (page) order.

        The registry is the single source of truth for a page's section order
        ("order defines the admin list order"), but rows are stored with
        creation order — so newly added sections would otherwise be appended.
        This admin-level ordering maps each row's key to its registry position
        for this page (unknown keys sort last). No Meta change, no migration.
        """
        keys = [key for page, key, _ in SECTION_REGISTRY if page == self.target_page]
        if not keys:
            return super().get_ordering(request)
        return (
            Case(
                *[When(key=key, then=Value(index)) for index, key in enumerate(keys)],
                default=Value(len(keys)),
                output_field=IntegerField(),
            ),
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # identity is immutable once created
            return ('page_label', 'key', 'created_at', 'updated_at')
        return self.readonly_fields

    @admin.display(description='Page')
    def page_label(self, obj):
        """Read-only page label using the proxy's display name.

        Lets a page group show a friendlier name (e.g. the 'give' page group
        displays 'Partner', matching the public nav) while the stored page key
        — and therefore the database and registry — remain unchanged.
        """
        return obj.get_page_display() if obj else '—'

    def save_model(self, request, obj, form, change):
        if self.target_page:
            obj.page = self.target_page
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        ensure_registered()
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        return False  # rows come from sections_registry.SECTION_REGISTRY

    def has_delete_permission(self, request, obj=None):
        return False  # disable instead; deletion would self-heal anyway


@admin.register(HomepageSections)
class HomepageSectionsAdmin(BaseSectionsAdmin):
    target_page = 'homepage'


@admin.register(AboutSections)
class AboutSectionsAdmin(BaseSectionsAdmin):
    target_page = 'about'


@admin.register(EventsSections)
class EventsSectionsAdmin(BaseSectionsAdmin):
    target_page = 'events'


@admin.register(VisitSections)
class VisitSectionsAdmin(BaseSectionsAdmin):
    target_page = 'visit'


@admin.register(SermonsSections)
class SermonsSectionsAdmin(BaseSectionsAdmin):
    target_page = 'sermons'


@admin.register(SeriesSections)
class SeriesSectionsAdmin(BaseSectionsAdmin):
    target_page = 'series'


@admin.register(GiveSections)
class GiveSectionsAdmin(BaseSectionsAdmin):
    target_page = 'give'


@admin.register(PrayerSections)
class PrayerSectionsAdmin(BaseSectionsAdmin):
    target_page = 'prayer'


@admin.register(ContactSections)
class ContactSectionsAdmin(BaseSectionsAdmin):
    target_page = 'contact'