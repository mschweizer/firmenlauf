"""
Development settings for firmenlauf project.

These settings are used for local development.
"""

import os

from .base import *  # noqa
from .base import BASE_DIR  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
# In development, we use a default key if not provided in environment
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-=1kxvkqw)k&=r(d9n13cev**$yqh&!bxms_a$231bzhy+1508n"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
