from contact_form.forms import BasicContactForm
from django import template
from django.contrib.sites.models import Site

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

