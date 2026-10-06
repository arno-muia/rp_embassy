"""Seed Contact page section models from the currently rendered copy.

Creates one ContactHero / ContactDetailsSection (+ social links) /
ContactFormSection from the live contact.astro + site.ts copy so the
site renders identically until an admin edits something.

Blank email/address fields intentionally keep the SystemConfig 'site'
fallbacks — overrides live here only when an admin saves them.
Reverse operation only deletes the rows this migration created.
"""

from django.db import migrations


SOCIAL_LINKS = [
    (
        'instagram',
        'https://www.instagram.com/royalpriesthoodembassy',
        0,
    ),
    (
        'facebook',
        'https://www.facebook.com/people/Royal-Priesthood-Embassy/61575460188005/',
        1,
    ),
    (
        'youtube',
        'https://www.youtube.com/@RoyalPriesthoodEmbassy',
        2,
    ),
]


def seed_contact_content(apps, schema_editor):
    ContactHero = apps.get_model('content', 'ContactHero')
    ContactDetailsSection = apps.get_model(
        'content', 'ContactDetailsSection'
    )
    ContactSocialLink = apps.get_model('content', 'ContactSocialLink')
    ContactFormSection = apps.get_model('content', 'ContactFormSection')

    if not ContactHero.objects.exists():
        ContactHero.objects.create(
            title='Contact Us',
            subtitle="We'd love to hear from you. Reach out with "
            'questions, prayer requests, or to plan your visit.',
            scripture='',
            register='parchment',
            image='',
            image_alt='',
        )

    if not ContactDetailsSection.objects.exists():
        section = ContactDetailsSection.objects.create(
            email_heading='Email',
            email_address='',
            location_heading='Location',
            street='',
            city='',
            country='',
            maps_url='',
            directions_label='Get Directions \u2192',
            social_heading='Social Media',
        )
        for network, url, sort_order in SOCIAL_LINKS:
            ContactSocialLink.objects.create(
                section=section,
                network=network,
                label='',
                url=url,
                sort_order=sort_order,
                is_published=True,
            )

    if not ContactFormSection.objects.exists():
        ContactFormSection.objects.create(
            heading='Send a Message',
            name_label='Name',
            email_label='Email',
            phone_label='Phone (optional)',
            message_label='Message',
            submit_label='Send Message',
            sending_label='Sending\u2026',
            success_message="Message sent! We'll be in touch soon.",
            error_message='Something went wrong. '
            'Please email us directly.',
        )


def unseed_contact_content(apps, schema_editor):
    for model_name in (
        'ContactSocialLink',
        'ContactHero',
        'ContactDetailsSection',
        'ContactFormSection',
    ):
        apps.get_model('content', model_name).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            'content',
            '0027_contactdetailssection_contactformsection_contacthero_and_more',
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_contact_content, unseed_contact_content
        ),
    ]
