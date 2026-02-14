# Security Best Practices

## Django Security Configuration

```python
# settings/production.py

# Security middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# HTTPS settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")

# XSS protection
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# CORS configuration
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
```

## JWT Security

```python
# settings.py
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Short-lived
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    # Security
    'AUTH_COOKIE_SECURE': True,
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_SAMESITE': 'Lax',
}
```

## Input Validation & Sanitization

```python
# validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import bleach

def validate_password_strength(password):
    """Validate password meets security requirements"""
    if len(password) < 12:
        raise ValidationError('Password must be at least 12 characters.')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain uppercase letter.')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain lowercase letter.')
    
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain number.')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain special character.')

def sanitize_html(content):
    """Sanitize HTML content"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li']
    allowed_attrs = {}
    
    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

def validate_file_extension(file):
    """Validate file type"""
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    ext = file.name.lower().split('.')[-1]
    
    if f'.{ext}' not in allowed_extensions:
        raise ValidationError(f'File type not allowed. Allowed: {allowed_extensions}')
    
    # Check file size (max 5MB)
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('File size must be under 5MB.')

# Serializer validation
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password_strength]
    )
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
    
    def validate_email(self, value):
        """Validate email domain"""
        blocked_domains = ['tempmail.com', '10minutemail.com']
        domain = value.split('@')[1].lower()
        
        if domain in blocked_domains:
            raise serializers.ValidationError('Disposable emails not allowed.')
        
        return value.lower()
    
    def create(self, validated_data):
        # Hash password properly
        user = User.objects.create_user(**validated_data)
        return user
```

## Rate Limiting

```python
# throttling.py
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AnonRateThrottle(AnonRateThrottle):
    rate = '10/minute'

class UserRateThrottle(UserRateThrottle):
    rate = '100/minute'

class BurstRateThrottle(UserRateThrottle):
    """For burst requests"""
    rate = '20/minute'

class SustainedRateThrottle(UserRateThrottle):
    """For sustained requests"""
    rate = '1000/day'

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'api.throttling.AnonRateThrottle',
        'api.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',
        'user': '100/minute',
        'burst': '20/minute',
        'sustained': '1000/day',
    }
}
```
