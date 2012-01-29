# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Journal.seed_url'
        db.add_column('journal_journal', 'seed_url', self.gf('django.db.models.fields.URLField')(default=' ', max_length=200), keep_default=False)

        # Adding field 'Journal.title_pattern'
        db.add_column('journal_journal', 'title_pattern', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True), keep_default=False)

        # Adding field 'Journal.teaser_pattern'
        db.add_column('journal_journal', 'teaser_pattern', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True), keep_default=False)

        # Adding field 'Journal.additional_text_pattern'
        db.add_column('journal_journal', 'additional_text_pattern', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True), keep_default=False)

        # Adding field 'Journal.author_pattern'
        db.add_column('journal_journal', 'author_pattern', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Journal.seed_url'
        db.delete_column('journal_journal', 'seed_url')

        # Deleting field 'Journal.title_pattern'
        db.delete_column('journal_journal', 'title_pattern')

        # Deleting field 'Journal.teaser_pattern'
        db.delete_column('journal_journal', 'teaser_pattern')

        # Deleting field 'Journal.additional_text_pattern'
        db.delete_column('journal_journal', 'additional_text_pattern')

        # Deleting field 'Journal.author_pattern'
        db.delete_column('journal_journal', 'author_pattern')


    models = {
        'journal.journal': {
            'Meta': {'object_name': 'Journal'},
            'additional_text_pattern': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'author_pattern': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'crawled_pages': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_crawled': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'seed_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'teaser_pattern': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'title_pattern': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['journal']
