from django.conf.urls.defaults import url, patterns
from django.views.generic.detail import DetailView
from journal.models import Journal
from journal.views import JournalDetailView

urlpatterns = patterns('',

    # /journal/journal-slug -> Journal detail view (which contains a list of all the Journal's Stories that have been featured on a Day)
    url(r'^(?P<slug>[\w-]+)/$', JournalDetailView.as_view(model=Journal,
        queryset=Journal.objects.all(),
        context_object_name="journal",
        template_name='journal/journal.html'), {}, name="journal_detail"),
)