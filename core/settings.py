"""
Django konfiguratsiyasi.

Barcha maxfiy/muhitga bog'liq qiymatlar .env faylidan o'qiladi
(django-environ orqali) — hech qachon kodga hardcode qilinmaydi.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
)
# .env fayli loyiha ildizida (manage.py bilan bir qatorda) bo'lishi kerak
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-CHANGE-ME-IN-PRODUCTION")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])


# --- Application definition ---

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Loyiha app'lari
    "users",
    "catalog",
    "reading",
    "telegram_bot",
    "ai_assistant",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# --- Database (PostgreSQL) ---
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://library_user:library_pass@localhost:5432/smart_library",
    )
}


# --- Password validation ---

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Internationalization ---

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True


# --- Static & Media files ---
# Bosqich 2 da MEDIA fayllar (kitob PDF/audio) S3/MinIO'ga ko'chiriladi.
# Hozircha lokal diskda saqlanadi — kichik loyihalar uchun yetarli.

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Telegram Bot & AI sozlamalari (loyihaga xos) ---

BOT_TOKEN = env("BOT_TOKEN", default="")
BOT_USERNAME = env("BOT_USERNAME", default="SmartLibraryBot")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
CLAUDE_MODEL = env("CLAUDE_MODEL", default="claude-sonnet-4-6")

# Kitob fayllari (PDF/audio) saqlanadigan yopiq Telegram kanali.
# Botni shu kanalga ADMIN qilib qo'shish shart, aks holda kanal
# xabarlarini o'qiy olmaydi. Kanal ID'sini olish uchun: kanalga istalgan
# xabar yuboring, keyin botga forward qiling — bot javobida chat_id'ni ko'rsatadi
# (yoki @userinfobot / @getidsbot orqali oling; odatda -100 bilan boshlanadi).
STORAGE_CHANNEL_ID = env("STORAGE_CHANNEL_ID", default="")