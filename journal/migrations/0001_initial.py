# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Journal'
        db.create_table('journal_journal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_crawled', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('crawled_pages', self.gf('picklefield.fields.PickledObjectField')(null=True)),
        ))
        db.send_create_signal('journal', ['Journal'])


    def backwards(self, orm):
        
        # Deleting model 'Journal'
        db.delete_table('journal_journal')


    models = {
        'journal.journal': {
            'Meta': {'object_name': 'Journal'},
            'crawled_pages': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_crawled': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['journal']
