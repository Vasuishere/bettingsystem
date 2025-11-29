# Production Deployment & Update Guide

## 🚀 Complete Deployment Workflow

This guide explains how to deploy code updates from GitHub to your production server.

---

## 📋 Prerequisites

- GitHub repository: `https://github.com/Vasuishere/bettingsystem`
- Production server: `34.122.62.3` (betting-system-011)
- SSH key: `C:\Users\risha\.ssh\google_cloud_key`
- Application path: `/home/djangoapp/bettingsystem/`

---

## 🔧 One-Time Setup

### Step 1: Create Deployment Script on Server

SSH to your server and create the deployment script:

```bash
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3
```

Create the deployment script:

```bash
sudo nano /home/djangoapp/deploy.sh
```

Paste this content:

```bash
#!/bin/bash
# Production Deployment Script
# filepath: /home/djangoapp/deploy.sh

echo "=========================================="
echo "🚀 Starting Production Deployment"
echo "=========================================="

# Navigate to project directory
cd /home/djangoapp/bettingsystem || {
    echo "❌ Failed to navigate to project directory"
    exit 1
}

# Show current commit
echo "📍 Current version:"
git log -1 --oneline

# Stash any local changes
echo "📦 Stashing local changes..."
git stash

# Pull latest code from GitHub
echo "⬇️ Pulling latest code from GitHub..."
git pull origin main || {
    echo "❌ Failed to pull from GitHub"
    exit 1
}

# Show new commit
echo "📍 New version:"
git log -1 --oneline

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing/updating dependencies..."
pip install -r requirements.txt --upgrade --quiet

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Deactivate virtual environment
deactivate

# Restart application with supervisor
echo "🔄 Restarting application..."
sudo supervisorctl restart bettingsystem

# Wait for application to start
sleep 3

# Check application status
echo "✅ Checking application status..."
sudo supervisorctl status bettingsystem

# Test application response
echo "🌐 Testing application..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
    echo "✅ Application is responding correctly"
else
    echo "⚠️ Application may have issues - check logs"
fi

echo "=========================================="
echo "🎉 Deployment Completed Successfully!"
echo "=========================================="
echo ""
echo "📊 Quick Status Check:"
echo "  - View logs: sudo tail -f /home/djangoapp/logs/supervisor.log"
echo "  - Test URL: http://34.122.62.3"
echo "  - Admin: http://34.122.62.3/admin/"
```

Make it executable:

```bash
sudo chmod +x /home/djangoapp/deploy.sh
sudo chown djangoapp:djangoapp /home/djangoapp/deploy.sh
```

### Step 2: Create Rollback Script

Create a rollback script for emergencies:

```bash
sudo nano /home/djangoapp/rollback.sh
```

Paste this content:

```bash
#!/bin/bash
# Production Rollback Script
# filepath: /home/djangoapp/rollback.sh

echo "=========================================="
echo "⚠️ Rolling Back to Previous Version"
echo "=========================================="

cd /home/djangoapp/bettingsystem || exit

# Show current commit
echo "📍 Current version:"
git log -1 --oneline

# Go back one commit
echo "⏮️ Rolling back one commit..."
git reset --hard HEAD~1

# Show rolled back version
echo "📍 Rolled back to:"
git log -1 --oneline

# Activate virtual environment
source venv/bin/activate

# Run migrations (in case of rollback)
echo "🗄️ Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

deactivate

# Restart application
echo "🔄 Restarting application..."
sudo supervisorctl restart bettingsystem

sleep 3

# Check status
sudo supervisorctl status bettingsystem

echo "=========================================="
echo "✅ Rollback Completed!"
echo "=========================================="
```

Make it executable:

```bash
sudo chmod +x /home/djangoapp/rollback.sh
sudo chown djangoapp:djangoapp /home/djangoapp/rollback.sh
```

### Step 3: Setup Git on Production Server

Configure Git on the server:

```bash
# Switch to djangoapp user
sudo su - djangoapp

# Navigate to project
cd ~/bettingsystem

# Check if git is initialized
git status

# If not initialized, initialize git
git init

# Add remote (if not already added)
git remote add origin https://github.com/Vasuishere/bettingsystem.git

# Or update existing remote
git remote set-url origin https://github.com/Vasuishere/bettingsystem.git

# Configure git user
git config user.name "Production Server"
git config user.email "production@bettingsystem.com"

# For HTTPS authentication (recommended)
git config credential.helper store

# Pull the repository
git pull origin main

# Exit djangoapp user
exit
```

