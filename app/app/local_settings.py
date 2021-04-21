import os

# settings.pyの絶対パスを取って、親の親をBASE_DIRにしている
# settings.pyの親の親 = /path/to/projecthome/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v5n+o-2t6rk18xc_2s2-py#+c)uh)wjj6t_(1hmxi72co3)589'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tsugoukun',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'app/static')

DEBUG = True
