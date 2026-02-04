# Deploy ARRS via GitHub (Easiest Method)

## Step 1: Create GitHub Repository

1. Go to: **https://github.com/new**
2. Repository name: `arrs-tool`
3. Description: `ARRS - AI Readability & Recommendation Score by DevX Labs`
4. Make it **Public** (free Railway deployment requires public repos)
5. **Don't** initialize with README (we already have code)
6. Click "Create repository"

---

## Step 2: Push Code to GitHub

Copy your repository URL (should look like: `https://github.com/YOUR_USERNAME/arrs-tool.git`)

Then run these commands:

```bash
cd /Users/abhishekrawal/Desktop/claude_code

# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/arrs-tool.git

# Push code
git branch -M main
git push -u origin main
```

**Note:** You might need to authenticate with GitHub:
- Use Personal Access Token (not password)
- Or use GitHub CLI: `gh auth login`

---

## Step 3: Deploy to Railway from GitHub

1. Go to: **https://railway.app/new**
2. Click **"Deploy from GitHub repo"**
3. **Connect GitHub account** (if not already connected)
4. Select **`arrs-tool`** repository
5. Railway auto-detects Python and starts deploying!

---

## Step 4: Add Environment Variables

While it's deploying, add these variables:

1. Click on your deployment
2. Go to **"Variables"** tab
3. Add these one by one:

```
OPENAI_API_KEY = sk-proj-XzeFxwutPIlpJVC9GLgafdPP14EYuqdY9mN9Qf07MUT...
LLM_PROVIDER = openai
OPENAI_MODEL = gpt-4
DATABASE_URL = sqlite:///data/database.db
```

4. Click **"Save"**
5. Deployment will restart with new variables

---

## Step 5: Get Your URL

1. Go to **"Settings"** tab
2. Click **"Generate Domain"**
3. You'll get: `https://arrs-production-abc123.up.railway.app`

This URL is **permanent** and **never changes**!

---

## That's It!

✅ Your ARRS tool is now live 24/7
✅ Permanent URL
✅ Auto-deploys when you push to GitHub
✅ Professional hosting

---

## Update Your App (Later)

When you make changes:

```bash
git add .
git commit -m "Update feature"
git push
```

Railway automatically deploys the new version!

---

## Total Time: 10 minutes

Much easier than CLI! 🎉
