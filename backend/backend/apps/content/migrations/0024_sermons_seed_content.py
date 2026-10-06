"""Seed the Sermons page section models from the currently rendered copy.

B5.8: SermonsHero / SermonsBrowseSection / SermonsGridSection /
SermonDetailCopy / SermonsRelatedSection replace the hardcoded copy in
sermons.astro and sermons/[slug].astro, mirroring the B5.7 Visit seed.
The site renders identically until an admin edits something.

Reverse operation only deletes the rows this migration created.
"""

from django.db import migrations


def seed_sermons_content(apps, schema_editor):
    """Create one record per Sermons section from the live copy (idempotent)."""
    SermonsHero = apps.get_model('content', 'SermonsHero')
    SermonsBrowseSection = apps.get_model('content', 'SermonsBrowseSection')
    SermonsGridSection = apps.get_model('content', 'SermonsGridSection')
    SermonDetailCopy = apps.get_model('content', 'SermonDetailCopy')
    SermonsRelatedSection = apps.get_model('content', 'SermonsRelatedSection')

    if not SermonsHero.objects.exists():
        SermonsHero.objects.create(
            image='/images/Thumbnail_final.jpg',
            image_alt='Latest Teaching',
            label='Latest sermon',
            preacher='Pst Charles Muchemi',
            title='Emotional Intelligence',
            button_label='Watch Sermon →',
            button_url='/sermons',
            register='celestial',
        )

    if not SermonsBrowseSection.objects.exists():
        SermonsBrowseSection.objects.create(
            heading='Browse by Series',
        )

    if not SermonsGridSection.objects.exists():
        SermonsGridSection.objects.create(
            heading='All Sermons',
            empty_text='No sermons available yet.',
        )

    if not SermonDetailCopy.objects.exists():
        SermonDetailCopy.objects.create(
            video_note='Watch this teaching on our YouTube channel',
            watch_button_label='Watch on YouTube',
            secondary_button_label='Kingdom Formation',
            secondary_button_url='/academy',
        )

    if not SermonsRelatedSection.objects.exists():
        SermonsRelatedSection.objects.create(
            heading='Related Sermons',
        )


def unseed_sermons_content(apps, schema_editor):
    """Delete the seeded rows."""
    for model_name in (
        'SermonsHero', 'SermonsBrowseSection', 'SermonsGridSection',
        'SermonDetailCopy', 'SermonsRelatedSection',
    ):
        apps.get_model('content', model_name).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0023_sermondetailcopy_sermonsbrowsesection_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_sermons_content, unseed_sermons_content),
    ]