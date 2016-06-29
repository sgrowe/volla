import os
import re
import dj_database_url
from django.core.urlresolvers import reverse_lazy


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/


SECRET_KEY = 'p-zelz*2j$k-n6(b#i^1n4pnx53^zjw@)nln^+yr4o%h84#g#)'


DEBUG = os.environ.get('VOLLA_DEV') == 'TRUE'


ALLOWED_HOSTS = (
    'www.volla.co',
)

# Application definition


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'vollumes',
    'users',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
)


ROOT_URLCONF = 'Volla.urls'


WSGI_APPLICATION = 'Volla.wsgi.application'


template_loaders = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
if not DEBUG:
    template_loaders = (
        ('django.template.loaders.cached.Loader', template_loaders),
    )


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (),
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ),
            'loaders': template_loaders,
        },
    },
]


# Crispy forms
# http://django-crispy-forms.readthedocs.io/en/latest/index.html

# CRISPY_TEMPLATE_PACK = 'bootstrap3'

CRISPY_FAIL_SILENTLY = not DEBUG


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases


DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
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

# Use a custom user model

AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGIN_URL = reverse_lazy('login')


LOGIN_REDIRECT_URL = reverse_lazy('home')


# Static files


STATIC_URL = '/static/'


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Emails

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


SUPPORT_EMAIL = 'support@volla.co'


DEFAULT_FROM_EMAIL = SUPPORT_EMAIL


EMAIL_HOST = 'smtp.sparkpostmail.com'


EMAIL_HOST_USER = 'SMTP_Injection'


EMAIL_HOST_PASSWORD = '5c30e0406fae44e1f4bddfe3f580d91bde64862f'


EMAIL_PORT = 587


EMAIL_USE_TLS = True


# Logging


SERVER_EMAIL = 'errors@volla.co'


ADMINS = (
    ('Sam', 'sgrowe@live.co.uk'),
)


MANAGERS = ADMINS


IGNORABLE_404_URLS = (
    re.compile(r'\.(php|cgi)$'),
    re.compile(r'^/phpmyadmin/'),
)


INTERNAL_IPS = (
    '127.0.0.1',
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] pathname=%(pathname)s '
                       'lineno=%(lineno)s funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'volla': {
            'level': 'INFO',
            'handlers': ['console'],
        }
    },
}


# Caching


USE_ETAGS = True
