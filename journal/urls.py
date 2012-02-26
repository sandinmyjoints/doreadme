from django.conf.urls.defaults import url, patterns
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from journal.models import Journal

urlpatterns = patterns('',

    url(r'^list/$', ListView.as_view(model=Journal,
        context_object_name="journal_list",
        template_name="journal/journal_list.html"), {}, name="journal_list"),

    # /journal/journal-slug -> Journal detail view (which contains a list of all the Journal's Stories that have been featured on a Day)
    url(r'^(?P<slug>[\w-]+)/$', DetailView.as_view(model=Journal,
        queryset=Journal.objects.all(),
        context_object_name="journal",
        template_name='journal/journal.html'), {}, name="journal_detail"),


)