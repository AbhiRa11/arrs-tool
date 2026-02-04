#!/bin/bash

echo "================================================="
echo "ARRS - Railway Deployment Script"
echo "================================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if logged in
echo "Checking Railway login status..."
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway"
    echo ""
    echo "Please run this command in a new terminal:"
    echo "  railway login"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Railway login verified!"
echo ""

# Initialize project
echo "Creating Railway project..."
railway init --name "arrs-devxlabs" 2>&1 | tee /tmp/railway_init.log

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Project might already exist. Continuing..."
fi

echo ""

# Set environment variables
echo "Setting environment variables..."

railway variables set OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
railway variables set LLM_PROVIDER="openai"
railway variables set OPENAI_MODEL="gpt-4"
railway variables set DATABASE_URL="sqlite:///data/database.db"

echo "✅ Environment variables set!"
echo ""

# Deploy
echo "================================================="
echo "Deploying to Railway..."
echo "This will take 3-5 minutes..."
echo "================================================="
echo ""

railway up

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================="
    echo "✅ Deployment Successful!"
    echo "================================================="
    echo ""
    echo "Getting your permanent URL..."
    echo ""

    # Get domain
    DOMAIN=$(railway domain 2>&1)

    if [ -n "$DOMAIN" ]; then
        echo "🎉 Your ARRS tool is live at:"
        echo ""
        echo "   $DOMAIN"
        echo ""
    else
        echo "URL not yet available. Check Railway dashboard:"
        echo "   https://railway.app/project"
    fi

    echo "================================================="
    echo ""
    echo "Next steps:"
    echo "1. Test your URL"
    echo "2. Share it with clients"
    echo "3. View logs: railway logs"
    echo "4. Check status: railway status"
    echo ""
else
    echo ""
    echo "❌ Deployment failed. Check the errors above."
    echo ""
    echo "Common fixes:"
    echo "1. Check railway logs"
    echo "2. Verify environment variables: railway variables"
    echo "3. Try deploying again: railway up"
    echo ""
fi
