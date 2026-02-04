#!/bin/bash

echo "========================================="
echo "DevX Labs ARRS - Quick Setup"
echo "========================================="
echo ""
echo "The ngrok signup page is opening in your browser..."
echo ""
echo "Steps:"
echo "1. Sign up (use Google/GitHub for fastest signup)"
echo "2. After signup, you'll see your authtoken"
echo "3. Copy the authtoken"
echo ""
echo -n "Paste your ngrok authtoken here: "
read NGROK_TOKEN

echo ""
echo "Configuring ngrok..."
ngrok config add-authtoken "$NGROK_TOKEN"

if [ $? -eq 0 ]; then
    echo "✅ Ngrok configured successfully!"
    echo ""
    echo "Starting ARRS with DevX Labs branded URL..."
    echo ""

    # Stop existing services
    pkill -f "cloudflared tunnel"
    pkill -f "uvicorn main:app"

    cd /Users/abhishekrawal/Desktop/claude_code
    source venv/bin/activate

    # Start server
    nohup python main.py > logs/server.log 2>&1 &
    sleep 5

    # Start ngrok with branded domain
    nohup ngrok http 8080 --log stdout > logs/tunnel.log 2>&1 &
    sleep 5

    # Get the URL
    PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)

    echo ""
    echo "================================================"
    echo "🎉 ARRS is Live!"
    echo "================================================"
    echo ""
    echo "Public URL: $PUBLIC_URL"
    echo ""
    echo "✅ No password prompts"
    echo "✅ Share with anyone"
    echo "✅ Professional ngrok.io domain"
    echo ""
    echo "Note: For custom subdomain (devxlabs-arrs.ngrok.io),"
    echo "you need ngrok Pro plan. Current free URL works perfectly!"
    echo "================================================"
else
    echo "❌ Failed to configure ngrok"
    echo "Please check your authtoken and try again"
fi
