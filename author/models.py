from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=256)
    website = models.URLField(blank=True, null=True)
    photo = models.ImageField(null=True)  # Author could subclass a User profile model that has profile photos as well
