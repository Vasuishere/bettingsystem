# Complete Coolify Deployment - Step by Step Instructions

## 🎯 Your SSH Public Key
Copy this entire key (including "ssh-rsa" at the beginning):

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC8qQQFFBz3ZfvnUNXHgOusw0L7ZCChtuqpT8rNn4mvNLX4oZElBOK1oAqAomM2Ga9tVdEzlqIROSMhZsRRi6bRw5eD+V6Xbfy99TBY+SJTF9/EmChEYQaS0PSZkyjNVTveksrOtQyHN013cu0XWqsMSwoz9BWA7+aaHY5oLf0yIuji1D3oyqKP3Q7K4fQPZm2eZapozqkxqqi+Do3AdcvTDKHMrqw0zaWWoQQYZDfz3RUdEmP4wcTmiPsujrYMoMbfkjeddN9sLQrXPBFwH8Eq9tGUPgH0NWbjbHfXTIp6FegEntIn1VmHf/hY/OuWVG8oXSvZPgBJaK29EfkJ3Hq/voaEzwees6uA7ZxzyFxzw1oIxibg6557JztlBpvNruCXRT2dOPN1ksYsUTPNHFrxljvfmTtF1m9kxwSrsMpOWbIkVrSTvnF8wBirll2WBdF2tTlU4lyF7LTokNfUz7Q/qhJRz+rLSzxbrwMmRH0h2E3jXblH/lSrOtZu0+/JF5LYqAze5XY8sSVTn7vA7SDISIO+oA8WfoSIrI+rXr8ymEtVsN0cii1aTKYezoOjGvjYgVX9ear5hvvJ3muEQk3wgEP+2UPAqZJP6lDGOMQZhZb7Dy4afnEtJvGYNx89BqvIymkfABx7qXKW2mUNBAkd84Ogum8jTEnMOZfNyHIhcw== rishabh@Rishabh_Pandey
```

---

## 📋 PHASE 1: Setup SSH Access to New VM

### Option A: Add SSH Key via Google Cloud Console (RECOMMENDED)

1. **Open Google Cloud Console**
   - Go to: https://console.cloud.google.com/compute/instances
   - Login to your Google account

2. **Find Your New VM**
   - Look for instance with IP: **35.200.208.215**
   - Should be named something like: betting-system-xxxx

3. **Edit VM Instance**
   - Click on the instance name (not the SSH button!)
   - Click **"EDIT"** button at the top of the page
   - Scroll down to **"SSH Keys"** section

4. **Add Your SSH Key**
   - Click **"+ ADD ITEM"** in SSH Keys section
   - Paste the entire SSH key from above (starting with "ssh-rsa")
   - The username "rishabh" should be automatically detected
   - Click **"SAVE"** at the bottom of the page
   - Wait for the instance to update (30 seconds)

5. **Test Connection**
   ```powershell
   ssh -i "$env:USERPROFILE\.ssh\google_cloud_key" rishabh@35.200.208.215
   ```
   You should now be connected!

### Option B: Use Browser SSH (ALTERNATIVE)

If Option A doesn't work:

1. Go to: https://console.cloud.google.com/compute/instances
2. Find VM with IP 35.200.208.215
3. Click the **"SSH"** button (dropdown) → **"Open in browser window"**
4. A terminal will open in your browser
5. Run all commands from there

---

## 📋 PHASE 2: Install Coolify on New VM

### Step 1: Connect to VM

Using PowerShell:
```powershell
ssh -i "$env:USERPROFILE\.ssh\google_cloud_key" rishabh@35.200.208.215
```

OR use browser SSH from Google Cloud Console

### Step 2: Update System
```bash
sudo apt update && sudo apt upgrade -y
```
*This takes 2-3 minutes*

### Step 3: Install Coolify
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

**What this installs:**
- Docker Engine
- Docker Compose
- Coolify platform
- Required dependencies

**Installation time: 5-10 minutes**

You'll see output like:
```
Installing Docker...
Installing Coolify...
Starting Coolify...
Coolify is ready!
```

### Step 4: Verify Installation
```bash
docker --version
docker-compose --version
sudo docker ps
```

You should see Coolify containers running.

### Step 5: Configure Firewall in Google Cloud

1. **Go to Google Cloud Console**
   - Navigate to: VPC Network → Firewall

2. **Create Firewall Rule for Coolify Dashboard**
   - Click **"CREATE FIREWALL RULE"**
   - Name: `allow-coolify-dashboard`
   - Targets: All instances in the network
   - Source IP ranges: `0.0.0.0/0` (or your specific IP for security)
   - Protocols and ports: `tcp:8000`
   - Click **"CREATE"**

3. **Create Firewall Rule for HTTP**
   - Click **"CREATE FIREWALL RULE"**
   - Name: `allow-http-80`
   - Targets: All instances in the network
   - Source IP ranges: `0.0.0.0/0`
   - Protocols and ports: `tcp:80`
   - Click **"CREATE"**

4. **Create Firewall Rule for HTTPS (Optional)**
   - Click **"CREATE FIREWALL RULE"**
   - Name: `allow-https-443`
   - Targets: All instances in the network
   - Source IP ranges: `0.0.0.0/0`
   - Protocols and ports: `tcp:443`
   - Click **"CREATE"**

### Step 6: Access Coolify Dashboard

1. **Open in browser:**
   ```
   http://35.200.208.215:8000
   ```

2. **Complete Initial Setup:**
   - Set admin email: `your-email@example.com`
   - Create strong password
   - Click "Get Started"

3. **Configure Server:**
   - Server Name: Django Betting System
   - Server IP: 35.200.208.215
   - Click "Validate Server"

---

## 📋 PHASE 3: Commit and Push Docker Files

Back in VS Code PowerShell terminal:

### Step 1: Check Git Status
```powershell
git status
```

### Step 2: Add All New Files
```powershell
git add .
```

### Step 3: Commit Changes
```powershell
git commit -m "Add Docker and Coolify configuration for production deployment"
```

### Step 4: Push to GitHub
```powershell
git push origin main
```

---

## 📋 PHASE 4: Deploy to Coolify

### Step 1: Add New Resource in Coolify

1. **In Coolify Dashboard:**
   - Click **"+ New"** or **"New Resource"**
   - Select **"Public Repository"**

2. **Repository Configuration:**
   - Repository URL: `https://github.com/Vasuishere/bettingsystem`
   - Branch: `main`
   - Click **"Continue"**

