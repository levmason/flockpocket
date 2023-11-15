"""
Django settings for the flockpocket project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import sys
import yaml
from datetime import timedelta
from common import root_config as cfg

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = cfg.django_secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = cfg.debug

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    # flockpocket
    'common.apps.CommonConfig',
    'webapp.apps.WebappConfig',
    'api.apps.ApiConfig',
    # other
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATE_DEBUG = False
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['webapp/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'flockpocket.urls'
WSGI_APPLICATION = 'flockpocket.wsgi.application'
ASGI_APPLICATION = "flockpocket.asgi.application"

AUTH_USER_MODEL = "common.User"
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': cfg.db_name,
        'USER': cfg.db_username,
        'PASSWORD': cfg.db_password,
        'HOST': cfg.db_host,
        'PORT': cfg.db_port,
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = True

USE_I18N = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

USE_X_FORWARDED_HOST = True
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

SUB_URL = cfg.sub_url
if SUB_URL:
    ROOT_URL = '/%s/' % SUB_URL
else:
    ROOT_URL = '/'

STATIC_URL = '%sstatic/' % ROOT_URL
LOGIN_URL = '%slogin' % ROOT_URL
LOGIN_REDIRECT_URl = ROOT_URL

# HTTPS
SESSION_COOKIE_NAME = "%s.sessionid" % cfg.tool_name
X_FRAME_OPTIONS = 'SAMEORIGIN'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://localhost', 'https://192.168.1.57', 'https://174.109.30.190']

# LEVY: Debug junk
#SESSION_COOKIE_SECURE = False
#CSRF_COOKIE_SECURE = False

# Set the default id field type for postgres tables
DEFAULT_AUTO_FIELD='django.db.models.AutoField'
