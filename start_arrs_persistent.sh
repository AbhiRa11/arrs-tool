#!/bin/bash

# ARRS Persistent Startup Script
# This script keeps the ARRS server and localtunnel running

cd /Users/abhishekrawal/Desktop/claude_code

# Activate virtual environment
source venv/bin/activate

# Kill any existing processes
pkill -f "uvicorn main:app"
pkill -f "cloudflared tunnel"
pkill -f "ngrok"
pkill -f "lt --port"

# Start the FastAPI server in background
echo "Starting ARRS server..."
nohup python main.py > logs/server.log 2>&1 &
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for server to start
sleep 5

# Start Cloudflare tunnel in background (no warnings, no password!)
echo "Starting public tunnel with Cloudflare (no warnings)..."
nohup cloudflared tunnel --url http://localhost:8080 > logs/tunnel.log 2>&1 &
TUNNEL_PID=$!
echo "Tunnel started with PID: $TUNNEL_PID"

# Wait for tunnel to initialize
sleep 5

# Display the public URL
echo ""
echo "================================================"
echo "ARRS is now running!"
echo "================================================"
echo "Local URL: http://localhost:8080"
PUBLIC_URL=$(cat logs/tunnel.log | grep -i "https://" | tail -1 | awk '{print $NF}')
echo "Public URL: $PUBLIC_URL"
echo ""
echo "Server PID: $SERVER_PID"
echo "Tunnel PID: $TUNNEL_PID"
echo ""
echo "Logs:"
echo "  Server: logs/server.log"
echo "  Tunnel: logs/tunnel.log"
echo ""
echo "To stop: ./stop_arrs.sh"
echo "================================================"
