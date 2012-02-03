from datetime import datetime
import random
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

# Create your models here.
from django.db.models import permalink
from story.models import Story

class Day(models.Model):
    day = models.DateField()
    story = models.ForeignKey(Story, null=True, related_name="featured_days")

    def __unicode__(self):
        return "%s -> %s" % (self.day, self.story)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.story:
            self.story = Day.find_random_unfeatured_story(num_days_recent=settings.NUM_DAYS_RECENT)

        super(Day, self).save(force_insert=force_insert, force_update=force_update, using=using)


    @classmethod
    def random(cls, allow_future=False):
        days = cls.objects.all()
        if not allow_future:
            days = days.filter(day__le=datetime.today().date())
        all_days = [d for d in days]
        random.shuffle(all_days)
        return all_days.pop()

    @permalink
    def get_absolute_url(self):
        return ('day_archive', [self.day.year, self.day.month, self.day.day])

    @classmethod
    def find_random_unfeatured_story(cls, num_days_recent=7):
        """
        Returns a Story that has never been featured and, if at all possible, does not have the same author or journal as a Story that
        has been featured in the past num_days_recent days.
        :param cls:
        :param num_days_recent:
        :return:
        """
        # Get all the stories that do not have any featured_days set
        possible_stories = [s for s in Story.objects.all() if not s.featured_days.count()]
        random.shuffle(possible_stories)

        try:
            s = possible_stories.pop()
        except IndexError:
            # There are no possible stories! TODO log an error
            return None

        today = datetime.today().date()
        recent_cutoff = datetime.fromordinal(today.toordinal() - num_days_recent).date()
        recent_stories = [d.story for d in cls.objects.filter(day__gt=recent_cutoff).filter(day__lt=today)]

        while possible_stories:
            # Check whether this journal or author was featured recently
            for r in recent_stories:
                if s.author == r.author or s.journal == r.journal:
                    s = possible_stories.pop()
                    break

        if not possible_stories:
            # We exhausted all possible stories and couldn't find one that didn't repeat something
            # If num_days_recent is anything greater than 1, try again with num_days_recent=1 to see if we can at least
            # avoid repeating yesterday's author/journal
            if num_days_recent > 1:
                return cls.find_random_unfeatured_story(num_days_recent=1)
            else:
                # Or if it is 1, then we'll just have to return a random story that repeats, because they all repeat...
                return random.sample(cls.objects.filter(date_featured=None))
        else:
            # We didn't exhaust possible_stories, so we found a fresh one
            return s