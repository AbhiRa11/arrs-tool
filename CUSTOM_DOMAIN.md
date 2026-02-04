# Custom DevX Labs Branded URL Setup

## Current URL (No Password Required)
**https://inquiries-athens-seed-pavilion.trycloudflare.com**

This Cloudflare tunnel has:
- ✅ No password prompts
- ✅ No authentication needed
- ✅ Works immediately
- ❌ Random subdomain (changes on restart)

---

## Option 1: Ngrok with Custom Subdomain (Recommended)

Get a branded URL like: `devxlabs-arrs.ngrok-free.app`

### Setup (Takes 2 minutes):

1. **Sign up for free ngrok account:**
   - Visit: https://dashboard.ngrok.com/signup
   - Sign up with email or GitHub

2. **Get your authtoken:**
   - After signup, visit: https://dashboard.ngrok.com/get-started/your-authtoken
   - Copy your authtoken (looks like: `2abc...xyz`)

3. **Configure ngrok:**
   ```bash
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```

4. **Start with custom subdomain:**
   ```bash
   # Stop current tunnel
   pkill -f cloudflared

   # Start ngrok with custom subdomain
   ngrok http 8080 --domain devxlabs-arrs.ngrok-free.app
   ```

### Benefits:
- ✅ No password prompts for visitors
- ✅ Custom branded URL with "devxlabs"
- ✅ URL stays same on restart (if you use --domain)
- ✅ Free forever
- ✅ Professional appearance

---

## Option 2: Keep Current Cloudflare Setup

If branding isn't critical, the current Cloudflare URL works perfectly:
- No password prompts
- No authentication
- Free forever
- URL changes on restart

---

## Quick Start Script

Once ngrok is configured, I can create a script that automatically starts with your branded domain:

```bash
#!/bin/bash
# start_with_branded_url.sh

cd /Users/abhishekrawal/Desktop/claude_code
source venv/bin/activate

# Start server
nohup python main.py > logs/server.log 2>&1 &

# Start ngrok with branded domain
nohup ngrok http 8080 --domain devxlabs-arrs.ngrok-free.app > logs/tunnel.log 2>&1 &

echo "ARRS is running at: https://devxlabs-arrs.ngrok-free.app"
```

---

## Current Status

**Active URL:** https://inquiries-athens-seed-pavilion.trycloudflare.com

You can share this URL right now - it works without passwords!

To get the DevX Labs branded URL, just complete the 3-step ngrok setup above.
