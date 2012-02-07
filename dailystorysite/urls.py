# / => Today's story
from django.conf.urls.defaults import url, patterns, include
from dailystorysite.views import AboutView, SiteHomePageView
from day.models import Day

urlpatterns = patterns('',

    url(r'^story/', include('dailystory.story.urls')),

    #    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'story/login.html'}),
    url(r'^about/$', AboutView.as_view(), name="about"),

    url(r'^$', SiteHomePageView.as_view(), {}, name="today"),

    url(r'day/', include('dailystory.day.urls')),

)