import os
from pathlib import Path
from datetime import timedelta
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 对应 Flask 的 SECRET_KEY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'a-strong-default-secret-key-replace-this') # 确保设置一个强密钥

DEBUG = True # 生产环境中应设为 False

ALLOWED_HOSTS = []


# Application definition
# 必须注册 Django-Rest-Framework, CORS 和我们的新应用
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    # 第三方库
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # 我们的应用
    'users.apps.UsersConfig',
    'chemicals.apps.ChemicalsConfig',
    'inventory.apps.InventoryConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # 添加 CORS 中间件
    'corsheaders.middleware.CorsMiddleware', 
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aoxinbs_django.urls'

# 迁移 Flask-CORS 配置
CORS_ALLOW_ALL_ORIGINS = True # 对应 CORS(app, resources={r"/api/*": {"origins": "*"}})


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

WSGI_APPLICATION = 'aoxinbs_django.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lab_chemical_db',
        'USER': 'root',
        'PASSWORD': '666666',
        'HOST': 'localhost',
        'PORT': '3307',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# 扩展 Django 默认 User 模型 (在 users/models.py 中定义)
AUTH_USER_MODEL = 'users.CustomUser'

# 迁移邮件配置 (用于密码重置)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
# EMAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
# EMAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
# EMAIL_HOST_USER = os.environ.get('MAIL_USERNAME', 'qjlgghenshuai@gmail.com')
# EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PASSWORD', 'ysdg eapx evwc xmgj')
# DEFAULT_FROM_EMAIL = os.environ.get('MAIL_DEFAULT_SENDER', 'qjlgghenshuai@gmail.com')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('MAIL_SERVER', 'smtp.zoho.com.cn')
EMAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('MAIL_USERNAME', 'ax2437525578@zohomail.cn')
EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PASSWORD', '9c0zjQw89xaj')
DEFAULT_FROM_EMAIL = os.environ.get('MAIL_DEFAULT_SENDER', 'ax2437525578@zohomail.cn')
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),

}