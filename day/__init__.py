from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    settings.NUM_DAYS_RECENT
except NameError:
    raise ImproperlyConfigured("NUM_DAYS_RECENT is not set in settings.py.")