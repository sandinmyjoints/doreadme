from django.db import models


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
    """"Returns only verified fiction that has not been featured."""

    def get_query_set(self):
        qs = super(VerifiedNonFeaturedFictionStoryManager, self).get_query_set()
        return qs.filter(featured_days__isnull=True)


class FeaturedFictionStoryManager(models.Manager):
    """
    Returns only fiction that has been featured on a Day.
    """
    def get_query_set(self):
        return super(FeaturedFictionStoryManager, self).get_query_set().filter(featured_days__isnull=False)
