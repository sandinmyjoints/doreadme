from django.shortcuts import redirect
from django.views.generic.dates import TodayArchiveView, DayArchiveView
from day.models import Day

class TodayStoryView(TodayArchiveView):
    pass

class TodayRandomView(DayArchiveView):
    model = Day
    context_object_name="day_list"
    template_name='day/singleday_archive.html'
    date_field = "day"

def random_day_view(request):
    return redirect(Day.random().get_absolute_url())