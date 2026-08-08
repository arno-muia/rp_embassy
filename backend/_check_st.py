import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from backend.apps.content.models import ServiceTime
print('Total records:', ServiceTime.objects.count())
for s in ServiceTime.objects.order_by('display_order'):
    print(f'  [{s.display_order}] id={s.id} name={s.name!r} day={s.day!r} time={s.time!r} platform={s.platform!r} location={s.location!r} link={s.link!r} description={s.description!r} image={s.image!r} is_published={s.is_published}')
