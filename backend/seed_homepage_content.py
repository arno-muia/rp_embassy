"""
Seed script for populating homepage CMS content.
Populates: HomepageSettings, ChurchProfile, ContentBlock (VALUE/BELIEF/FAQ/EXPECTATION), HomepageSection, ServiceTime
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.content.models import (
    HomepageSettings,
    ChurchProfile,
    ContentBlock,
    HomepageSection,
    ServiceTime,
    DayOfWeek,
)


def seed_homepage_settings():
    """Populate HomepageSettings hero configuration."""
    settings, created = HomepageSettings.objects.get_or_create(
        defaults={
            'hero_title': 'Welcome to Revival Palace',
            'hero_subtitle': 'A place where lives are transformed by the power of God',
            'hero_scripture': 'For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.',
            'hero_scripture_reference': 'Jeremiah 29:11',
            'hero_background_image': 'https://images.unsplash.com/photo-1501285679463-5d3b5c6e6b7a?w=1920&q=80',
            'hero_cta_text': 'Plan Your Visit',
            'hero_cta_url': '/visit',
        }
    )
    if created:
        print(f"Created HomepageSettings: {settings}")
    else:
        print(f"HomepageSettings already exists, updating...")
        settings.hero_title = 'Welcome to Revival Palace'
        settings.hero_subtitle = 'A place where lives are transformed by the power of God'
        settings.hero_scripture = 'For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.'
        settings.hero_scripture_reference = 'Jeremiah 29:11'
        settings.hero_background_image = 'https://images.unsplash.com/photo-1501285679463-5d3b5c6e6b7a?w=1920&q=80'
        settings.hero_cta_text = 'Plan Your Visit'
        settings.hero_cta_url = '/visit'
        settings.save()
        print(f"Updated HomepageSettings: {settings}")
    return settings


def seed_church_profile():
    """Populate ChurchProfile mission, vision, and about content."""
    profile, created = ChurchProfile.objects.get_or_create(
        defaults={
            'mission': 'Our mission is to make disciples of Jesus Christ by proclaiming the gospel, nurturing believers through teaching and fellowship, and sending them out to transform communities with the love of God. We exist to know Christ, make Him known, and show His love to the world.',
            'vision': 'To be a kingdom-centered church that multiplies through discipleship, impacting nations with the transformative power of the Gospel. We envision a community where every believer is equipped, empowered, and released to fulfill their divine purpose.',
            'welcome_message': 'We are delighted to have you join us. At Revival Palace, you will experience the tangible presence of God, the warmth of authentic community, and the truth of His Word that transforms lives. Whether you are seeking, questioning, or growing in faith, there is a place for you here.',
            'pastor_message': 'Dear friends, as your pastor, I want you to know that you are deeply loved and valued. This church exists to serve you and your family, to help you grow in your relationship with Christ, and to walk alongside you through every season of life. May you encounter His presence today.',
            'about_text': 'Revival Palace is a multi-cultural, spirit-filled congregation passionate about making Jesus known. Founded on biblical truth and empowered by the Holy Spirit, we pursue authentic Christianity that transforms individuals, families, and communities. Through worship, teaching, and fellowship, we equip believers to live out their faith boldly.',
        }
    )
    if created:
        print(f"Created ChurchProfile: {profile}")
    else:
        print(f"ChurchProfile already exists, updating...")
        profile.mission = 'Our mission is to make disciples of Jesus Christ by proclaiming the gospel, nurturing believers through teaching and fellowship, and sending them out to transform communities with the love of God. We exist to know Christ, make Him known, and show His love to the world.'
        profile.vision = 'To be a kingdom-centered church that multiplies through discipleship, impacting nations with the transformative power of the Gospel. We envision a community where every believer is equipped, empowered, and released to fulfill their divine purpose.'
        profile.welcome_message = 'We are delighted to have you join us. At Revival Palace, you will experience the tangible presence of God, the warmth of authentic community, and the truth of His Word that transforms lives. Whether you are seeking, questioning, or growing in faith, there is a place for you here.'
        profile.pastor_message = 'Dear friends, as your pastor, I want you to know that you are deeply loved and valued. This church exists to serve you and your family, to help you grow in your relationship with Christ, and to walk alongside you through every season of life. May you encounter His presence today.'
        profile.about_text = 'Revival Palace is a multi-cultural, spirit-filled congregation passionate about making Jesus known. Founded on biblical truth and empowered by the Holy Spirit, we pursue authentic Christianity that transforms individuals, families, and communities. Through worship, teaching, and fellowship, we equip believers to live out their faith boldly.'
        profile.save()
        print(f"Updated ChurchProfile: {profile}")
    return profile


def seed_content_blocks():
    """Populate ContentBlock entries for VALUE, BELIEF, FAQ, and EXPECTATION categories."""
    values = [
        ('sonship', 'Sonship', 'We believe every believer is adopted as a beloved child of God, secure in His love and empowered by His Spirit to live in freedom and purpose.', 1),
        ('kingdom-culture', 'Kingdom Culture', 'We cultivate a culture that reflects heaven on earth, where Gods values of love, justice, and righteousness guide all we do.', 2),
        ('excellence', 'Excellence', 'We pursue excellence in all things, recognizing that our God is excellent and deserves our very best in every endeavor.', 3),
        ('integrity', 'Integrity', 'We walk in honesty and transparency before God and man, upholding truth even when it is costly or inconvenient.', 4),
        ('discipleship', 'Discipleship', 'We are committed to making disciples who multiply, growing in maturity and equipping others to do the same.', 5),
    ]
    beliefs = [
        ('salvation', 'Salvation', 'Salvation is received by grace through faith in Jesus Christ, resulting in eternal life, forgiveness of sins, and transformation by the Holy Spirit.', 1),
        ('lordship-of-christ', 'Lordship of Christ', 'Jesus Christ is the Lord over all creation, and His lordship transforms every area of life including family, work, and society.', 2),
        ('authority-of-scripture', 'Authority of Scripture', 'The Bible is the inspired, infallible Word of God, the ultimate authority for faith and practice, relevant for all generations.', 3),
        ('holy-spirit', 'Holy Spirit', 'The Holy Spirit empowers believers for service, produces spiritual fruit, and brings the gifts of the Spirit to build up the church.', 4),
        ('kingdom-embassy-theology', 'Kingdom Embassy Theology', 'We are called to represent heaven on earth, serving as ambassadors of Gods kingdom and advancing His purposes in society.', 5),
    ]
    faqs = [
        ('first-visit', 'What should I expect on my first visit?', 'Youll be warmly welcomed by friendly faces, led in meaningful worship, and taught biblical truth in a practical way. Dress is casual, atmosphere is relaxed, and theres no pressure to participate beyond your comfort level.', 1),
        ('cell-group', 'How do I join a cell group?', 'Cell groups meet throughout the week in homes and at church. Visit our welcome desk on Sunday or contact us to find a group near you that fits your life stage and interests.', 2),
        ('membership', 'How do I become a member?', 'Membership involves attending our membership class, meeting with a pastor, and publicly declaring your commitment to our church family.', 3),
        ('serve', 'How can I serve?', 'We have diverse serving opportunities in kids ministry, worship, hospitality, outreach, media, and more. Fill out our serve interest form to explore possibilities.', 4),
        ('online-services', 'Do you have online services?', 'Yes! We stream our services live on Sundays at 9am and 11am. You can also access past sermons and resources on our website anytime.', 5),
        ('prayer-request', 'How can I request prayer?', 'Submit a prayer request through our website, app, or prayer wall in the sanctuary. Our prayer team intercedes daily for all requests.', 6),
    ]
    expectations = [
        ('warm-welcome', 'Warm Welcome', 'You will be greeted with genuine warmth by people who are glad you came. We want you to feel at home from the moment you arrive.', 1),
        ('worship', 'Worship', 'Experience heartfelt worship led by gifted musicians and singers, combining contemporary songs with timeless hymns in Spirit-led expression.', 2),
        ('practical-teaching', 'Practical Teaching', 'Hear biblical truth presented in ways that connect to real life, helping you grow in faith and apply scripture to daily challenges.', 3),
        ('fellowship', 'Fellowship', 'Connect with others through conversation, coffee, and community. We value authentic relationships that encourage spiritual growth.', 4),
        ('prayer-ministry', 'Prayer Ministry', 'Receive prayer from trained prayer ministers available after each service. We believe in the power of prayer to bring healing and breakthrough.', 5),
    ]
    all_blocks = (
        [('VALUE', values), ('BELIEF', beliefs), ('FAQ', faqs), ('EXPECTATION', expectations)]
    )
    created_count = 0
    for content_type, blocks in all_blocks:
        for key, title, content, order in blocks:
            block, created = ContentBlock.objects.get_or_create(
                key=key,
                defaults={
                    'title': title,
                    'content': content,
                    'content_type': content_type,
                    'display_order': order,
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                print(f"Created ContentBlock: {key} ({content_type})")
            else:
                print(f"ContentBlock exists: {key} ({content_type})")
    return created_count


def seed_service_times():
    """Populate ServiceTime entries with all UI fields from the single source of truth.

    Each record stores every field rendered in the Service Times UI:
    name, day, time, platform, location, link, description, image, is_published, display_order
    """
    services = [
        {
            'name': 'Sunday Online Service',
            'day': DayOfWeek.SUNDAY,
            'time': '6:00 AM - 8:00 AM',
            'platform': 'online',
            'location': 'Google Meet',
            'link': 'https://www.youtube.com/@RoyalPriesthoodEmbassy',
            'description': 'Early morning worship and teaching for our online family. Join from anywhere in the world.',
            'image': '/images/events/sunday-online-service-poster-1.jpeg',
            'display_order': 1,
        },
        {
            'name': 'Saturday Physical Service',
            'day': DayOfWeek.SATURDAY,
            'time': '9:00 AM - 12:00 PM',
            'platform': 'physical',
            'location': 'Voice of Grace, Behind Spoonzoom, Thika',
            'link': None,
            'description': 'Our primary worship gathering -- worship, teaching, and ministry time in the sanctuary.',
            'image': '/images/services/kingdom-formation-2.jpg',
            'display_order': 2,
        },
        {
            'name': 'Kingdom Formation',
            'day': DayOfWeek.TUESDAY,
            'time': '8:30 PM',
            'platform': 'online',
            'location': 'Google Meet',
            'link': 'https://www.youtube.com/@RoyalPriesthoodEmbassy',
            'description': 'Blueprint Tuesdays -- deep discipleship teaching and Holy Communion. Where Kingdom patterns are revealed.',
            'image': '/images/events/kingdom-formation-poster.jpeg',
            'display_order': 3,
        },
        {
            'name': "Thursday Partner's Meeting",
            'day': DayOfWeek.THURSDAY,
            'time': 'TBD',
            'platform': 'online',
            'location': 'Voice of Grace, Behind Spoonzoom, Thika',
            'link': None,
            'description': 'Corporate prayer and intercession for the nation, church, and families.',
            'image': '/images/services/kingdom-formation-3.jpg',
            'display_order': 4,
        },
        {
            'name': 'Cell Group Meetings',
            'day': DayOfWeek.WEDNESDAY,
            'time': 'TBD',
            'platform': 'physical',
            'location': 'Thika, Juja, Bypass, Kahawa Sukari, Kasarani, Kitengela',
            'link': None,
            'description': '',
            'image': '/images/services/kingdom-formation-3.jpg',
            'display_order': 5,
        },
    ]

    created_count = 0
    for svc in services:
        name = svc['name']
        obj, created = ServiceTime.objects.get_or_create(
            name=name,
            defaults={
                'day': svc['day'],
                'time': svc['time'],
                'platform': svc['platform'],
                'location': svc['location'],
                'link': svc['link'],
                'description': svc['description'],
                'image': svc['image'],
                'is_published': True,
                'display_order': svc['display_order'],
            }
        )
        if created:
            created_count += 1
            print(f"Created ServiceTime: {name}")
        else:
            # Update all fields to ensure DB matches the source of truth
            updated = False
            for field, value in svc.items():
                if getattr(obj, field) != value:
                    setattr(obj, field, value)
                    updated = True
            obj.is_published = True
            if updated:
                obj.save()
                print(f"Updated ServiceTime: {name}")
            else:
                print(f"ServiceTime exists: {name}")
    return created_count


def seed_homepage_sections():
    """Populate HomepageSection entries for configurable homepage sections."""
    sections = [
        ('welcome', 'Welcome Section', 1),
        ('mission', 'Mission Section', 2),
        ('vision', 'Vision Section', 3),
        ('kingdom-culture', 'Kingdom Culture Section', 4),
        ('cell-groups', 'Join A Cell Group Section', 5),
    ]
    created_count = 0
    for key, name, order in sections:
        section, created = HomepageSection.objects.get_or_create(
            section_name=key,
            defaults={
                'enabled': True,
                'display_order': order,
            }
        )
        if created:
            created_count += 1
            print(f"Created HomepageSection: {name}")
        else:
            print(f"HomepageSection exists: {name}")
    return created_count


def main():
    print("=" * 60)
    print("Seeding Homepage CMS Content")
    print("=" * 60)

    print("\n[1/5] Populating HomepageSettings...")
    seed_homepage_settings()

    print("\n[2/5] Populating ChurchProfile...")
    seed_church_profile()

    print("\n[3/5] Populating ContentBlocks...")
    seed_content_blocks()

    print("\n[4/5] Populating HomepageSections...")
    seed_homepage_sections()

    print("\n[5/5] Populating ServiceTimes...")
    seed_service_times()

    print("\n" + "=" * 60)
    print("Seeding complete!")
    print("=" * 60)

    # Print summary
    print("\nRecord Counts:")
    print(f"  HomepageSettings: {HomepageSettings.objects.count()}")
    print(f"  ChurchProfile: {ChurchProfile.objects.count()}")
    print(f"  ContentBlock (all): {ContentBlock.objects.count()}")
    print(f"  HomepageSection: {HomepageSection.objects.count()}")
    print(f"  ServiceTime: {ServiceTime.objects.count()}")

    print("\nServiceTime records:")
    for st in ServiceTime.objects.all().order_by('display_order'):
        print(f"  [{st.display_order}] {st.name} — {st.get_day_display()} {st.time} ({st.platform})")


if __name__ == '__main__':
    main()
