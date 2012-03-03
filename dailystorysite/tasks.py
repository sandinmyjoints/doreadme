from datetime import datetime, date
from django.conf import settings
from day.models import Day

__author__ = 'wbert'

from celery.task import task

@task
def select_story_for_tomorrow():
    """
    If tomorrow (Day after today) exists and has a Story, does nothing.
    If it doesn't exist, creates it. (Note: for now, Day.save() automatically assigns a Story, so the next step shouldn't happen.)
    If it exists and doesn't have a Story assigned, assigns it a Story.
    :return:
    """
    try:
        today = date.today()
        tomorrow = date.fromordinal(today.toordinal()+1)
        tomorrow_days = Day.objects.filter(day__gte=today).filter(day__lte=tomorrow)

        if tomorrow_days.count() > 1:
            # error--multiple Days for tomorrow! this violates the db constraint on Day so should never happen
            # TODO log this error
            pass

        if tomorrow_days:
            tomorrow_day = tomorrow_days[0]
        else:
            tomorrow_day = Day.objects.create(day=tomorrow)

        if not tomorrow_day.story:
            # As long as Day.save() is also calling find_random_unfeatured_story, this should not be called
            tomorrow_day.story = Day.find_random_unfeatured_story(num_days_recent=settings.NUM_DAYS_RECENT)

    except Exception, exc:
        select_story_for_new_day.retry(exc=exc)  # retry in default (3 * 60 seconds)