from datetime import datetime
from django import template

register = template.Library()

# inclusion tag to put the contact form into a page
# the contact form is a div. a link to it that should work if js is disabled, otherwise it opens in a modal dialog
# the form is submitted via ajax, and a thank you page is shown via ajax
@register.inclusion_tag('day/calendar.html')
def get_calendar_widget():
    today = datetime.today().date()
    return { 'month': today.month,
            'day': today.day,
            'year': today.year
    }

@register.inclusion_tag('day/more_actions.html')
def include_more_actions(day):
    current_day = day.day
    previous_day = datetime.fromordinal((current_day.toordinal() - 1)).date()
    if current_day < datetime.today().date():
        next_day = datetime.fromordinal((current_day.toordinal() + 1)).date()
    else:
        next_day = None
    nice_month = datetime.strftime(current_day, "%B")

    return {
        'current_day': current_day,
        'previous_day': previous_day,
        'next_day': next_day,
        'nice_month': nice_month,
    }