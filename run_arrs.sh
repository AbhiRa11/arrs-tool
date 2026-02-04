#!/bin/bash

echo "🚀 Starting ARRS Web Server..."
echo ""

# 1. Activate virtual environment
source venv/bin/activate

# 2. Check if Ollama is running
echo "✓ Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Starting it..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# 3. Verify phi model is available
echo "✓ Checking phi model..."
ollama list | grep phi || echo "⚠️  Run: ollama pull phi"

# 4. Start the web server
echo "✓ Starting ARRS web server..."
echo ""
echo "🌐 Access ARRS at:"
echo "   Local:   http://localhost:8000"
echo "   Network: http://$(ipconfig getifaddr en0):8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 main.py
