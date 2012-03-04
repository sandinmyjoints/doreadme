from datetime import datetime, date
from sys import maxint
import logging
import uuid

from django.db import models
from django.db.models import permalink
from django.template.defaultfilters import slugify

logger = logging.getLogger(__name__)

class Journal(models.Model):
    """A website that publishes pieces of creative writing.

        """
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(unique=True)  # auto-generated on save
    url = models.URLField()  # main website url
    seed_url = models.URLField()  # where to start crawling.
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
#    logo = models.ImageField(null=True)
    description = models.TextField(max_length=1024, null=True)

    # These fields are BeautifulSoup code for scraping stories from a page on the Journal's website
    title_pattern = models.CharField(max_length=256, blank=True, default="")
    teaser_pattern = models.CharField(max_length=256, blank=True, default="")
    additional_text_pattern = models.CharField(max_length=256, blank=True, default="")
    author_pattern = models.CharField(max_length=256, blank=True, default="")

    class Meta():
        ordering = ["name"]

    # TODO optimize this
    def featured_stories(self, future_only=True):
        featured_stories = self.story_set.filter(featured_days__isnull=False)
        if future_only:
            return featured_stories.filter(featured_days__day__lte=date.today())
        else:
            return featured_stories

    def generate_slug(self):
        slug_prefix = full_slug = slugify(self.name)
        i = 0
        while Journal.objects.filter(slug=self.slug).count() > 0:
            i += 1
            full_slug = "-".join([slug_prefix, i])
            if i >= maxint - 1:
                # prevent an overflow
                logger.warn("In generate_slug, i is %d" % i)
                # give up on nice ints and try a UUID
                full_slug = "-".join([slug_prefix, str(uuid.uuid4())])

        return full_slug

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.slug or self.slug == "":
            self.slug = self.generate_slug()

        if not self.seed_url:
            self.seed_url = self.url

        super(Journal, self).save(force_insert=force_insert, force_update=force_update, using=using)

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return ('journal_detail', [str(self.id)])