**For GitHub Authentication:**

If your repository is private, you'll need a Personal Access Token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "Production Server"
4. Select scope: `repo` (full control of private repositories)
5. Generate token and copy it
6. Use this token as password when prompted during `git pull`

### Step 4: Create Local Deployment Script (Windows PowerShell)

On your local machine, create `deploy.ps1`:

```powershell
# filepath: C:\Users\risha\Documents\vasu\bett\deploy.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Deploying to Production Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if there are uncommitted changes
Write-Host "📋 Checking for uncommitted changes..." -ForegroundColor Yellow
$status = git status --porcelain
if ($status) {
    Write-Host "⚠️ You have uncommitted changes!" -ForegroundColor Red
    Write-Host "Please commit and push your changes first:" -ForegroundColor Yellow
    Write-Host "  git add ." -ForegroundColor White
    Write-Host "  git commit -m 'Your message'" -ForegroundColor White
    Write-Host "  git push origin main" -ForegroundColor White
    exit 1
}

# Check if local is up to date with remote
Write-Host "🔍 Checking if local is synced with remote..." -ForegroundColor Yellow
git fetch origin
$behind = git rev-list --count HEAD..origin/main
if ($behind -gt 0) {
    Write-Host "⚠️ Your local branch is behind remote by $behind commits" -ForegroundColor Red
    Write-Host "Please pull latest changes first: git pull origin main" -ForegroundColor Yellow
    exit 1
}

$ahead = git rev-list --count origin/main..HEAD
if ($ahead -gt 0) {
    Write-Host "⚠️ You have $ahead unpushed commits" -ForegroundColor Red
    Write-Host "Please push your changes first: git push origin main" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Local repository is synced with remote" -ForegroundColor Green
Write-Host ""

# Deploy to production
Write-Host "🚀 Deploying to production server..." -ForegroundColor Cyan
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3 "bash /home/djangoapp/deploy.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ Deployment Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 Your application is live at:" -ForegroundColor Yellow
    Write-Host "   http://34.122.62.3" -ForegroundColor White
    Write-Host "   http://34.122.62.3/admin/" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ Deployment Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs:" -ForegroundColor Yellow
    Write-Host "  ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3 'sudo tail -f /home/djangoapp/logs/supervisor.log'" -ForegroundColor White
}
```

---

## 🔄 Regular Deployment Process

### Method 1: From Local Machine (Recommended)

**Step 1: Make Changes and Push to GitHub**

```powershell
# Navigate to project directory
cd C:\Users\risha\Documents\vasu\bett

# Make your code changes
# ... edit files ...

# Check what changed
git status

# Add all changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push origin main
```

**Step 2: Deploy to Production**

```powershell
# Run deployment script
.\deploy.ps1
```

That's it! The script will:
- ✅ Check for uncommitted changes
- ✅ Verify you're synced with GitHub
- ✅ SSH to server
- ✅ Pull latest code
- ✅ Install dependencies
- ✅ Run migrations
- ✅ Collect static files
- ✅ Restart application
- ✅ Verify deployment

### Method 2: From Production Server

```bash
# SSH to server
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3

# Switch to app user
sudo su - djangoapp

# Run deployment
bash /home/djangoapp/deploy.sh
```

### Method 3: Quick One-Liner

```powershell
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3 "bash /home/djangoapp/deploy.sh"
```

---

## 🚨 Emergency Rollback

If deployment breaks something:

**From Local Machine:**
```powershell
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3 "bash /home/djangoapp/rollback.sh"
```

**From Server:**
```bash
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3
sudo su - djangoapp
bash /home/djangoapp/rollback.sh
```

---

## 🔍 Verification & Monitoring

### Check Deployment Status

```bash
# Check application status
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3 "sudo supervisorctl status"

# View real-time logs
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3 "sudo tail -f /home/djangoapp/logs/supervisor.log"

# Test HTTP response
curl -I http://34.122.62.3
```

### Check Git Status on Server

```bash
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3
sudo su - djangoapp
cd ~/bettingsystem

# Check current commit
git log -1 --oneline

# Check current branch
git branch

# Check remote URL
git remote -v

# Check status
git status
```

---

## 📊 Deployment Checklist

