# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Crawl'
        db.create_table('journal_crawl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('journal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['journal.Journal'])),
            ('seed_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('crawled_pages', self.gf('picklefield.fields.PickledObjectField')(null=True)),
        ))
        db.send_create_signal('journal', ['Crawl'])

        # Deleting field 'Journal.last_crawled'
        db.delete_column('journal_journal', 'last_crawled')

        # Deleting field 'Journal.crawled_pages'
        db.delete_column('journal_journal', 'crawled_pages')

        # Adding unique constraint on 'Journal', fields ['slug']
        db.create_unique('journal_journal', ['slug'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Journal', fields ['slug']
        db.delete_unique('journal_journal', ['slug'])

        # Deleting model 'Crawl'
        db.delete_table('journal_crawl')

        # Adding field 'Journal.last_crawled'
        db.add_column('journal_journal', 'last_crawled', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Adding field 'Journal.crawled_pages'
        db.add_column('journal_journal', 'crawled_pages', self.gf('picklefield.fields.PickledObjectField')(null=True), keep_default=False)


    models = {
        'journal.crawl': {
            'Meta': {'object_name': 'Crawl'},
            'crawled_pages': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['journal.Journal']"}),
            'seed_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'journal.journal': {
            'Meta': {'object_name': 'Journal'},
            'additional_text_pattern': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'author_pattern': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'seed_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'teaser_pattern': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'title_pattern': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['journal']