3. **Select Build Pack:**
   - Choose **"Docker Compose"**
   - Coolify will detect `docker-compose.yml`
   - Click **"Continue"**

### Step 2: Configure Environment Variables

Click on **"Environment Variables"** and add:

```env
SECRET_KEY=django-insecure-ewp)6*&#cx!)d%fd49=xsv@cl&^quvi^+co!$g(gw1!k^_a0e#
DEBUG=False
ALLOWED_HOSTS=35.200.208.215,localhost,127.0.0.1

POSTGRES_DB=bettingdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=StrongPassword123!@#
POSTGRES_HOST=db
POSTGRES_PORT=5432

DATABASE_URL=postgresql://postgres:StrongPassword123!@#@db:5432/bettingdb
```

**Important:** Generate a new SECRET_KEY for production!
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 3: Configure Domain (Optional)

If you have a domain:
1. Point A record to: `35.200.208.215`
2. In Coolify, add domain name
3. Enable automatic SSL

Without domain:
- Application will be at: `http://35.200.208.215:8000`

### Step 4: Deploy

1. Click **"Deploy"** button
2. Monitor build logs in real-time
3. Wait for deployment to complete (5-10 minutes)

**Build Process:**
- Pull code from GitHub
- Build Docker images
- Start PostgreSQL container
- Start Django application
- Run migrations
- Create superuser
- Collect static files

### Step 5: Verify Deployment

1. **Access Application:**
   ```
   http://35.200.208.215:8000
   ```

2. **Login to Admin:**
   ```
   http://35.200.208.215:8000/admin/
   Username: admin
   Password: admin123
   ```

3. **Test Betting Functionality:**
   - Create some bets
   - Verify data persists
   - Check all features work

---

## 📋 PHASE 5: Post-Deployment Security

### Step 1: Change Admin Password

```bash
# SSH to VM
ssh -i "$env:USERPROFILE\.ssh\google_cloud_key" rishabh@35.200.208.215

# Access Django container
sudo docker exec -it betting_web python manage.py changepassword admin
```

### Step 2: Setup Database Backups

```bash
# Create backup script
nano /home/rishabh/backup.sh
```

Paste this:
```bash
#!/bin/bash
BACKUP_DIR="/home/rishabh/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
sudo docker exec betting_postgres pg_dump -U postgres bettingdb > $BACKUP_DIR/db_backup_$DATE.sql
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
echo "Backup completed: $DATE"
```

Make executable:
```bash
chmod +x /home/rishabh/backup.sh
```

Add to crontab:
```bash
crontab -e
# Add this line for daily backup at 2 AM:
0 2 * * * /home/rishabh/backup.sh
```

---

## ✅ Success Checklist

After deployment, verify:

- [ ] Coolify dashboard accessible at http://35.200.208.215:8000
- [ ] Application loads at http://35.200.208.215:8000
- [ ] Can login to admin panel
- [ ] Can create bets
- [ ] Bets persist after page refresh
- [ ] Master delete button works
- [ ] Static files (CSS, JS) load correctly
- [ ] No console errors in browser
- [ ] Database container running: `sudo docker ps | grep postgres`
- [ ] Web container running: `sudo docker ps | grep web`

---

## 🔧 Troubleshooting

### Application Not Starting

```bash
# Check logs
sudo docker logs betting_web

# Check if containers are running
sudo docker ps -a

# Restart containers
cd /path/to/coolify/project
sudo docker-compose restart
```

### Database Connection Issues

```bash
# Check database container
sudo docker logs betting_postgres

# Test database connection
sudo docker exec -it betting_postgres psql -U postgres -d bettingdb -c "SELECT 1;"
```

### View All Logs

```bash
sudo docker-compose logs -f
```

---

## 📞 Quick Reference

**VM IP:** 35.200.208.215
**Application:** http://35.200.208.215:8000
**Admin Panel:** http://35.200.208.215:8000/admin/
**Coolify Dashboard:** http://35.200.208.215:8000
**GitHub Repo:** https://github.com/Vasuishere/bettingsystem

**Default Credentials:**
- Username: admin
- Password: admin123 (CHANGE THIS!)

**Docker Commands:**
```bash
# View containers
sudo docker ps

# View logs
sudo docker logs -f betting_web
sudo docker logs -f betting_postgres

# Restart
sudo docker-compose restart

# Stop
sudo docker-compose down

# Start
sudo docker-compose up -d
```

---

**Ready to Deploy! Follow each phase step by step. 🚀**
