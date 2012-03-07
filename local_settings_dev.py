__author__ = 'wbert'

INTERNAL_IPS = ('127.0.0.1', '192.168.199.132', '192.168.1.101', '192.168.199.1')

MANAGERS = ADMINS = (
    ('William', 'william.bert@gmail.com'),
)

SITE_ID = 1

DEBUG = True

DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'doreadme',                      # Or path to database file if using sqlite3.
        'USER': 'doreadme',                      # Not used with sqlite3.
        'PASSWORD': 'glbnocb9doreadme',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_HOST = ('smtp.gmail.com')
EMAIL_PORT = ('587')
EMAIL_HOST_USER = ('email.daily.story@gmail.com')
EMAIL_HOST_PASSWORD = ('glbnocb9dailystory')
EMAIL_USE_TLS = True


BROKER_HOST = "ubuntu"
BROKER_PORT = 5672
BROKER_USER = "doreadme"
BROKER_PASSWORD = "glbnocb9doreadme"
BROKER_VHOST = "doreadmevhost"
CELERYD_CONCURRENCY = 1
CELERYD_NODES="w1"
CELERY_RESULT_BACKEND="amqp"