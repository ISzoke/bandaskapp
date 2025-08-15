# BandaskApp - Technical Requirements

## System Requirements

### Hardware Requirements
- **Raspberry Pi**: Model 3B+ or 4B (recommended)
- **RAM**: Minimum 2GB, recommended 4GB
- **Storage**: Minimum 16GB SD card, recommended 32GB
- **Network**: Ethernet or WiFi connection
- **Display**: 10" touch display with HDMI connection
- **Unipi1.1**: Hardware interface module
- **Temperature Sensors**: DS18B20 sensors (3 required)
- **Relays**: Digital output relays (3 required)

### Software Requirements
- **Operating System**: Raspberry Pi OS (Bullseye or newer)
- **Python**: Version 3.9 or higher
- **Django**: Version 4.2 or higher
- **Database**: SQLite (development), PostgreSQL (production optional)
- **Web Server**: Django development server (dev), Gunicorn (production)
- **Browser**: Chromium in kiosk mode

## Python Dependencies

### Core Dependencies
```txt
# requirements.txt
Django>=4.2.0,<5.0.0
requests>=2.28.0
python-dateutil>=2.8.0
django-crispy-forms>=2.0
crispy-bootstrap5>=0.7
django-background-tasks>=1.2.5
psutil>=5.9.0
```

### Development Dependencies
```txt
# requirements-dev.txt
-r requirements.txt
pytest>=7.0.0
pytest-django>=4.5.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
pre-commit>=3.0.0
```

### Optional Dependencies
```txt
# requirements-optional.txt
gunicorn>=20.1.0
whitenoise>=6.5.0
django-debug-toolbar>=4.0.0
django-extensions>=3.2.0
```

## Environment Setup

### Conda Environment
```bash
# Create conda environment
conda create -n bandaskapp python=3.9
conda activate bandaskapp

# Install dependencies
pip install -r requirements.txt
```

### Virtual Environment (Alternative)
```bash
# Create virtual environment
python3.9 -m venv bandaskapp_env
source bandaskapp_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
```bash
# .env file
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EVOK_BASE_URL=http://127.0.0.1:8080
HARDWARE_MODE=simulator
UPDATE_INTERVAL=10
DATA_RETENTION_DAYS=7
SWITCH_COOLDOWN_TIME_FURNACE=30
SWITCH_COOLDOWN_TIME_PUMP=5
```

## Django Configuration

### Settings Structure
```python
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'background_task',
    'core',
    'hardware',
]

# BandaskApp specific configuration
BANDASKAPP_CONFIG = {
    'HARDWARE_MODE': os.getenv('HARDWARE_MODE', 'simulator'),
    'EVOK_BASE_URL': os.getenv('EVOK_BASE_URL', 'http://127.0.0.1:8080'),
    'UPDATE_INTERVAL': int(os.getenv('UPDATE_INTERVAL', 10)),
    'TEMPERATURE_THRESHOLDS': {
        'dhw_low': 45.0,
        'dhw_high': 60.0,
        'hhw_low': 40.0,
        'hhw_high': 50.0,
        'pve_max': 80.0,
    },
    'SENSOR_CIRCUITS': {
        'dhw_1': '2895DCD509000035',
        'hhw_1': '2895DCD509000036',
        'hhw_5': '2895DCD509000037',
    },
    'RELAY_CIRCUITS': {
        'furnace': '1_01',
        'heating_pump': '1_02',
        'pve_heater': '1_03',
    }
}
```

## Database Configuration

### Development (SQLite)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Production (PostgreSQL - Optional)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'bandaskapp'),
        'USER': os.getenv('DB_USER', 'bandaskapp'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

## Static Files Configuration

### Development
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

### Production
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## Logging Configuration

### Development Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'bandaskapp.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'bandaskapp': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## Deployment Configuration

### Systemd Service
```ini
# /etc/systemd/system/bandaskapp.service
[Unit]
Description=BandaskApp Django Application
After=evok.service
Wants=evok.service

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/BandaskApp
Environment=PATH=/home/pi/miniconda3/envs/bandaskapp/bin
ExecStartPre=/bin/sleep 10
ExecStart=/home/pi/miniconda3/envs/bandaskapp/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Kiosk Mode Setup
```bash
# /etc/xdg/lxsession/LXDE-pi/autostart
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash
@chromium-browser --kiosk --disable-web-security --user-data-dir=/tmp/chrome-kiosk http://localhost:8000
```

### Production with Gunicorn
```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

## Security Configuration

### Django Security Settings
```python
# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS settings (if using HTTPS)
SECURE_SSL_REDIRECT = False  # Set to True if using HTTPS
SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
CSRF_COOKIE_SECURE = False  # Set to True if using HTTPS
```

### Network Security
- **Firewall**: Configure ufw to allow only necessary ports
- **SSH**: Disable root login, use key-based authentication
- **Updates**: Regular system updates and security patches
- **Monitoring**: Log monitoring and intrusion detection

## Performance Configuration

### Database Optimization
```python
# Database optimization settings
DATABASES = {
    'default': {
        # ... existing config ...
        'OPTIONS': {
            'timeout': 20,
            'check_same_thread': False,
        },
    }
}
```

### Caching Configuration
```python
# Simple memory cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Static Files Optimization
```python
# Static files optimization
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Compression
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.rCSSMinFilter']
```

## Testing Configuration

### Test Settings
```python
# test_settings.py
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable background tasks during testing
BACKGROUND_TASK_RUN_ASYNC = False
```

### Test Configuration
```ini
# pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = bandaskapp.test_settings
python_files = tests.py test_*.py *_tests.py
addopts = --nomigrations --tb=short
```

## Monitoring and Maintenance

### Health Checks
- **Application Health**: `/health/` endpoint
- **Database Health**: Database connection monitoring
- **Hardware Health**: Sensor and relay status monitoring
- **System Resources**: CPU, memory, and disk usage monitoring

### Backup Configuration
```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/home/pi/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Database backup
python manage.py dumpdata > $BACKUP_DIR/db_backup_$DATE.json

# TSV files backup
tar -czf $BACKUP_DIR/tsv_backup_$DATE.tar.gz data/tsv/

# Logs backup
tar -czf $BACKUP_DIR/logs_backup_$DATE.tar.gz logs/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.json" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Log Rotation
```ini
# /etc/logrotate.d/bandaskapp
/home/pi/BandaskApp/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 pi pi
}
```
