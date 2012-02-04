import inspect
import datetime
from time import sleep
from django.db import transaction
from django.db.utils import IntegrityError
import os
import urllib2
from urlparse import urlparse, urljoin
import re
import logging
import sys
from django.core.management.base import NoArgsCommand, LabelCommand
from django.conf import settings

from journal.models import Journal, Crawl

from story.models import Story

__author__ = 'wbert'

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

# TODO: fix logging to file; and setting verbose on class vs. on function or whatever

SCRIPT_ROOT = os.path.dirname(__file__)

domain = lambda url: ".".join(url.split(".")[-2:])

convert_entities = lambda bit: unicode(BeautifulStoneSoup(bit, convertEntities="html"))

def get_soup(source):
    soup = None

    try:
        # this will open files if they are prefixed with 'file:`
        soup = BeautifulSoup(urllib2.urlopen(source))
    except Exception:
        pass

    try:
        # is it a file?
        soup = BeautifulSoup(open(source))
    except Exception:
        pass
    return soup


class StoryCrawler(object):

    journal_name = ""
    # TODO don't override this in inherited classes, but rather extend it. Generalize it to be just the regex string, and add to it
    base_exclude_from_urls = [
        "blog",
        "author",
        "contributor",
        "about",
        "contact",
        "reviews",
        "bios",
        "nonfiction",
        "poet",
        "poem",
        "essay",
    ]
#    exclude_from_urls = r're.search(r"(blog|author|contributor|about|contact|reviews|bios|nonfiction|poet|poem|essay)", cur_url)'

    def __init__(self, min_teaser_length=20, max_teaser_length=1000, max_title_length=256, max_author_length=128, verbose=False):
        super(StoryCrawler, self).__init__()
        self.crawled_pages = set()
        self.verbose = verbose
        self.MIN_TEASER_LENGTH = min_teaser_length
        self.MAX_TEASER_LENGTH = max_teaser_length
        self.MAX_TITLE_LENGTH = max_title_length
        self.MAX_AUTHOR_LENGTH = max_author_length

        self.exclude_from_urls.extend(self.base_exclude_from_urls)
        self.exclude_url_pattern = 're.search(r"' + "|".join(self.exclude_from_urls) + '", cur_url)'

