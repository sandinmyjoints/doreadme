import logging

from django.conf import settings
from celery.task import task
from django.core.mail import mail_admins
from django.core.mail.message import BadHeaderError
from story.models import Story

logger = logging.getLogger(__name__)

WARNING_MESSAGE = """
            Story.verified_nonfeatured_fiction.count() indicates that there are only %d verified,
            non-featured stories left. Consider running a crawl and classifying unverified stories to fix this.
            """

@task
def ensure_enough_verifiednonfeaturedfiction():
    logger = dummy_task.get_logger(logfile="logs/user/tasks.log")
    logger.info("ensure_enough")

    fiction_count = Story.verified_nonfeatured_fiction.count()
    if fiction_count <= settings.MIN_STORIES_WARNING:
        logger.warn(WARNING_MESSAGE % fiction_count)

        try:

            mail_admins(subject="Only %d stories left" % fiction_count,
                message=WARNING_MESSAGE)
        except (BadHeaderError, SMTPEexception), ex:
            logger.warn("Error sending mail from ensure_enough_verifiednonfeaturedfiction: %s" % ex)
