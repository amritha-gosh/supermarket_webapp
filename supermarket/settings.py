"""
Django settings for supermarket project.
"""
import os
SETUP_TOKEN = os.environ.get("SETUP_TOKEN")


from dotenv import load_dotenv
load_dotenv()

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-g30x1zon8u=e@fwv^j(#fa)u8^rt=b@gptu%5glzucns5*g6zx'
DEBUG = True
import os

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# Application definition
INSTALLED_APPS = [
    # Django
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',

    # Local apps
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'shop.middleware.store_required.StoreRequiredMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'supermarket.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # global templates dir (if needed)
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.global_vars',
                'shop.context_processors.selected_store',
            ],
        },
    },
]

WSGI_APPLICATION = 'supermarket.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",   # Top-level static directory
]
STATIC_ROOT = BASE_DIR / "staticfiles"   # For collectstatic

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Django Allauth
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Email backend (dev only; use SMTP in production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'your_email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your_app_password'
# EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = 'Supermarket <your_email@gmail.com>'



# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]
}

JAZZMIN_SETTINGS = {
    "site_title": "Spicexpress Admin",
    "site_header": "Spicexpress",
    "site_brand": "Spicexpress",
    "welcome_sign": "Welcome to Spicexpress Admin",
    "custom_css": "admin/css/custom.css",
    "copyright": "Spicexpress © 2024",

    # Top menu links
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
    {"name": "Dashboard", "url": "/admin/dashboard/", "permissions": ["auth.view_user"]},
        {"name": "Visit Site", "url": "/", "new_window": True},
    ],

    # Icons for models
    "icons": {
        "auth.user": "fa fa-user",
        "auth.group": "fa fa-users",
        "shop.Product": "fa fa-shopping-bag",
        "shop.Order": "fa fa-receipt",
        "shop.Category": "fa fa-list",
        "shop.Brand": "fa fa-tag",
        "shop.Banner": "fa fa-image",
        "shop.Review": "fa fa-star",
        "shop.Wishlist": "fa fa-heart",
        "shop.Address": "fa fa-map-marker-alt",
        "shop.DiscountCode": "fa fa-percent",
        "shop.NewsletterSubscriber": "fa fa-envelope",
    },

    # Order of appearance in sidebar
    "order_with_respect_to": [
        "shop.Category",
        "shop.Product",
        "shop.Brand",
        "shop.Banner",
        "shop.Order",
        "shop.OrderItem",
        "shop.Wishlist",
        "shop.DiscountCode",
        "shop.NewsletterSubscriber",
        "shop.Address",
        "shop.Review",
    ],

    "navigation_expanded": True,
    "site_logo": "logo.png",  # Your logo file in static/ folder
    "site_icon": "logo.png",  # Favicon, also in static/ (you can use .ico or .png)
    "use_google_fonts_cdn": True,
}
JAZZMIN_UI_TWEAKS = {
    "theme": "solar",  # try "lux", "flatly", "cosmo", etc. (lux = orange buttons)
    "dark_mode_theme": "solar",
    # Use custom colors for sidebar, navbar, buttons
    "navbar": "navbar-warning navbar-light",   # orange navbar
    "accent": "accent-warning",                # red highlights
    "sidebar": "sidebar-light-warning",        # light orange sidebar
    "button": "btn-warning",                   # orange buttons
}

# --- Store Locations for Spicexpress ---
STORE_LOCATIONS = [
    {
        "key": "wigan",
        "name": "Wigan",
        "lat": 53.552925,
        "lng": -2.627962,
        "radius_miles": 5,
        "email": "wigan@spicexpress.com",
    },
    {
        "key": "southport",
        "name": "Southport",
        "lat": 53.639413,
        "lng": -3.004943,
        "radius_miles": 5,
        "email": "southport@spicexpress.com",
    },
]

