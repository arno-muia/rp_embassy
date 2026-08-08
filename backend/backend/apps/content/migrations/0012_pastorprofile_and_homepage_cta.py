"""Create PastorProfile model and add CTA fields to HomepageSettings."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('content', '0011_servicetime_expand_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='PastorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('image', models.CharField(max_length=512)),
                ('biography', models.TextField()),
                ('cta_text', models.CharField(blank=True, default='Learn More', max_length=255)),
                ('cta_url', models.CharField(blank=True, default='/about', max_length=512)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Pastor Profile',
                'verbose_name_plural': 'Pastor Profiles',
            },
        ),
        migrations.AddField(
            model_name='homepagesettings',
            name='cta_heading',
            field=models.CharField(blank=True, default='Join Us This Sunday', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='homepagesettings',
            name='cta_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='homepagesettings',
            name='cta_button_text',
            field=models.CharField(blank=True, default='Plan Your Visit', max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='homepagesettings',
            name='cta_button_url',
            field=models.URLField(blank=True, default='/visit', max_length=512, null=True),
        ),
    ]
