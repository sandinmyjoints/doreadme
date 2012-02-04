from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from dailystorysite.views import AboutView

admin.autodiscover()

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^contact/', include('contact_form.urls')),

    url(r'^', include('dailystory.dailystorysite.urls')),
)
