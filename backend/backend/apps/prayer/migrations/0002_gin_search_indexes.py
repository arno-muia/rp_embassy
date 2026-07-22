# Generated for GIN search indexes - B2.3B
# PostgreSQL GIN index for PrayerRequest full-text search

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prayer', '0001_initial'),
    ]

    operations = [
        # GIN index for PrayerRequest search (title=A, content=C)
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS idx_prayerrequest_search
            ON prayer_prayerrequest
            USING GIN (
                (setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
                 setweight(to_tsvector('simple', COALESCE(content, '')), 'C'))
            );
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_prayerrequest_search;",
        ),
    ]