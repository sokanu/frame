"""
Django settings for frame project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wr#$q1lop5zwb--8*3%9xv-lix+ab2@dp6h&p0&l1@5w5jm^ui'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG_ENABLED', False)

TEMPLATE_DEBUG = True
TEMPLATE_DIRS =(
    os.path.join(BASE_DIR, 'templates'),
)

ALLOWED_HOSTS = ['.herokuapp.com', 'localhost']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_coverage',

    'images',
    'client',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom, view-based middelware. Middleware rules are defined in urls.py
    'urlmiddleware.URLMiddleware',
)

#MIDDLEWARE_CLASSES = (
#    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#)


ROOT_URLCONF = 'frame.urls'

WSGI_APPLICATION = 'frame.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
import dj_database_url

if dj_database_url.config():
    DATABASES = {'default': dj_database_url.config()}
else:
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')


# Frame-specific settings
ALLOWED_FORMATS = ('image/jpg', 'image/jpeg', 'image/gif', 'image/png')

FRAME_STORAGE_LIBRARY = 'images.storage.S3Storage'
#FRAME_STORAGE_LIBRARY = 'images.storage.LocalStorage'

# Caching options
if os.environ.get('MEMCACHEDCLOUD_SERVERS'):
    CACHE_BACKEND = 'django_bmemcached.memcached.BMemcached'
    CACHE_LOCATION = os.environ.get('MEMCACHEDCLOUD_SERVERS').split(',')
    CACHE_OPTIONS = {'username': os.environ.get('MEMCACHEDCLOUD_USERNAME'), 'password': os.environ.get('MEMCACHEDCLOUD_PASSWORD')}
else:
    CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'
    CACHE_LOCATION = 'unique-snowflake'
    CACHE_OPTIONS = {}


CACHES = {
    'default': {
        'BACKEND': CACHE_BACKEND,
        'LOCATION': CACHE_LOCATION,
        'OPTIONS': CACHE_OPTIONS
    }
}


# Load local settings if file is found
try:
    from frame.settings_local import *
except ImportError:
    pass


