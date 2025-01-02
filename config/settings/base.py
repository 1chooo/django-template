"""Base settings to build other settings files upon."""

import json
import os
from pathlib import Path

import boto3
import environ
from botocore.exceptions import ClientError

from utils.logging import JsonFormatter

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent


DISABLE_DOT_ENV = os.environ.get("DISABLE_DOT_ENV", default=False)

if (ROOT_DIR / "dotenv" / ".env").exists():
    DOT_ENV_PATH = ROOT_DIR / "dotenv" / ".env"
else:
    DOT_ENV_PATH = ROOT_DIR / "dotenv" / ".env.local"

env = environ.Env()
if not DISABLE_DOT_ENV:
    env.read_env(DOT_ENV_PATH)

# General
# ------------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG", default=False)
# Local time zone
TIME_ZONE = "Asia/Taipei"
LANGUAGE_CODE = "en-us"
SITE_ID = 1
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [
    ROOT_DIR / "locale",
]
APPEND_SLASH = False
TRALLING_SLASH = True
SERVER_HOST = env("SERVER_HOST", default="127.0.0.1")
SERVER_PORT = env.int("SERVER_PORT", default=80)

# AWS
# ------------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = env("AWS_REGION_NAME")


# AWS S3
# ------------------------------------------------------------------------------
AWS_S3_ENABLED = env.bool("AWS_S3_ENABLED", default=False)
if AWS_S3_ENABLED:
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#authentication-settings
    AWS_S3_ACCESS_KEY_ID = env("AWS_S3_ACCESS_KEY_ID ", default=AWS_ACCESS_KEY_ID)
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#authentication-settings
    AWS_S3_SECRET_ACCESS_KEY = env("AWS_S3_SECRET_ACCESS_KEY", default=AWS_SECRET_ACCESS_KEY)
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default=AWS_REGION_NAME)
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

# AWS SES
# ------------------------------------------------------------------------------
AWS_SES_ACCESS_KEY_ID = env("AWS_SES_ACCESS_KEY_ID", default=AWS_ACCESS_KEY_ID)
AWS_SES_SECRET_ACCESS_KEY = env("AWS_SES_SECRET_ACCESS_KEY", default=AWS_SECRET_ACCESS_KEY)
AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME", default=AWS_REGION_NAME)
AWS_SES_REGION_ENDPOINT = env("AWS_SES_REGION_ENDPOINT", default=f"email.{AWS_SES_REGION_NAME}.amazonaws.com")

# Storage
# ------------------------------------------------------------------------------
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
# https://django-storages.readthedocs.io/en/1.5.2/backends/amazon-S3.html
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"


# Database
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SILENCED_SYSTEM_CHECKS = [
    # Allow index names >30 characters, because we are not using Oracle
    "models.E034",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("DATABASE_HOST"),
        "PORT": env("DATABASE_PORT"),
        "NAME": env("DATABASE_DB"),
    },
}
db_secret_name = env("DATABASE_SECRET_NAME", default=None)
if db_secret_name is not None:
    session = boto3.session.Session()  # type: ignore
    with session.client(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        service_name="secretsmanager",
        region_name=AWS_REGION_NAME,
    ) as client:
        try:
            get_secret_value_response = client.get_secret_value(SecretId=db_secret_name)
        except ClientError as e:
            raise e from e
        secret = json.loads(get_secret_value_response["SecretString"])
        DATABASES["default"]["USER"] = secret["username"]
        DATABASES["default"]["PASSWORD"] = secret["password"]

else:
    DATABASES["default"]["USER"] = env("DATABASE_USER")
    DATABASES["default"]["PASSWORD"] = env("DATABASE_PASSWORD")

# Cache
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/0"),
    "OPTIONS": {
        "CLIENT_CLASS": "django_redis.client.DefaultClient",
        "PARSER_CLASS": "redis.connection.HiredisParser",
    },
}

