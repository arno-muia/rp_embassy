"""Seed the Partner (Give) page section models from the currently rendered copy.

GiveHero / GiveWhySection / GiveMpesaSection / GiveAllocationSection (+ items)
replace the hardcoded copy in give.astro, mirroring the Visit B5.7 / Sermons
B5.8 seeds. The site renders identically until an admin edits something.

GiveMpesaSection becomes the canonical till/account source for /give; the
legacy GlobalSettings.mpesa_till and SystemConfig 'site'.giving keys are never
modified. Reverse operation only deletes the rows this migration created.
"""

from django.db import migrations


# Copy hardcoded in give.astro at the time of this migration.
ALLOCATION_ITEMS = [
    ('Community Programs', '35%', 'Local outreach and support in Thika', 0),
    ('Global Missions', '30%', 'Church planting and missionary support', 1),
    ('Ministry Operations', '25%', 'Facilities, media, and resources', 2),
    ('Benevolence Fund', '10%', 'Emergency assistance for families in crisis', 3),
]


def seed_give_content(apps, schema_editor):
    """Create one record per Give section from the live copy (idempotent)."""
    GiveHero = apps.get_model('content', 'GiveHero')
    GiveWhySection = apps.get_model('content', 'GiveWhySection')
    GiveMpesaSection = apps.get_model('content', 'GiveMpesaSection')
    GiveAllocationSection = apps.get_model('content', 'GiveAllocationSection')
    GiveAllocationItem = apps.get_model('content', 'GiveAllocationItem')

    if not GiveHero.objects.exists():
        GiveHero.objects.create(
            title='Give',
            subtitle='Your generosity fuels community outreach, global missions, '
                     'and the daily work of the Kingdom Embassy.',
            scripture='2 Corinthians 9:7',
            register='warm',
            image='',
            image_alt='',
        )

    if not GiveWhySection.objects.exists():
        GiveWhySection.objects.create(
            eyebrow='',
            heading='',
            body='We give because God first gave — generously, sacrificially, '
                 'and with joy. Your giving is an act of worship and partnership in '
                 'advancing the Gospel. Every contribution, whether large or small, '
                 'makes a Kingdom impact in Thika and beyond.',
        )

    if not GiveMpesaSection.objects.exists():
        GiveMpesaSection.objects.create(
            eyebrow='M-Pesa Giving',
            till_number='8598004',
            till_caption='Till Number',
            account_name='Salome Njuguna Waruguru',
            instructions='Go to M-Pesa → Lipa na M-Pesa → Buy Goods and Services '
                         '→ Enter Till Number',
            button_label='Need Help Giving?',
            button_url='/contact',
        )

    if not GiveAllocationSection.objects.exists():
        section = GiveAllocationSection.objects.create(
            heading='Where Your Giving Goes',
            subtitle='',
        )
        for title, percentage, description, sort_order in ALLOCATION_ITEMS:
            GiveAllocationItem.objects.create(
                section=section,
                title=title,
                percentage=percentage,
                description=description,
                image='',
                image_alt='',
                sort_order=sort_order,
                is_published=True,
            )


def unseed_give_content(apps, schema_editor):
    """Delete the seeded rows (legacy giving keys are never modified)."""
    for model_name in (
        'GiveAllocationItem', 'GiveHero', 'GiveWhySection',
        'GiveMpesaSection', 'GiveAllocationSection',
    ):
        apps.get_model('content', model_name).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0025_giveallocationsection_givehero_givempesasection_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_give_content, unseed_give_content),
    ]
