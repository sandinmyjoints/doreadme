import urllib2
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup

for s in Story.objects.filter(slug=2):
    print "changing %s to %s" % (s.slug, slugify(s.title))
    s.slug = slugify(s.title)
    s.save()
