from django.conf.urls.defaults import url, patterns
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from story.models import Story

urlpatterns = patterns('',

    url(r'^list/$', ListView.as_view(template_name="story/list_include.html", model=Story), name="story_list"),
    url(r'^(?P<slug>[\d\w\-_]+)/$', DetailView.as_view(template_name='story/story.html', model=Story), {}, name="story_detail_slug"),
)