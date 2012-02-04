
# / => Today's story
from datetime import datetime
from django.conf.urls.defaults import url, patterns, include
from django.views.generic.dates import TodayArchiveView
from dailystorysite.views import AboutView, MyTodayArchiveView
from day.models import Day

urlpatterns = patterns('',

    url(r'^story/', include('dailystory.story.urls')),

    #    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'story/login.html'}),
    url(r'^about/$', AboutView.as_view(), name="about"),

    url(r'^$', MyTodayArchiveView.as_view(model=Day,
        date_field="day",
        context_object_name="day_list",
        template_name='index.html'), {}, name="today"),

    url(r'day/', include('dailystory.day.urls')),

)