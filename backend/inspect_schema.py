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

print('=== TABLES ===')
cur.execute("select table_schema, table_name from information_schema.tables where table_type='BASE TABLE' order by table_schema, table_name;")
rows = cur.fetchall()
for r in rows:
    print(f'{r[0]}|{r[1]}')

print('\n=== COLUMNS FOR LEGACY TABLEs ===')
names = ['SystemConfig','SermonSeries','PublicSermon','WebsiteLeader','WebsiteTestimonial','WebsiteAcademyModule','ContactSubmission','VisitRsvp']
cur.execute("select table_name, column_name, data_type, is_nullable, column_default from information_schema.columns where table_name in %s order by table_name, ordinal_position;", (tuple(names),))
rows = cur.fetchall()
print('TABLE_NAME|COLUMN_NAME|DATA_TYPE|IS_NULLABLE|COLUMN_DEFAULT')
print('---------|-----------|---------|-----------|-------------')
for r in rows:
    print(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[4]}')

cur.close()
conn.close()