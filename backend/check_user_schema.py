"""Check the User table schema to understand the id column type."""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = 'User' ORDER BY ordinal_position"
    )
    rows = cursor.fetchall()
    print("=== User table columns ===")
    for col in rows:
        print(f"  {col[0]}: {col[1]}")