#        self.journal_name = re.findall(r"'__\w+__\.(\S+)'>", str(self.__class__))[0]

        try:
            journals = Journal.objects.filter(name=self.journal_name)
            if journals.count() > 1:
                log_msg("Found %d Journals with name=%s." % (journals.count(), self.journal_name), logging.WARN)

            self.db_object = journals[0]
        except IndexError:
            # no entry in Journal table, so create it
            self.log_msg("Creating db object for %s." % self.journal_name)
            self.db_object = Journal.objects.create(name=self.journal_name, url=self.seed_url)
        except AttributeError:
            self.log_msg("Running without journal_name or db_object.", logging.WARN)
            self.db_object = None

    def log_msg(self, msg, level=logging.INFO):
        msg = ": ".join(["%s" % self.journal_name if self.journal_name else "no journal_name", msg])
        logging.log(level, msg)
        if self.verbose:
            print "%s: %s" % (level, msg)

    def add_to_crawled(self, url):
        self.crawled_pages.add(url)

    def has_been_crawled(self, url):
        return (url in self.crawled_pages) or ("".join([url, "/"]) in self.crawled_pages)

    def crawl(self, depth=2, ignore_previously_crawled_pages=False, verbose=None):
        """Crawls a site, starting from seed_url. Starting with seed_url, for each page it:
                * Attempts to parse the page as a story for the journal. If successful, a Story object is saved to the db.
                * Adds all the links on the page that could potentially be stories themselves to a queue of urls to crawl.
                * Moves to the next url in the queue.

                When all urls have been examined, the db_object's last_crawled date is updated to now, and its crawled_pages set becomes the
                intersection of urls that were crawled and urls that were already in crawled_pages (whether they were ignored or not).

                :param depth: how many pages beyond the seed_url to look. Zero examines only seed_url;
                1 looks at every page linked to from the seed_url, etc.

                :param ignore_previously_crawled_pages: Whether to ignore urls that are in the journal db_object's set of already-crawled urls.

                """

        be_verbose = self.verbose if verbose is None else verbose

        this_crawl = Crawl.objects.create(journal=self.db_object, seed_url=self.seed_url)

        if not self.seed_url.startswith("http://"):
            self.seed_url = "http://" + self.seed_url

        # calculate the site's domain for use in grabbing links
        site_domain = domain(urlparse(self.seed_url).netloc)

        urls_to_process = {self.seed_url}
        for i in range(depth):
            if be_verbose:
                print "Round %d: entered with %d urls to process." % (i, len(urls_to_process))

            new_urls = set()

            for j, cur_url in enumerate(urls_to_process):

                if ignore_previously_crawled_pages and cur_url in self.previously_crawled:
                    if be_verbose:
                        print "Round %d: skipping url %d/%d." % (i, j, len(urls_to_process))
                    continue

                self.add_to_crawled(cur_url)

                if self.exclude_url_pattern and eval(self.exclude_url_pattern):
                    continue

                if be_verbose:
                    print "Round %d: processing url %d/%d: %s." % (i, j, len(urls_to_process), cur_url)

                sleep(1)
                soup = get_soup(cur_url)
                if not soup:
                    self.log_msg("Could not open %s." % cur_url)
                    continue

                # parse this page to grab a story if it is one
                try:
                    self.parse_story(cur_url)
                except (IndexError), ex:
                    self.log_msg("Caught in parse_story for %s: %s." % (cur_url, ex))

                # regex checks if href has the domain in it, or if it doesn't start with http, meaning it's a relative link
                links = soup.findAll("a", {'href': re.compile(r"(%s|^(?!http))" % site_domain)})

                # grab all the links on this page, and save the ones that look like potential stories for the next round
                for link in links:
#                    if ('href' in dict(link.attrs)):
                    link = urljoin(cur_url, link['href']) # computes absolute url if link is a relative url

                    if link.find("'") != -1:
                        continue

                    link = link.split('#')[0] # remove location portion

                    if link[0:4] == 'http' and not self.has_been_crawled(link):
                        # add url to url queue
                        new_urls.add(link)

            urls_to_process = new_urls

        # dump all the crawled urls to the db and update the last time crawled
        # TODO what if end is not set because the crawl did not end? of course, then it wouldn't have crawled_pages, either
        previously_crawled = self.db_object.crawl_set.order_by('-end').order_by('-start')
        previously_crawled_pages = previously_crawled[0].crawled_pages if (previously_crawled.count() and previously_crawled[0].crawled_pages) else set()
        self.log_msg("Updating %s..." % this_crawl)
        this_crawl.end = datetime.datetime.now()
        this_crawl.crawled_pages = self.crawled_pages.union(previously_crawled_pages) if self.crawled_pages else previously_crawled_pages
        this_crawl.save()
        self.log_msg("Finished updating %s." % this_crawl)

