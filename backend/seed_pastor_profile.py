"""Seed initial PastorProfile record from existing hardcoded content."""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.content.models import PastorProfile

# Existing hardcoded content from PastorSection.astro
pastor_data = {
    'name': 'Charles Muchemi',
    'title': 'Our Pastor',
    'image': '/images/team/charles-muchemi.jpg',
    'biography': (
        'Welcome to Royal Priesthood Embassy. I am honored to serve as your pastor '
        'and to be part of this incredible community of believers. Our church is a '
        'place where you can experience the love of Christ, grow in your faith, and '
        'discover your God-given purpose.'
        '\n\n'
        'Whether you are joining us for the first time or have been part of our '
        'congregation for years, we are glad you are here. We believe that every '
        'person is created in the image of God and has a unique role to play in '
        'His kingdom.'
        '\n\n'
        'At RP, we are more than just a church—we are a family. We invite you to '
        'explore our ministries, connect with our community, and let us walk '
        'alongside you in your spiritual journey.'
        '\n\n'
        'Pastor Charles Muchemi'
    ),
    'cta_text': 'Learn more about RP',
    'cta_url': '/about',
    'display_order': 0,
    'is_active': True,
}

# Check if a PastorProfile already exists
existing = PastorProfile.objects.first()
if existing:
    print(f'PastorProfile already exists: {existing.name}')
    print('Skipping seed. Update via Django Admin if needed.')
    sys.exit(0)

# Create the initial PastorProfile
pastor = PastorProfile.objects.create(**pastor_data)
print(f'Successfully created PastorProfile: {pastor.name}')
print(f'ID: {pastor.id}')
print(f'Active: {pastor.is_active}')