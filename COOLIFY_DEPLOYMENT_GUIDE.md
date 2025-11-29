# Django Betting System - Coolify Deployment Guide

## 🎯 Overview
This guide will help you deploy the Django Betting System to Coolify with internal PostgreSQL on your VM at `35.200.208.215`.

## 📋 Prerequisites
- Ubuntu 24.04 VM with at least 4GB RAM and 20GB storage
- Root or sudo access to the VM
- GitHub repository: https://github.com/Vasuishere/bettingsystem
- Domain name (optional, but recommended)

---

## Part 1: Prepare Your VM and Install Coolify

### Step 1: Connect to Your New VM
```powershell
# From Windows PowerShell
ssh rishabh@35.200.208.215
```

### Step 2: Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3: Install Coolify
```bash
# Run the Coolify installation script
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

This will:
- Install Docker and Docker Compose
- Install Coolify
- Configure networking
- Set up the Coolify dashboard

**Installation takes 5-10 minutes**

### Step 4: Access Coolify Dashboard
1. Open browser: `http://35.200.208.215:8000`
2. Complete initial setup:
   - Set admin email
   - Create password
   - Configure server

### Step 5: Configure Firewall (Google Cloud)
In Google Cloud Console:
1. Go to VPC Network → Firewall
2. Create firewall rules:

**Rule 1: Coolify Dashboard**
- Name: allow-coolify
- Targets: All instances
- Source IP ranges: 0.0.0.0/0 (or your IP for security)
- Protocols/ports: tcp:8000

**Rule 2: Application HTTP**
- Name: allow-http
- Targets: All instances
- Source IP ranges: 0.0.0.0/0
- Protocols/ports: tcp:80

**Rule 3: Application HTTPS (if using domain)**
- Name: allow-https
- Targets: All instances
- Source IP ranges: 0.0.0.0/0
- Protocols/ports: tcp:443

---

## Part 2: Deploy Application to Coolify

### Step 1: Add GitHub Repository to Coolify

1. **In Coolify Dashboard:**
   - Click "New Resource"
   - Select "Docker Compose"
   - Choose "Public Repository" or connect your GitHub account

2. **Repository Settings:**
   - Repository URL: `https://github.com/Vasuishere/bettingsystem`
   - Branch: `main`
   - Build Pack: `Docker Compose`

3. **Configure Compose File:**
   - Coolify will automatically detect `docker-compose.yml`
   - Select `docker-compose.yml` as the deployment file

### Step 2: Set Environment Variables

In Coolify dashboard, add these environment variables:

```env
# Django Settings
SECRET_KEY=<GENERATE-STRONG-SECRET-KEY-HERE>
DEBUG=False
ALLOWED_HOSTS=35.200.208.215,localhost,127.0.0.1

# Database Settings
POSTGRES_DB=bettingdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<GENERATE-STRONG-PASSWORD-HERE>
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Optional: DATABASE_URL format
DATABASE_URL=postgresql://postgres:<YOUR-PASSWORD>@db:5432/bettingdb
```

**Generate SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 3: Configure Domain (Optional but Recommended)

1. **If you have a domain:**
   - Point A record to: `35.200.208.215`
   - In Coolify, add domain to application
   - Enable automatic SSL certificate

2. **Without domain:**
   - Application will be available at: `http://35.200.208.215:8000`

### Step 4: Deploy Application

1. Click "Deploy" in Coolify dashboard
2. Monitor build logs
3. Wait for deployment to complete (5-10 minutes)

### Step 5: Verify Deployment

1. **Check Application:**
   ```
   http://35.200.208.215:8000
   ```

2. **Check Admin Panel:**
   ```
   http://35.200.208.215:8000/admin/
   Username: admin
   Password: admin123
   ```

3. **Check Database:**
   - Coolify dashboard → Application → PostgreSQL
   - View logs to confirm database is running

---

## Part 3: Post-Deployment Tasks

### Step 1: Change Default Admin Password

```bash
# SSH into the web container
docker exec -it betting_web python manage.py changepassword admin
```

### Step 2: Backup Configuration

**Create backup script on VM:**
```bash
#!/bin/bash
# /home/rishabh/backup.sh

BACKUP_DIR="/home/rishabh/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec betting_postgres pg_dump -U postgres bettingdb > $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make it executable and add to crontab:
```bash
chmod +x /home/rishabh/backup.sh
crontab -e
# Add this line for daily backup at 2 AM:
0 2 * * * /home/rishabh/backup.sh
```

### Step 3: Monitor Application

**View Application Logs:**
```bash
# Web application logs
docker logs -f betting_web

# PostgreSQL logs
docker logs -f betting_postgres
```

**Monitor Resource Usage:**
```bash
docker stats
```

---

## Part 4: Troubleshooting

### Application Won't Start

1. **Check logs:**
   ```bash
   docker logs betting_web
   ```

2. **Check environment variables:**
   - Verify all required variables are set in Coolify
   - Ensure no typos in variable names

3. **Check database connection:**
   ```bash
   docker exec -it betting_web python manage.py check --database default
   ```

### Database Issues

1. **Reset database:**
   ```bash
   docker exec -it betting_postgres psql -U postgres -c "DROP DATABASE bettingdb;"
   docker exec -it betting_postgres psql -U postgres -c "CREATE DATABASE bettingdb;"
   docker exec -it betting_web python manage.py migrate
   ```

2. **Create superuser:**
   ```bash
   docker exec -it betting_web python manage.py createsuperuser
   ```

### Performance Issues

1. **Scale workers:**
   - Edit `docker-compose.yml`
   - Change `--workers 3` to `--workers 4` or more

2. **Add Redis cache (future enhancement):**
   - Add Redis service to docker-compose.yml
   - Update Django settings to use Redis

---

## Part 5: Maintenance

### Update Application

1. **Push changes to GitHub:**
   ```powershell
   git add .
   git commit -m "Your update message"
   git push origin main
   ```

2. **In Coolify:**
   - Click "Redeploy"
   - Or enable auto-deploy on push

### Database Migrations

```bash
# Run new migrations
docker exec -it betting_web python manage.py migrate

# Or rebuild entire application in Coolify
```

### Rollback Deployment

In Coolify dashboard:
- Go to deployments history
- Click "Rollback" on previous successful deployment

---

## 🔒 Security Checklist

- [ ] Change default admin password
- [ ] Use strong SECRET_KEY (50+ characters)
- [ ] Use strong database password
- [ ] Configure firewall rules (Google Cloud)
- [ ] Enable HTTPS with domain + SSL certificate
- [ ] Regular database backups
- [ ] Monitor application logs
- [ ] Keep Coolify updated
- [ ] Keep Docker images updated

---

## 📞 Support

### Useful Commands

```bash
# View all containers
docker ps -a

# Restart application
docker-compose restart

# View real-time logs
docker-compose logs -f

# Access Django shell
docker exec -it betting_web python manage.py shell

# Access database shell
docker exec -it betting_postgres psql -U postgres -d bettingdb
```

### Common URLs

- Application: `http://35.200.208.215:8000`
- Admin Panel: `http://35.200.208.215:8000/admin/`
- Coolify Dashboard: `http://35.200.208.215:8000` (Coolify UI)
- GitHub Repo: `https://github.com/Vasuishere/bettingsystem`

---

## 🎉 Success Indicators

✅ Coolify dashboard is accessible
✅ Application loads without errors
✅ Can login to admin panel
✅ Can create and view bets
✅ Database persists data after restart
✅ Static files load correctly

---

**Deployment Date:** November 29, 2025
**Server IP:** 35.200.208.215
**Platform:** Coolify + Docker + PostgreSQL
