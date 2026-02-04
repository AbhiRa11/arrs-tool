#!/bin/bash

# ARRS Monitoring Script
# Checks if services are running and restarts them if needed
# Run this in background with: ./monitor_arrs.sh &

cd /Users/abhishekrawal/Desktop/claude_code

while true; do
    # Check if server is running
    if ! pgrep -f "uvicorn main:app" > /dev/null; then
        echo "[$(date)] Server not running, restarting..."
        source venv/bin/activate
        nohup python main.py > logs/server.log 2>&1 &
        sleep 5
    fi

    # Check if tunnel is running
    if ! pgrep -f "cloudflared tunnel" > /dev/null; then
        echo "[$(date)] Tunnel not running, restarting..."
        nohup cloudflared tunnel --url http://localhost:8080 > logs/tunnel.log 2>&1 &
        sleep 5
        NEW_URL=$(cat logs/tunnel.log | grep -i "https://" | tail -1 | awk '{print $NF}')
        echo "[$(date)] New public URL: $NEW_URL"
    fi

    # Check every 30 seconds
    sleep 30
done
