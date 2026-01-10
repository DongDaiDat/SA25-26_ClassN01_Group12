import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
    "django_filters",

    # shared & modules
    "modules.shared.apps.SharedConfig",
    "modules.identity_access",
    "modules.audit",
    "modules.program",
    "modules.course_catalog",
    "modules.term_scheduling",
    "modules.class_section",
    "modules.enrollment",
    "modules.assessment",
    "modules.certificate",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "modules.shared.middleware.RequestIDMiddleware",
    "modules.shared.middleware.ApiExceptionMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "tpms_core"),
        "USER": os.getenv("POSTGRES_USER", "tpms"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "tpms"),
        "HOST": os.getenv("POSTGRES_HOST", "postgres_core"),
        "PORT": int(os.getenv("POSTGRES_PORT", "5432")),
    }
}

AUTH_USER_MODEL = "identity_access.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Bangkok"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", str(BASE_DIR / "staticfiles"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "modules.shared.api.exception_handler",
    "DEFAULT_RENDERER_CLASSES": (
        "modules.shared.api.ApiRenderer",
    ),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "TPMS Core API",
    "DESCRIPTION": "Training Program Management System - Core API",
    "VERSION": "1.0.0",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "20"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s","request_id":"%(request_id)s"}'
        }
    },
    "filters": {
        "request_id": {"()": "modules.shared.logging.RequestIDLogFilter"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json", "filters": ["request_id"]},
    },
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
}

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

NOTIFICATION_CELERY_TASK = os.getenv("NOTIFICATION_CELERY_TASK", "notification.tasks.handle_event")

CELERY_BEAT_SCHEDULE = {
    'publish-outbox-every-5s': {
        'task': 'modules.shared.tasks.publish_outbox',
        'schedule': 5.0,
    },
}
