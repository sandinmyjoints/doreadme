from django.views.generic.detail import DetailView

class JournalDetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super(JournalDetailView, self).get_context_data(**kwargs)
        journal = self.get_object(self.get_queryset())

        # This puts into the template context a queryset consisting only of this journal's stories that have been
        # featured, ie, their featured_days relation is not null. This is a separate object from journal.story_set, which is all of
        # the Journal's Stories. Is it possible to make a custom manager on Journal that uses the custom manager on Story that
        # only returns the Stories that have been featured? Not sure. But this works for now.
        context["journals_featured_stories_set"] = journal.story_set.filter(featured_days__isnull=False)
        return context