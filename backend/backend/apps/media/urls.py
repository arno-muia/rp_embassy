from django.urls import path
from .views import upload_image_view

urlpatterns = [
    path('content/upload-image', upload_image_view, name='admin-upload-image'),
    path('content/upload-image/', upload_image_view, name='admin-upload-image-slash'),
]
