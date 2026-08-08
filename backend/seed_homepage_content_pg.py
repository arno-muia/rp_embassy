"""
Direct PostgreSQL seed script for homepage CMS content.
Populates: HomepageSettings, ChurchProfile, ContentBlock (VALUE/BELIEF/FAQ/EXPECTATION), HomepageSection
"""
import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Database connection
conn = psycopg2.connect(
    dbname=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT')
)
cur = conn.cursor()

def seed_homepage_settings():
    """Populate HomepageSettings hero configuration."""
    cur.execute("""
        INSERT INTO "HomepageSettings" (
            hero_title, hero_subtitle, hero_scripture, hero_scripture_reference,
            hero_background_image, hero_cta_text, hero_cta_url, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT DO NOTHING
    """, (
        'Welcome to Revival Palace',
        'A place where lives are transformed by the power of God',
        'For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.',
        'Jeremiah 29:11',
        'https://images.unsplash.com/photo-1501285679463-5d3b5c6e6b7a?w=1920&q=80',
        'Plan Your Visit',
        '/visit'
    ))
    print("HomepageSettings seeded")
    conn.commit()


def seed_church_profile():
    """Populate ChurchProfile mission, vision, and about content."""
    cur.execute("""
        INSERT INTO "ChurchProfile" (
            mission, vision, welcome_message, pastor_message, about_text, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT DO NOTHING
    """, (
        'Our mission is to make disciples of Jesus Christ by proclaiming the gospel, nurturing believers through teaching and fellowship, and sending them out to transform communities with the love of God. We exist to know Christ, make Him known, and show His love to the world.',
        'To be a kingdom-centered church that multiplies through discipleship, impacting nations with the transformative power of the Gospel. We envision a community where every believer is equipped, empowered, and released to fulfill their divine purpose.',
        'We are delighted to have you join us. At Revival Palace, you will experience the tangible presence of God, the warmth of authentic community, and the truth of His Word that transforms lives. Whether you are seeking, questioning, or growing in faith, there is a place for you here.',
        'Dear friends, as your pastor, I want you to know that you are deeply loved and valued. This church exists to serve you and your family, to help you grow in your relationship with Christ, and to walk alongside you through every season of life. May you encounter His presence today.',
        'Revival Palace is a multi-cultural, spirit-filled congregation passionate about making Jesus known. Founded on biblical truth and empowered by the Holy Spirit, we pursue authentic Christianity that transforms individuals, families, and communities. Through worship, teaching, and fellowship, we equip believers to live out their faith boldly.'
    ))
    print("ChurchProfile seeded")
    conn.commit()


