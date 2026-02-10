# Deployment Guide for National Assembly e-Library

This guide provides step-by-step instructions for deploying the e-Library system on your production server.

## Prerequisites

- Ubuntu 22.04 LTS Server
- PostgreSQL 14+
- Python 3.10+
- Nginx
- Gunicorn
- SSL Certificate (Let's Encrypt recommended)

## Step 1: Server Setup

### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Required Packages
```bash
sudo apt install -y python3-pip python3-venv postgresql nginx git supervisor
```

### Create Deployment User
```bash
sudo adduser deploy
sudo usermod -aG sudo deploy
```

## Step 2: Database Setup

### Create Database and User
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE elibrary_db;
CREATE USER elibrary_admin WITH PASSWORD 'your-secure-password-here';
ALTER DATABASE elibrary_db OWNER TO elibrary_admin;
GRANT ALL PRIVILEGES ON DATABASE elibrary_db TO elibrary_admin;
\q
```

## Step 3: Application Deployment

### Switch to Deploy User
```bash
su - deploy
```

### Clone Repository
```bash
git clone https://github.com/nationalassembly/elibrary.git
cd elibrary
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure Environment
```bash
cp .env.example .env
nano .env
```

Set the following values:
```
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_DEBUG=False
DB_NAME=elibrary_db
DB_USER=elibrary_admin
DB_PASSWORD=your-secure-password
```

### Run Migrations
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Test Application
```bash
python manage.py check --deploy
```

## Step 4: Gunicorn Setup

### Create Gunicorn Configuration
```bash
nano /home/deploy/elibrary/gunicorn_config.py
```

```python
command = '/home/deploy/elibrary/venv/bin/gunicorn'
pythonpath = '/home/deploy/elibrary'
bind = 'unix:/home/deploy/elibrary/gunicorn.sock'
workers = 4
timeout = 120
capture_output = True
enable_stdio_inheritance = True
```

### Create Supervisor Configuration
```bash
sudo nano /etc/supervisor/conf.d/elibrary.conf
```

```ini
[program:elibrary]
command=/home/deploy/elibrary/venv/bin/gunicorn -c /home/deploy/elibrary/gunicorn_config.py elibrary_project.wsgi:application
directory=/home/deploy/elibrary
user=deploy
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/elibrary/gunicorn.err.log
stdout_logfile=/var/log/elibrary/gunicorn.out.log
```

### Create Log Directory
```bash
sudo mkdir -p /var/log/elibrary
sudo chown deploy:deploy /var/log/elibrary
```

### Start Supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start elibrary
```

## Step 5: Nginx Configuration

### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/elibrary
```

```nginx
server {
    listen 80;
    server_name elibrary.nationalassembly.gm;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name elibrary.nationalassembly.gm;
    
    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/elibrary.nationalassembly.gm/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/elibrary.nationalassembly.gm/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;
    
    # Static files
    location /static/ {
        alias /home/deploy/elibrary/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /home/deploy/elibrary/media/;
        expires 30d;
    }
    
    # Gunicorn socket
    location / {
        proxy_pass http://unix:/home/deploy/elibrary/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
    
    # Access log
    access_log /var/log/nginx/elibrary_access.log;
    error_log /var/log/nginx/elibrary_error.log;
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/elibrary /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 6: SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d elibrary.nationalassembly.gm
```

## Step 7: Firewall Setup

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Step 8: Backup Configuration

### Create Backup Script
```bash
nano /home/deploy/elibrary/backup.sh
```

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/home/deploy/backups"
DB_NAME="elibrary_db"
DB_USER="elibrary_admin"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup uploads
tar -czf $BACKUP_DIR/uploads_backup_$DATE.tar.gz /home/deploy/elibrary/media/

# Keep only last 7 backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Make Executable and Schedule
```bash
chmod +x /home/deploy/elibrary/backup.sh
crontab -e
```

Add line:
```
0 2 * * * /home/deploy/elibrary/backup.sh
```

## Step 9: Monitoring

### Create Health Check Endpoint
Add to your nginx configuration:
```nginx
location /health {
    access_log off;
    return 200 "OK";
    add_header Content-Type text/plain;
}
```

## Step 10: Maintenance Commands

### Update Application
```bash
cd /home/deploy/elibrary
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart elibrary
```

### View Logs
```bash
tail -f /var/log/elibrary/gunicorn.out.log
tail -f /var/log/nginx/elibrary_access.log
```

### Check Application Status
```bash
sudo supervisorctl status elibrary
```

## Security Checklist

- [ ] Change default Django secret key
- [ ] Enable HTTPS only
- [ ] Configure strong database password
- [ ] Set up regular backups
- [ ] Configure firewall
- [ ] Enable audit logging
- [ ] Set up monitoring
- [ ] Configure rate limiting
- [ ] Disable debug mode
- [ ] Secure file permissions

## Troubleshooting

### Gunicorn Not Starting
```bash
sudo supervisorctl restart elibrary
sudo tail -f /var/log/elibrary/gunicorn.err.log
```

### Database Connection Issues
```bash
sudo -u postgres psql -c "SELECT 1"
```

### Static Files Not Loading
```bash
python manage.py collectstatic
sudo systemctl restart nginx
```

## Support

For deployment support:
- Email: ict-support@parliament.gm
- Phone: +220 422 7621
