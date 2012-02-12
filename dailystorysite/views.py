from datetime import datetime
from contact_form.views import ContactFormView
from contact_form.forms import BasicContactForm
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.dates import TodayArchiveView, MonthMixin, YearMixin
from django.utils import simplejson as json

from day.models import Day


class AboutView(TemplateView):
    template_name = "dailystorysite/about.html"

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context["today"] = datetime.today()
        return context


class NewsView(TemplateView):
    template_name = "dailystorysite/news.html"


class JSONResponseMixin(object):
    def render_to_response(self, context):
        """Returns a JSON response containing 'context' as payload"""
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        """Construct an `HttpResponse` object."""
        return HttpResponse(content,
            content_type='application/json',
            **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        """Convert the context dictionary into a JSON object"""
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)


class DailyStoryContactFormView(ContactFormView, JSONResponseMixin):
    template_name = "contact_form/contact_form.html"
    form_class = BasicContactForm

    def get(self, request, *args, **kwargs):
        super(DailyStoryContactFormView, self).get(request, *args, **kwargs)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)

        if request.is_ajax():
            return JSONResponseMixin.render_to_response(self, context=context)
        else:
            return ContactFormView.render_to_response(self, context=context)

    def get_success_url(self):
        return reverse("contact_form_completed")


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


class SiteHomePageView(DailyStoryTodayArchiveView):
    """
    Shows today's story, as well as a (hidden) form for contact through a modal dialog.
    """

    def get(self, request, *args, **kwargs):
        self.date_list, self.object_list, extra_context = self.get_dated_items()
        context = self.get_context_data(object_list=self.object_list,
            date_list=self.date_list)
        context.update(extra_context)
        return self.render_to_response(context)



