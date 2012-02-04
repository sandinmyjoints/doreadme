from datetime import datetime
from django.views.generic.base import TemplateView
from django.views.generic.dates import TodayArchiveView

from day.models import Day

class AboutView(TemplateView):
    template_name = "about.html"

class MyTodayArchiveView(TodayArchiveView):
    context_object_name="day_list"
    model = Day

    def get_context_data(self, **kwargs):
        context = super(MyTodayArchiveView, self).get_context_data(**kwargs)
        context['nice_month'] = datetime.strftime(datetime.today(), "%B")
        context['today'] = datetime.today()
        return context

