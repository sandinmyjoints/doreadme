from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
from django.views.generic.dates import TodayArchiveView, DayArchiveView
from day.models import Day

class TodayStoryView(TodayArchiveView):
    pass

class TodayRandomView(DayArchiveView):
    model = Day
    context_object_name="day_list"
    template_name='day/singleday_archive.html'
    date_field = "day"

class DayRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        try:
            year = self.request.GET["year"]
            month = self.request.GET["month"]
            day = self.request.GET["day"]
            return reverse('day_day_archive', args=[year, month, day])

        except KeyError:
            raise Http404


def random_day_view(request):
    return redirect(Day.random().get_absolute_url())