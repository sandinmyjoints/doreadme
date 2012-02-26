from datetime import datetime
from day.models import Day

__author__ = 'wbert'

def first_day(request):
    # TODO optimize this
    first_day = Day.first_day()
    if not first_day:
        first_day = datetime.today()

    return {"FIRST_DAY": first_day }