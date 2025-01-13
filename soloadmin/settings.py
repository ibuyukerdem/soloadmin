import os
from datetime import timedelta
from pathlib import Path
from decouple import config
from django.core.exceptions import ImproperlyConfigured

# Ortam Ayarları
ENV = config('DJANGO_ENV', default='development')  # Varsayılan olarak "development"

# Dizin Ayarı
BASE_DIR = Path(__file__).resolve().parent.parent  # Projenin ana dizini

# Güvenlik Ayarları
SECRET_KEY = config('DJANGO_SECRET_KEY', default='unsafe-default-key')  # Güvenlik anahtarı
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)  # Debug modu
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='', cast=lambda v: [s.strip() for s in v.split(',')])
SECURE_SSL_REDIRECT = config('DJANGO_SECURE_SSL_REDIRECT', default=False, cast=bool)

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Ortam Değişkenine Göre Güvenlik Ayarları
if ENV == 'production':
    SECURE_HSTS_SECONDS = 31536000  # HSTS süresi (1 yıl)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Alt alan adlarında da HSTS zorlaması
    SECURE_HSTS_PRELOAD = True  # HSTS preload listesine dahil edilme
    SECURE_BROWSER_XSS_FILTER = True  # XSS koruma mekanizması etkin
    SECURE_CONTENT_TYPE_NOSNIFF = True  # MIME türü zorunlu doğrulama
    CSRF_COOKIE_SECURE = True  # CSRF çerezlerini yalnızca HTTPS üzerinden gönder
    SESSION_COOKIE_SECURE = True  # Oturum çerezlerini yalnızca HTTPS üzerinden gönder
    X_FRAME_OPTIONS = 'DENY'  # Sayfanın iframe ile başka bir sitede yüklenmesini engelle
    SECURE_REFERRER_POLICY = 'strict-origin'  # Referrer politikası
else:
    SECURE_HSTS_SECONDS = 0  # HSTS devre dışı
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_BROWSER_XSS_FILTER = False
    SECURE_CONTENT_TYPE_NOSNIFF = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    SECURE_REFERRER_POLICY = None

# Uygulama Tanımı
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
    'django_filters',
    'corsheaders',
    'axes',
    'django_recaptcha',
]

LOCAL_APPS = [
    'soloservice.apps.SoloserviceConfig',
    'solofinance.apps.SolofinanceConfig',
    'soloaccounting.apps.SoloaccountingConfig',
    'soloecommerce.apps.SoloecommerceConfig',
    'soloweb.apps.SolowebConfig',
    'solopayment.apps.SolopaymentConfig',
    'soloblog.apps.SoloblogConfig',
    'common.apps.CommonConfig',
    'solosurvey.apps.SolosurveyConfig',
    'solosite.apps.SolositeConfig',
    'accounts.apps.AccountsConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware Ayarları
SECURITY_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Güvenlik
    'corsheaders.middleware.CorsMiddleware',  # CORS desteği
    'django.contrib.sessions.middleware.SessionMiddleware',  # Oturum yönetimi
    'django.middleware.common.CommonMiddleware',  # Genel ayarlar
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF koruması
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Kimlik doğrulama
    'axes.middleware.AxesMiddleware',  # Axes lockout middleware
    'django.contrib.messages.middleware.MessageMiddleware',  # Mesaj yönetimi
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking koruması
]

CUSTOM_MIDDLEWARE = [
    # 'middleware.soloadmin.ip_blocking.BlockIPMiddleware',  # Özel engelleme
    # 'middleware.soloadmin.request_validator.ValidateRequestMiddleware',  # İstek doğrulama
    # 'middleware.soloadmin.cors_manager.DynamicCorsMiddleware',  # Dinamik CORS
    # 'middleware.soloadmin.global_rate_limit.GlobalRateLimitMiddleware',  # Global rate limit
    # 'middleware.soloadmin.site_management.SiteMiddleware',  # Site yönetimi
    'middleware.soloadmin.UserTimezone.UserTimezoneMiddleware',  # Time Zone Yönetimi
    # 'middleware.soloaccounting.recaptcha_admin.ReCaptchaAdminMiddleware',  # ReCaptcha admin
    'django.middleware.locale.LocaleMiddleware',
]

MIDDLEWARE = SECURITY_MIDDLEWARE + CUSTOM_MIDDLEWARE

