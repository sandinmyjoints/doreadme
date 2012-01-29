from django.db import models
from django.db.models import permalink
from django.template.defaultfilters import slugify
from picklefield.fields import PickledObjectField


class Journal(models.Model):
    """A website that publishes stories.

        """
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(unique=True)  # auto-generated on save
    url = models.URLField()  # main website url
    seed_url = models.URLField()  # where to start crawling.
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    last_crawled = models.DateTimeField(null=True)
    crawled_pages = PickledObjectField(null=True)

    # These fields are BeautifulSoup code for scraping stories from a page on the Journal's website
    title_pattern = models.CharField(max_length=256, blank=True, default="")
    teaser_pattern = models.CharField(max_length=256, blank=True, default="")
    additional_text_pattern = models.CharField(max_length=256, blank=True, default="")
    author_pattern = models.CharField(max_length=256, blank=True, default="")

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.slug or self.slug=="":
            self.slug = slugify(self.name)
            i = 0
            while Journal.objects.filter(slug=self.slug).count() > 0:
                i += 1
                self.slug = "-".join([self.slug, i])

        if not self.seed_url:
            self.seed_url = self.url

        super(Journal, self).save(force_insert=force_insert, force_update=force_update, using=using)

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return ('journal_detail', [str(self.id)])