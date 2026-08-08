"""Convert EventRegistration FK columns and ensure PK types are UUID.

This repair migration drops lingering FK constraints and converts:
- ChurchEvent.id to uuid
- EventRegistration.id to uuid
- EventRegistration.eventId to uuid
- EventRegistration.memberId to uuid

Existing values are preserved via ::uuid cast.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0007_convert_text_pk_to_uuid'),
    ]

    operations = [
        # Drop constraints that block column type conversions
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'EventRegistration_eventId_fkey') THEN
                    ALTER TABLE "EventRegistration" DROP CONSTRAINT "EventRegistration_eventId_fkey";
                END IF;
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'EventRegistration_memberId_fkey') THEN
                    ALTER TABLE "EventRegistration" DROP CONSTRAINT "EventRegistration_memberId_fkey";
                END IF;
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ChurchEvent_createdById_fkey') THEN
                    ALTER TABLE "ChurchEvent" DROP CONSTRAINT "ChurchEvent_createdById_fkey";
                END IF;
            END $$;
            """,
            reverse_sql="",
        ),
        # Convert PK columns to uuid
        migrations.RunSQL(
            sql="""
            ALTER TABLE "ChurchEvent" ALTER COLUMN id TYPE uuid USING id::uuid;
            ALTER TABLE "EventRegistration" ALTER COLUMN id TYPE uuid USING id::uuid;
            """,
            reverse_sql="""
            ALTER TABLE "ChurchEvent" ALTER COLUMN id TYPE text;
            ALTER TABLE "EventRegistration" ALTER COLUMN id TYPE text;
            """,
        ),
        # Convert FK columns to uuid
        migrations.RunSQL(
            sql="""
            ALTER TABLE "EventRegistration" ALTER COLUMN "eventId" TYPE uuid USING "eventId"::uuid;
            ALTER TABLE "EventRegistration" ALTER COLUMN "memberId" TYPE uuid USING "memberId"::uuid;
            """,
            reverse_sql="""
            ALTER TABLE "EventRegistration" ALTER COLUMN "eventId" TYPE text;
            ALTER TABLE "EventRegistration" ALTER COLUMN "memberId" TYPE text;
            """,
        ),
    ]
