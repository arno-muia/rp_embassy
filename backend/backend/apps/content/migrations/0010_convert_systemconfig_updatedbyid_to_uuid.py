"""Convert SystemConfig.updatedById from TEXT to UUID to match User.id.

This repair migration aligns the FK column with the referenced User PK type.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('content', '0009_convert_publicsermon_seriesid_to_uuid'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE "SystemConfig"
            ALTER COLUMN "updatedById" TYPE uuid
            USING "updatedById"::uuid;
            """,
            reverse_sql="""
            ALTER TABLE "SystemConfig"
            ALTER COLUMN "updatedById" TYPE text;
            """,
        ),
    ]