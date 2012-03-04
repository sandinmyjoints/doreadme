from django.db import models

from picklefield.fields import PickledObjectField
from journal.models import Journal

class Crawl(models.Model):
    """
    Represents a crawl of a Journal.
    """

    journal = models.ForeignKey(Journal)
    seed_url = models.URLField()
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(null=True)
    crawled_pages = PickledObjectField(null=True)  # a set() of urls

    def __unicode__(self):
        return "%s crawl of %d pages starting %s %s" % (self.journal.name,
                                                        len(self.crawled_pages) if self.crawled_pages else 0,
                                                        self.start.strftime("%Y-%m-%d %H:%m:%S"),
                                                        ("ending %s " % self.end.strftime(
                                                            "%Y-%m-%d %H:%m:%S")) if self.end else "",
            )


