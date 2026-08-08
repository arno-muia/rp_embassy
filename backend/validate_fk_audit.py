import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from backend.apps.content.models import PublicSermon, SermonSeries, SystemConfig, WebsiteTestimonial, WebsiteLeader
from backend.apps.events.models import EventRegistration, ChurchEvent

print("=== FK Column Type Verification ===")
cursor = connection.cursor()
cursor.execute("""
    select table_name, column_name, data_type
    from information_schema.columns
    where table_name in ('EventRegistration','PublicSermon','SystemConfig','ChurchEvent')
      and column_name in ('eventId','memberId','seriesId','updatedById','id')
    order by table_name, column_name;
""")
rows = cursor.fetchall()
print('TABLE_NAME|COLUMN_NAME|DATA_TYPE')
for r in rows:
    print(f'{r[0]}|{r[1]}|{r[2]}')

print("\n=== ORM Join Test ===")
try:
    qs = PublicSermon.objects.select_related('series').all()
    count = qs.count()
    print(f'PublicSermon.select_related(series) OK — {count} rows')
except Exception as e:
    print(f'PublicSermon.select_related FAILED: {e}')

try:
    qs = EventRegistration.objects.select_related('event').all()
    count = qs.count()
    print(f'EventRegistration.select_related(event) OK — {count} rows')
except Exception as e:
    print(f'EventRegistration.select_related FAILED: {e}')

print("\n=== Admin Page Simulation ===")
try:
    for model in [WebsiteTestimonial, WebsiteLeader, PublicSermon, SermonSeries]:
        fields = [f.name for f in model._meta.get_fields()]
        print(f'{model.__name__} fields: {fields}')
except Exception as e:
    print(f'Admin model inspection FAILED: {e}')

cursor.close()