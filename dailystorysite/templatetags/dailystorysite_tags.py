from datetime import datetime
from contact_form.forms import BasicContactForm
from django import template
from django.contrib.sites.models import Site
from day.models import Day
from journal.models import Journal
from story.models import Story

HEADLESS_DESCRIPTION = "presents new short fiction from across the internet every day. Read on if you're into it, or come back tomorrow for a different story."

register = template.Library()

# inclusion tag to put the contact form into a page
# the contact form is a div. a link to it that should work if js is disabled, otherwise it opens in a modal dialog
# the form is submitted via ajax, and a thank you page is shown via ajax
@register.inclusion_tag('contact_form/contact_form_include.html')
def include_contact_form():
    return {'form': BasicContactForm()}


@register.inclusion_tag('dailystorysite/site_name.html')
def include_site_name_header():
# This assumes the current site name is storyb.it
#    assert Site.objects.get_current().name == "storyb.it"
#    return {"SITE_NAME": '<span class="pink">story</span><span class="black">b</span><span class="black">.</span><span class="black">it</span>' }

    # This assumes the current site name is doread.me.
    assert Site.objects.get_current().name == "doread.me"
    return {"SITE_NAME": '<span class="do">do</span><span class="read">read</span><span class="me">.me</span>'}


@register.simple_tag()
def include_description_long():
    return " ".join([Site.objects.get_current().name, HEADLESS_DESCRIPTION])


@register.inclusion_tag('dailystorysite/description_short.html')
def include_description_short():
    return {}


@register.simple_tag()
def include_headless_description():
    return HEADLESS_DESCRIPTION

@register.inclusion_tag('dailystorysite/statistics.html')
def include_statistics():
    # TODO cache these or otherwise optimize them
    start_date = Day.first_day()
    num_total_stories = Story.all_fiction.count()
    mod_ten = num_total_stories % 10
    num_total_stories -= mod_ten
    featured_stories = Story.verified_fiction.exclude(featured_days=None).filter(featured_days__day__lte=datetime.today())
    num_featured_stories = featured_stories.count()
    num_total_journals = Journal.objects.count()
    num_featured_journals = len(set([s.journal for s in featured_stories]))
    return {
        "start_date": start_date,
        "num_total_journals": num_total_journals,
        "num_total_stories": num_total_stories,
        "num_featured_stories": num_featured_stories,
        "num_featured_journals": num_featured_journals,
    }

# Since Feb 1, 2012, 7 featured stories from 12 unique journals, drawn from 345 stories from 12 unique journals.