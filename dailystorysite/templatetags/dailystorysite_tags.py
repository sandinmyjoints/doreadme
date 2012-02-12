from contact_form.forms import BasicContactForm
from django import template

register = template.Library()

# inclusion tag to put the contact form into a page
# the contact form is a div. a link to it that should work if js is disabled, otherwise it opens in a modal dialog
# the form is submitted via ajax, and a thank you page is shown via ajax
@register.inclusion_tag('contact_form/contact_form_include.html')
def include_contact_form():
    return { 'form': BasicContactForm() }