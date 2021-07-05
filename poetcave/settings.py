"""
Django settings for poetcave project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'poem',

    'termsandconditions',
    'django_markdown2',
    'django_registration',
    'languagecontrol',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'languagecontrol.middleware.LanguageControlMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'termsandconditions.middleware.TermsAndConditionsRedirectMiddleware',
]

ROOT_URLCONF = 'poetcave.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'core.context_processors.globals',
            ],
        },
    },
]

WSGI_APPLICATION = 'poetcave.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

# Pages and redirect
LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('main')
LOGOUT_REDIRECT_URL = reverse_lazy('main')

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'is'
TIME_ZONE = 'UTC'
DATE_FORMAT = 'j. E Y'
DATETIME_FORMAT = 'H:i, j. E Y'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [
    BASE_DIR / 'poetcave' / 'locale',
]

# Alphabet information
ALPHABET = {
    'is': {
        'letters': [
            'A',
            'B',
            'C',
            'D',
            'E',
            'F',
            'G',
            'H',
            'I',
            'J',
            'K',
            'L',
            'M',
            'N',
            'O',
            'P',
            'Q',
            'R',
            'S',
            'T',
            'U',
            'V',
            'W',
            'X',
            'Y',
            'Z',
            'Þ',
            'Æ',
            'Ö'
        ],
        'implies': {
            'A': ['Á'],
            'E': ['É'],
            'I': ['Í'],
            'O': ['Ó'],
            'U': ['Ú'],
            'Y': ['Ý'],
        },
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

# User customization
AUTH_USER_MODEL = 'core.User'

# Registration stuff
ACCOUNT_ACTIVATION_DAYS = 1

# Import customizable settings.
from poetcave.local_settings import *

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
    },
    # These are hard-coded because they will never change, and in fact will be
    # removed once the data has been imported.
    'old': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ljod_db',
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Terms and conditions
# See: https://django-termsandconditions.readthedocs.io/en/latest/#terms-and-conditions-middleware
ACCEPT_TERMS_PATH = '/terms/accept/'
TERMS_EXCLUDE_URL_PREFIX_LIST = ['/admin/']
TERMS_EXCLUDE_URL_LIST = [
    '/terms/reject/',
    '/terms/required/',
    '/user/delete/confirm/',
    '/user/logout/',
    '/user/retrieve-data/download/',
]
TERMS_EXCLUDE_URL_CONTAINS_LIST = []
