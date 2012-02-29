from day.models import Day
from django.contrib import admin


class DayAdmin(admin.ModelAdmin):
    list_display = ('day_and_story_and_journal',)

    def day_and_story_and_journal(self, obj):
        if obj.story:
            return ("%s (%s) %s" % (obj, obj.story.journal, "(Verified)" if obj.story.verified else ""))
    day_and_story_and_journal.short_description = 'Day, Story, Journal'

admin.site.register(Day, DayAdmin)
