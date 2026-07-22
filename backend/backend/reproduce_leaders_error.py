"""Script to reproduce the /api/leaders 500 error and capture traceback."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from rest_framework.test import APIRequestFactory
from backend.apps.content.views import LeaderViewSet

factory = APIRequestFactory()
request = factory.get('/api/leaders')
view = LeaderViewSet.as_view({'get': 'list'})

try:
    resp = view(request)
    print(f"Status: {resp.status_code}")
    data = resp.data
    print(f"Data: {data}")
except Exception as e:
    import traceback
    print("=== FULL TRACEBACK ===")
    traceback.print_exc()
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception message: {e}")