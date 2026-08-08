"""
Migration to expand ServiceTime model with all UI fields.

Adds: name, platform, location, link, description, image, is_published
Alters: time (TimeField -> CharField for display strings), label (nullable)
Adds: index on is_published
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_convert_systemconfig_updatedbyid_to_uuid'),
    ]

    operations = [
        # Add name field with a one-off default for existing rows
        migrations.AddField(
            model_name='servicetime',
            name='name',
            field=models.CharField(
                default='Service',
                help_text="Display name, e.g. 'Sunday Online Service'",
                max_length=128,
            ),
            preserve_default=False,
        ),
        # Add platform field
        migrations.AddField(
            model_name='servicetime',
            name='platform',
            field=models.CharField(
                choices=[('physical', 'Physical'), ('online', 'Online')],
                default='physical',
                max_length=12,
            ),
        ),
        # Add location field
        migrations.AddField(
            model_name='servicetime',
            name='location',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        # Add link field
        migrations.AddField(
            model_name='servicetime',
            name='link',
            field=models.URLField(blank=True, max_length=512, null=True),
        ),
        # Add description field
        migrations.AddField(
            model_name='servicetime',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        # Add image field
        migrations.AddField(
            model_name='servicetime',
            name='image',
            field=models.CharField(blank=True, help_text='Image path or URL', max_length=512, null=True),
        ),
        # Add is_published field
        migrations.AddField(
            model_name='servicetime',
            name='is_published',
            field=models.BooleanField(default=True),
        ),
        # Alter time field from TimeField to CharField for display strings
        migrations.AlterField(
            model_name='servicetime',
            name='time',
            field=models.CharField(
                help_text="Display string, e.g. '6:00 AM - 8:00 AM' or 'TBD'",
                max_length=64,
            ),
        ),
        # Alter label field to be nullable (legacy field, kept for backward compat)
        migrations.AlterField(
            model_name='servicetime',
            name='label',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        # Add index on is_published
        migrations.AddIndex(
            model_name='servicetime',
            index=models.Index(
                fields=['is_published'],
                name='servicetime_published_idx',
            ),
        ),
    ]