if ENV == 'development':
    INSTALLED_APPS += ['debug_toolbar', 'django_extensions']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

    # Debug Toolbar Ayarları
    INTERNAL_IPS = ['127.0.0.1', '192.168.1.253']
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_CREDENTIALS = True

# Site Ayarı
SITE_ID = 3
ROOT_URLCONF = 'soloadmin.urls'

# CORS Ayarı
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)

# Şablon Ayarları
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "soloaccounting/templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'soloaccounting.context_processors.recaptcha_key',
            ],
        },
    },
]

WSGI_APPLICATION = 'soloadmin.wsgi.application'

# Veritabanı Ayarları
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

# Şifre Doğrulama
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Kimlik Doğrulama Backend'leri
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
# DRF ayarları
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.AllowAny',
    # ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',  # Sayfalama sınıfı
    'PAGE_SIZE': 20,  # Her sayfada kaç öğe olacağını belirtir
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

if ENV == 'production':
    # Üretim ortamı için Redis cache ayarları
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',  # Sunucunuzun Redis adresi ve db numarası
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # Geliştirme ortamı için yerel bellek cache ayarları
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-sample',
        }
    }

# Axes Ayarları
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address', 'user_agent']
AXES_VERBOSE = True
AXES_RESET_ON_SUCCESS = True
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'
AXES_FAILURE_LIMIT_PER_SITE = False

# Swagger Ayarları
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,  # Session Authentication devre dışı bırakıldı
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',  # API anahtarı olarak ayarlandı
            'name': 'Authorization',  # Header'da kullanılacak anahtar
            'in': 'header',  # Header'da gönderilecek
        },
    },
    'DEFAULT_INFO': 'soloadmin.api.urls',  # Projenizde API bilgilerini tanımlayın
    'LOGIN_URL': 'rest_framework:login',  # Eğer oturum açma sayfanız varsa
    'LOGOUT_URL': 'rest_framework:logout',
}
# Cache Ayarları
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Uluslararasılaşma Ayarları
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('tr', 'Türkçe'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('nl', 'Nederlands (Hollanda Felemenkçesi)'),
    ('ar', 'العربية'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Statik ve Medya Dosyaları
STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / 'soloaccounting' / 'static', ]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = config('STATIC_URL', default='static/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = config('MEDIA_URL', default='/media/')

# Varsayılan Otomatik Alan Tipi
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Admin Panel Ayarları
ADMIN_SITE_HEADER = "Solofor Yönetim Paneli"
ADMIN_SITE_TITLE = "Solofor Yönetim Paneli"
ADMIN_INDEX_TITLE = "Hoş Geldiniz! Solofor Yönetim Paneli"

# Kullanıcı Modeli
AUTH_USER_MODEL = 'common.CustomUser'

# reCAPTCHA v3 configuration (using your keys from .env)
RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY', default='').strip()
RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY', default='').strip()

# print("RECAPTCHA_PUBLIC_KEY:", RECAPTCHA_PUBLIC_KEY)
# print("RECAPTCHA_PRIVATE_KEY:", RECAPTCHA_PRIVATE_KEY)

# Check if reCAPTCHA keys are set
if not RECAPTCHA_PUBLIC_KEY or not RECAPTCHA_PRIVATE_KEY:
    raise ImproperlyConfigured("HATA: RECAPTCHA anahtarları ayarlanmamış.")

# reCAPTCHA settings to silence test key warnings (if using test keys)
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

# reCAPTCHA v3 score requirement
RECAPTCHA_REQUIRED_SCORE = 0.85

LOGIN_REDIRECT_URL = '/admin/'

ADMINS = [('Admin', 'ibrahim@solofor.com')]  # E-posta gönderilecek yöneticiler

SERVER_EMAIL = 'soloadmin@hortumcesitleri.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.hortumcesitleri.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = False
EMAIL_HOST_USER = 'soloadmin@hortumcesitleri.com'
EMAIL_HOST_PASSWORD = 'pPqGEghA4JNc31D'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '{asctime} - {levelname} - {message}'
            ),
            'style': '{',
        },
        'simple': {
            'format': '{levelname} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/actions.log',
            'when': 'D',
            'interval': 1,
            'backupCount': 7,  # 7 günlük yedek
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/error.log',
            'when': 'D',
            'interval': 1,
            'backupCount': 7,  # 7 günlük yedek
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
        'db_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/db.log',
            'when': 'D',
            'interval': 1,
            'backupCount': 7,  # 7 günlük yedek
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'common': {
            'handlers': ['console', 'file', 'error_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['db_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
