# / => Today's story
from contact_form.views import CompletedPage
from django.conf.urls.defaults import url, patterns, include
from dailystorysite.views import AboutView, SiteHomePageView, NewsView, DailyStoryContactFormView

urlpatterns = patterns('',

    url(r'^contact_form/$', DailyStoryContactFormView.as_view(), name="contact_form"),
    url(r'^contact_form_completed/$', CompletedPage.as_view(template_name="contact_form/contact_completed.html"), name="contact_form_completed"),

    url(r'^day/', include('dailystory.day.urls')),
    url(r'^story/', include('dailystory.story.urls')),
    url(r'^journal/', include('dailystory.journal.urls')),

    #    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'story/login.html'}),
    url(r'^about/$', AboutView.as_view(), name="about"),
    url(r'^news/$', NewsView.as_view(), name="news"),

    url(r'^$', SiteHomePageView.as_view(), {}, name="index"),


)