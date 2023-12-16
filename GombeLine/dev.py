from .settings import *
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-*p0hyn6s!)sxte2#2!uux-cra0n_c-r8r-e7r4e-clji%^xfrh" #env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*',]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': "ec2-174-129-100-198.compute-1.amazonaws.com",
        'NAME': "d30pi7sqc1vvrd", #"irmdb",
        'USER': "vmxbstkpfhbnss",#"admin",
        'PASSWORD': "089b684e43a8d014aae599b990479beb90b4828aa2a30cdb763fe8236f5de566",
        'CONN_MAX_AGE ': None,
        'PORT': "5432",
    }
}
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
# Actual directory user files go to
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')

# URL used to access the media
MEDIA_URL = '/media/'


# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