#    def crawl_for_stories(self, urls):
#        for url in self.crawled:
#            self.parse_story(url)

    @transaction.commit_manually
    def parse_story(self, source):
        soup = get_soup(source)

        if not soup:
            # couldn't open it
            self.log_msg("Failed to open %s." % source)
            return None

        try:
            title = convert_entities(eval(self.title)).strip()
            teaser = convert_entities(eval(self.teaser)).strip()
            additional_text = convert_entities(eval(self.additional_text)).strip()
            author = convert_entities(eval(self.author)).strip()
        except (TypeError, IndexError, AttributeError):
            self.log_msg("Couldn't find story in %s." % source, logging.DEBUG)
            return None
        except SyntaxError, ex:
            self.log_msg("Syntax error parsing %s: %s." % (source, ex), logging.WARN)

        # sanity check on author
        if len(author) > self.MAX_AUTHOR_LENGTH:
            self.log_msg("Author too long: %s" % author)
            author = author[:self.MAX_AUTHOR_LENGTH] + "..."

        if author.lower().strip() in ["interview", "interviews"]:
            self.log_msg("Author was interview.")
            return

        if len(title) > self.MAX_TITLE_LENGTH:
            self.log_msg("Title too long: %s" % title)
            title = title[:self.MAX_TITLE_LENGTH] + "..."

        if title.strip().lower() == "from":
            self.log_msg("Title consists only of 'from' at %s" % source)

        if len(teaser) < self.MIN_TEASER_LENGTH:
            self.log_msg("Teaser too short: %s\nAdding: %s" % (teaser, additional_text))
            teaser = teaser + "<br />" if teaser else ""
            teaser = "".join([teaser, additional_text])

        # check if teaser is > max_length
        if len(teaser) > self.MAX_TEASER_LENGTH:
            self.log_msg("Teaser too long: %s" % teaser)
            teaser = teaser[:self.MAX_TEASER_LENGTH] + "..."

        if title and (title != "") and \
        teaser and (teaser != "") and \
        author and (author != ""):
            try:
                story = Story.objects.create(title=title,
                                            author=author,
                                            teaser=teaser,
                                            url=source,
                                            journal=self.db_object,
                                            )

            except IntegrityError, ex:
                transaction.rollback()
                self.log_msg("Skipping duplicate story at %s." % source, logging.DEBUG)
                return None
            else:
                self.log_msg("Added '%s' by %s at %s." % (title, author, source))
                transaction.commit()
                return story
        else:
            self.log_msg("Got non-story or invalid story from %s." % source, logging.DEBUG)
            return None


class Annalemma(StoryCrawler):
    journal_name = "Annalemma"
    seed_url = "annalemma.net"

    title = 're.findall(r"^(.*) \| Annalemma Magazine$", soup.title.text)[0]'
    author = 'soup.find(attrs={"class": "post-meta-key"}).next.next.strip()'
    teaser = 'soup.find("div", "entry").next.next.text'
    additional_text = 'soup.find("div", "entry").findAll("p")[1].text'
    exclude_from_urls = r're.search(r"(contributor|blog|about|contact|print|subscribe)", cur_url)'

    # use \S instead of \" so that when it's eval'ed, Python doesn't interpret nested "s as ending the string
#    url = 're.findall(r"url: \S(.*)\S }\);", soup.find("a", text=re.compile("SHARETHIS")))[0]'


class Ploughshares(StoryCrawler):
    journal_name = "Ploughshares"
    seed_url = "pshares.org"

    title = 'soup.h1.text.strip()'
    author = 'soup.find("span", "by").next.next.strip()'
    teaser = r"re.findall(r'^<p>(.*)<br />', str(soup.find('span', 'by').next.next.next.next.next))[0]"
    exclude_from_urls = r"re.findall(r'^<p>.*<br />\n<br />\n(.*)<br />', str(soup.find('span', 'by').next.next.next.next.next))[0]"


class AnomalousPress(StoryCrawler):
    journal_name = "Anomalous Press"
    seed_url = "anomalouspress.org"

    title = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChild(name="h1").text'
    author = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChild(name="h3").text'
    teaser = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChildren(name="p")[0].text'
    exclude_from_urls = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChildren(name="p")[1].text'


class FailBetter(StoryCrawler):
    journal_name = "FailBetter"
    seed_url = "failbetter.com"

    title = 'soup.findAll("div", {"id": "piece_data_display"})[0].findChild("h1").contents[0]'
    author = 'soup.find("span", "byline").text'
    teaser = 'soup.find("div", attrs={"id": "share_menu"}).findNextSiblings("p", attrs={"class": None})[0].text'
    additional_text = 'soup.find("div", attrs={"id": "share_menu"}).findNextSiblings("p", attrs={"class": None})[1].text'
    exclude_from_urls = r're.search(r"(Interview)", cur_url)'


class StorySouth(StoryCrawler):
    journal_name = "StorySouth"
    seed_url = "storysouth.com"

    title = 'soup.find("h4").text'
    author = '" ".join([n.capitalize() for n in soup.find("h5").findChild("a").text.split])'
    teaser = 'soup.find(attrs={"id": "closed"}).findChild("h1").text'
    exclude_from_urls = 'soup.find(attrs={"id": "closed"}).findChildren("h1")[1].text'


