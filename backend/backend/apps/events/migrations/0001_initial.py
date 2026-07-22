import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChurchEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('type', models.CharField(choices=[('SERVICE', 'Service'), ('FELLOWSHIP', 'Fellowship'), ('OUTREACH', 'Outreach'), ('CONFERENCE', 'Conference'), ('FUNDRAISER', 'Fundraiser'), ('OTHER', 'Other')], max_length=20)),
                ('start_date_time', models.DateTimeField(db_column='startDateTime')),
                ('end_date_time', models.DateTimeField(blank=True, db_column='endDateTime', null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('image_url', models.CharField(blank=True, db_column='imageUrl', max_length=512, null=True)),
                ('gallery_url', models.CharField(blank=True, db_column='galleryUrl', max_length=512, null=True)),
                ('registration_required', models.BooleanField(db_column='registrationRequired', default=False)),
                ('max_attendees', models.IntegerField(blank=True, db_column='maxAttendees', null=True)),
                ('cost_cents', models.IntegerField(blank=True, db_column='costCents', null=True)),
                ('registration_open_date', models.DateTimeField(blank=True, db_column='registrationOpenDate', null=True)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('PUBLISHED', 'Published'), ('CANCELLED', 'Cancelled'), ('COMPLETED', 'Completed')], default='DRAFT', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='createdAt')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updatedAt')),
                ('created_by', models.UUIDField(blank=True, db_column='createdById', null=True)),
            ],
            options={
                'db_table': 'ChurchEvent',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EventRegistration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('walk_in_name', models.CharField(blank=True, db_column='walkInName', max_length=255, null=True)),
                ('walk_in_phone', models.CharField(blank=True, db_column='walkInPhone', max_length=64, null=True)),
                ('walk_in_email', models.CharField(blank=True, db_column='walkInEmail', max_length=255, null=True)),
                ('registration_date', models.DateTimeField(auto_now_add=True, db_column='registrationDate')),
                ('attended', models.BooleanField(blank=True, null=True)),
                ('payment_status', models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('WAIVED', 'Waived')], db_column='paymentStatus', max_length=20, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='createdAt')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updatedAt')),
            ],
            options={
                'db_table': 'EventRegistration',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField(blank=True, null=True)),
                ('severity', models.CharField(choices=[('INFO', 'Info'), ('SUCCESS', 'Success'), ('WARNING', 'Warning'), ('URGENT', 'Urgent')], default='INFO', max_length=10)),
                ('workflow_status', models.CharField(choices=[('DRAFT', 'Draft'), ('IN_REVIEW', 'In Review'), ('APPROVED', 'Approved'), ('PUBLISHED', 'Published'), ('ARCHIVED', 'Archived')], default='DRAFT', max_length=20)),
                ('display_from', models.DateTimeField(blank=True, null=True)),
                ('display_until', models.DateTimeField(blank=True, null=True)),
                ('link_url', models.URLField(blank=True, max_length=512, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('priority', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Announcement',
                'verbose_name_plural': 'Announcements',
                'managed': True,
                'indexes': [models.Index(fields=['is_active', 'display_from'], name='announce_active_idx'), models.Index(fields=['severity'], name='announce_severity_idx')],
            },
        ),
    ]
