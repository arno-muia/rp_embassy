"""Seed the About page section models from the live SystemConfig 'site' row.

B5.5: AboutWelcome / AboutValuesSection (+ cards) / AboutTheme replaced the
B5.4 JSON proxies. This migration copies the currently rendered copy — the
'site' subkeys ``welcomeMessage`` / ``values`` / ``theme2026`` — plus the
labels that were hardcoded in the page, so the site renders identically
until an admin edits something.

The ``SystemConfig`` rows are never modified; the reverse operation only
deletes the rows this migration created.
"""

from django.db import migrations

# Copy that was hardcoded in the About page at the time of this migration.
# Used only when the corresponding 'site' subkey is absent.
FALLBACK_WELCOME_MESSAGE = (
    "When you step into Royal Priesthood Embassy, you are entering a space "
    "where the laws of this place are not Kenya's laws — you are entering the "
    "Kingdom. Whether you're exploring faith for the first time or you've "
    "walked with Jesus for years, there is a place here for you. We can't "
    "wait to meet you."
)
FALLBACK_VALUES_SUBTITLE = (
    'The Mantle, Rod, and Sword — Identity, Authority, and Execution'
)
FALLBACK_SCRIPTURE_TEXT = (
    'Ask the LORD for rain in the time of the latter rain. The LORD will make '
    'flashing clouds; He will give them showers of rain, Grass in the field '
    'for everyone.'
)


def seed_about_content(apps, schema_editor):
    """Create one record per About section from the live content (idempotent)."""
    SystemConfig = apps.get_model('content', 'SystemConfig')
    AboutWelcome = apps.get_model('content', 'AboutWelcome')
    AboutValuesSection = apps.get_model('content', 'AboutValuesSection')
    AboutValue = apps.get_model('content', 'AboutValue')
    AboutTheme = apps.get_model('content', 'AboutTheme')

    site = {}
    site_cfg = SystemConfig.objects.filter(key='site').first()
    if site_cfg and isinstance(site_cfg.value, dict):
        site = site_cfg.value

    if not AboutWelcome.objects.exists():
        welcome = site.get('welcomeMessage') or {}
        AboutWelcome.objects.create(
            eyebrow='1 Peter 2:9',
            title=welcome.get('title') or 'Welcome to the Embassy',
            vision_label='our Vision',
            vision_text=welcome.get('message') or FALLBACK_WELCOME_MESSAGE,
            mission_label='Our Mission',
            mission_text=welcome.get('message') or FALLBACK_WELCOME_MESSAGE,
        )

    if not AboutValuesSection.objects.exists():
        section = AboutValuesSection.objects.create(
            heading='Our Values',
            subtitle=FALLBACK_VALUES_SUBTITLE,
        )
        for index, item in enumerate(site.get('values') or []):
            if not isinstance(item, dict):
                continue
            AboutValue.objects.create(
                section=section,
                title=item.get('title') or '',
                description=item.get('description') or '',
                sort_order=index,
                is_published=True,
            )

    if not AboutTheme.objects.exists():
        theme = site.get('theme2026') or {}
        AboutTheme.objects.create(
            eyebrow='2026 Theme',
            title=theme.get('title') or 'The Latter Rain',
            scripture=theme.get('scripture') or 'Zechariah 10:1',
            scripture_text=theme.get('scriptureText') or FALLBACK_SCRIPTURE_TEXT,
            image=theme.get('image') or '/images/posters/theme-2026-latter-rain.jpeg',
            button_label='Join Us',
            button_url='/visit',
        )


def unseed_about_content(apps, schema_editor):
    """Delete the seeded rows (SystemConfig is never modified)."""
    for model_name in ('AboutValue', 'AboutWelcome', 'AboutValuesSection', 'AboutTheme'):
        apps.get_model('content', model_name).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0019_abouttheme_aboutvalue_aboutvaluessection_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_about_content, unseed_about_content),
    ]
