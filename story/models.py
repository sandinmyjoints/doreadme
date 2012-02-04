from datetime import datetime
import random
from django.db import models
from django.db.models import permalink
from django.template.defaultfilters import slugify

from journal.models import Journal


GENRE_CHOICES = (
    ('FI', "Fiction"),
    ('PO', "Poetry"),
    ("NF", "Nonfiction"),
    ("OT", "Other"),
    ("RE", "Review"),
    ("IN", "Interview"),
)


class FictionStoryManager(models.Manager):
    def get_query_set(self):
        return super(FictionStoryManager, self).get_query_set().filter(genre="FI")


class Story(models.Model):
    """Represents a story on a literary journal site somewhere.
        """

    fiction = FictionStoryManager()

    title = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)  # If not supplied, will be auto-generated in save()
    teaser = models.TextField(blank=True)
    url = models.URLField()
    author = models.CharField(max_length=128, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    genre = models.CharField(max_length=2, choices=GENRE_CHOICES, default='FI')
    # Featured, for a past date, means it was shown as Today's Story on the front page on that date. This can only happen once. If null, it has never been shown.
    # For a future date, date_featured means it is scheduled to run on that date.
    # If date_featured is None, this story hasn't been scheduled yet.
#    date_featured = models.ForeignKey(Day, blank=True, null=True)
    journal = models.ForeignKey(Journal, null=True)

    class Meta:
        verbose_name_plural = "stories"
        unique_together = (("title", "author"),)

    def generate_slug(self):
        slug_prefix = full_slug = slugify(self.title)
        i = 0
        # TODO could probably redo this to grab everything that starts with slug, then reduce it by filtering
        while Story.objects.filter(slug=full_slug).count() > 0:
            i += 1
            full_slug = "-".join([slug_prefix, unicode(i)])
            # TODO bounds checking on i, do something like generate a random string suffix if i gets too big
            # TODO also log it as a warning

        return full_slug

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.slug or self.slug == "":
            self.slug = self.generate_slug()

        #        if not self.date_featured:
        #            # Careful, setting save=True here will generate an infinite loop.
        #            self.schedule_featured_date(save=False)

        super(Story, self).save(force_insert=force_insert, force_update=force_update, using=using)

#    def schedule_featured_date(self, date=None, save=True):
#        """Sets this Story's date_featured to date if supplied, or to the next available slot if no date is supplied.
#                    Call self.save() only if save is True.
#
#                :param date:
#                :return:
#                """
#        if not date:
#            today = datetime.today().date()
#            future_stories = Story.objects.filter(date_featured__gt=today).order_by("date_featured")
#            date_index = Story.add_days(today)
#            for fs in future_stories:
#                if date_index != fs.date_featured:
#                    # Found a hole in the upcoming schedule..
#                    date = date_index
#                    break
#
#                date_index = Story.add_days(date_index)
#
#        # If we didn't find any holes in the schedule, put this one after the last scheduled day.
#        if not date:
#            date = date_index
#
#        self.date_featured = date
#        if save:
#            self.save()

#    @staticmethod
#    def add_days(dt=None, days=1):
#        if not dt:
#            dt = datetime.today().date()
#
#        return datetime.fromordinal(dt.toordinal()+days).date()

#    @classmethod
#    def schedule_unscheduled_stories(cls):
#        unscheduled_stories = cls.objects.filter(date_featured=None)
#        for s in unscheduled_stories:
#            s.schedule_featured_date()
#            s.save()

    def __unicode__(self):
        return " ".join([self.title, "by", self.author])

    @permalink
    def get_absolute_url(self):
        return ('story_detail_slug', [str(self.slug)])