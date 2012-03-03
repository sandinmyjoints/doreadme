import random
from sys import maxint
import logging
import uuid
from django.db import models
from django.db.models import permalink
from django.template.defaultfilters import slugify

from journal.models import Journal


logger = logging.getLogger(name=__name__)

GENRE_CHOICES = (
    ('FI', "Fiction"),
    ('PO', "Poetry"),
    ("NF", "Nonfiction"),
    ("RE", "Review"),
    ("IN", "Interview"),
    ("OW", "Other Writing"),
    ("NW", "Not Writing"),
)


class FictionStoryManager(models.Manager):
    """Returns only fiction.
    """
    def get_query_set(self):
        return super(FictionStoryManager, self).get_query_set().filter(genre="FI")

class VerifiedFictionStoryManager(models.Manager):
    """Returns only verified fiction.
    """
    def get_query_set(self):
        return super(VerifiedFictionStoryManager, self).get_query_set().filter(genre="FI").filter(verified=True)

class VerifiedNonFeaturedFictionStoryManager(VerifiedFictionStoryManager):
    def get_query_set(self):
        qs = super(VerifiedNonFeaturedFictionStoryManager, self).get_query_set()
        return qs.filter(featured_days__isnull=True)

class FeaturedFictionStoryManager(models.Manager):
    """
    Returns only fiction that has been featured on a Day.
    """
    def get_query_set(self):
        return super(FeaturedFictionStoryManager, self).get_query_set().filter(featured_days__isnull=False)


class Story(models.Model):
    """Represents a story on a literary journal site somewhere.
        """

    objects = models.Manager()
    all_fiction = FictionStoryManager()
    featured_fiction = FeaturedFictionStoryManager()
    verified_fiction = VerifiedFictionStoryManager()
    verified_nonfeatured_fiction = VerifiedNonFeaturedFictionStoryManager()

    title = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)  # If not supplied, will be auto-generated in save()
    teaser = models.TextField(blank=True)  # first paragraph or two depending on length
    additional_teaser = models.TextField(blank=True)  # next paragraph, provides additional text if necessary
    extra_teaser = models.TextField(blank=True)  # next paragraph, provides additional text if necessary
    url = models.URLField()
    author = models.CharField(max_length=128, blank=True)  # TODO convert to a ForeignKey to Author
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    genre = models.CharField(max_length=2, choices=GENRE_CHOICES, default='FI')
    journal = models.ForeignKey(Journal, null=True)
    # verified indicates that a human verified that this Story is correct. A Story can only be shown live if this is True
    verified = models.BooleanField(default=False)
    # crawl_flagged is an experimental feature that indicates the crawler has flagged this Story as potentially having something that needs human attention.
    crawl_flagged = models.BooleanField(default=False)

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
            if i >= maxint-1:
                # prevent an overflow
                logger.warn("In generat_slug, i is %d" % i)
                # give up on nice ints and try a UUID
                full_slug = "-".join([slug_prefix, str(uuid.uuid4())])

        return full_slug

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.slug or self.slug == "":
            self.slug = self.generate_slug()

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
        return "%s by %s %s" % (self.title, self.author, "(Verified)" if self.verified else "")

    @permalink
    def get_absolute_url(self):
        return ('story_detail_slug', [str(self.slug)])