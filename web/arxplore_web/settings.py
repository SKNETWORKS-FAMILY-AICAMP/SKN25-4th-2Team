"""Django settings for arxplore_web project."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from arxplore_web.bootstrap import configure_environment

configure_environment()

from src.shared import build_django_postgres_database_config, get_settings


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"
APP_SETTINGS = get_settings()


SECRET_KEY = 'django-insecure-6-2%pdjwz^)7-yobk0p*md+=$@(0^d4k!3z!yfm*9#g!sqspvx'
DEBUG = True
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "5173")

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    f'http://localhost:{FRONTEND_PORT}',
    f'http://127.0.0.1:{FRONTEND_PORT}',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'papers',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'arxplore_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'arxplore_web.wsgi.application'

try:
    DATABASES = {
        'default': build_django_postgres_database_config(APP_SETTINGS),
    }
except ValueError as exc:
    raise ImproperlyConfigured(str(exc)) from exc

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

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    ('frontend', FRONTEND_DIST_DIR),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
