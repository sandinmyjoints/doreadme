from django.conf.urls.defaults import patterns, url
from django.views.generic.dates import DayArchiveView, MonthArchiveView, TodayArchiveView
from django.views.generic.list import ListView
from day.models import Day

urlpatterns = patterns('',
    # /year/month/date => Story archive
    url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', DayArchiveView.as_view(model=Day,
        month_format="%m",
        date_field="day",
        context_object_name="day_list",
        template_name='day/archive.html'), {}, name="day_archive"),

    # /year/month => List for that month
    url(r'^(?P<year>\d+)/(?P<month>\d+)/$', MonthArchiveView.as_view(model=Day,
        month_format="%m",
        date_field="day",
        context_object_name="day_list",
        template_name='day/archive.html'), {}, name="month_archive"),

    url(r'^$', TodayArchiveView.as_view(model=Day,
        date_field="day",
        context_object_name="day_list",
        template_name='day/archive.html'), {}, name="today"),
)