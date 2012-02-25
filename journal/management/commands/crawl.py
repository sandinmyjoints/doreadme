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
from django.core.management.base import LabelCommand

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

    # This dict contains key, value pairs where key is a kind of pattern in the url to check for, and value are strings that signal a match of that pattern.
    # So, eg, exclude contains strings such that if any of those strings are found in a url, that url is excluded from being crawled. So this is a good
    # to put patterns that have a very high likelihood of not containing any writing that we want to crawl.
    # The other pattern types are used to guess at the genre of the crawled page (eg, poetry patterns mean the crawl sets Story.genre = "PO").
    # In inherited classes, you can extend these patterns by creating a list named "self.additional_<type of pattern>", eg,
    # self.additional_poetry. Any items in that list will get added to the strings that are checked for in urls.
    url_patterns_dict = {
        "exclude": [
            "blog",
            "author",
            "contributor",
            "about",
            "contact",
            "bios",
            "subscribe",
            ],

        "only_include": [
          # empty by default
        ],

        "fiction": [
            'fiction',
        ],

        "poetry": [
            "poe",
            ],

        "nonfiction": [
            "nonfiction",
            "essay"
        ],

        "interview": [
            "interview",
            ],

        "review": [
            "reviews" # don't use "review" because too many journals have that in their name, eg, haydensferryreview
        ],
        }
    #    exclude_from_urls = r're.search(r"(blog|author|contributor|about|contact|reviews|bios|nonfiction|poet|poem|essay)", cur_url)'

    def __init__(self, min_teaser_length=20, max_teaser_length=2000, max_title_length=256, max_author_length=128,
                 verbose=False):
        super(StoryCrawler, self).__init__()
        self.crawled_pages = set()
        self.verbose = verbose
        self.MIN_TEASER_LENGTH = min_teaser_length
        self.MAX_TEASER_LENGTH = max_teaser_length
        self.MAX_TITLE_LENGTH = max_title_length
        self.MAX_AUTHOR_LENGTH = max_author_length

        for pattern_name, patterns in self.url_patterns_dict.iteritems():
            setattr(self, pattern_name, patterns)
            if hasattr(self, "additional_" + pattern_name):
                additional = getattr(self, "additional_" + pattern_name)
                setattr(self, pattern_name, getattr(self, pattern_name).extend(additional))
            url_patterns_attribute_name = pattern_name + "_url_patterns"
            setattr(self,
                url_patterns_attribute_name,
                're.search(r"' + "|".join([pattern for pattern in getattr(self, pattern_name)]) + '", cur_url)')
            print "%s.%s is %s" % (self, url_patterns_attribute_name, getattr(self, url_patterns_attribute_name))

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

                if hasattr(self, "exclude_url_patterns") and self.exclude_url_patterns and eval(self.exclude_url_patterns):
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
        previously_crawled_pages = previously_crawled[0].crawled_pages if (
        previously_crawled.count() and previously_crawled[0].crawled_pages) else set()
        self.log_msg("Updating %s..." % this_crawl)
        this_crawl.end = datetime.datetime.now()
        this_crawl.crawled_pages = self.crawled_pages.union(
            previously_crawled_pages) if self.crawled_pages else previously_crawled_pages
        this_crawl.save()
        self.log_msg("Finished updating %s." % this_crawl)

    #    def crawl_for_stories(self, urls):
    #        for url in self.crawled:
    #            self.parse_story(url)

    @transaction.commit_manually
    def parse_story(self, source):
        cur_url = source
        soup = get_soup(source)

        if not soup:
            # couldn't open it
            self.log_msg("Failed to open %s." % source)
            return None

        try:
            title = convert_entities(eval(self.title)).strip()
            teaser = convert_entities(eval(self.teaser)).strip()
            additional_text1 = convert_entities(eval(self.additional_text1)).strip()
            additional_text2 = convert_entities(eval(self.additional_text2)).strip()
            author = convert_entities(eval(self.author)).strip()
        except (TypeError, IndexError, AttributeError):
            self.log_msg("Couldn't find story in %s." % source, logging.DEBUG)
            return None
        except SyntaxError, ex:
            self.log_msg("Syntax error parsing %s: %s." % (source, ex), logging.WARN)

        # Begin the processing. First, initialize some variables
        genre = None # start off as None, and then we will set it if we see certain features. If it falls through all that without being set, the default
        # is Fiction
        crawl_flagged = False  # an experimental feature to see how well the crawl can flag suspicious pages

        # sanity checks
        if len(author) > self.MAX_AUTHOR_LENGTH:
            self.log_msg("Author too long: %s" % author)
            author = author[:self.MAX_AUTHOR_LENGTH-3] + "..."
            crawl_flagged = True

        if author.lower().strip() in ["interview", "interviews"]:
            self.log_msg("Author was interview.")
            genre = "IN"

        if len(title) > self.MAX_TITLE_LENGTH:
            self.log_msg("Title too long: %s" % title)
            title = title[:self.MAX_TITLE_LENGTH-3] + "..."
            crawl_flagged = True

        if title.strip().lower() == "from":
            self.log_msg("Title consists only of 'from' at %s" % source)
            crawl_flagged = True

        extra = ""
        if len(teaser) < self.MIN_TEASER_LENGTH:
            self.log_msg("Teaser too short: %s\nAdding: %s" % (teaser, additional_text1))
            teaser = teaser + "<br />" if teaser else ""
            teaser = "".join([teaser, additional_text1])
            # we used up additional_text1 to make teaser long enough, so we use additional_text2 as .additional on the model object
            additional = additional_text2
            crawl_flagged = True
        else:
            # we didn't need additional_text1 for the teaser, so we can use it as additional on the db object
            additional = additional_text1
            # so what do we do with additional_text2? stash it in the extra field on the db model for now...
            extra = additional_text2

        # check if teaser is > max_length
        if len(teaser) > self.MAX_TEASER_LENGTH:
            self.log_msg("Teaser too long: %s" % teaser)
            #            teaser = teaser[:self.MAX_TEASER_LENGTH] + "..."
            crawl_flagged = True

        # Additional checks for possible flags and genre traits
        if not teaser.endswith(".") and not teaser.endswith('"'):
            crawl_flagged = True
            genre = "PO"

        if not teaser[0].istitle():
            # checks the case of the first letter of teaser
            crawl_flagged = True
            genre = "PO"

        lower_teaser = teaser.lower()
        if lower_teaser.startswith("for") or lower_teaser.startswith("after"):
            crawl_flagged = True
            genre = "PO"

        if teaser.startswith(("[", "(", "-", ":", ".", ",", "{")):
            crawl_flagged = True
            genre = "PO"

        if teaser.find("<") > -1 or teaser.find(">") > -1:
            crawl_flagged = True
            genre = "OW"

        if lower_teaser.find("adobe") > -1 or\
           lower_teaser.find("flash") > -1 or\
           lower_teaser.find("javascript") > -1 or\
           lower_teaser.find("audio") > -1 or\
           lower_teaser.find("download") > -1 or\
           lower_teaser.find("clip") > -1:
            crawl_flagged = True
            genre = "OW"

        # Guess at the genre.
        # This has a dependency on Story.models.GENRE_CHOICES.
        # These have a higher accuracy than the heuristic checks, so they can override them.
        if hasattr(self, "fiction_url_patterns") and self.fiction_url_patterns and eval(self.fiction_url_patterns):
            genre = "FI"
        elif hasattr(self, "poetry_url_patterns") and self.poetry_url_patterns and eval(self.poetry_url_patterns):
            genre = "PO"
        elif hasattr(self, "interview_url_patterns") and self.interview_url_patterns and eval(self.interview_url_patterns):
            genre = "IN"
        elif hasattr(self, "nonfiction_url_patterns") and self.nonfiction_url_patterns and eval(self.nonfiction_url_patterns):
            genre = "NF"
        elif hasattr(self, "review_url_patterns") and self.review_url_patterns and eval(self.review_url_patterns):
            genre = "RE"

        # If genre still isn't set, we'll assume it's fiction
        if not genre:
            genre = "FI"

        if title and (title != "") and\
           teaser and (teaser != "") and\
           additional and (additional != "") and\
           author and (author != ""):
            try:
                story = Story.objects.create(title=title,
                    author=author,
                    teaser=teaser,
                    additional_teaser=additional,
                    extra_teaser=extra,
                    url=source,
                    genre=genre,
                    crawl_flagged=crawl_flagged,
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
    additional_text1 = 'soup.find("div", "entry").findAll("p")[1].text'
    additional_text2 = 'soup.find("div", "entry").findAll("p")[2].text'

    # use \S instead of \" so that when it's eval'ed, Python doesn't interpret nested "s as ending the string

#    url = 're.findall(r"url: \S(.*)\S }\);", soup.find("a", text=re.compile("SHARETHIS")))[0]'


# This one doesn't work too well
class Ploughshares(StoryCrawler):
    journal_name = "Ploughshares"
    seed_url = "pshares.org"

    title = 'soup.h1.text.strip()'
    author = 'soup.find("span", "by").next.next.strip()'
    #    teaser = r"re.findall(r'^<p>(.*)<br />', str(soup.find('span', 'by').next.next.next.next.next))[0]"
    teaser = r"re.findall(r'^<p>(.*)<br />', str(soup.find('p')))"
    additional_text1 = r"re.findall(r'<br />\r\n(.*?)<br />', str(soup.find('p')))[0]"
    additional_text2 = r"re.findall(r'<br />\r\n(.*?)<br />', str(soup.find('p')))[1]"
#    exclude_from_urls = r"re.findall(r'^<p>.*<br />\n<br />\n(.*)<br />', str(soup.find('span', 'by').next.next.next.next.next))[0]"


class AnomalousPress(StoryCrawler):
    journal_name = "Anomalous Press"
    seed_url = "anomalouspress.org"

    title = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChild(name="h1").text'
    author = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChild(name="h3").text'
    teaser = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChildren(name="p")[1].text'
    additional_text1 = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChildren(name="p")[2].text'
    additional_text2 = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChildren(name="p")[3].text'
#    exclude_from_urls = 'soup.findAll("div", attrs={"id": "current_body"})[0].findChildren(name="p")[1].text'


class FailBetter(StoryCrawler):
    journal_name = "FailBetter"
    seed_url = "failbetter.com"

    title = 'soup.findAll("div", {"id": "piece_data_display"})[0].findChild("h1").contents[0]'
    author = 'soup.find("span", "byline").text'
    teaser = 'soup.find("div", attrs={"id": "share_menu"}).findNextSiblings("p", attrs={"class": None})[0].text'
    additional_text1 = 'soup.find("div", attrs={"id": "share_menu"}).findNextSiblings("p", attrs={"class": None})[1].text'
    additional_text2 = 'soup.find("div", attrs={"id": "share_menu"}).findNextSiblings("p", attrs={"class": None})[2].text'


class StorySouth(StoryCrawler):
    journal_name = "StorySouth"
    seed_url = "storysouth.com"

    title = 'soup.find("h4").text'
    author = '" ".join([n.capitalize() for n in soup.find("h5").findChild("a").text.split()])'
    teaser = 'soup.find(attrs={"id": "closed"}).findChildren("h1")[0].text'
    additional_text1 = 'soup.find(attrs={"id": "closed"}).findChildren("h1")[1].text'
    additional_text2 = 'soup.find(attrs={"id": "closed"}).findChildren("h1")[2].text'


class AGNI(StoryCrawler):
    journal_name = "AGNI"
#    seed_url = r"bu.edu/agni"
    seed_url = r"www.bu.edu/agni/fiction.html"

    title = 'soup.find("h1").text'
    author = 'soup.find("h2").find("a").text'
    teaser = 'soup.find("h2").findNextSibling().text'
    additional_text1 = 'soup.find("h2").findNextSibling().findNextSibling().text'
    additional_text2 = 'soup.find("h2").findNextSibling().findNextSibling().findNextSibling().text'


# TODO this one needs work--doesn't seem to find anything, and tries too many irrelevant links through asu.edu
class HaydensFerryReview(StoryCrawler):
    journal_name = "Hayden's Ferry Review"
    seed_url = "asu.edu/pipercwcenter/publications/haydensferryreview/"

    title = "soup.findAll(attrs={'class': 'style2'})[0].text.replace('&quot;', '')"
    author = 'soup.findAll(attrs={"class": "style2"})[1].text.replace("by ", "")'
    teaser = 'soup.findAll(attrs={"class": "style3"})[1].text'
    additional_text1 = 'soup.findAll(attrs={"class": "style3"})[2].text'
    additional_text2 = 'soup.findAll(attrs={"class": "style3"})[3].text'


class TriQuarterly(StoryCrawler):
    journal_name = "TriQuarterly"
    seed_url = "triquarterly.org"

    title = 'soup.find("title").text.split("|")[0].strip()'
    author = 'soup.find(attrs={"class": "auth"}).find("a").text'
    teaser = 'soup.find(attrs={"class": "content"}).findAll("p")[0].text'
    additional_text1 = 'soup.find(attrs={"class": "content"}).findAll("p")[1].text'
    additional_text2 = 'soup.find(attrs={"class": "content"}).findAll("p")[2].text'


class Shenandoah(StoryCrawler):
    journal_name = "Shenandoah"
    seed_url = "shenandoahliterary.org"

    title = 'soup.find(attrs={"class": "entry-title"}).text'
    author = 'soup.find(attrs={"class": "about-author"}).findChild("h3").findChild("span").findChild("a").next.strip()'
    teaser = 'soup.find("div", "entry-content").findChildren()[0].text'
    additional_text1 = 'soup.find("div", "entry-content").findChildren()[1].text'
    additional_text2 = 'soup.find("div", "entry-content").findChildren()[2].text'


# This one has trouble with author--selects the wrong thing a lot of the time
class AdirondackReview(StoryCrawler):
    journal_name = "The Adirondack Review"
    seed_url = "theadirondackreview.com"

    title = 'soup.find("font").text'
    author = '" ".join([n.capitalize() for n in soup.findChildren("font")[2].text.split()])'
    teaser = 'soup.find("div", attrs={"id": "element13"}).findAll("font")[0].text'
    additional_text1 = 'soup.find("div", attrs={"id": "element13"}).findAll("font")[2].text' # number of font elements seems to be arbitrary
    additional_text2 = 'soup.find("div", attrs={"id": "element13"}).findAll("font")[5].text' # it might be specific to each story--how to deal with that?


def story_count():
    for j in Journal.objects.all():
        print "%s: %d" % (j, Story.all_verified_fiction.filter(journal__exact=j.id).count())

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
#    s = Shenandoah(verbose=True)
#    s.crawl(depth=depth)

#    a = TriQuarterly(verbose=True)
#    a.crawl(depth=depth)

#    p = StorySouth(verbose=True)
#    p.crawl(depth=depth)

#    hfr = HaydensFerryReview(verbose=True)
#    hfr.seed_url = "http://asu.edu/piper/publications/haydensferryreview/archive.html"
#    hfr.additional_exclude = "www.asu.edu"
    # TODO also need to exclude anything that doesn't have /piper/publications/haydensferryreview in the url
#    hfr.crawl(depth=depth)

#    a = AGNI(verbose=True)
#    a.crawl(depth=3)

#    a = AnomalousPress(verbose=True)
#    a.seed_url = "http://www.anomalouspress.org/archive/then.php"
#    a.crawl(depth=3)

#    a = AdirondackReview(verbose=True)
#    a.seed_url = "http://www.theadirondackreview.com/archives.html"
#    a.crawl(depth=3)

    a = Annalemma(verbose=True)
    a.seed_url = "http://annalemma.net/category/features/page/2"
    a.crawl(depth=3)

if __name__ == "__main__":
    print "Usage: python manage.py crawl"
    sys.exit(0)

class Command(LabelCommand):
    def handle_label(self, label, **options):
        if label == "verbose":
            main(verbose=True)
        else:
            main(verbose=False)



