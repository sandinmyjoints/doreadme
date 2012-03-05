from datetime import date
import logging

from django.conf import settings
from celery.task import task

from day.models import Day

logger = logging.getLogger(__name__)

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
        logger.debug("Starting select_story_for_tomorrow. Today is %s. Tomorrow is %s. tomorrow_days.count() is %d." % (today, tomorrow, tomorrow_days.count()))

        if tomorrow_days.count() > 1:
            # error--multiple Days for tomorrow! this violates the db constraint on Day so should never happen
            logger.warn("tomorrow_days.count() is %d." % tomorrow_days.count())

        if tomorrow_days:
            tomorrow_day = tomorrow_days[0]
        else:
            tomorrow_day = Day.objects.create(day=tomorrow)

        if not tomorrow_day.story:
            # As long as Day.save() is also calling find_random_unfeatured_story, this should not be called
            tomorrow_day.story = Day.find_random_unfeatured_story(num_days_recent=settings.NUM_DAYS_RECENT)

    except Exception, exc:
        logger.warn("Exception in select_story_for_tomorrow. Retrying. Exception was '%s'." % exc)
        select_story_for_new_day.retry(exc=exc)  # retry in default (3 * 60 seconds)