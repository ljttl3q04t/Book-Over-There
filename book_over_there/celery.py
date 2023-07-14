from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_over_there.settings')

app = Celery('book_over_there')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.log.setup(loglevel='INFO', logfile='/var/log/django/celery.log')

app.autodiscover_tasks()
