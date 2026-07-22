import psycopg2

conn = psycopg2.connect(dbname='RP', user='postgres', password='arno', host='localhost', port='5432')
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