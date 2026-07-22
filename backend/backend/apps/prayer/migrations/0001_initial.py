import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PrayerSubmission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('request', models.TextField()),
                ('anonymous', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='createdAt')),
            ],
            options={
                'db_table': 'PrayerSubmission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PrayerRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('category', models.CharField(choices=[('GENERAL', 'General'), ('HEALING', 'Healing'), ('THANKSGIVING', 'Thanksgiving'), ('FINANCE', 'Finance'), ('FAMILY', 'Family'), ('SALVATION', 'Salvation'), ('OTHER', 'Other')], default='GENERAL', max_length=20)),
                ('is_public', models.BooleanField(default=False)),
                ('is_anonymous', models.BooleanField(default=False)),
                ('workflow_status', models.CharField(choices=[('DRAFT', 'Draft'), ('IN_REVIEW', 'In Review'), ('APPROVED', 'Approved'), ('PUBLISHED', 'Published'), ('ARCHIVED', 'Archived')], default='DRAFT', max_length=20)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('ANSWERED', 'Answered'), ('CLOSED', 'Closed')], default='ACTIVE', max_length=20)),
                ('prayer_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Prayer Request',
                'verbose_name_plural': 'Prayer Requests',
                'managed': True,
                'indexes': [models.Index(fields=['workflow_status'], name='prayreq_wf_idx'), models.Index(fields=['is_public'], name='prayreq_public_idx')],
            },
        ),
    ]
