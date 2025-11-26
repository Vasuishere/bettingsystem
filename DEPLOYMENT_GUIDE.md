# 🚀 Complete Deployment Guide: Django Betting System on Google Cloud VM

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Google Cloud VM Setup](#google-cloud-vm-setup)
3. [Server Configuration](#server-configuration)
4. [Application Deployment](#application-deployment)
5. [Database Setup (Aiven PostgreSQL)](#database-setup)
6. [Nginx & SSL Configuration](#nginx--ssl-configuration)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Local Requirements
- Google Cloud Account with billing enabled
- SSH client (PuTTY for Windows or built-in terminal)
- Your project files ready
- Basic understanding of Django

### What You'll Deploy
- Django Application (Port 8000 → Nginx → 80/443)
- Gunicorn WSGI Server (4 workers)
- Nginx Web Server (Reverse Proxy)
- Google Cloud SQL PostgreSQL (Managed Database)
- Redis (for caching)
- SSL Certificate (Let's Encrypt)

---

## 1. Google Cloud VM Setup

### Step 1: Create VM Instance

1. **Go to Google Cloud Console**
   - Navigate to: https://console.cloud.google.com
   - Go to: Compute Engine → VM Instances

2. **Click "CREATE INSTANCE"**

3. **Configure Instance**:
   ```
   Name: betting-server
   Region: us-central1 (or closest to your users)
   Zone: us-central1-a
   
   Machine Configuration:
   - Series: E2
   - Machine type: e2-micro (2 vCPU shared, 1 GB memory)
     * Perfect for 5 users - costs only ~$6/month!
     * Upgrade to e2-small if needed later
   
   Boot Disk:
   - Operating System: Ubuntu
   - Version: Ubuntu 22.04 LTS
   - Boot disk type: SSD persistent disk (FASTER!)
   - Size: 10 GB (sufficient for 5 users)
   
   Firewall:
   ✅ Allow HTTP traffic
   ✅ Allow HTTPS traffic
   ```

4. **Click "CREATE"**

### Step 2: Configure Firewall Rules

1. **Go to VPC Network → Firewall**

2. **Create rule for Django (if needed for testing)**:
   ```
   Name: allow-django-8000
   Direction: Ingress
   Targets: All instances
   Source IP ranges: 0.0.0.0/0
   Protocols and ports: tcp:8000
   ```

3. **SSH Access** (already configured by default on port 22)

### Step 3: Reserve Static IP (Recommended)

1. **Go to VPC Network → External IP addresses**
2. **Click on your VM's IP address**
3. **Change Type from "Ephemeral" to "Static"**
4. **Give it a name**: `betting-static-ip`
5. **Save**

---

## 2. Server Configuration

### Step 1: Connect to VM

**Option A: Via Google Cloud Console**
```bash
# Click "SSH" button next to your VM instance
```

**Option B: Via Local Terminal**
```bash
gcloud compute ssh betting-server --zone=us-central1-a
```

**Option C: Via SSH Key**
```bash
ssh -i ~/.ssh/google_compute_engine username@YOUR_VM_EXTERNAL_IP
```

### Step 2: Update System

```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y build-essential git curl wget vim
```

### Step 3: Install Python & Dependencies

```bash
# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install pip
sudo apt install -y python3-pip

# Install PostgreSQL client
sudo apt install -y postgresql-client libpq-dev

# Install Nginx
sudo apt install -y nginx

# Install Redis
sudo apt install -y redis-server

# Install Supervisor (process manager)
sudo apt install -y supervisor

# Install Certbot (for SSL)
sudo apt install -y certbot python3-certbot-nginx
```

### Step 4: Create Application User

```bash
# Create dedicated user for the application
sudo useradd -m -s /bin/bash djangoapp

# Set password (optional)
sudo passwd djangoapp

# Add to www-data group
sudo usermod -aG www-data djangoapp
```

---

## 3. Application Deployment

### Step 1: Upload Your Application

**Option A: Via Git (Recommended)**
```bash
# Switch to djangoapp user
sudo su - djangoapp

# Clone repository
git clone https://github.com/Vasuishere/bettingsystem.git
cd bettingsystem

# Or if private repo:
git clone https://<token>@github.com/Vasuishere/bettingsystem.git
```

**Option B: Via SCP (from your local machine)**
```bash
# From local Windows PowerShell:
scp -r C:\Users\risha\Documents\vasu\bett username@VM_IP:/home/djangoapp/
```

**Option C: Via Google Cloud Storage**
```bash
# From local machine:
gsutil -m cp -r C:\Users\risha\Documents\vasu\bett gs://your-bucket/
# Then on VM:
gsutil -m cp -r gs://your-bucket/bett /home/djangoapp/
```

### Step 2: Setup Virtual Environment

```bash
# As djangoapp user
cd /home/djangoapp/bettingsystem

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install production servers
pip install gunicorn
pip install gevent  # For async workers
```

### Step 3: Configure Environment Variables

```bash
# Create .env file
nano /home/djangoapp/bettingsystem/.env
```

**Add the following** (replace with your actual values):
```env
# Django Settings
SECRET_KEY='your-super-secret-key-here-generate-new-one'
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR_VM_IP

# Database Configuration (Google Cloud SQL)
DB_NAME=betting_db
DB_USER=betting_user
DB_PASSWORD=your-strong-password
DB_HOST=127.0.0.1  # If using Cloud SQL Proxy
# DB_HOST=34.x.x.x  # Or use public IP directly
# DB_HOST=10.x.x.x  # Or use private IP if VPC configured
DB_PORT=5432

# Cloud SQL Connection (if using proxy)
CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Performance - SPEED OPTIMIZATIONS
CONN_MAX_AGE=3600  # Keep connections alive longer for instant queries

# Redis Cache (local) - AGGRESSIVE CACHING FOR SPEED
REDIS_URL=redis://127.0.0.1:6379/0
CACHE_TTL=3600  # Cache for 1 hour
CACHE_MIDDLEWARE=True
```

**Generate a new SECRET_KEY**:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 4: Update Django Settings

Edit `mymainserver/settings.py`:

```python
# Add to settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'CONN_MAX_AGE': int(os.getenv('CONN_MAX_AGE', 600)),
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}       'CONN_MAX_AGE': int(os.getenv('CONN_MAX_AGE', 600)),
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] if os.path.exists(os.path.join(BASE_DIR, 'static')) else []

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Caching with Redis - ULTRA-FAST CONFIGURATION
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'betting',
        'TIMEOUT': 3600,  # 1 hour default
    }
}

# Session in cache for instant loading
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours

# Cache middleware for automatic page caching
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # First
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # Last
    # ... other middleware ...
]

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300  # Cache pages for 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'betting_page'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/djangoapp/bettingsystem/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### Step 5: Prepare Application

```bash
# As djangoapp user with venv activated
cd /home/djangoapp/bettingsystem

# Create logs directory
mkdir -p logs

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
# Or use the auto command:
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@betting.com \
DJANGO_SUPERUSER_PASSWORD=admin123 \
python manage.py createsuperuser_auto

# Test if application runs
python manage.py runserver 0.0.0.0:8000
# Press Ctrl+C to stop
```

---

## 4. Database Setup (Google Cloud SQL PostgreSQL)

### Step 1: Create Cloud SQL Instance

1. **Go to Google Cloud Console**
   - Navigate to: SQL → Create Instance → Choose PostgreSQL

2. **Configure Database**:
   ```
   Instance ID: betting-db
   Password: [Set a strong password]
   Database version: PostgreSQL 15
   
   Configuration:
   - Region: Same as your VM (e.g., us-central1)
   - Zonal availability: Single zone
   - Machine type: db-f1-micro (FASTEST for small apps!)
     * Shared core, perfect for 5 users
     * Includes 3062 MB RAM
     * Built-in caching for instant queries
   
   Storage:
   - Storage type: SSD (ESSENTIAL for speed!)
   - Storage capacity: 10 GB (more than enough)
   - ✅ Enable automatic storage increases
   - ✅ Enable high availability: NO (saves cost, 5 users don't need it)
   
   Connections:
   - ✅ Private IP (FASTEST - no internet latency!)
   - ⚠️ Public IP: Only if needed for external access
   - Choose Private IP for maximum speed
   
   Data Protection:
   - ✅ Automated backups
   - Backup window: Choose off-peak hours
   ```

3. **Click "CREATE INSTANCE"** (takes 5-10 minutes)

### Step 2: Configure Database Access

**Option A: Using Public IP (Quick Setup)**

1. **Add Authorized Network**:
   - Go to your Cloud SQL instance
   - Click "Connections" → "Networking"
   - Under "Authorized networks", click "Add network"
   - Name: `vm-access`
   - Network: `YOUR_VM_EXTERNAL_IP/32`
   - Save

2. **Create Database and User**:
   ```bash
   # From Google Cloud Console, go to Cloud SQL → Databases
   # Click "Create Database"
   Database name: betting_db
   
   # Go to Users → Create User Account
   Username: betting_user
   Password: [Set strong password]
   ```

**Option B: Using Private IP (More Secure)**

1. **Setup VPC Peering**:
   - Cloud SQL automatically handles this
   - Your VM can access via private IP (10.x.x.x)
   - No need to authorize networks

2. **Get Connection Details**:
   ```bash
   # From Cloud SQL instance page:
   Private IP: 10.x.x.x (shown in Overview)
   Public IP: 34.x.x.x (if enabled)
   ```

### Step 3: Connect from VM

**Install Cloud SQL Proxy (Recommended for Production)**:

```bash
# Download Cloud SQL Proxy
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy

# Make executable
chmod +x cloud_sql_proxy

# Move to system path
sudo mv cloud_sql_proxy /usr/local/bin/

# Get connection name from Cloud SQL instance page
# Format: PROJECT_ID:REGION:INSTANCE_NAME
# Example: my-project:us-central1:betting-db

# Start proxy (replace with your connection name)
cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432 &

# Now connect via localhost:5432
psql -h 127.0.0.1 -U betting_user -d betting_db
```

**Or Connect Directly via IP**:

```bash
# Using public IP
psql -h PUBLIC_IP -U betting_user -d betting_db

# Using private IP (if VPC configured)
psql -h PRIVATE_IP -U betting_user -d betting_db

# Test connection
\dt  # List tables (empty initially)
\q   # Exit
```

### Database Optimization

Add these indexes for better performance:

```bash
# Connect to database
python manage.py dbshell
```

```sql
-- Add indexes for frequent queries
CREATE INDEX IF NOT EXISTS idx_bet_user_bazar_date ON userbaseapp_bet(user_id, bazar, bet_date);
CREATE INDEX IF NOT EXISTS idx_bet_created ON userbaseapp_bet(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bulk_user_date ON userbaseapp_bulkbetaction(user_id, action_date DESC);

-- Analyze tables for query optimization
ANALYZE userbaseapp_bet;
ANALYZE userbaseapp_bulkbetaction;
ANALYZE userbaseapp_customuser;
```

---

## 5. Nginx & SSL Configuration

### Step 1: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/betting
```

**Add this configuration**:
```nginx
upstream betting_app {
    server unix:/home/djangoapp/bettingsystem/gunicorn.sock fail_timeout=0;
    keepalive 32;  # Keep connections alive for speed
}

# Cache zone for ultra-fast loading
proxy_cache_path /var/cache/nginx/betting levels=1:2 keys_zone=betting_cache:10m max_size=100m inactive=60m use_temp_path=off;

server {
    listen 80;
    server_name your-domain.com www.your-domain.com YOUR_VM_IP;

    client_max_body_size 10M;

    # Logs
    access_log /var/log/nginx/betting_access.log;
    error_log /var/log/nginx/betting_error.log;

    # Static files - AGGRESSIVE CACHING
    location /static/ {
        alias /home/djangoapp/bettingsystem/staticfiles/;
        expires 365d;  # Cache for 1 year!
        add_header Cache-Control "public, immutable";
        add_header X-Cache-Status $upstream_cache_status;
        
        # Gzip compression for speed
        gzip on;
        gzip_static on;
        gzip_vary on;
        gzip_comp_level 9;
    }

    # Media files - LONG CACHE
    location /media/ {
        alias /home/djangoapp/bettingsystem/media/;
        expires 90d;  # Cache for 3 months
        add_header Cache-Control "public";
    }

    # Main application - WITH CACHING FOR SPEED
    location / {
        proxy_pass http://betting_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # HTTP/1.1 for keepalive
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        
        # Caching for instant page loads
        proxy_cache betting_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        proxy_cache_background_update on;
        proxy_cache_lock on;
        add_header X-Cache-Status $upstream_cache_status;
        
        # Fast timeouts
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Buffering for speed
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

### Step 2: Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/betting /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Step 3: Setup SSL (Let's Encrypt)

```bash
# Install SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (recommended)

# Certbot will automatically update Nginx config

# Test SSL renewal
sudo certbot renew --dry-run
```

---

## 6. Gunicorn Configuration

### Step 1: Create Gunicorn Config

```bash
# Create config file
nano /home/djangoapp/bettingsystem/gunicorn_config.py
```

**Add this content**:
```python
import multiprocessing

# Socket
bind = 'unix:/home/djangoapp/bettingsystem/gunicorn.sock'

# Workers - OPTIMIZED FOR SPEED (5 users)
workers = 2  # 2 workers perfect for 5 users - faster startup
worker_class = 'gevent'  # Async for instant response
worker_connections = 100  # Lower = faster for small load
max_requests = 5000  # Higher = less restarts = faster
max_requests_jitter = 100
preload_app = True  # Preload for instant response

# Timeouts - OPTIMIZED FOR SPEED
timeout = 30  # Lower timeout = faster failure recovery
keepalive = 10  # Higher keepalive = reuse connections = faster
graceful_timeout = 15

# Logging
accesslog = '/home/djangoapp/bettingsystem/logs/gunicorn_access.log'
errorlog = '/home/djangoapp/bettingsystem/logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'betting_gunicorn'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
pidfile = '/home/djangoapp/bettingsystem/gunicorn.pid'
umask = 0o007
user = 'djangoapp'
group = 'www-data'
```

### Step 2: Create Supervisor Configuration

```bash
# Create supervisor config
sudo nano /etc/supervisor/conf.d/betting.conf
```

**Add this content**:
```ini
[program:betting]
command=/home/djangoapp/bettingsystem/venv/bin/gunicorn -c /home/djangoapp/bettingsystem/gunicorn_config.py mymainserver.wsgi:application
directory=/home/djangoapp/bettingsystem
user=djangoapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/djangoapp/bettingsystem/logs/supervisor.log
environment=PATH="/home/djangoapp/bettingsystem/venv/bin"
```

### Step 3: Start Application

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start application
sudo supervisorctl start betting

# Check status
sudo supervisorctl status betting

# View logs
sudo tail -f /home/djangoapp/bettingsystem/logs/supervisor.log
```

### Management Commands

```bash
# Stop application
sudo supervisorctl stop betting

# Restart application
sudo supervisorctl restart betting

# View status
sudo supervisorctl status

# Restart Nginx
sudo systemctl restart nginx
```

---

## 7. Performance Optimization

### Database Connection Pooling

Install pgbouncer:
```bash
sudo apt install -y pgbouncer

# Configure pgbouncer
sudo nano /etc/pgbouncer/pgbouncer.ini
```

```ini
[databases]
betting = host=pg-2bb12e2b-vasuishere.h.aivencloud.com port=12345 dbname=defaultdb

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 100
default_pool_size = 25
```

### Redis Optimization

```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf
```

```conf
# Speed optimizations for 5 users
maxmemory 128mb  # Plenty for 5 users
maxmemory-policy allkeys-lru
save ""  # Disable disk writes for speed
appendonly no  # No persistence = faster

# Network optimizations
tcp-backlog 511
timeout 300
tcp-keepalive 60

# Performance
loglevel warning  # Less logging = faster
databases 1  # We only need one database

# Faster data structures
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
```

```bash
# Restart Redis
sudo systemctl restart redis
```

### Nginx Optimization

```bash
# Edit Nginx config
sudo nano /etc/nginx/nginx.conf
```

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;
worker_priority -5;  # Higher priority for Nginx

events {
    worker_connections 2048;  # Good for 5 users
    use epoll;
    multi_accept on;
    accept_mutex off;  # Faster connection acceptance
}

http {
    # Speed optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    
    # Gzip compression - AGGRESSIVE
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;  # Balance between speed and compression
    gzip_min_length 256;  # Only compress files > 256 bytes
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss
               application/x-javascript text/x-js;

    # File cache - INSTANT ACCESS
    open_file_cache max=1000 inactive=30s;
    open_file_cache_valid 60s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;

    # Fast timeouts
    client_body_timeout 10;
    client_header_timeout 10;
    keepalive_timeout 65;
    keepalive_requests 100;
    send_timeout 10;
    reset_timedout_connection on;

    # Optimized buffers
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    client_max_body_size 10m;
    large_client_header_buffers 4 8k;
    
    # Response buffering
    fastcgi_buffering on;
    fastcgi_buffer_size 4k;
    fastcgi_buffers 8 4k;
}
```

---

## 8. Monitoring & Maintenance

### Setup Monitoring

**Install monitoring tools**:
```bash
sudo apt install -y htop iotop nethogs

# Install monitoring script
pip install django-debug-toolbar  # Only for testing, remove in production
```

### Create Health Check Endpoint

Add to `urls.py`:
```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'betting'})

urlpatterns = [
    path('health/', health_check),
    # ... other urls
]
```

### Setup Automated Backups

```bash
# Create backup script
nano /home/djangoapp/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/djangoapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump "postgresql://avnadmin:PASSWORD@pg-2bb12e2b-vasuishere.h.aivencloud.com:12345/defaultdb?sslmode=require" > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/djangoapp/bettingsystem/media/

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
chmod +x /home/djangoapp/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
```

Add this line:
```
0 2 * * * /home/djangoapp/backup.sh >> /home/djangoapp/backups/backup.log 2>&1
```

### Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/betting
```

```
/home/djangoapp/bettingsystem/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 djangoapp www-data
    sharedscripts
    postrotate
        sudo supervisorctl restart betting
    endscript
}
```

---

## 9. Deployment Checklist

### Pre-Deployment
- [ ] Update all dependencies: `pip install -r requirements.txt --upgrade`
- [ ] Run tests: `python manage.py test`
- [ ] Check for migrations: `python manage.py makemigrations --check`
- [ ] Security check: `python manage.py check --deploy`
- [ ] Collect static files: `python manage.py collectstatic`

### Deployment
- [ ] Upload code to server
- [ ] Activate virtual environment
- [ ] Install/update requirements
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files
- [ ] Restart Gunicorn: `sudo supervisorctl restart betting`
- [ ] Restart Nginx: `sudo systemctl restart nginx`
- [ ] Clear cache: `python manage.py shell -c "from django.core.cache import cache; cache.clear()"`

### Post-Deployment
- [ ] Check application is running: Visit your domain
- [ ] Check logs: `tail -f logs/*.log`
- [ ] Test critical features (login, betting, etc.)
- [ ] Monitor resource usage: `htop`
- [ ] Check SSL certificate: https://www.ssllabs.com/ssltest/

---

## 10. Troubleshooting

### Application Won't Start

```bash
# Check supervisor logs
sudo tail -f /home/djangoapp/bettingsystem/logs/supervisor.log

# Check gunicorn logs
sudo tail -f /home/djangoapp/bettingsystem/logs/gunicorn_error.log

# Check for syntax errors
cd /home/djangoapp/bettingsystem
source venv/bin/activate
python manage.py check

# Test gunicorn manually
gunicorn -c gunicorn_config.py mymainserver.wsgi:application
```

### 502 Bad Gateway

```bash
# Check if gunicorn is running
sudo supervisorctl status betting

# Check gunicorn socket
ls -la /home/djangoapp/bettingsystem/gunicorn.sock

# Check Nginx error logs
sudo tail -f /var/log/nginx/betting_error.log

# Restart services
sudo supervisorctl restart betting
sudo systemctl restart nginx
```

### Database Connection Issues

```bash
# Test connection
python manage.py dbshell

# Check environment variables
cat /home/djangoapp/bettingsystem/.env

# Test connection manually
psql -h 127.0.0.1 -U betting_user -d betting_db

# If using Cloud SQL Proxy, check if it's running
ps aux | grep cloud_sql_proxy

# Restart Cloud SQL Proxy
pkill cloud_sql_proxy
cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432 &

# Check Cloud SQL instance status in Google Cloud Console
```

### High Memory Usage

```bash
# Check memory
free -h

# Reduce Gunicorn workers in gunicorn_config.py
workers = 2  # Reduce from auto-calculated

# Restart
sudo supervisorctl restart betting
```

### Static Files Not Loading

```bash
# Collect static files again
python manage.py collectstatic --clear --noinput

# Check permissions
sudo chown -R djangoapp:www-data /home/djangoapp/bettingsystem/staticfiles/
sudo chmod -R 755 /home/djangoapp/bettingsystem/staticfiles/

# Check Nginx config
sudo nginx -t
sudo systemctl restart nginx
```

---

## 11. Quick Reference Commands

### Application Management
```bash
# Restart application
sudo supervisorctl restart betting

# View logs
sudo tail -f /home/djangoapp/bettingsystem/logs/supervisor.log
sudo tail -f /home/djangoapp/bettingsystem/logs/gunicorn_error.log

# Django shell
cd /home/djangoapp/bettingsystem
source venv/bin/activate
python manage.py shell

# Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

### Server Management
```bash
# Restart Nginx
sudo systemctl restart nginx

# Restart Redis
sudo systemctl restart redis

# System resource usage
htop
df -h  # Disk usage
free -h  # Memory usage
```

### Database Management
```bash
# Connect to database
python manage.py dbshell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

## 12. Cost Optimization

### Already Optimized! ✅
- ✅ **e2-micro VM** - Perfect for 5 users
- ✅ **db-f1-micro** - Fast SSD storage
- ✅ **SSD boot disk** - Maximum speed
- ✅ **Private IP** - No internet latency
- ✅ **Aggressive caching** - Instant page loads
- ✅ **Optimized workers** - Fast response
- ✅ **Redis caching** - Sub-10ms queries

### To Reduce Costs Further (if needed)
1. Use **Preemptible VM** for 60-70% discount (~$2/month VM!)
   - Auto-restarts after 24 hours, but with supervisor it's seamless
2. Setup **auto-shutdown during off-hours**
3. Use **sustained use discounts** (automatic after 25% of month)
### To Reduce Costs
1. Use **e2-micro** or **e2-small** for lower traffic
2. Use **Preemptible VM** for 60-90% discount (good for testing)
3. Use **Committed Use Discounts** for long-term (30% off)
4. Setup auto-shutdown during off-hours

---

## 13. Security Best Practices

### Firewall Setup
```bash
# Install UFW
sudo apt install -y ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### SSH Security
```bash
# Disable password authentication (use SSH keys only)
sudo nano /etc/ssh/sshd_config
```

Change:
```
PasswordAuthentication no
PermitRootLogin no
```

```bash
sudo systemctl restart sshd
```

### Regular Updates
```bash
# Setup automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 14. Success Indicators

Your deployment is successful when:
- ✅ Application accessible via HTTPS
- ✅ SSL certificate valid (green padlock)
- ✅ Admin panel accessible at `/admin/`
- ✅ Static files loading correctly
- ✅ Database operations working
- ✅ No errors in logs
- ✅ Health check endpoint returns 200 OK

**Test URL**: `https://your-domain.com/health/`
Expected response: `{"status": "healthy", "service": "betting"}`

---
- **Django Documentation**: https://docs.djangoproject.com/
- **Gunicorn Documentation**: https://docs.gunicorn.org/
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Cloud SQL Documentation**: https://cloud.google.com/sql/docs/postgres
- **Cloud SQL Proxy Guide**: https://cloud.google.com/sql/docs/postgres/sql-proxyrn.org/
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Aiven Documentation**: https://docs.aiven.io/

---

## Need Help?

If you encounter issues:
1. Check logs first: `sudo tail -f /home/djangoapp/bettingsystem/logs/*.log`
2. Verify services are running: `sudo supervisorctl status`
3. Test database connection: `python manage.py dbshell`
4. Check firewall: `sudo ufw status`
5. Review Nginx config: `sudo nginx -t`

**Good luck with your deployment! 🚀**
