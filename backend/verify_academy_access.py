"""Verify AcademyAccess state: users, members, and existing grants."""
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check users
    cursor.execute("SELECT id, email, role, \"isActive\" FROM \"User\" LIMIT 10")
    users = cursor.fetchall()
    print("=== Users (up to 10) ===")
    for u in users:
        print(f"  id={u[0]}, email={u[1]}, role={u[2]}, isActive={u[3]}")

    # Check members
    cursor.execute("SELECT id, \"firstName\", \"lastName\", status, \"userId\" FROM \"Member\" LIMIT 10")
    members = cursor.fetchall()
    print("\n=== Members (up to 10) ===")
    for m in members:
        print(f"  id={m[0]}, name={m[1]} {m[2]}, status={m[3]}, userId={m[4]}")

    # Check AcademyAccess records
    cursor.execute("SELECT id, user_id, \"is_active\", note FROM \"AcademyAccess\" LIMIT 10")
    access = cursor.fetchall()
    print("\n=== AcademyAccess records (up to 10) ===")
    for a in access:
        print(f"  id={a[0]}, user_id={a[1]}, is_active={a[2]}, note={a[3]}")

    # Check if any users are linked to ACTIVE members
    cursor.execute(
        'SELECT COUNT(*) FROM "User" u '
        'JOIN "Member" m ON u.id = m."userId" '
        'WHERE m.status = %s AND u."isActive" = true',
        ['ACTIVE']
    )
    count = cursor.fetchone()[0]
    print(f"\n=== Users linked to ACTIVE members: {count} ===")