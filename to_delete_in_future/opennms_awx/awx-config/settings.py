import os

# Disable K8s-specific features for Docker Compose
K8S_SERVICE_ACCOUNT_NAME = None
K8S_NAMESPACE = None
SECRETS_BACKEND = 'awx.secrets.backends.default.DefaultSecretsBackend'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'awx'),
        'USER': os.getenv('DATABASE_USER', 'awx'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'awxpass'),
        'HOST': os.getenv('DATABASE_HOST', 'awx-postgres'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}

# Redis Configuration
BROKER_URL = 'redis://{}:{}'.format(
    os.getenv('REDIS_HOST', 'awx-redis'),
    os.getenv('REDIS_PORT', '6379')
)

# Secret Key
SECRET_KEY = os.getenv('SECRET_KEY', 'awxsecret123456789012345678901234')

# Allowed Hosts
ALLOWED_HOSTS = ['*']

# Static and Media
STATIC_ROOT = '/var/lib/awx/public/static'
MEDIA_ROOT = '/var/lib/awx/projects'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Disable K8s-style secret IDs - use direct environment variables
REDHAT_PASSWORD = os.getenv('REDHAT_PASSWORD', '')
AUTH_LDAP_BIND_PASSWORD = os.getenv('AUTH_LDAP_BIND_PASSWORD', '')
