# / => Today's story
from django.conf.urls.defaults import url, patterns, include
from dailystorysite.views import AboutView, SiteHomePageView, NewsView

urlpatterns = patterns('',

    url(r'^story/', include('dailystory.story.urls')),
    url(r'^journal/', include('dailystory.journal.urls')),

    #    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'story/login.html'}),
    url(r'^about/$', AboutView.as_view(), name="about"),
    url(r'^news/$', NewsView.as_view(), name="news"),

    url(r'^$', SiteHomePageView.as_view(), {}, name="index"),

    url(r'^day/', include('dailystory.day.urls')),

)