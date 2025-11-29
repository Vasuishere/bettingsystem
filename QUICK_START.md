# 🚀 QUICK START - Deploy Now!

## ✅ COMPLETED
All Docker and configuration files are ready and pushed to GitHub!

---

## 📋 NEXT STEPS - Follow These in Order:

### 1. Add SSH Key to New VM (5 minutes)
- Open: https://console.cloud.google.com/compute/instances
- Find VM with IP: **35.200.208.215**
- Click instance name → **EDIT**
- Scroll to "SSH Keys" → **+ ADD ITEM**
- Paste this key:
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC8qQQFFBz3ZfvnUNXHgOusw0L7ZCChtuqpT8rNn4mvNLX4oZElBOK1oAqAomM2Ga9tVdEzlqIROSMhZsRRi6bRw5eD+V6Xbfy99TBY+SJTF9/EmChEYQaS0PSZkyjNVTveksrOtQyHN013cu0XWqsMSwoz9BWA7+aaHY5oLf0yIuji1D3oyqKP3Q7K4fQPZm2eZapozqkxqqi+Do3AdcvTDKHMrqw0zaWWoQQYZDfz3RUdEmP4wcTmiPsujrYMoMbfkjeddN9sLQrXPBFwH8Eq9tGUPgH0NWbjbHfXTIp6FegEntIn1VmHf/hY/OuWVG8oXSvZPgBJaK29EfkJ3Hq/voaEzwees6uA7ZxzyFxzw1oIxibg6557JztlBpvNruCXRT2dOPN1ksYsUTPNHFrxljvfmTtF1m9kxwSrsMpOWbIkVrSTvnF8wBirll2WBdF2tTlU4lyF7LTokNfUz7Q/qhJRz+rLSzxbrwMmRH0h2E3jXblH/lSrOtZu0+/JF5LYqAze5XY8sSVTn7vA7SDISIO+oA8WfoSIrI+rXr8ymEtVsN0cii1aTKYezoOjGvjYgVX9ear5hvvJ3muEQk3wgEP+2UPAqZJP6lDGOMQZhZb7Dy4afnEtJvGYNx89BqvIymkfABx7qXKW2mUNBAkd84Ogum8jTEnMOZfNyHIhcw== rishabh@Rishabh_Pandey
```
- Click **SAVE**

### 2. Test SSH Connection
```powershell
ssh -i "$env:USERPROFILE\.ssh\google_cloud_key" rishabh@35.200.208.215
```

### 3. Install Coolify (10 minutes)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

### 4. Configure Firewall (5 minutes)
Go to: https://console.cloud.google.com/networking/firewalls/list

Create 3 rules:
1. **allow-coolify-dashboard**: tcp:8000, source: 0.0.0.0/0
2. **allow-http-80**: tcp:80, source: 0.0.0.0/0  
3. **allow-https-443**: tcp:443, source: 0.0.0.0/0

### 5. Access Coolify Dashboard
Open: http://35.200.208.215:8000
- Set admin email and password
- Complete initial setup

### 6. Deploy Application in Coolify
1. Click **"+ New Resource"** → **"Public Repository"**
2. Repository: `https://github.com/Vasuishere/bettingsystem`
3. Branch: `main`
4. Build Pack: **Docker Compose**
5. Add Environment Variables:
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
6. Click **"Deploy"**
7. Wait 5-10 minutes

### 7. Access Your Application
- App: http://35.200.208.215:8000
- Admin: http://35.200.208.215:8000/admin/
- Username: admin
- Password: admin123

---

## 📚 Detailed Guides Available:

1. **DEPLOYMENT_STEPS.md** - Complete step-by-step instructions with screenshots
2. **COOLIFY_DEPLOYMENT_GUIDE.md** - Full deployment and maintenance guide
3. **SSH_SETUP_NEW_VM.md** - SSH key setup instructions

---

## ⚡ Quick Commands Reference

### SSH to VM:
```powershell
ssh -i "$env:USERPROFILE\.ssh\google_cloud_key" rishabh@35.200.208.215
```

### View Application Logs:
```bash
sudo docker logs -f betting_web
```

### View Database Logs:
```bash
sudo docker logs -f betting_postgres
```

### Restart Application:
```bash
sudo docker-compose restart
```

### Change Admin Password:
```bash
sudo docker exec -it betting_web python manage.py changepassword admin
```

---

## 🎯 Success Indicators:
✅ SSH connection works
✅ Coolify dashboard accessible
✅ Application loads at http://35.200.208.215:8000
✅ Can login to admin panel
✅ Can create and manage bets
✅ Data persists after refresh

---

**Everything is ready! Just follow steps 1-7 above. 🚀**
