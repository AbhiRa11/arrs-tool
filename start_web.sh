#!/bin/bash

# ARRS Web Interface Startup Script

echo "🚀 Starting ARRS Web Interface..."
echo ""
echo "Features:"
echo "  ✓ Beautiful web UI"
echo "  ✓ Paste URLs in browser"
echo "  ✓ Share with others on your network"
echo ""

# Activate virtual environment
source venv/bin/activate

# Get local IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ Server starting..."
echo ""
echo "📱 Access ARRS:"
echo ""
echo "  Local:    http://localhost:8000"
echo "  Network:  http://$LOCAL_IP:8000"
echo ""
echo "  Share the Network URL with others!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start server
python3 main.py
