import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-change-this-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # For token rotation/blacklisting
    'django_filters',
    'corsheaders',
    'drf_spectacular',
    # Our apps
    'accounts',
    'products',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # CorsMiddleware MUST be before CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# DRF GLOBAL CONFIGURATION
# ============================================================
REST_FRAMEWORK = {
    # ── AUTHENTICATION ──
    # JWTAuthentication: reads "Authorization: Bearer <token>" header
    # SessionAuthentication: for browsable API login
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],

    # ── PERMISSIONS ──
    # IsAuthenticatedOrReadOnly: GET is public, write ops need auth
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],

    # ── FILTERING ──
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    # ── PAGINATION ──
    # Applied globally to all list views
    
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,


    # ── THROTTLING ──
    # AnonRateThrottle: limits anonymous (unauthenticated) requests
    # UserRateThrottle: limits authenticated user requests
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',       # Anon users: 30 requests/minute
        'user': '200/minute',      # Auth users: 200 requests/minute
        'products': '60/minute',   # Scoped throttle for products
        'orders': '30/minute',     # Scoped throttle for orders
    },

    # ── CUSTOM EXCEPTION HANDLER ──
    # Replaces DRF's default with our consistent error format
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',

    # ── SCHEMA (drf-spectacular) ──
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # ── RENDERERS ──
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],

    # ── VERSIONING ──
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'VERSION_PARAM': 'version',
}

# ============================================================
# JWT CONFIGURATION (djangorestframework-simplejwt)
# ============================================================
SIMPLE_JWT = {
    # Access token: short-lived (15 min) — used for API requests
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),

    # Refresh token: long-lived (7 days) — used to get new access tokens
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    # Rotate refresh tokens: each /token/refresh/ gives a NEW refresh token
    'ROTATE_REFRESH_TOKENS': True,

    # Blacklist used refresh tokens (prevents reuse)
    'BLACKLIST_AFTER_ROTATION': True,

    # Algorithm — RS256 is better for production; HS256 is simpler
    'ALGORITHM': 'HS256',

    # Signing key — uses Django SECRET_KEY for HS256
    'SIGNING_KEY': SECRET_KEY,

    # The header prefix — "Authorization: Bearer <token>"
    'AUTH_HEADER_TYPES': ('Bearer',),

    # Extra data added to token payload
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),

    # Token type claim in payload
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ============================================================
# CORS CONFIGURATION (django-cors-headers)
# ============================================================
# CORS_ALLOW_ALL_ORIGINS = True  # ← Development only, dangerous in production

# Whitelist specific origins for production
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',     # React dev server
    'http://localhost:5173',     # Vite dev server
    'http://127.0.0.1:5500',    # VS Code Live Server
    'http://localhost:8080',     # Vue dev server
]

# Allow these headers in cross-origin requests
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'x-csrftoken',
    'x-requested-with',
]

# Allow cookies to be sent with cross-origin requests
CORS_ALLOW_CREDENTIALS = True

# ============================================================
# drf-spectacular CONFIGURATION
# ============================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'E-Commerce Product API',
    'DESCRIPTION': 'Production-ready e-commerce REST API with JWT auth, filtering, pagination and more.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Auth', 'description': 'JWT Authentication endpoints'},
        {'name': 'Products', 'description': 'Product catalog management'},
        {'name': 'Orders', 'description': 'Order management'},
    ],
}