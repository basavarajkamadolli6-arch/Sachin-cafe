import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/'.env')
SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','dev-only-change-me-before-deployment')
DEBUG=os.getenv('DJANGO_DEBUG','False').lower()=='true'
ALLOWED_HOSTS=[s.strip() for s in os.getenv('DJANGO_ALLOWED_HOSTS','127.0.0.1,localhost').split(',') if s.strip()]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','cafe']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','cafe.context.cart_count']}}]
WSGI_APPLICATION='config.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'
TIME_ZONE='Asia/Kolkata'
USE_I18N=True
USE_TZ=True
STATIC_URL='static/'
STATICFILES_DIRS=[BASE_DIR/'static']
STATIC_ROOT=BASE_DIR/'staticfiles'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_REDIRECT_URL='menu'
LOGOUT_REDIRECT_URL='home'
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=False
SECURE_CONTENT_TYPE_NOSNIFF=True
CAFE_ADDRESS=os.getenv('CAFE_ADDRESS','Haveri, Karnataka, India')
