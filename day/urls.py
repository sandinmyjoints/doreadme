from django.conf.urls.defaults import patterns, url
from django.views.generic.dates import DayArchiveView, MonthArchiveView, TodayArchiveView, DateDetailView
from django.views.generic.list import ListView
from day.models import Day
from day.views import random_day_view, DayRedirectView

urlpatterns = patterns('',
    # /year/month/date => Story archive
    url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', DayArchiveView.as_view(model=Day,
        month_format="%m",
        date_field="day",
        context_object_name="day_list",
        template_name='day/singleday_archive.html'), {}, name="day_day_archive"),

    # /year/month => List for that month
    url(r'^(?P<year>\d+)/(?P<month>\d+)/$', MonthArchiveView.as_view(model=Day,
        month_format="%m",
        date_field="day",
        context_object_name="day_list",
        template_name='day/archive.html'), {}, name="day_month_archive"),

    url(r'^list/$', ListView.as_view(model=Day,
        context_object_name="day_list",
        template_name='day/archive.html'), {}, name="day_all_archive"),

    url(r'^$', TodayArchiveView.as_view(model=Day,
        date_field="day",
        context_object_name="day_list",
        template_name='day/singleday_archive.html'), {}, name="day_today"),

    # /day/random => random Day
    # TODO redo as a class-based view
    url(r'^random$', random_day_view, {}, name="random_day"),

    url(r'^day_redirect$', DayRedirectView.as_view(), name="day_redirect"),
)