"""
URL configuration for backend project.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'healthy',
        'service': 'backend',
        'version': '1.0.0',
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('backend.apps.content.urls')),
    path('api/', include('backend.apps.events.urls')),
    path('api/', include('backend.apps.prayer.urls')),
    path('api/health', health_check, name='health-check'),
]
