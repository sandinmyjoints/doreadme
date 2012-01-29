"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime

from django.test import TestCase
from story.models import Story


class StoryTest(TestCase):

    def test_add_days(self):
        dt = datetime.fromordinal(10)
        dt = Story.add_days(dt=dt)
        self.assertEqual(11, dt.toordinal())

        dt = datetime.fromordinal(10)
        dt = Story.add_days(dt=dt, days=2)
        self.assertEqual(12, dt.toordinal())

        dt = None
        Story.add_days(dt)
        self.assertEqual(datetime.today().toordinal(), dt.toordinal())

    def test_schedule_featured_date(self):
        pass