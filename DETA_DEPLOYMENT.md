# Deploy Django Betting System to Deta Space

## Prerequisites
1. Install Space CLI: `curl -fsSL https://get.deta.dev/space-cli.sh | sh` (Linux/Mac) or download from https://deta.space/docs/en/build/quick-starts
2. Create Deta Space account at https://deta.space

## Deployment Steps

### 1. Install Deta Space CLI
```bash
# Windows (PowerShell)
iwr https://get.deta.dev/space-cli.ps1 -useb | iex

# Verify installation
space version
```

### 2. Login to Deta Space
```bash
space login
```

### 3. Link Your Project
```bash
cd C:\Users\risha\Documents\vasu\bett
space link
```

### 4. Configure Environment Variables
After linking, set your environment variables in Deta Space:

```bash
space env add SECRET_KEY "your-django-secret-key"
space env add DEBUG "False"
space env add DATABASE_URL "your-aiven-database-url-from-env-file"
space env add DJANGO_SUPERUSER_USERNAME "admin"
space env add DJANGO_SUPERUSER_EMAIL "your-email@example.com"
space env add DJANGO_SUPERUSER_PASSWORD "your-secure-password"
```

**Note:** Copy your DATABASE_URL from your local `.env` file.

### 5. Push to Deta Space
```bash
space push
```

### 6. Release Your App
```bash
space release
```

### 7. Open Your App
```bash
space open
```

## Important Notes

1. **Spacefile**: Already configured with Python 3.9, Gunicorn, and environment presets
2. **Database**: Uses your Aiven PostgreSQL (same as Render)
3. **Static Files**: WhiteNoise handles static files automatically
4. **Auto-deploy**: After initial setup, just run `space push` to update

## Advantages Over Render
- ⚡ **Faster**: Near-instant cold starts
- 🌍 **Global CDN**: Built-in edge caching
- 🆓 **Free**: Generous free tier
- 🚀 **Simple**: One-command deployment

## View Logs
```bash
space logs
```

## Update App
```bash
git add .
git commit -m "Update app"
space push
space release
```

## Environment Variables in Deta Space Dashboard
Alternatively, you can set env vars in the web dashboard:
1. Go to https://deta.space
2. Select your app
3. Go to Configuration → Environment
4. Add variables there

**Required Environment Variables:**
- `SECRET_KEY`: Your Django secret key
- `DEBUG`: Set to `False` for production
- `DATABASE_URL`: Your Aiven PostgreSQL connection string (copy from `.env` file)
- `DJANGO_SUPERUSER_USERNAME`: Admin username
- `DJANGO_SUPERUSER_EMAIL`: Admin email
- `DJANGO_SUPERUSER_PASSWORD`: Admin password
