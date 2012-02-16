from contact_form.forms import BasicContactForm
from django import template
from django.contrib.sites.models import Site

register = template.Library()

# inclusion tag to put the contact form into a page
# the contact form is a div. a link to it that should work if js is disabled, otherwise it opens in a modal dialog
# the form is submitted via ajax, and a thank you page is shown via ajax
@register.inclusion_tag('contact_form/contact_form_include.html')
def include_contact_form():
    return { 'form': BasicContactForm() }

@register.inclusion_tag('dailystorysite/site_name.html')
def include_site_name_header():
    # This assumes the current site name is doread.me.
    assert Site.objects.get_current().name == "doread.me"
    return {"SITE_NAME": '<span class="do">do</span><span class="read">read</span><span class="me">.me</span>' }