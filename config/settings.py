
import os
from pathlib import Path
from urllib.parse import urlparse, unquote
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-me-before-deploying')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv(
        'ALLOWED_HOSTS',
        '127.0.0.1,localhost,testserver,sharespace-lilac.vercel.app'
    ).split(',')
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    u.strip()
    for u in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if u.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "accounts",
    "core",
    "resources",
    "bookings",
    "operations",
    "notifications",
    "audit",
]
