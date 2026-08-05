"""
Django settings for GestorONG project.
"""

import os
from pathlib import Path
import dj_database_url

# Directorio base
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de seguridad
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-h23vkq14r!ga7m@p^nky_9rz=wwb5ucr5j^x+s1(-7tao--kx1')

# Modificado para evitar errores de despliegue en producción
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GestorONG.urls'

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

WSGI_APPLICATION = 'GestorONG.wsgi.application'

# Base de datos (PostgreSQL en Render / SQLite local)
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Idioma y zona horaria
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'gestion' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Configuración de correo para notificaciones de Donantes y Voluntarios
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'jeniffer.chicaiza7566@utc.edu.ec'
EMAIL_HOST_PASSWORD = 'bvfi jkrk xfdj bihc'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Redirecciones
LOGIN_REDIRECT_URL = 'inicio'
LOGOUT_REDIRECT_URL = 'inicio'