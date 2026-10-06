import io
import os
import re
import uuid
from pathlib import Path
from PIL import Image, ImageOps

from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

ALLOWED_MIME_TYPES = {
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
    'image/gif': '.gif',
    'image/avif': '.avif',
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_DIMENSION = 2560  # Max width/height in px


def sanitize_folder(folder_name: str) -> str:
    """Sanitize folder name to prevent directory traversal."""
    if not folder_name:
        return 'general'
    cleaned = re.sub(r'[^a-zA-Z0-9_-]', '', folder_name.lower().strip())
    return cleaned or 'general'


@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def upload_image_view(request):
    """
    Real-time image upload endpoint for Django Admin and CMS editors.
    Saves image into MEDIA_ROOT/uploads/<folder>/<filename>.
    Returns JSON with the public URL and metadata.
    """
    file_obj = request.FILES.get('file') or request.FILES.get('image')
    if not file_obj:
        return Response(
            {'error': 'No file was provided in the request.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if file_obj.size > MAX_FILE_SIZE:
        return Response(
            {'error': f'File size ({file_obj.size / (1024 * 1024):.1f}MB) exceeds the 10MB limit.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Determine extension and validate image with Pillow
    content_type = getattr(file_obj, 'content_type', '').lower()
    original_name = file_obj.name or 'upload'
    stem = Path(original_name).stem
    clean_stem = slugify(stem)[:40] or 'image'

    try:
        image = Image.open(file_obj)
        image.verify()  # Verify valid image data
        # Re-open because verify() consumes the file pointer / leaves it in unusable state
        file_obj.seek(0)
        image = Image.open(file_obj)
    except Exception as e:
        return Response(
            {'error': f'Invalid or corrupted image file: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Auto-orient based on EXIF tag (handles phone photos taken in portrait)
    try:
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass

    orig_width, orig_height = image.size

    # Downscale if excessively large while preserving aspect ratio
    if orig_width > MAX_DIMENSION or orig_height > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)

    # Determine target folder
    folder = sanitize_folder(request.data.get('folder', request.GET.get('folder', 'general')))
    target_dir = Path(settings.MEDIA_ROOT) / 'uploads' / folder
    target_dir.mkdir(parents=True, exist_ok=True)

    # Save format
    unique_suffix = uuid.uuid4().hex[:8]
    ext = ALLOWED_MIME_TYPES.get(content_type, Path(original_name).suffix.lower() or '.jpg')
    if ext not in ALLOWED_MIME_TYPES.values():
        ext = '.jpg'

    # Save as WebP if PNG/JPEG for modern efficiency, or retain format
    save_format = image.format or 'JPEG'
    filename = f"{clean_stem}-{unique_suffix}{ext}"
    target_path = target_dir / filename

    try:
        if save_format in ('JPEG', 'JPG') and image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Save to disk
        image.save(target_path, format=save_format, quality=88, optimize=True)
    except Exception as e:
        # Fallback save raw
        file_obj.seek(0)
        with open(target_path, 'wb+') as dest:
            for chunk in file_obj.chunks():
                dest.write(chunk)

    final_width, final_height = image.size
    final_size = os.path.getsize(target_path)
    relative_url = f"{settings.MEDIA_URL.rstrip('/')}/uploads/{folder}/{filename}"

    return Response({
        'success': True,
        'url': relative_url,
        'filename': filename,
        'width': final_width,
        'height': final_height,
        'size': final_size,
        'folder': folder,
    }, status=status.HTTP_201_CREATED)
