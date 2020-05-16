import os
import json

#with open('/etc/conf.json') as config_file:
#    config = json.load(config_file)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = config['SECRET_KEY']
SECRET_KEY = 's(n=govm%toe1tt5zr(^-768kt-0e3po3hhu7!6fg34bu+gbrl'

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = False
DEBUG = True

#ALLOWED_HOSTS = ["alimentos.pe","www.alimentos.pe"]
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'django.contrib.humanize',
    'main',
    'django.contrib.gis',
    'dashboard',
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

ROOT_URLCONF = 'mibodega.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'mibodega.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': { # user access and system stuff
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'mibodega',
        'USER': 'kplrm',
        'PASSWORD': 'color800',
	    'HOST': 'localhost',
        'PORT': '5432',
    },
#    'stores': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'store_data',
#        'USER': 'kplrm',
#        'PASSWORD': 'color800',
#	    'HOST': 'localhost',
#        'PORT': '5432',
#    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

#EMAIL_HOST = config['EMAIL_HOST']
#EMAIL_HOST_USER = config['EMAIL_USER']
#EMAIL_HOST_PASSWORD = config['EMAIL_PASSWORD']
#EMAIL_PORT = 465

EMAIL_HOST = 'smtp.zoho.eu'
EMAIL_HOST_USER = 'hola@alimentos.pe'
EMAIL_HOST_PASSWORD = 'C4mp30n123.'
EMAIL_PORT = 465


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS= False
EMAIL_USE_SSL= True
