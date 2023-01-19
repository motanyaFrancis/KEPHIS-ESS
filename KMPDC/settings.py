from pathlib import Path
import os
from decouple import config
from requests import Session
from zeep import Client
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = ['.localhost','.127.0.0.1','.20.127.107.47','.essportal.kobby.co.ke']

DEBUG = True

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': '',
        }

    }

# Application definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard',
    'bootstrap5',
    'HR',
    'Finance',
    'Procurement',
    'Approvals',
    'accounts',
    'advance',
    'fleet',
    'roombooking',
    'Appraisals',
    'myRequest',

]

ASGI_APPLICATION = "KMPDC.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'KMPDC.urls'

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

WSGI_APPLICATION = 'KMPDC.wsgi.application'

FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler"]


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
MEDIA_URL = '/images/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
MEDIA_ROOT = os.path.join(BASE_DIR, 'images')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTHS = Session()


WEB_SERVICE_UID = config('WEB_SERVICE_UID')
WEB_SERVICE_PWD = config('WEB_SERVICE_PWD')

O_DATA = "http://20.231.15.166:7048/BC140/ODataV4/Company('CRONUS%20International%20Ltd.'){}"
BASE_URL = 'http://20.231.15.166:7047/BC140/WS/CRONUS%20International%20Ltd./Codeunit/Employee_Self_Service'
AUTHS.auth = HTTPBasicAuth(WEB_SERVICE_UID, WEB_SERVICE_PWD) #type:ignore
CLIENT = Client(BASE_URL, transport=Transport(session=AUTHS))
AUTHS = HTTPBasicAuth(WEB_SERVICE_UID, WEB_SERVICE_PWD) #type:ignore
