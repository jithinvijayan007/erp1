"""
Django settings for POS project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from corsheaders.defaults import default_headers
import datetime
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2po)^b19qga5lq@1oq@1=fwozihi4b_ef=ndm69)fs!5c^86*p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

HOSTNAME="http://196.168.0.18:8000"




LOYALTY_POINT=10 # LOYALTY POINTS FOR RS.1
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'aldjemy',
    'brands',
    'salary_struct',
    'job_position',
    'company',
    'url_check',
    'branch',
    'category',
    'groups',
    'userdetails',
    'products',
    'item_category',
    'item_group',
    'supplier',
    'dealer',
    'purchase',
    'customer',
    'invoice',
    'internal_stock',
    'branch_stock',
    'states',
    'enquiry',
    'coupon',
    'terms',
    'pricelist',
    'loyalty_card',
    'day_closure',
    'company_permissions',
    'stock_prediction',
    'add_combo',
    'receipt',
    'sales_return',
    'payment',
    'group_permissions',
    'case_closure',
    'sap_api',
    'ledger_details',
    'tool_settings',
    'accounts_map',
    'exchange_sales',
    'quotation',
    'department',
    'transaction',
    'ledger_report',
    'detailedmodelreport',
    'schema',
    'emi_report',
    'specialsales',
    'stock_transfer',
    'goods_return',
    'paytm_api',
    'hierarchy',
    'salary_components',
    'shift_schedule',
    'territory',
    'zone',
    'salary_process',
    'salary_advance',
    'attendance',
    'leave_management',
    'professional_tax',
    'location',
    'enquiry_mobile',
    'stock_app',
    'expenses',
    'source',
    'priority',
    'reminder',
    'staff_rewards',
    'staff_rewards2',
    'buy_back',
    'na_enquiry',
    'finance_enquiry',
    'adminsettings',
    'customer_rating'

]
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=30000),
    'JWT_ALLOW_REFRESH': True,
}

CORS_ORIGIN_WHITELIST = (
    'google.com',
    'hostname.example.com',
    'localhost:4201',
    'localhost:4200',
    'localhost:4000',
    '127.0.0.1:4200',
    '127.0.0.1:8002',
    '127.0.0.1:1234',
    '192.168.0.13:4321',
    '192.168.0.11:2000',
    '192.168.0.17:4200',
    '192.168.0.13',
    'localhost',
    '192.168.0.25:5000',
    '192.168.0.21:8000',
    '192.168.0.25:4200',
    '192.168.0.25:80',
    '192.168.0.25'
    '192.168.0.25:4200',
    'localhost:2000',
    'localhost:8000',
    '192.168.0.3:5555',

)
CORS_ALLOW_HEADERS = default_headers + (
    'version',
)
CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'userdetails.middleware.InsertUserLog'
]

ROOT_URLCONF = 'POS.urls'
STATIC_URL = '/static/'
STATIC_ROOT = 'static_root/'
STATICFILES_DIRS = [STATIC_DIR,]
MEDIA_ROOT = os.path.join(BASE_DIR, 'static_root/media')


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR,],
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

WSGI_APPLICATION = 'POS.wsgi.application'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.pepipost.com'
EMAIL_HOST_USER = 'testname'
EMAIL_HOST_EMAIL = 'info@test.com'
EMAIL_HOST_PASSWORD = 'Tdx@test'
EMAIL_PORT = 587
EMAIL_USE_SSL = False

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
if DEBUG:
    CHAT_URL = "http://127.0.0.1:2021/"
    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'oxygen_db',
                'USER': 'admin',
                'PASSWORD':'tms@123',
                'HOST': '127.0.0.1',
                # 'HOST':'192.168.0.114',
                'PORT': '5432',
            }
        }

if not DEBUG:
    CHAT_URL = "https://producttionurl:2020/"
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'test@gdot.in'
    EMAIL_HOST_EMAIL = 'test@gdot.in'
    EMAIL_HOST_PASSWORD = 'test@2014'

    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': '1test_pos_live2',
                'USER': 'admin',
                'PASSWORD':'uDS$CJ8j',
                'HOST': '127.0.0.1',
                # 'HOST':'192.168.0.114',
                'PORT': '5432',
            }
        }

    STATIC_ROOT = 'pos_static/'
    STATICFILES_DIRS = [STATIC_DIR,]
    MEDIA_ROOT = os.path.join(BASE_DIR, '../pos_static/media')
# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

TIME_ZONE =  'Asia/Kolkata'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [STATIC_DIR,]