def seed_content_blocks():
    """Populate ContentBlock entries for VALUE, BELIEF, FAQ, and EXPECTATION categories."""
    # VALUE records (5)
    values = [
        ('sonship', 'Sonship', 'We believe every believer is adopted as a beloved child of God, secure in His love and empowered by His Spirit to live in freedom and purpose.', 1),
        ('kingdom-culture', 'Kingdom Culture', 'We cultivate a culture that reflects heaven on earth, where Gods values of love, justice, and righteousness guide all we do.', 2),
        ('excellence', 'Excellence', 'We pursue excellence in all things, recognizing that our God is excellent and deserves our very best in every endeavor.', 3),
        ('integrity', 'Integrity', 'We walk in honesty and transparency before God and man, upholding truth even when it is costly or inconvenient.', 4),
        ('discipleship', 'Discipleship', 'We are committed to making disciples who multiply, growing in maturity and equipping others to do the same.', 5),
    ]
    
    # BELIEF records (5)
    beliefs = [
        ('salvation', 'Salvation', 'Salvation is received by grace through faith in Jesus Christ, resulting in eternal life, forgiveness of sins, and transformation by the Holy Spirit.', 1),
        ('lordship-of-christ', 'Lordship of Christ', 'Jesus Christ is the Lord over all creation, and His lordship transforms every area of life including family, work, and society.', 2),
        ('authority-of-scripture', 'Authority of Scripture', 'The Bible is the inspired, infallible Word of God, the ultimate authority for faith and practice, relevant for all generations.', 3),
        ('holy-spirit', 'Holy Spirit', 'The Holy Spirit empowers believers for service, produces spiritual fruit, and brings the gifts of the Spirit to build up the church.', 4),
        ('kingdom-embassy-theology', 'Kingdom Embassy Theology', 'We are called to represent heaven on earth, serving as ambassadors of Gods kingdom and advancing His purposes in society.', 5),
    ]
    
    # FAQ records (6)
    faqs = [
        ('first-visit', 'What should I expect on my first visit?', 'Youll be warmly welcomed by friendly faces, led in meaningful worship, and taught biblical truth in a practical way. Dress is casual, atmosphere is relaxed, and theres no pressure to participate beyond your comfort level.', 1),
        ('cell-group', 'How do I join a cell group?', 'Cell groups meet throughout the week in homes and at church. Visit our welcome desk on Sunday or contact us to find a group near you that fits your life stage and interests.', 2),
        ('membership', 'How do I become a member?', 'Membership involves attending our membership class, meeting with a pastor, and publicly declaring your commitment to our church family.', 3),
        ('serve', 'How can I serve?', 'We have diverse serving opportunities in kids ministry, worship, hospitality, outreach, media, and more. Fill out our serve interest form to explore possibilities.', 4),
        ('online-services', 'Do you have online services?', 'Yes! We stream our services live on Sundays at 9am and 11am. You can also access past sermons and resources on our website anytime.', 5),
        ('prayer-request', 'How can I request prayer?', 'Submit a prayer request through our website, app, or prayer wall in the sanctuary. Our prayer team intercedes daily for all requests.', 6),
    ]
    
    # EXPECTATION records (5)
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
    
    for content_type, blocks in all_blocks:
        for key, title, content, order in blocks:
            cur.execute("""
                INSERT INTO "ContentBlock" (key, title, content, content_type, display_order, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (key) DO UPDATE
                SET title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    content_type = EXCLUDED.content_type,
                    display_order = EXCLUDED.display_order,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
            """, (key, title, content, content_type, order, True))
            print(f"Seeded ContentBlock: {key} ({content_type})")
    
    conn.commit()


def seed_service_times():
    """Populate ServiceTime entries matching homepage source of truth.

    Note: Current model lacks platform, location, link, description, image,
    and time-range support. We map what we can using start times and names.
    """
    services = [
        ('SUNDAY', '06:00', 'Sunday Online Service', 1),
        ('SATURDAY', '09:00', 'Saturday Physical Service', 2),
        ('TUESDAY', '20:30', 'Kingdom Formation', 3),
        ('THURSDAY', '00:00', "Thursday Partner's Meeting", 4),
        ('WEDNESDAY', '00:00', 'Cell Group Meetings', 5),
    ]

    for day, time, label, order in services:
        cur.execute("""
            INSERT INTO "ServiceTime" (day, time, label, display_order, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (day, time) DO UPDATE
            SET label = EXCLUDED.label,
                display_order = EXCLUDED.display_order,
                updated_at = NOW()
        """, (day, time, label, order))
        print(f"Seeded ServiceTime: {day} {time} — {label}")


def seed_homepage_sections():
    """Populate HomepageSection entries for configurable homepage sections."""
    sections = [
        ('welcome', 'Welcome Section', 1),
        ('mission', 'Mission Section', 2),
        ('vision', 'Vision Section', 3),
        ('kingdom-culture', 'Kingdom Culture Section', 4),
        ('cell-groups', 'Join A Cell Group Section', 5),
    ]
    
    for key, name, order in sections:
        cur.execute("""
            INSERT INTO "HomepageSection" (section_name, enabled, display_order, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            ON CONFLICT (section_name) DO UPDATE
            SET enabled = EXCLUDED.enabled,
                display_order = EXCLUDED.display_order,
                updated_at = NOW()
        """, (key, True, order))
        print(f"Seeded HomepageSection: {name}")
    
    conn.commit()


def main():
    print("=" * 60)
    print("Seeding Homepage CMS Content via Direct PostgreSQL")
    print("=" * 60)
    
    print("\n[1/4] Populating HomepageSettings...")
    seed_homepage_settings()
    
    print("\n[2/4] Populating ChurchProfile...")
    seed_church_profile()
    
    print("\n[3/4] Populating ContentBlocks...")
    seed_content_blocks()
    
    print("\n[4/4] Populating HomepageSections...")
    seed_homepage_sections()
    
    print("\n[5/5] Populating ServiceTimes...")
    seed_service_times()
    
    print("\n" + "=" * 60)
    print("Seeding complete!")
    print("=" * 60)
    
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()