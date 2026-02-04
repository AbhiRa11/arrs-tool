# Railway Deployment Guide - ARRS

## Quick Deploy (10 minutes)

### Step 1: Create Railway Account
1. Go to: **https://railway.app/**
2. Click "Start a New Project"
3. Sign up with GitHub (recommended) or email

---

### Step 2: Deploy from CLI

Open a new terminal in this directory and run:

```bash
# Login to Railway
railway login

# Initialize project
railway init

# Add environment variables
railway variables set OPENAI_API_KEY="sk-proj-XzeFxwutPIlpJVC9GLgafdPP14EYuqdY9mN9Qf07MUT..."
railway variables set LLM_PROVIDER="openai"
railway variables set OPENAI_MODEL="gpt-4"
railway variables set DATABASE_URL="sqlite:///data/database.db"

# Deploy!
railway up

# Get your URL
railway domain
```

---

### Step 3: Alternative - Deploy via GitHub

**Even Easier Method:**

1. Push code to GitHub:
   ```bash
   # Create new repo on GitHub first, then:
   git remote add origin https://github.com/YOUR_USERNAME/arrs-tool.git
   git push -u origin main
   ```

2. Go to Railway dashboard
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `arrs-tool` repository
5. Railway auto-detects Python and deploys!

---

### Step 4: Configure Environment Variables (in Railway Dashboard)

After deployment, add these variables in Railway dashboard:

```
OPENAI_API_KEY = sk-proj-XzeFxwutPIlpJVC9GLgafdPP14EYuqdY9mN9Qf07MUT...
LLM_PROVIDER = openai
OPENAI_MODEL = gpt-4
DATABASE_URL = sqlite:///data/database.db
PORT = 8080
```

---

### Step 5: Get Your Permanent URL

Railway will give you a URL like:
```
https://arrs-production-abc123.up.railway.app
```

This URL **never changes**!

---

## What You Get

✅ **Permanent URL** - Never changes, ever
✅ **24/7 Uptime** - Runs even when laptop is off
✅ **Auto HTTPS** - Secure by default
✅ **Auto Deploys** - Push to GitHub = auto update
✅ **Free Tier** - $5 free credit/month (enough for ARRS)

---

## Railway Free Tier Limits

- **$5 credit/month** = ~500 hours of usage
- **512 MB RAM** (ARRS uses ~200 MB)
- **1 GB disk** (ARRS uses ~100 MB)
- **Public projects only**

**Perfect for ARRS!**

---

## Estimated Costs

If you exceed free tier:
- **Compute:** $0.000463/min = ~$20/month for 24/7
- **Network:** Free for most use cases

**Tip:** Free tier is enough for moderate usage (testing, demos, small client base)

---

## Manual Commands

### Deploy from CLI:
```bash
cd /Users/abhishekrawal/Desktop/claude_code
railway login
railway init
railway up
```

### Update deployment:
```bash
git add .
git commit -m "Update"
git push  # If using GitHub integration
# OR
railway up  # If using CLI deployment
```

### View logs:
```bash
railway logs
```

### Check status:
```bash
railway status
```

---

## Troubleshooting

### Playwright Installation Fails:
Add this to railway.json:
```json
{
  "deploy": {
    "startCommand": "playwright install chromium && playwright install-deps chromium && uvicorn main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### Database Errors:
Railway uses ephemeral storage. For production, use:
- Railway's PostgreSQL addon (free tier available)
- Or keep SQLite for simplicity (data resets on redeploy)

### Port Issues:
Railway sets `$PORT` environment variable automatically. The app already uses it:
```python
# main.py
port = int(os.getenv("PORT", 8080))
uvicorn.run(app, host="0.0.0.0", port=port)
```

---

## Next Steps After Deployment

1. ✅ Get your Railway URL
2. ✅ Test it with sample URLs
3. ✅ Share it with clients
4. ✅ Optional: Add custom domain ($0/year with Cloudflare)

---

## Custom Domain (Optional)

Once deployed, add your own domain:

1. Buy domain (e.g., `arrs.devxlabs.com`)
2. In Railway dashboard: Settings → Domains → Add Custom Domain
3. Add CNAME record in your DNS:
   ```
   CNAME arrs -> your-railway-url.up.railway.app
   ```
4. Access via: `https://arrs.devxlabs.com`

---

**Ready to deploy? Run these commands in your terminal:**

```bash
railway login
railway init
railway up
```

Your permanent URL will be displayed when deployment completes!