class AGNI(StoryCrawler):
    journal_name = "AGNI"
    seed_url = r"bu.edu/agni"

    title = 'soup.find("h1").text'
    author = 'soup.find("h2").find("a").text'
    teaser = 'soup.find("h2").findNextSibling().text'
    additional_text = 'soup.find("h2").findNextSibling().findNextSibling().text'
    exclude_from_urls = r're.search(r"(authors)", cur_url)'


class HaydensFerryReview(StoryCrawler):
    journal_name = "Hayden's Ferry Review"
    seed_url = "asu.edu/pipercwcenter/publications/haydensferryreview/"

    title = "soup.findAll(attrs={'class': 'style2'})[0].text.replace('&quot;', '')"
    author = 'soup.findAll(attrs={"class": "style2"})[1].text.replace("by ", "")'
    teaser = 'soup.findAll(attrs={"class": "style3"})[1].text'
    exclude_from_urls = 'soup.findAll(attrs={"class": "style3"})[2].text'


class TriQuarterly(StoryCrawler):
    journal_name = "TriQuarterly"
    seed_url = "triquarterly.org"

    title = 'soup.find("title").text.split("|")[0].strip()'
    author = 'soup.find(attrs={"class": "auth"}).find("a").text'
    teaser = 'soup.find(attrs={"class": "content"}).find("p").text'
    exclude_from_urls = 'soup.find(attrs={"class": "content"}).findAll("p")[1].text'


class Shenandoah(StoryCrawler):
    journal_name = "Shenandoah"
    seed_url = "shenandoahliterary.org"

    title = 'soup.find(attrs={"class": "entry-title"}).text'
    author = 'soup.find(attrs={"class": "about-author"}).findChild("h3").findChild("span").findChild("a").next.strip()'
    teaser = 'soup.find("div", "entry-content").findChild().text'
    exclude_from_urls = 'soup.find("div", "entry-content").findChildren("p")[1].text'


class AdirondackReview(StoryCrawler):
    journal_name = "The Adirondack Review"
    seed_url = "theadirondackreview.com"

    title = 'soup.find("font").text'
    author = '" ".join([n.capitalize() for n in soup.findChildren("font")[2].text.split()])'
    teaser = 'soup.find("div", attrs={"id": "element13"}).findAll("font")[0]'
    exclude_from_urls = 'soup.find("div", attrs={"id": "element13"}).findAll("font")[2]'


def main(depth=3, verbose=False):
    logging.basicConfig(filename=os.path.abspath(os.path.join(SCRIPT_ROOT, "parse.log")), level=logging.INFO)

    journal_classes = [journal_class for journal_name, journal_class
                       in inspect.getmembers(sys.modules[__name__], inspect.isclass)
                       if StoryCrawler in inspect.getmro(journal_class) and journal_name != "StoryCrawler"]
    logging.info("%s\nStarting crawl of %s." % ('=' * 50, ",".join([str(j) for j in journal_classes])))
    for journal in journal_classes:
        logging.info("%s\nCrawling %s." % ('-' * 50, journal))
        journal(verbose=verbose).crawl(depth=depth)

def test_main(depth=2):
    logging.basicConfig(filename=os.path.abspath(os.path.join(SCRIPT_ROOT, "parse.log")), level=logging.DEBUG)
    logging.info("%s\nStarting test_main at %s" % ("-" * 50, datetime.datetime.now()))
    s = Shenandoah(verbose=True)
    s.crawl(depth=depth)

    a = TriQuarterly(verbose=True)
    a.crawl(depth=depth)

    p = StorySouth(verbose=True)
    p.crawl(depth=depth)

if __name__ == "__main__":
    print "Usage: python manage.py crawl"
    sys.exit(0)

class Command(LabelCommand):
    def handle_label(self, label, **options):
        if label == "verbose":
            main(verbose=True)
        else:
            main(verbose=False)



