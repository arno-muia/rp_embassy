# Generated for GIN search indexes - B2.3B
# PostgreSQL GIN index for Announcement full-text search

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        # GIN index for Announcement search (title=A, body=C)
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS idx_announcement_search
            ON events_announcement
            USING GIN (
                (setweight(to_tsvector('simple', COALESCE(title, '')), 'A') ||
                 setweight(to_tsvector('simple', COALESCE(body, '')), 'C'))
            );
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_announcement_search;",
        ),
    ]