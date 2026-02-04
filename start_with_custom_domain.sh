#!/bin/bash

# ARRS Start with Custom DevX Labs Branded Domain
# Requires ngrok authentication (see CUSTOM_DOMAIN.md)

cd /Users/abhishekrawal/Desktop/claude_code

# Check if ngrok is configured
if [ ! -f ~/.ngrok2/ngrok.yml ]; then
    echo "❌ Ngrok not configured!"
    echo ""
    echo "Please follow these steps:"
    echo "1. Sign up: https://dashboard.ngrok.com/signup"
    echo "2. Get token: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "3. Run: ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Kill any existing processes
pkill -f "uvicorn main:app"
pkill -f "cloudflared tunnel"
pkill -f "ngrok"

# Start the FastAPI server in background
echo "Starting ARRS server..."
nohup python main.py > logs/server.log 2>&1 &
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for server to start
sleep 5

# Start ngrok with custom subdomain
# Note: You can request a custom subdomain like "devxlabs-arrs"
echo "Starting ngrok tunnel with custom domain..."
echo "Requesting: devxlabs-arrs.ngrok-free.app"
echo ""

nohup ngrok http 8080 --domain devxlabs-arrs.ngrok-free.app > logs/tunnel.log 2>&1 &
TUNNEL_PID=$!

# Wait for tunnel to initialize
sleep 5

# Display the public URL
echo ""
echo "================================================"
echo "ARRS is now running with DevX Labs branding!"
echo "================================================"
echo "Local URL: http://localhost:8080"
echo "Public URL: https://devxlabs-arrs.ngrok-free.app"
echo ""
echo "Server PID: $SERVER_PID"
echo "Tunnel PID: $TUNNEL_PID"
echo ""
echo "✅ No password prompts"
echo "✅ Branded DevX Labs URL"
echo "✅ Professional appearance"
echo ""
echo "Share this URL with anyone: https://devxlabs-arrs.ngrok-free.app"
echo "================================================"
