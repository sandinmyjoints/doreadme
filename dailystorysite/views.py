from datetime import datetime
from contact_form.views import ContactFormView
from contact_form.forms import BasicContactForm
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.dates import TodayArchiveView, MonthMixin, YearMixin

from day.models import Day


class AboutView(TemplateView):
    template_name = "dailystorysite/about.html"

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context["today"] = datetime.today()
        return context


class NewsView(TemplateView):
    template_name = "dailystorysite/news.html"


class DailyStoryContactFormMixin(ContactFormView):
    form_class = BasicContactForm


class DailyStoryTodayArchiveView(TodayArchiveView):
    model = Day
    context_object_name="day_list"
    template_name='index.html'
    date_field = "day"

    def get_context_data(self, **kwargs):
        context = super(DailyStoryTodayArchiveView, self).get_context_data(**kwargs)
        context['nice_month'] = datetime.strftime(datetime.today(), "%B")
        context['today'] = datetime.today()
        return context


class SiteHomePageView(DailyStoryTodayArchiveView, DailyStoryContactFormMixin):
    """
    Shows today's story, as well as a (hidden) form for contact through a modal dialog.
    """

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        self.date_list, self.object_list, extra_context = self.get_dated_items()
        context = self.get_context_data(form=form, object_list=self.object_list,
            date_list=self.date_list)
        context.update(extra_context)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SiteHomePageView, self).get_context_data(**kwargs)
        return context

    def failure(self):
        return HttpResponse("form not ok")

    def success(self):
        return HttpResponse("form sent")
