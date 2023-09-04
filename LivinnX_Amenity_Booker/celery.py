import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LivinnX_Amenity_Booker.settings')

app = Celery('LivinnX_Amenity_Booker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()