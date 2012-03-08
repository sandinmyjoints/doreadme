import logging

from django.conf import settings
from celery.task import task
from django.core.mail import mail_admins
from django.core.mail.message import BadHeaderError
from journal.models import Journal
from story.models import Story

logger = logging.getLogger(__name__)

WARNING_MESSAGE = """
            Story.verified_nonfeatured_fiction.count() indicates that there are only %d verified,
            non-featured stories left. Consider running a crawl and classifying unverified stories to fix this.
            """

@task
def ensure_enough_verifiednonfeaturedfiction():
    logger = ensure_enough_verifiednonfeaturedfiction.get_logger(logfile="logs/user/tasks.log")
    logger.info("ensure_enough")

    fiction_count = Story.verified_nonfeatured_fiction.count()
    if fiction_count <= settings.MIN_STORIES_WARNING:
        logger.warning(WARNING_MESSAGE % fiction_count)

        try:

            mail_admins(subject="Only %d stories left" % fiction_count,
                message=WARNING_MESSAGE)
        except (BadHeaderError, SMTPEexception), ex:
            logger.warning("Error sending mail from ensure_enough_verifiednonfeaturedfiction: %s" % ex)

    for journal in Journal.objects.all():
        stories = journal.story_set.filter(genre__exact="FI")
        total_stories = stories.count()
        featured_stories = stories.filter(featured_days__isnull=False).count()
        unfeatured_stories = stories.filter(featured_days__isnull=True).count()
        entry = "%s\t Total stories: %d\t Featured stories: %d\t Unfeatured stories: %d" % (journal, total_stories, featured_stories, unfeatured_stories)
        logger.info("%s" % entry)