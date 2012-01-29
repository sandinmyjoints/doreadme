# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Story.author'
        db.add_column('story_story', 'author', self.gf('django.db.models.fields.CharField')(default='', max_length=256), keep_default=False)

        # Adding field 'Story.active'
        db.add_column('story_story', 'active', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Story.author'
        db.delete_column('story_story', 'author')

        # Deleting field 'Story.active'
        db.delete_column('story_story', 'active')


    models = {
        'story.story': {
            'Meta': {'object_name': 'Story'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'teaser': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['story']
