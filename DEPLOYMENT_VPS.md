# 🚀 VPS/AWS Deployment Guide with Google OAuth

This guide provides step-by-step instructions for deploying EchoChat on a VPS or AWS Ubuntu server with Google OAuth authentication.

## Prerequisites

- Ubuntu server (20.04 or 22.04)
- Domain name pointing to your server (e.g., echochat.iafluence.cloud)
- Google Cloud Console account for OAuth credentials
- Root or sudo access to the server

## Part 1: Google OAuth Setup

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Click "Create Credentials" → "OAuth 2.0 Client ID"
4. Configure the consent screen if prompted
5. Choose "Web application" as application type
6. Add authorized redirect URIs:
   ```
   https://echochat.iafluence.cloud/api/auth/callback/google
   http://localhost:3000/api/auth/callback/google
   ```
7. Click "Create" and save your:
   - **Client ID** (looks like: `xxxxx.apps.googleusercontent.com`)
   - **Client Secret** (looks like: `GOCSPX-xxxxx`)

### 2. Generate NextAuth Secret

On your local machine or server:
```bash
openssl rand -base64 32
```
Save this value, you'll need it for `NEXTAUTH_SECRET`.

## Part 2: Server Setup

### 1. Run the Setup Script

```bash
cd /home/user/EchoChat/deploy
chmod +x setup-aws.sh
sudo ./setup-aws.sh
```

### 2. Create Frontend Environment File

Create `/opt/echochat/frontend/.env.production`:

```bash
sudo nano /opt/echochat/frontend/.env.production
```

Add the following content (replace with your actual values):

```env
NODE_ENV=production
PORT=3001
NEXT_PUBLIC_API_URL=http://localhost:8001

# NextAuth.js Configuration
NEXTAUTH_SECRET=your-generated-secret-from-openssl
NEXTAUTH_URL=https://echochat.iafluence.cloud

# Google OAuth
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx

# Allowed admin emails (comma-separated)
ALLOWED_ADMIN_EMAILS=suan.tay.job@gmail.com,j.wallut.pro@gmail.com
```

**Important**: Replace all placeholder values with your actual credentials!

### 3. Create Backend Environment File

Create `/opt/echochat/backend/.env`:

```bash
sudo nano /opt/echochat/backend/.env
```

Add your backend configuration:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
TARGET_URL=https://www.yoursite.fr
SCRAPE_FREQUENCY_HOURS=24
CORS_ORIGINS=https://echochat.iafluence.cloud
```

## Part 3: Build and Deploy

### 1. Build Frontend

```bash
cd /opt/echochat/frontend
npm install
npm run build
```

**Critical**: The build process must have access to environment variables. Check build output for any errors.

### 2. Copy Systemd Service Files

```bash
# Copy the updated service files
sudo cp /opt/echochat/deploy/echochat-frontend.service /etc/systemd/system/
sudo cp /opt/echochat/deploy/echochat-backend.service /etc/systemd/system/

# Set correct permissions
sudo chmod 644 /etc/systemd/system/echochat-frontend.service
sudo chmod 644 /etc/systemd/system/echochat-backend.service
```

### 3. Set File Permissions

```bash
sudo chown -R www-data:www-data /opt/echochat/frontend
sudo chown -R www-data:www-data /opt/echochat/backend

# IMPORTANT: Ensure the data directory has write permissions for SQLite
sudo mkdir -p /opt/echochat/backend/data
sudo chmod 755 /opt/echochat/backend/data
sudo chown -R www-data:www-data /opt/echochat/backend/data
```

**Note**: SQLite requires write permissions not only on the database file itself, but also on the parent directory to create temporary files (.db-journal, .db-wal, .db-shm). If you encounter "attempt to write a readonly database" errors, verify that:
- The `/opt/echochat/backend/data` directory exists and has write permissions (755 or 777)
- The database file (if it exists) has write permissions (644)
- The directory owner matches the user running the service (www-data)

### 4. Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable echochat-backend
sudo systemctl enable echochat-frontend

# Start services
sudo systemctl start echochat-backend
sudo systemctl start echochat-frontend

# Check status
sudo systemctl status echochat-backend
sudo systemctl status echochat-frontend
```

## Part 4: Troubleshooting

### Check if Google Login Button Appears

