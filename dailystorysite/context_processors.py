from django.conf import settings
from django.contrib.sites.models import Site

__author__ = 'wbert'

def site_name(request):
    return {"SITE_NAME": Site.objects.get_current().name }