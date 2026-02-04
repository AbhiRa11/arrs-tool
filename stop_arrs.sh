#!/bin/bash

# Stop ARRS services

echo "Stopping ARRS server and tunnel..."

# Kill server
pkill -f "uvicorn main:app"
pkill -f "python main.py"

# Kill tunnels
pkill -f "lt --port"
pkill -f "cloudflared tunnel"
pkill -f "ngrok"

echo "ARRS services stopped."
