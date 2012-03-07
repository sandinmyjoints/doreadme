__author__ = 'wbert'

MANAGERS = ADMINS = (
    ('William', 'william.bert@gmail.com'),
)

SITE_ID = 2

DEBUG = False

DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'wjb_doreadme',                      # Or path to database file if using sqlite3.
        'USER': 'wjb_doreadme',                      # Not used with sqlite3.
        'PASSWORD': '295b6f33',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_HOST = ('smtp.webfaction.com')
#EMAIL_PORT = ('587')
EMAIL_HOST_USER = ('wjb_doreadme')
EMAIL_HOST_PASSWORD = ('glbnocb9doreadme')
#EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'william@doread.me'
SERVER_EMAIL = "william@doread.me"

STATIC_ROOT = '/home/wjb/webapps/doreadme_static'


BROKER_HOST = "localhost"
BROKER_PORT = 25508
BROKER_USER = "doreadme"
BROKER_PASSWORD = "glbnocb9doreadme"
BROKER_VHOST = "doreadmevhost"
CELERYD_CONCURRENCY = 1
CELERYD_NODES="w1"
CELERY_RESULT_BACKEND="amqp"