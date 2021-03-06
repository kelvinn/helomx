# Django settings for mxmon project.
import os
import socket

if socket.gethostname() == 'ip-10-128-139-221':
    DEBUG = False
else:
    DEBUG = True


ENABLE_SDB = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'helomx'             # Or path to database file if using sqlite3.
DATABASE_USER = 'helomx'             # Not used with sqlite3.
DATABASE_PASSWORD = 'helomx'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

#DATABASE_HOST = '10.176.71.243'             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = '3306'             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Australia/Sydney'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://media.helomx.com/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'abcd'

EMAIL_HOST = 'smtp.gmail.com'
DEFAULT_FROM_EMAIL='no-reply@helomx.com'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'no-reply@helomx.com'
EMAIL_HOST_PASSWORD = 'abcd'
EMAIL_PORT = 587

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'helomx.urls'

ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = '/dashboard/'


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.realpath (os.path.join (os.path.dirname (__file__), 'templates'))
)

PAYPAL_RECEIVER_EMAIL = "user@emample.com"
PAYPAL_SANDBOX_IMAGE = "https://www.paypal.com/en_US/i/btn/x-click-but9.gif"
PAYPAL_IMAGE = "https://www.paypal.com/en_US/i/btn/x-click-but9.gif"

PAYPAL_PRIVATE_CERT = '/etc/apache2/ssl/helomx.com/paypal.pem'
PAYPAL_PUBLIC_CERT = '/etc/apache2/ssl/helomx.com/pubpaypal.pem'
PAYPAL_CERT = '/etc/apache2/ssl/helomx.com/paypal_cert.pem'
PAYPAL_CERT_ID = 'abcd'



INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.flatpages',
    'django.contrib.sitemaps',
    #'django_evolution',
    'helomx.billing',
    'helomx.hosts',
    'helomx.monitor',
    'helomx.profiles',
    'helomx.contact',
    'helomx.infolog',
    'helomx.postfix',
    'paypal.standard.ipn',
    'registration',
    #'debug_toolbar',
    'GChartWrapper.charts',
)
