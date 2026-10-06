"""Seed the Visit page section models from the currently rendered copy.

B5.6: VisitHero / VisitLocation / VisitExpectSection (+ steps) /
VisitFaqSection (+ faqs from live SystemConfig 'site' visitFaqs) /
VisitRsvpSection / VisitComingSunday replace the hardcoded copy in
visit.astro, mirroring the B5.5 About seed. The site renders identically
until an admin edits something.

The ``SystemConfig`` rows are never modified; the reverse operation only
deletes the rows this migration created.
"""

from django.db import migrations


# Copy hardcoded in visit.astro at the time of this migration.
EXPECT_STEPS = [
    ('Arrive', 'Our hospitality team will greet you at the door and help you find a seat.', 'users', 0),
    ('Worship', "Experience authentic, Spirit-led worship that draws you into God's presence.", 'music', 1),
    ('Teaching', 'Receive practical, Bible-based teaching on your royal identity in Christ.', 'book-open', 2),
    ('Community', "Connect with others after service — we'd love to meet you personally.", 'trending-up', 3),
]


def seed_visit_content(apps, schema_editor):
    """Create one record per Visit section from the live content (idempotent)."""
    SystemConfig = apps.get_model('content', 'SystemConfig')
    VisitHero = apps.get_model('content', 'VisitHero')
    VisitLocation = apps.get_model('content', 'VisitLocation')
    VisitExpectSection = apps.get_model('content', 'VisitExpectSection')
    VisitExpectStep = apps.get_model('content', 'VisitExpectStep')
    VisitFaqSection = apps.get_model('content', 'VisitFaqSection')
    VisitFaq = apps.get_model('content', 'VisitFaq')
    VisitRsvpSection = apps.get_model('content', 'VisitRsvpSection')
    VisitComingSunday = apps.get_model('content', 'VisitComingSunday')

    site = {}
    site_cfg = SystemConfig.objects.filter(key='site').first()
    if site_cfg and isinstance(site_cfg.value, dict):
        site = site_cfg.value

    if not VisitHero.objects.exists():
        VisitHero.objects.create(
            title="You're Welcome Here",
            subtitle='Everything you need to know for your first visit to Royal Priesthood Embassy in Thika, Kenya.',
            scripture='',
            variant='warm',
        )

    if not VisitLocation.objects.exists():
        VisitLocation.objects.create()

    if not VisitExpectSection.objects.exists():
        section = VisitExpectSection.objects.create(
            eyebrow='First Visit?',
            title='What to Expect',
        )
        for step, description, icon, sort_order in EXPECT_STEPS:
            VisitExpectStep.objects.create(
                section=section,
                step=step,
                description=description,
                icon=icon,
                sort_order=sort_order,
                is_published=True,
            )

    if not VisitFaqSection.objects.exists():
        section = VisitFaqSection.objects.create(
            title='Frequently Asked Questions',
        )
        for index, item in enumerate(site.get('visitFaqs') or []):
            if not isinstance(item, dict):
                continue
            VisitFaq.objects.create(
                section=section,
                question=item.get('question') or '',
                answer=item.get('answer') or '',
                sort_order=index,
                is_published=True,
            )

    if not VisitRsvpSection.objects.exists():
        VisitRsvpSection.objects.create()

    if not VisitComingSunday.objects.exists():
        VisitComingSunday.objects.create()


def unseed_visit_content(apps, schema_editor):
    """Delete the seeded rows (SystemConfig is never modified)."""
    for model_name in (
        'VisitExpectStep', 'VisitFaq', 'VisitHero', 'VisitLocation',
        'VisitExpectSection', 'VisitFaqSection', 'VisitRsvpSection',
        'VisitComingSunday',
    ):
        apps.get_model('content', model_name).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0021_visit_section_models'),
    ]

    operations = [
        migrations.RunPython(seed_visit_content, unseed_visit_content),
    ]