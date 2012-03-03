from datetime import datetime
import random
import logging
from django.conf import settings
from django.db import models

# Create your models here.
from django.db.models import permalink
from story.models import Story

logger = logging.getLogger(name=__name__)

class Day(models.Model):
    day = models.DateField(unique=True)
    story = models.ForeignKey(Story, null=True, related_name="featured_days")

    class Meta:
        ordering = ['-day']

    def __unicode__(self):
        return "%s -> %s" % (self.day, self.story if self.story else "")

    def save(self, force_insert=False, force_update=False, using=None):

        # This automatically sets a story if no story was set. This can also be covered by the celery task--maybe this should be commented
        # out so that a blank Day can be created?
        if not self.story:
            self.story = Day.find_random_unfeatured_story(num_days_recent=settings.NUM_DAYS_RECENT)

        logger.info("Saving Day %s" % unicode(self))

        super(Day, self).save(force_insert=force_insert, force_update=force_update, using=using)

    @classmethod
    def first_day(cls):
        return cls.objects.order_by("day")[0].day if cls.objects.count() else None

    @classmethod
    def random(cls, allow_future=False):
        days = cls.objects.all()
        if not allow_future:
            days = days.filter(day__lte=datetime.today().date())
        all_days = [d for d in days]
        random.shuffle(all_days)
        return all_days.pop()

    @permalink
    def get_absolute_url(self):
        return ('day_day_archive', [self.day.year, self.day.month, self.day.day])

    @classmethod
    def find_random_unfeatured_story(cls, num_days_recent=7):
        """
        Returns a verified Story that has never been featured and, if at all possible, does not have the same author or journal as a Story that
        has been featured in the past num_days_recent days.
        :param cls:
        :param num_days_recent:
        :return:
        """
        # Get all the verified stories that do not have any featured_days set
        potential_stories = [s for s in Story.verified_nonfeatured_fiction.all()]
        random.shuffle(potential_stories)

        # grab the first potential Story
        try:
            s = potential_stories.pop()
        except IndexError:
            # There are no possible stories!
            logger.warn("In find_random_unfeatured_story, potential_stories.count() is %d." % potential_stories.count())
            return None

        today = datetime.today().date()
        recent_cutoff = datetime.fromordinal(today.toordinal() - num_days_recent).date()
        recent_stories = [d.story for d in cls.objects.filter(day__gt=recent_cutoff).filter(day__lt=today)]

        while potential_stories:
            # Check whether this journal or author was featured recently
            for r in recent_stories:
                if s.author == r.author or s.journal == r.journal:
                    s = potential_stories.pop()  # move onto the next potential story
                    break
            else:  # s passed the recent journal/author test
                break

        if not potential_stories:
            # We exhausted all possible stories and couldn't find one that didn't repeat something
            # If num_days_recent is anything greater than 1, try again with num_days_recent=1 to see if we can at least
            # avoid repeating yesterday's author/journal
            if num_days_recent > 1:
                return cls.find_random_unfeatured_story(num_days_recent=1)
            else:
                # Or if it is 1, then we'll just have to return a random story that repeats, because they all repeat...
                return random.choice(cls.objects.filter(date_featured=None))
        else:
            # We didn't exhaust possible_stories, so we found a fresh one
            return s