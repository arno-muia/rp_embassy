"""Add cta_location field to HomepageSettings."""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0012_pastorprofile_and_homepage_cta"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepagesettings",
            name="cta_location",
            field=models.CharField(
                max_length=255,
                null=True,
                blank=True,
                default="Thika, Kenya",
            ),
        ),
    ]