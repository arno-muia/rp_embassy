"""B4.2.9 — SystemConfig Admin Failure Audit — diagnostic script.

Queries PostgreSQL to verify actual column names on the User table,
and attempts to reproduce the failing SQL via Django ORM.
"""
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

# ---------------------------------------------------------------------------
# 1. PostgreSQL schema inspection via psycopg2
# ---------------------------------------------------------------------------
print("=" * 70)
print("PHASE 1: PostgreSQL Schema Inspection — User table")
print("=" * 70)

try:
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

    cur.execute("""
        select column_name, data_type, is_nullable, column_default
        from information_schema.columns
        where table_name = 'User'
        order by ordinal_position;
    """)
    rows = cur.fetchall()
    print("\nCOLUMN_NAME|DATA_TYPE|IS_NULLABLE|COLUMN_DEFAULT")
    print("-----------|----------|-----------|-------------")
    for r in rows:
        print(f'{r[0]}|{r[1]}|{r[2]}|{r[3]}')

    cur.close()
    conn.close()
except Exception as e:
    print(f"psycopg2 query failed: {e}")

# ---------------------------------------------------------------------------
# 2. Django model field / db_column mapping inspection
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 2: Django Model Field -> db_column Mapping -- accounts.User")
print("=" * 70)

from backend.apps.accounts.models import User

print(f"\nModel: {User}")
print(f"db_table: {User._meta.db_table}")
print(f"managed: {User._meta.managed}")

print("\nField Name | db_column | is_relation")
print("-----------|-----------|------------")
for field in User._meta.get_fields():
    db_col = getattr(field, 'db_column', None)
    # For non-concrete fields, db_column may not exist
    if hasattr(field, 'db_column'):
        db_col = field.db_column
    else:
        db_col = '(N/A)'
    is_rel = field.is_relation
    print(f"{field.name}|{db_col}|{is_rel}")

# ---------------------------------------------------------------------------
# 3. Reproduce the failing SQL — Django ORM query on User
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 3: Reproduce Failing SQL — Django ORM query")
print("=" * 70)

from django.db import connection, reset_queries

# Enable query capture
reset_queries()

try:
    # This is what Django Admin does when rendering the updated_by FK dropdown:
    # it creates a ModelChoiceField with queryset = User.objects.all()
    # which selects ALL fields including password_hash
    users = list(User.objects.all()[:1])
    print(f"\nQuerySet returned {len(users)} row(s)")
except Exception as e:
    print(f"\nQuery FAILED: {type(e).__name__}: {e}")

# Show captured SQL
print("\nCaptured SQL queries:")
for i, q in enumerate(connection.queries):
    print(f"\nQuery #{i+1}:")
    print(f"  SQL: {q['sql']}")
    print(f"  Time: {q['time']}s")

# ---------------------------------------------------------------------------
# 4. Show the exact SQL that references password_hash
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 4: SQL containing 'password_hash'")
print("=" * 70)

found = False
for i, q in enumerate(connection.queries):
    if 'password_hash' in q['sql']:
        found = True
        print(f"\nQuery #{i+1} references password_hash:")
        print(f"  SQL: {q['sql']}")

if not found:
    print("\nNo captured query references 'password_hash'.")
    print("This may indicate the query failed before SQL was logged.")
    print("Check the error message above for the column name.")

# ---------------------------------------------------------------------------
# 5. SystemConfig FK field inspection
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PHASE 5: SystemConfig FK field — updated_by")
print("=" * 70)

from backend.apps.content.models import SystemConfig

for field in SystemConfig._meta.get_fields():
    if field.name == 'updated_by':
        print(f"\nField: {field.name}")
        print(f"  Type: {type(field).__name__}")
        print(f"  Related model: {field.related_model}")
        print(f"  db_column: {field.db_column}")
        print(f"  db_constraint: {field.db_constraint}")
        print(f"  remote_field.model: {field.remote_field.model}")

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)