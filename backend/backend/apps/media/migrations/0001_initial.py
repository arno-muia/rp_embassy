import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MediaAsset',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('file_path', models.CharField(blank=True, max_length=1024, null=True)),
                ('alt_text', models.CharField(blank=True, default='', max_length=512)),
                ('mime_type', models.CharField(blank=True, max_length=128, null=True)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('file_size', models.BigIntegerField(blank=True, null=True)),
                ('checksum', models.CharField(blank=True, max_length=64, null=True)),
                ('focal_point_x', models.FloatField(default=0.5)),
                ('focal_point_y', models.FloatField(default=0.5)),
                ('is_public', models.BooleanField(default=True)),
                ('usage_count', models.IntegerField(default=0)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Media Asset',
                'verbose_name_plural': 'Media Assets',
                'managed': True,
                'indexes': [models.Index(fields=['mime_type'], name='media_mime_idx'), models.Index(fields=['checksum'], name='media_checksum_idx'), models.Index(fields=['is_public'], name='media_public_idx')],
            },
        ),
    ]
