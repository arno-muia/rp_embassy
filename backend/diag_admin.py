"""Diagnostic script for ServiceTime admin visibility investigation."""
import os
import sys

# Ensure backend directory is on the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from backend.apps.content.models import ServiceTime, GlobalSettings, ContentBlock

User = get_user_model()

print("=" * 70)
print("PHASE 1: Admin Registration Audit")
print("=" * 70)

# Check if ServiceTime is in the registry
print(f"\n1. ServiceTime in admin.site._registry: {ServiceTime in admin.site._registry}")

# List all registered models
print("\n2. All registered models in admin.site._registry:")
for model, model_admin in admin.site._registry.items():
    print(f"   - {model._meta.app_label}.{model.__name__} -> {model_admin.__class__.__name__}")

# Check for duplicate registrations
print("\n3. Checking for duplicate registrations:")
st_count = sum(1 for m in admin.site._registry if m == ServiceTime)
print(f"   ServiceTime registered {st_count} time(s)")

# Check the ServiceTime admin
if ServiceTime in admin.site._registry:
    st_admin = admin.site._registry[ServiceTime]
    print(f"\n4. ServiceTimeAdmin details:")
    print(f"   Class: {st_admin.__class__.__name__}")
    print(f"   Module: {st_admin.__class__.__module__}")
    print(f"   Has get_model_perms: {hasattr(st_admin, 'get_model_perms')}")
    print(f"   Has has_module_permission: {hasattr(st_admin, 'has_module_permission')}")

# Check app config
print("\n5. App config for content:")
from django.apps import apps
content_app = apps.get_app_config('content')
print(f"   App config class: {content_app.__class__.__name__}")
print(f"   App config module: {content_app.__class__.__module__}")
print(f"   App label: {content_app.label}")
print(f"   App name: {content_app.name}")
print(f"   Verbose name: {content_app.verbose_name}")
print(f"   Has default attr: {hasattr(content_app, 'default')}")
if hasattr(content_app, 'default'):
    print(f"   default = {content_app.default}")

# List all models in the content app
print("\n6. All models in content app:")
for model in content_app.get_models():
    in_admin = model in admin.site._registry
    print(f"   - {model.__name__} (in admin: {in_admin})")

print("\n" + "=" * 70)
print("PHASE 2: Admin URL Audit")
print("=" * 70)

# Check URL resolution
from django.urls import reverse, NoReverseMatch
print("\n7. URL resolution for ServiceTime:")
urls_to_check = [
    ('changelist', 'admin:content_servicetime_changelist'),
    ('add', 'admin:content_servicetime_add'),
    ('change', 'admin:content_servicetime_change'),
    ('delete', 'admin:content_servicetime_delete'),
]
for name, url_name in urls_to_check:
    try:
        url = reverse(url_name, args=[1] if 'changelist' not in name and 'add' not in name else [])
        print(f"   {name}: {url} - OK")
    except NoReverseMatch as e:
        print(f"   {name}: NoReverseMatch - {e}")

print("\n" + "=" * 70)
print("PHASE 3: Admin Index Rendering Audit")
print("=" * 70)

# Create a fake request with a superuser
factory = RequestFactory()
superuser = User.objects.filter(is_superuser=True).first()
if superuser is None:
    print("\n   WARNING: No superuser found in database")
    # Create a mock request
    request = factory.get('/admin/')
    request.user = type('MockUser', (), {'is_active': True, 'is_staff': True, 'is_superuser': True})()
else:
    print(f"\n   Using superuser: {superuser.username}")
    request = factory.get('/admin/')
    request.user = superuser

# Check get_model_perms for ServiceTime
if ServiceTime in admin.site._registry:
    st_admin = admin.site._registry[ServiceTime]
    perms = st_admin.get_model_perms(request)
    print(f"\n8. ServiceTime get_model_perms: {perms}")
    print(f"   has_module_permission: {st_admin.has_module_permission(request)}")
    print(f"   has_view_permission: {st_admin.has_view_permission(request)}")
    print(f"   has_change_permission: {st_admin.has_change_permission(request)}")

# Check get_app_list
print("\n9. Admin app list (get_app_list):")
app_list = admin.site.get_app_list(request)
for app in app_list:
    print(f"   App: {app['name']} ({app['app_label']})")
    for model in app['models']:
        print(f"     - {model['name']} ({model['object_name']})")

# Check if ServiceTime appears in the app list
print("\n10. ServiceTime in app list:")
st_in_app_list = False
for app in app_list:
    for model in app['models']:
        if model['object_name'] == 'ServiceTime':
            st_in_app_list = True
            print(f"   FOUND: {model}")
if not st_in_app_list:
    print("   NOT FOUND in app list!")

# Check all models in app list
print("\n11. All models in app list:")
for app in app_list:
    for model in app['models']:
        print(f"   {app['app_label']}.{model['object_name']}")

print("\n" + "=" * 70)
print("PHASE 4: Additional Checks")
print("=" * 70)

# Check if admin.py is importable
print("\n12. Checking admin module import:")
try:
    from backend.apps.content import admin as content_admin
    print(f"   admin module: {content_admin}")
    print(f"   admin module file: {content_admin.__file__}")
except Exception as e:
    print(f"   ERROR importing admin: {e}")

# Check the __init__.py situation
print("\n13. Checking __init__.py:")
import importlib
content_init = importlib.util.find_spec('backend.apps.content')
if content_init:
    print(f"   content package origin: {content_init.origin}")
    print(f"   content package submodule_search_locations: {content_init.submodule_search_locations}")

# Check if there are any custom admin templates
print("\n14. Checking for custom admin templates:")
from django.conf import settings
print(f"   TEMPLATES DIRS: {settings.TEMPLATES[0].get('DIRS', [])}")
print(f"   TEMPLATES APP_DIRS: {settings.TEMPLATES[0].get('APP_DIRS', False)}")
print(f"   ADMIN_INDEX_TEMPLATE: {getattr(settings, 'ADMIN_INDEX_TEMPLATE', 'NOT SET')}")

# Check if there's a custom AdminSite
print("\n15. Checking AdminSite:")
print(f"   admin.site class: {admin.site.__class__.__name__}")
print(f"   admin.site module: {admin.site.__class__.__module__}")

# Check get_model_perms for other content models
print("\n16. Comparing get_model_perms for content models:")
for model in content_app.get_models():
    if model in admin.site._registry:
        model_admin = admin.site._registry[model]
        perms = model_admin.get_model_perms(request)
        module_perm = model_admin.has_module_permission(request)
        print(f"   {model.__name__}: perms={perms}, module_perm={module_perm}")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
