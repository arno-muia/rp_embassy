import sys
import os
from dotenv import load_dotenv

print("Attempting import psycopg2...")
try:
    import psycopg2
    print("psycopg2 imported OK")
except Exception as e:
    print("psycopg2 import failed:", e)
    sys.exit(1)

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

print("Connecting...")
conn = psycopg2.connect(
    dbname=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT')
)
conn.autocommit = True
cur = conn.cursor()

tables = [
    'PublicSermon', 'SystemConfig', 'SermonSeries', 'ContactSubmission',
    'VisitRsvp', 'WebsiteAcademyModule', 'WebsiteTestimonial'
]

for t in tables:
    print(f"--- {t} ---")
    cur.execute(
        "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = %s ORDER BY indexname;",
        [t]
    )
    rows = cur.fetchall()
    for r in rows:
        print(f"  {r[0]} | {r[1]}")

cur.close()
conn.close()
print("Done")