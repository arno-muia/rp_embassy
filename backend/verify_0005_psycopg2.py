import sys
print("Attempting import psycopg2...")
try:
    import psycopg2
    print("psycopg2 imported OK")
except Exception as e:
    print("psycopg2 import failed:", e)
    sys.exit(1)

print("Connecting...")
conn = psycopg2.connect(
    dbname='RP', user='postgres', password='arno', host='localhost', port='5432'
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