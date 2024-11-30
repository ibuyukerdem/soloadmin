from pathlib import Path

from decouple import config

ENV = config('DJANGO_ENV', default='development')  # Varsayılan olarak development

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY', default='unsafe-default-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='', cast=lambda v: [s.strip() for s in v.split(',')])

SECURE_SSL_REDIRECT = config('DJANGO_SECURE_SSL_REDIRECT', default=False, cast=bool)

# Ortam değişkenine göre güvenlik ayarları
if ENV == 'production':  # Eğer ortam değişkeni "production" ise
    # Üretim ortamı için güvenlik ayarları
    SECURE_HSTS_SECONDS = 31536000  # HTTP Strict Transport Security (HSTS) için süre (1 yıl)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Alt alan adlarında da HSTS zorlaması
    SECURE_HSTS_PRELOAD = True  # Tarayıcıların HSTS preload listesine dahil edilmesi
    SECURE_BROWSER_XSS_FILTER = True  # Tarayıcının XSS koruma mekanizmasını etkinleştir
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Tarayıcıların MIME türünü zorunlu doğrulamasını sağla
    CSRF_COOKIE_SECURE = True  # CSRF çerezlerini yalnızca HTTPS üzerinden gönder
    SESSION_COOKIE_SECURE = True  # Oturum çerezlerini yalnızca HTTPS üzerinden gönder
    X_FRAME_OPTIONS = 'DENY'  # Sayfanın iframe ile başka bir sitede yüklenmesini engelle
    SECURE_REFERRER_POLICY = 'strict-origin'  # Tarayıcıların yalnızca güvenli origin bilgisi paylaşmasını sağla
else:  # Eğer ortam değişkeni "production" değilse (geliştirme ortamı)
    # Geliştirme ortamı için güvenlik ayarları
    SECURE_HSTS_SECONDS = 0  # HSTS devre dışı bırakılır
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # Alt alan adları için HSTS zorlanmaz
    SECURE_HSTS_PRELOAD = False  # HSTS preload devre dışı
    SECURE_BROWSER_XSS_FILTER = False  # XSS koruma mekanizması devre dışı
    SECURE_CONTENT_TYPE_NOSNIFF = False  # MIME türü doğrulaması yapılmaz
    CSRF_COOKIE_SECURE = False  # CSRF çerezlerini HTTP üzerinden de göndermeye izin ver
    SESSION_COOKIE_SECURE = False  # Oturum çerezlerini HTTP üzerinden de göndermeye izin ver
    X_FRAME_OPTIONS = 'SAMEORIGIN'  # Aynı origin içindeki iframe'lere izin ver
    SECURE_REFERRER_POLICY = None  # Referrer politikası yok (varsayılan tarayıcı davranışı)

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'drf_yasg',
    'rest_framework',
]

LOCAL_APPS = [
    'soloservice.apps.SoloserviceConfig',
    'solofinance.apps.SolofinanceConfig',
    'soloaccounting.apps.SoloaccountingConfig',
    'soloecommerce.apps.SoloecommerceConfig',
    'soloweb.apps.SolowebConfig',
    'solopayment.apps.SolopaymentConfig',
    'soloblog.apps.SoloblogConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SECURITY_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
]

CORE_MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

CUSTOM_MIDDLEWARE = [
    'soloadmin.SiteMiddleware.SiteMiddleware',
]

MIDDLEWARE = SECURITY_MIDDLEWARE + SESSION_MIDDLEWARE + CORE_MIDDLEWARE + CUSTOM_MIDDLEWARE
SITE_ID = 1
ROOT_URLCONF = 'soloadmin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,  # Bu True olmalı
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

WSGI_APPLICATION = 'soloadmin.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE'),
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER', default=''),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default=''),
        'PORT': config('DATABASE_PORT', default=''),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Geliştirme ortamında statik dosyaların nerede olduğunu belirtir.
STATICFILES_DIRS = [BASE_DIR / "static"]  # Proje içindeki statik dosyaların bulunduğu klasör

# Üretim ortamında tüm statik dosyaların toplandığı yer.
# `python manage.py collectstatic` komutuyla bu dizine taşınır.
STATIC_ROOT = BASE_DIR / "staticfiles"  # Statik dosyaların üretim için toplandığı dizin

# Statik dosyalara tarayıcı üzerinden erişim için kullanılan URL.
# Örneğin: 'https://example.com/static/' veya '/static/' olarak ayarlanabilir.
STATIC_URL = config('STATIC_URL', default='static/')  # Statik dosyaların URL yolu

# Kullanıcılar tarafından yüklenen dosyaların (ör. resimler, belgeler) kaydedileceği dizin.
MEDIA_ROOT = BASE_DIR / "media"  # Yüklenen dosyaların depolandığı yer

# Kullanıcılar tarafından yüklenen dosyaların tarayıcıdan erişim yolu.
# Örneğin: 'https://example.com/media/' veya '/media/' olarak ayarlanabilir.
MEDIA_URL = config('MEDIA_URL', default='/media/')  # Medya dosyalarının URL yolu

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMIN_SITE_HEADER = "Solofor Yönetim Paneli"
ADMIN_SITE_TITLE = "Solofor Yönetim Paneli"
ADMIN_INDEX_TITLE = "Hoş Geldiniz! Solofor Yönetim Paneli"

AUTH_USER_MODEL = 'soloaccounting.CustomUser'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,  # Varsayılan loglayıcıları devre dışı bırak
    'handlers': {
        'file': {
            'level': 'DEBUG',  # Minimum log seviyesi
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',  # Log dosyasının tam yolu
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],  # Sadece dosyaya log yaz
            'level': 'DEBUG',  # Minimum log seviyesi
            'propagate': False,  # Üst loglayıcılara iletmeyi durdur
        },
    },
}
