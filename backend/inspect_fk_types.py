import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

conn = psycopg2.connect(
    dbname=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT')
)
cur = conn.cursor()

# Check FK-like columns across all relevant tables
tables = [
    'SystemConfig','SermonSeries','PublicSermon','WebsiteLeader','WebsiteTestimonial',
    'WebsiteAcademyModule','ContactSubmission','VisitRsvp','ChurchEvent','EventRegistration',
    'PrayerSubmission','PrayerRequest','Member','Household','HouseholdMember',
    'User','AuditLog','Announcement','MediaAsset'
]

cur.execute("""
    select table_name, column_name, data_type, is_nullable
    from information_schema.columns
    where table_name in (
        'SystemConfig','SermonSeries','PublicSermon','WebsiteLeader','WebsiteTestimonial',
        'WebsiteAcademyModule','ContactSubmission','VisitRsvp','ChurchEvent','EventRegistration',
        'PrayerSubmission','PrayerRequest','Member','Household','HouseholdMember',
        'User','AuditLog','Announcement','MediaAsset'
    )
      and (column_name ilike '%Id' or column_name ilike '%_id')
    order by table_name, ordinal_position;
""")
rows = cur.fetchall()

print('TABLE_NAME|COLUMN_NAME|DATA_TYPE|IS_NULLABLE')
print('---------|-----------|---------|----------')
for r in rows:
    print(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}')

cur.close()
conn.close()