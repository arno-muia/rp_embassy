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