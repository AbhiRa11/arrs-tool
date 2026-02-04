# ARRS Deployment Guide

## Current Status

Your ARRS tool is currently running and publicly accessible!

**Public URL:** https://honest-moments-wish.loca.lt
**Local URL:** http://localhost:8080

---

## Quick Commands

### Start Services (Manual)
```bash
./start_arrs_persistent.sh
```

### Stop Services
```bash
./stop_arrs.sh
```

### Monitor & Auto-Restart (Run in background)
```bash
./monitor_arrs.sh &
```

---

## Option 1: Keep Running While Laptop is On

### Method A: Simple Background Process
The services are already running. To keep them running:

1. The monitoring script will auto-restart if services crash:
   ```bash
   ./monitor_arrs.sh &
   ```

2. To make it start automatically on login:
   ```bash
   # Copy launchd file
   cp com.devxlabs.arrs.plist ~/Library/LaunchAgents/

   # Load the service
   launchctl load ~/Library/LaunchAgents/com.devxlabs.arrs.plist

   # Check status
   launchctl list | grep arrs
   ```

3. To stop auto-start:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.devxlabs.arrs.plist
   ```

### Important Notes:
- **Localtunnel URL changes** each time you restart. Save the new URL from `logs/tunnel.log`
- Services will stop when laptop sleeps or shuts down
- For 24/7 access, you need cloud deployment (see below)

---

## Option 2: Cloud Deployment (Recommended for 24/7 Access)

For the service to run even when your laptop is off, deploy to cloud:

### A. Deploy to Railway (Easiest - Free Tier)

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login and deploy:
   ```bash
   railway login
   railway init
   railway up
   ```

3. Add environment variables in Railway dashboard:
   - `OPENAI_API_KEY`: Your OpenAI key
   - `DATABASE_URL`: Will use Railway's storage
   - `LLM_PROVIDER`: openai

4. Railway will provide a permanent public URL (e.g., `your-app.up.railway.app`)

**Cost:** Free tier includes 500 hours/month

### B. Deploy to Render (Simple - Free Tier)

1. Push code to GitHub (if not already)
2. Go to [render.com](https://render.com)
3. Create new "Web Service"
4. Connect your GitHub repo
5. Configure:
   - Build Command: `pip install -r requirements.txt && playwright install chromium`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

**Cost:** Free tier available (spins down after inactivity)

### C. Deploy to Google Cloud Run (Scalable)

1. Install Google Cloud SDK:
   ```bash
   brew install --cask google-cloud-sdk
   ```

2. Create Dockerfile (already in project):
   ```dockerfile
   FROM python:3.11
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   RUN playwright install chromium
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

3. Deploy:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   gcloud run deploy arrs --source . --platform managed --region us-central1 --allow-unauthenticated
   ```

**Cost:** Pay per use, free tier: 2M requests/month

### D. Deploy to AWS (Enterprise-grade)

1. Use AWS Elastic Beanstalk or ECS
2. Follow AWS Python deployment guide
3. Configure environment variables

---

## Sharing Your Public Link

### Current Public URL
**https://honest-moments-wish.loca.lt**

Share this link with anyone. They can:
1. Paste a URL to analyze
2. View ARRS scores with visual breakdowns
3. See AI simulation results
4. Download detailed JSON reports

### Note on Localtunnel URLs
- URL changes on each restart
- First-time visitors see a warning page (click "Continue")
- For permanent URLs, use cloud deployment

---

## Monitoring Logs

```bash
# Server logs
tail -f logs/server.log

# Tunnel logs
tail -f logs/tunnel.log

# Get current public URL
cat logs/tunnel.log | grep "your url is"
```

---

## Troubleshooting

### Services Not Running
```bash
# Check processes
ps aux | grep "uvicorn\|lt --port"

# Restart everything
./stop_arrs.sh
./start_arrs_persistent.sh
```

### Different Public URL
```bash
# Get new URL after restart
cat logs/tunnel.log | grep "your url is"
```

### Database Issues
```bash
# Reinitialize database
python scripts/init_db.py
```

---

## Recommended Setup

For production use with 24/7 availability:

1. **Deploy to Railway or Render** (free, automatic HTTPS, persistent URL)
2. Keep this local version for development/testing
3. Update `.env` with production API keys on cloud platform

**Current Setup** (Laptop-based):
- Good for: Development, testing, demos
- Limitations: Stops when laptop sleeps, URL changes on restart

**Cloud Setup**:
- Good for: Production, sharing with clients, 24/7 availability
- Cost: Free tier available on Railway/Render
- Setup time: 10-15 minutes

---

## Next Steps

1. ✅ Public URL is live: **https://honest-moments-wish.loca.lt**
2. ✅ Monitoring script available
3. ⏳ Optional: Set up launchd for auto-start on login
4. ⏳ Optional: Deploy to cloud for 24/7 access

Choose your deployment strategy based on your needs!
