from django.conf.urls.defaults import url, patterns
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from story.models import Story
from story.views import random_story, StoryArchiveView

urlpatterns = patterns('',

    # /random => random Story
    url(r'^random$', random_story, {}, name="random_story"),

#    url(r'^(?P<pk>\d+)$', DetailView.as_view(template_name='story/story.html', model=Story), {}, name="story_detail_pk"),
    # /slug => Story detail view
    url(r'^(?P<slug>[\d\w\-_]+)/$', DetailView.as_view(template_name='story/story.html', model=Story), {}, name="story_detail_slug"),
)