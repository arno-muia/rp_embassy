#!/usr/bin/env python
"""Verify content.0005 schema changes exist in PostgreSQL."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
django.setup()

from django.db import connection

def check_columns():
    """Check for columns added by migration 0005."""
    expected_columns = {
        'PublicSermon': ['seriesId'],
        'SystemConfig': ['updatedById'],
    }
    
    results = {}
    with connection.cursor() as cursor:
        for table, columns in expected_columns.items():
            cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY column_name;",
                [table]
            )
            existing = {row[0] for row in cursor.fetchall()}
            for col in columns:
                results[f"{table}.{col}"] = col in existing
    return results

def check_indexes():
    """Check for indexes created by migration 0005."""
    expected_indexes = {
        'ContactSubmission': ['contactsub_creat_idx'],
        'PublicSermon': [
            'sermon_serislug_idx',
            'sermon_ispub_idx',
            'sermon_date_idx',
            'PublicSermon_seriesId_959d1c5b',
        ],
        'SermonSeries': ['series_ispub_idx', 'series_sort_idx'],
        'SystemConfig': ['syscfg_key_idx', 'SystemConfig_updatedById_b94f0d76'],
        'VisitRsvp': ['rsvp_created_idx', 'rsvp_status_idx'],
        'WebsiteAcademyModule': ['academy_sort_idx'],
        'WebsiteTestimonial': ['testi_sort_idx'],
    }
    
    results = {}
    with connection.cursor() as cursor:
        for table, indexes in expected_indexes.items():
            cursor.execute(
                "SELECT indexname FROM pg_indexes WHERE tablename = %s ORDER BY indexname;",
                [table]
            )
            existing = {row[0] for row in cursor.fetchall()}
            for idx in indexes:
                results[f"{table}.{idx}"] = idx in existing
    return results

if __name__ == '__main__':
    print("=== Column Verification ===")
    col_results = check_columns()
    for key, exists in col_results.items():
        status = "EXISTS" if exists else "MISSING"
        print(f"  {key}: {status}")
    
    print("\n=== Index Verification ===")
    idx_results = check_indexes()
    for key, exists in idx_results.items():
        status = "EXISTS" if exists else "MISSING"
        print(f"  {key}: {status}")
    
    all_exist = all(col_results.values()) and all(idx_results.values())
    print(f"\n=== OVERALL: {'ALL SCHEMA ELEMENTS EXIST' if all_exist else 'SOME SCHEMA ELEMENTS MISSING'} ===")