# Urls
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# Apps
# ------------------------------------------------------------------------------
APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "django_celery_beat",
    "django_celery_results",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_framework",
    "ninja",
    "ninja_extra",
    "corsheaders",
    "colorlog",
    "storages",
]
LOCAL_APPS = [
    "features.core",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = APPS + LOCAL_APPS

# Authentication
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#
AUTH_USER_MODEL = "core.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "token/login/"
LOGOUT_REDIRECT_URL = "admin/"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Middleware
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

if DEBUG:
    MIDDLEWARE += [
        "common.middlewares.APITimingMiddleware",
    ]

# Static
# ------------------------------------------------------------------------------

# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "static/"

if AWS_S3_ENABLED and env.bool("STATIC_USE_AWS_S3_STORAGE", default=False):
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    STORAGES["staticfiles"]["BACKEND"] = "utils.storage.StaticS3Storage"

    # https://docs.djangoproject.com/en/dev/ref/settings/#static-url
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
else:
    # https://docs.djangoproject.com/en/dev/ref/settings/#static-root
    STATIC_ROOT = ROOT_DIR / "static"

    # https://docs.djangoproject.com/en/dev/ref/settings/#static-url
    STATIC_URL = "static/"

# Media
# ------------------------------------------------------------------------------
if AWS_S3_ENABLED and env.bool("MEDIA_USE_AWS_S3_Storage", default=False):
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
    STORAGES["default"]["BACKEND"] = "storages.backends.s3.S3Storage"
    # https://docs.djangoproject.com/en/dev/ref/settings/#media-url
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    # https://docs.djangoproject.com/en/dev/ref/settings/#media-root
    MEDIA_ROOT = ROOT_DIR / "media"
    # https://docs.djangoproject.com/en/dev/ref/settings/#media-url
    MEDIA_URL = "media/"

# Template
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""FutureNest inc.""", "futurenest-inc.@example.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# https://cookiecutter-django.readthedocs.io/en/latest/settings.html#other-environment-settings
# Force the `admin` sign in process to go through the `django-allauth` workflow
DJANGO_ADMIN_FORCE_ALLAUTH = env("DJANGO_ADMIN_FORCE_ALLAUTH", default=False)

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
if DISABLE_DOT_ENV:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
            "uvicorn": {"format": "%(levelname)-8s - %(message)s"},
            "json": {"()": JsonFormatter},
        },
        "handlers": {
            "console": {"level": "CRITICAL", "class": "logging.StreamHandler", "formatter": "verbose"},
            "uvicorn_console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "json"},
        },
        "loggers": {
            "django": {"handlers": ["console"], "propagate": True},
            "uvicorn": {"handlers": ["uvicorn_console"], "propagate": True},
            "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
            "django.security.DisallowedHost": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        },
    }
elif os.name == "posix":
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
            "uvicorn": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(levelname)-8s%(blue)s - %(asctime)s - %(reset)s%(message)s",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            },
            "uvicorn_file": {"format": "%(levelname)-8s - %(asctime)s - %(message)s"},
        },
        "handlers": {
            "console": {"level": "CRITICAL", "class": "logging.StreamHandler", "formatter": "verbose"},
            "uvicorn_console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "uvicorn"},
        },
        "loggers": {
            "django": {"handlers": ["console"], "propagate": True},
            "uvicorn": {"handlers": ["uvicorn_console"], "propagate": True},
        },
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
            "uvicorn": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(levelname)-8s%(blue)s - %(asctime)s - %(reset)s%(message)s",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            },
            "json": {"()": JsonFormatter},
        },
        "handlers": {
            "console": {"level": "CRITICAL", "class": "logging.StreamHandler", "formatter": "verbose"},
            "uvicorn_console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "uvicorn"},
        },
        "loggers": {
            "django": {"handlers": ["console"], "propagate": True},
            "uvicorn": {"handlers": ["uvicorn_console"], "propagate": True},
        },
    }

# django-allauth
# ------------------------------------------------------------------------------
# https://docs.allauth.org/en/dev/account/configuration.html#configuration
ACCOUNT_USER_MODEL_USERNAME_FIELD = "name"
# https://docs.allauth.org/en/dev/account/configuration.html#configuration
ACCOUNT_EMAIL_REQUIRED = True
# https://docs.allauth.org/en/dev/account/configuration.html#configuration
ACCOUNT_USERNAME_REQUIRED = False
# https://docs.allauth.org/en/dev/account/configuration.html#configuration
ACCOUNT_USER_DISPLAY = "name"
# https://docs.allauth.org/en/dev/account/configuration.html#configuration
ACCOUNT_AUTHENTICATION_METHOD = "email"
# https://docs.allauth.org/en/dev/account/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
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
ACCOUNT_ADAPTER = "config.adapters.AccountAdapter"
LOGIN_REDIRECT_URL = "admin/"
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
            "openid",
            "https://www.googleapis.com/auth/calendar",
        ],
        "AUTH_PARAMS": {
            "access_type": "offline",
        },
        "OAUTH_PKCE_ENABLED": False,
        "FETCH_USERINFO": True,
    },
}
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_ADAPTER = "config.adapters.SocialAccountAdapter"
HEADLESS_ONLY = True
HEADLESS_ADAPTER = "config.adapters.HeadlessAdapter"

# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_FILTER_BACKENDS": ["rest_framework.filters.SearchFilter", "rest_framework.filters.OrderingFilter"],
}

# Cors
# ------------------------------------------------------------------------------
# https://github.com/adamchainz/django-cors-headers#setup
CORS_ALLOWED_ORIGINS = []
# https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"

# Celery
# ------------------------------------------------------------------------------
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = "Asia/Taipei"

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_URL = f"{env('RABBITMQ_PROTOCOL')}://{env('RABBITMQ_USER')}:{env('RABBITMQ_PASSWORD')}@{env('RABBITMQ_HOST')}:{env('RABBITMQ_PORT')}"
CELERY_RESULT_BACKEND = "django-db"
CELERY_TASK_RESULT_EXPIRES = None
CELERY_CACHE_BACKEND = "django-cache"

CELERY_TASK_TRACK_STARTED = True

CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_WORKER_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOSS = False
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Email
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = env("DJANGO_EMAIL_HOST", default="smtp.gmail.com")
# https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = env("DJANGO_EMAIL_USE_TLS", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = env("DJANGO_EMAIL_PORT", default=587)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = env("DJANGO_EMAIL_HOST_USER", default=None)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_HOST_PASSWORD", default=None)
