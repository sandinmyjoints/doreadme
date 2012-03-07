from datetime import date
import logging
import datetime

from django.conf import settings
from celery.task import task

from day.models import Day
from journal.models import Journal

logger = logging.getLogger(__name__)

@task
def dummy_task():
    now_ = "dummy task at %s" % datetime.datetime.now()
    print now_
    logger = dummy_task.get_logger(logfile="logs/user/tasks.log")
    logger.info(now_)
    Journal.objects.create(name=now_, url="http://www.site.com", seed_url="http://www.site.com", description="blah")

@task
def select_story_for_next_day():
    """
    If tomorrow (Day after today) exists and has a Story, does nothing.
    If it doesn't exist, creates it. (Note: for now, Day.save() automatically assigns a Story, so the next step shouldn't happen.)
    If it exists and doesn't have a Story assigned, assigns it a Story.
    :return:
    """
    logger = select_story_for_next_day.get_logger(logfile="logs/user/tasks.log")

    logger.info("select_story_for_next_day")

    try:
        logger.info("in try")

        today = date.today()
        logger.info("today is %s" % today)

        tomorrow = date.fromordinal(today.toordinal()+1)
        logger.info("tomorrow is %s" % tomorrow)

        day_after_tomorrow = date.fromordinal(tomorrow.toordinal()+1)
        logger.info("day_after_tomorrow is %s" % day_after_tomorrow)

        today_days = Day.objects.filter(day__gte=today).filter(day__lte=tomorrow)
        logger.info("today_days.count() is %d" % today_days)

        if today_days.count() < 1:
            logger.warn("No Day for today. Creating one.")
            today_day = Day.objects.create(day=today)
        else:
            today_day = today_days[0]
            if today_days.count() > 1:
                logger.warn("Multiple Days for today! This violates the db constraint on Day so should never happen. today_days.count() is %d." % today_days.count())

        logger.info("now today_day is %s" % today_day)

        if not today_day.story:
            logger.warn("No story set for today! Setting one.")
            today_day.story = Day.find_random_unfeatured_story(num_days_recent=settings.NUM_DAYS_RECENT)
            logger.info("today_day.story is %s" % today_day.story)

        tomorrow_days = Day.objects.filter(day__gte=tomorrow).filter(day__lte=day_after_tomorrow)
        logger.debug("Selecting story for %s. tomorrow_days.count() is %d." % (tomorrow, tomorrow_days.count()))

        if tomorrow_days.count() > 1:
            # error--multiple Days for tomorrow!
            logger.warn("Multiple Days for tomorrow! This violates the db constraint on Day so should never happen. tomorrow_days.count() is %d." % tomorrow_days.count())

        if tomorrow_days:
            tomorrow_day = tomorrow_days[0]
        else:
            tomorrow_day = Day.objects.create(day=tomorrow)

        logger.info("now tomorrow_day is %s" % tomorrow_day)

        if not tomorrow_day.story:
            # As long as Day.save() is also calling find_random_unfeatured_story, this should not be called
            tomorrow_day.story = Day.find_random_unfeatured_story(num_days_recent=settings.NUM_DAYS_RECENT)
            logger.info("tomorrow_day.story is %s" % tomorrow_day.story)

    except Exception, exc:
        logger.warn("Exception in select_story_for_tomorrow. Retrying. Exception was '%s'." % exc)
        select_story_for_next_day.retry(exc=exc)  # retry in default (3 * 60 seconds)