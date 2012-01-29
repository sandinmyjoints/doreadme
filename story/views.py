from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.list import ListView
from story.models import Story


class StoryArchiveView(ListView):
    template_name = "story/list.html"


#class RandomStory(TemplateView):
# TODO convert this to a class-based view
def random_story(request):
    return redirect(reverse("story_detail_slug", args=[Story.random().slug]))