import psycopg2

conn = psycopg2.connect(dbname='RP', user='postgres', password='arno', host='localhost', port='5432')
cur = conn.cursor()

print('=== ChurchEvent COLUMNS ===')
cur.execute("select column_name, data_type, is_nullable, column_default from information_schema.columns where table_name = 'ChurchEvent' order by ordinal_position;")
rows = cur.fetchall()
for r in rows:
    print(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}')

print('\n=== EventRegistration COLUMNS ===')
cur.execute("select column_name, data_type, is_nullable, column_default from information_schema.columns where table_name = 'EventRegistration' order by ordinal_position;")
rows = cur.fetchall()
for r in rows:
    print(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}')

cur.close()
conn.close()