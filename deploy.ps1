# Production Deployment Script for Windows PowerShell
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
    Write-Host ""
    Write-Host "Please commit and push your changes first:" -ForegroundColor Yellow
    Write-Host "  git add ." -ForegroundColor White
    Write-Host "  git commit -m 'Your message'" -ForegroundColor White
    Write-Host "  git push origin main" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Check if local is up to date with remote
Write-Host "🔍 Checking if local is synced with remote..." -ForegroundColor Yellow
git fetch origin 2>$null
$behind = git rev-list --count HEAD..origin/main 2>$null
if ($behind -gt 0) {
    Write-Host "⚠️ Your local branch is behind remote by $behind commits" -ForegroundColor Red
    Write-Host "Please pull latest changes first: git pull origin main" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

$ahead = git rev-list --count origin/main..HEAD 2>$null
if ($ahead -gt 0) {
    Write-Host "⚠️ You have $ahead unpushed commits" -ForegroundColor Red
    Write-Host "Please push your changes first: git push origin main" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ Local repository is synced with remote" -ForegroundColor Green
Write-Host ""

# Show last commit that will be deployed
Write-Host "📍 Latest commit to deploy:" -ForegroundColor Yellow
git log -1 --oneline
Write-Host ""

# Confirm deployment
$confirmation = Read-Host "Do you want to deploy this to production? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🚀 Deploying to production server..." -ForegroundColor Cyan
Write-Host ""

# Deploy to production
ssh -i $env:USERPROFILE\.ssh\google_cloud_key rishabh@34.122.62.3 "bash /home/djangoapp/deploy.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ Deployment Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 Your application is live at:" -ForegroundColor Yellow
    Write-Host "   http://34.122.62.3" -ForegroundColor White
    Write-Host "   http://34.122.62.3/admin/" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Next Steps:" -ForegroundColor Yellow
    Write-Host "  - Test the application" -ForegroundColor White
    Write-Host "  - Check logs: ssh -i $env:USERPROFILE\.ssh\google_cloud_key rishabh@34.122.62.3 'sudo tail -f /home/djangoapp/logs/supervisor.log'" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ Deployment Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔍 Check logs for errors:" -ForegroundColor Yellow
    Write-Host "  ssh -i $env:USERPROFILE\.ssh\google_cloud_key rishabh@34.122.62.3 'sudo tail -f /home/djangoapp/logs/supervisor.log'" -ForegroundColor White
    Write-Host ""
    Write-Host "🚨 If needed, rollback:" -ForegroundColor Yellow
    Write-Host "  ssh -i $env:USERPROFILE\.ssh\google_cloud_key rishabh@34.122.62.3 'bash /home/djangoapp/rollback.sh'" -ForegroundColor White
    Write-Host ""
}
