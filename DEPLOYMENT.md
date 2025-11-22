# 🚀 Deployment Guide

This guide provides detailed instructions for deploying EchoChat to various free hosting platforms.

## Table of Contents

1. [Backend Deployment](#backend-deployment)
   - [Render.com](#rendercom)
   - [Railway.app](#railwayapp)
   - [Fly.io](#flyio)
2. [Frontend Deployment](#frontend-deployment)
   - [Vercel](#vercel)
3. [Environment Configuration](#environment-configuration)

## Backend Deployment

### Render.com

**Best for**: Simple deployments with generous free tier

#### Steps:

1. **Create Account**: Sign up at https://render.com

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the branch to deploy

3. **Configure Service**:
   - **Name**: `echochat-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your preferred branch)
   - **Plan**: Free

4. **Environment Variables**:
   Add the following in the "Environment" tab:
   ```
   ANTHROPIC_API_KEY=your_key_here
   TARGET_URL=https://www.example.fr
   SCRAPE_FREQUENCY_HOURS=24
   ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ```

5. **Deploy**: Click "Create Web Service"

6. **Note your URL**: Save the URL (e.g., `https://echochat-backend.onrender.com`)

#### Important Notes:
- Free tier spins down after 15 minutes of inactivity
- First request after sleep may take 30+ seconds
- 750 hours/month free (enough for one service running 24/7)

---

### Railway.app

**Best for**: Easy deployment with CLI and generous free trial

#### Steps:

1. **Create Account**: Sign up at https://railway.app

2. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   ```

3. **Deploy via GitHub**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your EchoChat repository
   - Select "backend" directory

4. **Or Deploy via CLI**:
   ```bash
   cd backend
   railway login
   railway init
   railway up
   ```

5. **Environment Variables**:
   Add in the Railway dashboard or via CLI:
   ```bash
   railway variables set ANTHROPIC_API_KEY=your_key_here
   railway variables set TARGET_URL=https://www.example.fr
   railway variables set SCRAPE_FREQUENCY_HOURS=24
   ```

6. **Generate Domain**:
   - Go to Settings → Domains
   - Click "Generate Domain"
   - Save the URL

#### Important Notes:
- $5 free credit per month
- No cold starts
- Automatic HTTPS

---

### Fly.io

**Best for**: Global edge deployment with persistent storage

#### Steps:

1. **Install flyctl**:
   ```bash
   # macOS
   brew install flyctl
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Create fly.toml** in backend directory:
   ```toml
   app = "echochat-backend"
   
   [build]
     dockerfile = "Dockerfile"
   
   [env]
     PORT = "8000"
   
   [[services]]
     internal_port = 8000
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   
   [mounts]
     source = "echochat_data"
     destination = "/app/data"
   ```

4. **Deploy**:
   ```bash
   cd backend
   fly launch --no-deploy
   fly volumes create echochat_data --size 1
   fly secrets set ANTHROPIC_API_KEY=your_key_here
   fly secrets set TARGET_URL=https://www.example.fr
   fly deploy
   ```

5. **Get URL**:
   ```bash
   fly info
   ```

#### Important Notes:
- 3 GB storage free
- 160 GB bandwidth/month
- Always running (no cold starts)

---

## Frontend Deployment

### Vercel

**Best for**: Next.js apps (official platform by Next.js creators)

#### Steps:

1. **Create Account**: Sign up at https://vercel.com

2. **Import Project**:
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select the repository

3. **Configure Build**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

4. **Environment Variables**:
   Add in "Environment Variables" section:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```
   ⚠️ Replace with your actual backend URL from step 1

5. **Deploy**: Click "Deploy"

6. **Custom Domain** (optional):
   - Go to Settings → Domains
   - Add your custom domain

#### Important Notes:
- Automatic deployments on git push
- Unlimited bandwidth
- 100 GB-hours of serverless function execution/month
- Built-in CDN

---

## Environment Configuration

### Backend Environment Variables

Required for production:

```env
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Target website
TARGET_URL=https://www.yoursite.fr
SCRAPE_FREQUENCY_HOURS=24

# CORS (use your frontend URL)
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com

# Optional optimizations
SCRAPER_TIMEOUT=30000
SCRAPE_JOB_TIMEOUT=7200
CHUNK_SIZE=1000
TOP_K_RESULTS=5
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## Post-Deployment Checklist

- [ ] Backend is accessible and returns JSON at `/health`
- [ ] Frontend loads without errors
- [ ] Admin panel accessible at `/admin`
- [ ] Can start a scraping job from admin panel
- [ ] Chat widget appears on homepage
- [ ] Chat responds to questions
- [ ] Sources are linked correctly
- [ ] Mobile responsiveness works
- [ ] HTTPS is enabled
- [ ] Environment variables are set correctly
- [ ] CORS is configured for frontend domain

---

## Monitoring & Maintenance

### Backend Health Check

```bash
curl https://your-backend-url.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### View Logs

**Render**:
- Dashboard → Your Service → Logs

**Railway**:
- Dashboard → Your Service → Deployments → View Logs

**Fly.io**:
```bash
fly logs
```

**Vercel**:
- Dashboard → Your Project → Deployments → View Function Logs

---

## Troubleshooting

### Backend won't start

1. Check environment variables are set
2. Verify Anthropic API key is valid
3. Check logs for errors
4. Ensure Playwright can install browsers (may need more memory)

### Frontend can't reach backend

1. Verify `NEXT_PUBLIC_API_URL` is correct
2. Check CORS settings in backend
3. Ensure backend is running and accessible
4. Test backend endpoint directly with curl

### Scraping fails

1. Check target website is accessible
2. Verify Playwright browsers are installed
3. Increase scraper timeout if needed
4. Check logs for specific errors

---

## Cost Optimization

### Free Tier Limits

**Render** (1 free service):
- Use for backend only
- Accepts cold starts

**Railway**:
- $5/month credit
- Good for MVP testing

**Fly.io**:
- Best for always-on needs
- 3 GB storage included

**Vercel**:
- Unlimited for frontend
- Perfect for Next.js

### Recommended Setup for Free

- **Backend**: Render.com (with cold starts acceptable)
- **Frontend**: Vercel
- **Total cost**: $0/month

### Recommended Setup for Production

- **Backend**: Fly.io or Railway paid plan
- **Frontend**: Vercel
- **Total cost**: ~$5-10/month

---

## Support

For deployment issues:
- Check platform-specific documentation
- Open an issue on GitHub
- Review logs for error messages

Happy deploying! 🚀
