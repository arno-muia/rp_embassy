"""Registry of renderable page sections (B5_1 / R1).

Each tuple is (page, key, title). ``SiteSection`` rows are auto-created from
this registry. Inheritance recipe for a FUTURE section:

    1. add one tuple here
    2. wrap the section in the page template with ``isEnabled(page, key)``

No migration, no model change, and no admin code is required — the toggle
row appears in the page's admin group automatically, enabled by default.

``ensure_registered()`` is idempotent: it never deletes rows and never
resets an admin's enabled/disabled toggle.
"""

from .models import SectionPage, SiteSection

# (page, key, admin-facing title) — order defines the admin list order.
SECTION_REGISTRY = [
    # --- Homepage: six core sections + What-to-Expect + CTA (decisions D2b) ---
    (SectionPage.HOMEPAGE, 'hero', 'Hero Section'),
    (SectionPage.HOMEPAGE, 'service-times', 'Service Times'),
    (SectionPage.HOMEPAGE, 'upcoming-events', 'Upcoming Events'),
    (SectionPage.HOMEPAGE, 'latest-sermon', 'Latest Sermon'),
    (SectionPage.HOMEPAGE, 'testimonials', 'Website Testimonials'),
    (SectionPage.HOMEPAGE, 'pastor-profile', 'Pastor Profile'),
    (SectionPage.HOMEPAGE, 'what-to-expect', 'What to Expect'),
    (SectionPage.HOMEPAGE, 'cta-banner', 'CTA Banner'),
    # --- About ---
    (SectionPage.ABOUT, 'intro', 'Welcome, Vision & Mission'),
    (SectionPage.ABOUT, 'values', 'Our Values'),
    (SectionPage.ABOUT, 'leadership', 'Leadership Team'),
    (SectionPage.ABOUT, 'theme-2026', '2026 Theme'),
    # --- Events ---
    (SectionPage.EVENTS, 'page-hero', 'Page Hero'),
    (SectionPage.EVENTS, 'upcoming', 'Upcoming & Ongoing'),
    (SectionPage.EVENTS, 'past', 'Past Events'),
    # --- Visit ---
    (SectionPage.VISIT, 'page-hero', 'Page Hero'),
    (SectionPage.VISIT, 'service-times', 'Service Times'),
    (SectionPage.VISIT, 'location', 'Location & Map'),
    (SectionPage.VISIT, 'what-to-expect', 'What to Expect'),
    (SectionPage.VISIT, 'faqs', 'Frequently Asked Questions'),
    (SectionPage.VISIT, 'rsvp', 'RSVP Form'),
    (SectionPage.VISIT, 'coming-sunday', "I Am Coming This Sunday"),
    # --- Sermons / Series ---
    (SectionPage.SERMONS, 'page-hero', 'Page Hero'),
    (SectionPage.SERMONS, 'browse-by-series', 'Browse by Series'),
    (SectionPage.SERMONS, 'sermons-grid', 'All Sermons'),
    (SectionPage.SERIES, 'page-hero', 'Page Hero'),
    (SectionPage.SERIES, 'series-grid', 'Series Grid'),
    # --- Partner (page key: 'give') / Prayer / Contact ---
    (SectionPage.GIVE, 'page-hero', 'Page Hero'),
    (SectionPage.GIVE, 'why-we-give', 'Why We Give'),
    (SectionPage.GIVE, 'mpesa-giving', 'M-Pesa Giving'),
    (SectionPage.GIVE, 'where-giving-goes', 'Where Your Giving Goes'),
    (SectionPage.PRAYER, 'page-hero', 'Page Hero'),
    (SectionPage.PRAYER, 'prayer-form', 'Prayer Form'),
    (SectionPage.CONTACT, 'page-hero', 'Page Hero'),
    (SectionPage.CONTACT, 'contact-details', 'Contact Details & Form'),
]


def ensure_registered() -> None:
    """Create any missing registry rows (enabled=True). Idempotent.

    Two queries: one SELECT of existing (page, key) pairs, one bulk_create
    of the gaps. Existing toggles are never reset; rows are never deleted.
    """
    existing = set(SiteSection.objects.values_list('page', 'key'))
    SiteSection.objects.bulk_create(
        [
            SiteSection(page=page, key=key, title=title)
            for page, key, title in SECTION_REGISTRY
            if (page, key) not in existing
        ],
        ignore_conflicts=True,
    )