### Before Deployment
- [ ] All changes tested locally
- [ ] Code committed to Git
- [ ] Changes pushed to GitHub
- [ ] Backup database (if major changes)
- [ ] Review changes one last time

### During Deployment
- [ ] Run deployment script
- [ ] Monitor deployment logs
- [ ] Check for errors

### After Deployment
- [ ] Verify application is running
- [ ] Test main functionality
- [ ] Check admin panel
- [ ] Review logs for errors
- [ ] Test critical features

---

## 🛠️ Troubleshooting

### Issue: Git Pull Fails

**Error:** `Authentication failed`

**Solution:**
```bash
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3
sudo su - djangoapp
cd ~/bettingsystem

# Re-authenticate with GitHub
git pull origin main
# Enter your GitHub username and Personal Access Token
```

### Issue: Migration Errors

**Solution:**
```bash
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3
sudo su - djangoapp
cd ~/bettingsystem
source venv/bin/activate

# Check migration status
python manage.py showmigrations

# Try migrations again
python manage.py migrate --noinput

# If stuck, fake the migration
python manage.py migrate --fake appname migration_name
```

### Issue: Application Won't Start

**Solution:**
```bash
# Check detailed logs
sudo tail -100 /home/djangoapp/logs/supervisor.log

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Kill stuck processes
sudo pkill -f gunicorn

# Restart
sudo supervisorctl restart bettingsystem
```

### Issue: Static Files Not Loading

**Solution:**
```bash
sudo su - djangoapp
cd ~/bettingsystem
source venv/bin/activate

# Recollect static files
python manage.py collectstatic --clear --noinput

# Fix permissions
sudo chown -R djangoapp:djangoapp /home/djangoapp/bettingsystem/staticfiles/

# Restart nginx
sudo systemctl restart nginx
```

---

## 🔐 Security Best Practices

### Protect Your Deployment Scripts

The deployment scripts are already on the server and contain no sensitive information. However:

1. **Never commit** `.env` files to GitHub
2. **Never commit** SSH keys to GitHub
3. **Use `.gitignore`** properly (already configured)
4. **Use Personal Access Tokens** instead of passwords for GitHub

### Secure GitHub Token

If you need to update your GitHub token on the server:

```bash
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3
sudo su - djangoapp
cd ~/bettingsystem

# Clear stored credentials
git config --unset credential.helper

# Next git pull will ask for new credentials
git pull origin main
```

---

## 📈 Advanced: Automated Deployments

### Option 1: GitHub Actions (Future Enhancement)

Create `.github/workflows/deploy.yml` in your repository:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Server
        uses: appleboy/ssh-action@master
        with:
          host: 34.122.62.3
          username: rishabh
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: bash /home/djangoapp/deploy.sh
```

### Option 2: Webhook Deployment

Set up a webhook endpoint that triggers deployment when you push to GitHub.

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| Deploy from local | `.\deploy.ps1` |
| Deploy from server | `bash /home/djangoapp/deploy.sh` |
| Rollback | `bash /home/djangoapp/rollback.sh` |
| Check status | `sudo supervisorctl status` |
| View logs | `sudo tail -f /home/djangoapp/logs/supervisor.log` |
| Check git version | `git log -1 --oneline` |
| Manual restart | `sudo supervisorctl restart bettingsystem` |

---

## 🎯 Complete Workflow Example

```powershell
# 1. Make changes locally
cd C:\Users\risha\Documents\vasu\bett
# ... edit code ...

# 2. Test changes
python manage.py test

# 3. Commit and push
git add .
git commit -m "Added new feature X"
git push origin main

# 4. Deploy to production
.\deploy.ps1

# 5. Verify deployment
# Open browser: http://34.122.62.3

# 6. Check logs if needed
ssh -i C:\Users\risha\.ssh\google_cloud_key rishabh@34.122.62.3 "sudo tail -f /home/djangoapp/logs/supervisor.log"
```

---

## ✅ Summary

You now have a complete deployment pipeline:

1. **Development:** Make changes locally
2. **Version Control:** Commit and push to GitHub
3. **Deployment:** Run `.\deploy.ps1` from local machine
4. **Verification:** Check application status and logs
5. **Rollback:** If needed, run rollback script

**Your deployment is now automated and safe!** 🚀

---

**Last Updated:** November 26, 2025  
**Server:** betting-system-011 (34.122.62.3)  
**Repository:** https://github.com/Vasuishere/bettingsystem
