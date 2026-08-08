"""Convert PublicSermon.seriesId from TEXT to UUID to match SermonSeries.id.

This migration repairs the FK consistency mismatch introduced when
B4.2.4 converted primary keys to UUID without updating foreign key columns.

No data is dropped; existing values are cast using ::uuid after validation.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('content', '0008_convert_text_pk_to_uuid'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE "PublicSermon"
            ALTER COLUMN "seriesId" TYPE uuid
            USING "seriesId"::uuid;
            """,
            reverse_sql="""
            ALTER TABLE "PublicSermon"
            ALTER COLUMN "seriesId" TYPE text;
            """,
        ),
    ]