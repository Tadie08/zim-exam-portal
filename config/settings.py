from pathlib import Path

# 🔥 BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔥 SECURITY
SECRET_KEY = 'django-insecure-ww14(yvg$@u29sewpn(_i673x6qa*l(y-xjq7s^%*3&%k5wp&o'
DEBUG = True
ALLOWED_HOSTS = ['192.168.100.152', '127.0.0.1']

# 🔥 APPLICATIONS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    'core.apps.CoreConfig',   # 👈 your main app
]

# 🔥 MIDDLEWARE
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 🔥 URLS
ROOT_URLCONF = "config.urls"

# 🔥 TEMPLATES (IMPORTANT: points to the folder where your HTML files live)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],  # 👈 make sure this folder exists
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 🔥 WSGI
WSGI_APPLICATION = "config.wsgi.application"

# 🔥 DATABASE (default SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 🔥 PASSWORD VALIDATORS
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# 🔥 INTERNATIONALIZATION
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Harare"
USE_I18N = True
USE_TZ = True

# 🔥 STATIC FILES
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # optional: for custom static files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

X_FRAME_OPTIONS = 'SAMEORIGIN'

# 🔐AUTH REDIRECTS
LOGIN_REDIRECT_URL = '/profile/'  # Where to go after login
LOGIN_URL = '/login/'               # Where to redirect if @login_required fails
LOGOUT_REDIRECT_URL = '/'           # Where to go after logout

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Ensure cookies work
SESSION_COOKIE_SECURE = False  # True only for HTTPS
CSRF_COOKIE_SECURE = False     # True only for HTTPS

# Email settings for password reset
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For testing (prints to console)
# For production, use:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Paynow Settings
PAYNOW_INTEGRATION_ID = 'test-id'
PAYNOW_INTEGRATION_KEY = 'test-key'
PAYNOW_RESULT_URL = 'http://127.0.0.1:8000/payment/result/'
PAYNOW_RETURN_URL = 'http://127.0.0.1:8000/payment/return/'
