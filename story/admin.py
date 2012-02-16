from django.contrib.admin.options import ModelAdmin
from story.models import Story
from django.contrib import admin

class StoryAdmin(ModelAdmin):
    list_filter = ('genre', 'journal')

    def show_url(self, obj):
        return '<a href="%s">%s</a>' % (obj.url, obj.url)
    show_url.allow_tags = True

    list_display = ('title', 'author', 'journal', 'show_url')

admin.site.register(Story, StoryAdmin)