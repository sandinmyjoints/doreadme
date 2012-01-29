# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Story.date_created'
        db.add_column('story_story', 'date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.date(2012, 1, 14), blank=True), keep_default=False)

        # Adding field 'Story.date_modified'
        db.add_column('story_story', 'date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.date(2012, 1, 14), blank=True), keep_default=False)

        # Adding field 'Story.date_last_shown'
        db.add_column('story_story', 'date_last_shown', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Story.date_created'
        db.delete_column('story_story', 'date_created')

        # Deleting field 'Story.date_modified'
        db.delete_column('story_story', 'date_modified')

        # Deleting field 'Story.date_last_shown'
        db.delete_column('story_story', 'date_last_shown')


    models = {
        'story.story': {
            'Meta': {'object_name': 'Story'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_last_shown': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'teaser': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['story']