1. Open your browser and go to `https://echochat.iafluence.cloud/auth/signin`
2. You should see a "Continuer avec Google" button

If the button doesn't appear:

### 1. Check Service Logs

```bash
# Frontend logs
sudo journalctl -u echochat-frontend -f

# Backend logs
sudo journalctl -u echochat-backend -f
```

### 2. Verify Environment Variables are Loaded

```bash
# Check if the service can see the variables
sudo systemctl show echochat-frontend | grep Environment
```

### 3. Test NextAuth API

```bash
curl http://localhost:3001/api/auth/providers
```

Expected output:
```json
{
  "google": {
    "id": "google",
    "name": "Google",
    "type": "oauth",
    "signinUrl": "...",
    "callbackUrl": "..."
  }
}
```

If you get an empty object `{}`, NextAuth isn't loading the Google provider, which means environment variables aren't being read.

### 4. Common Issues and Solutions

#### Issue: Environment variables not loaded

**Solution 1**: Use explicit environment variables in service file

Edit `/etc/systemd/system/echochat-frontend.service`:
```bash
sudo nano /etc/systemd/system/echochat-frontend.service
```

Replace the content with the explicit version from `deploy/echochat-frontend-explicit.service`.

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart echochat-frontend
```

**Solution 2**: Check file permissions
```bash
sudo chmod 644 /opt/echochat/frontend/.env.production
sudo chown www-data:www-data /opt/echochat/frontend/.env.production
```

#### Issue: Google OAuth error "redirect_uri_mismatch"

**Solution**: Verify redirect URIs in Google Cloud Console exactly match:
- `https://echochat.iafluence.cloud/api/auth/callback/google`

#### Issue: "Access Denied" error after Google login

**Solution**: Check if your email is in the `ALLOWED_ADMIN_EMAILS` list in `.env.production`

#### Issue: Build fails or variables not available during build

**Solution**: Set environment variables before building:
```bash
export NEXTAUTH_SECRET="your-secret"
export NEXTAUTH_URL="https://echochat.iafluence.cloud"
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-secret"
cd /opt/echochat/frontend
npm run build
```

#### Issue: "attempt to write a readonly database" SQLite error

**Root Cause**: SQLite needs write permissions on both the database file AND its parent directory to create temporary files (.db-journal, .db-wal, .db-shm).

**Solution**:
```bash
# Ensure data directory exists with correct permissions
sudo mkdir -p /opt/echochat/backend/data
sudo chmod 755 /opt/echochat/backend/data
sudo chown -R www-data:www-data /opt/echochat/backend/data

# If database file exists, ensure it has write permissions
sudo chmod 644 /opt/echochat/backend/data/echochat.db

# Restart backend service
sudo systemctl restart echochat-backend
```

The application now includes automatic permission checks and fixes on startup, but manual intervention may still be needed in some deployment scenarios.

## Part 5: After Deployment

### 1. Configure Nginx (if not already done)

Create nginx config:
```bash
sudo nano /etc/nginx/sites-available/echochat
```

Add:
```nginx
server {
    listen 80;
    server_name echochat.iafluence.cloud;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/echochat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Setup SSL with Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d echochat.iafluence.cloud
```

### 3. Test Everything

1. Visit `https://echochat.iafluence.cloud/auth/signin`
2. Click "Continuer avec Google"
3. Sign in with your Google account
4. You should be redirected to `/admin` panel

## Part 6: Maintenance

### Update Deployment

```bash
cd /opt/echochat
git pull origin main

# Rebuild backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Rebuild frontend
cd ../frontend
npm install
npm run build

# Restart services
sudo systemctl restart echochat-backend
sudo systemctl restart echochat-frontend
```

### View Logs

```bash
# Frontend
sudo journalctl -u echochat-frontend -n 100

# Backend
sudo journalctl -u echochat-backend -n 100

# Follow logs in real-time
sudo journalctl -u echochat-frontend -f
```

## Support

If you encounter issues:
1. Check logs with `journalctl`
2. Verify environment variables are loaded
3. Test individual endpoints with `curl`
4. Ensure Google OAuth redirect URIs are correct
5. Check file permissions for www-data user

---

**Security Note**: Never commit `.env.production` or any file containing secrets to Git. Keep these files secure on the server only.
