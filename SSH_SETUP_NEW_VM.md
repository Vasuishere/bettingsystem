# SSH Key Setup for New VM (35.200.208.215)

## Quick Setup via Google Cloud Console

### Step 1: Get Your Public Key
```powershell
# In PowerShell
Get-Content "$env:USERPROFILE\.ssh\google_cloud_key.pub"
```

If the .pub file doesn't exist, generate a new key pair:
```powershell
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\google_cloud_key" -C "rishabh"
```

### Step 2: Add SSH Key to Google Cloud VM

1. **Open Google Cloud Console:**
   - Go to: https://console.cloud.google.com/compute/instances

2. **Find Your New VM:**
   - Look for instance with IP: 35.200.208.215

3. **Edit Instance:**
   - Click on the instance name
   - Click "EDIT" button at the top

4. **Add SSH Key:**
   - Scroll to "SSH Keys" section
   - Click "ADD ITEM"
   - Paste your public key from Step 1
   - Format should be: `ssh-rsa AAAAB3... rishabh`
   - Click "SAVE"

5. **Test Connection:**
```powershell
ssh -i "$env:USERPROFILE\.ssh\google_cloud_key" rishabh@35.200.208.215
```

### Alternative: Use Google Cloud SSH

You can also connect directly from browser:
1. Go to Compute Engine → VM instances
2. Click "SSH" button next to your instance
3. This opens a browser-based terminal

Then run all setup commands from there.

---

## Next: Install Coolify

Once connected, run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

This will take 5-10 minutes and install:
- Docker
- Docker Compose
- Coolify dashboard

After installation:
- Access Coolify at: http://35.200.208.215:8000
- Complete initial setup in browser
