#!/bin/bash

# Keyes Campaign System - Heroku Deployment Script
# Run this script to deploy to Heroku

set -e

echo "🚀 Keyes Campaign System - Heroku Deployment"
echo "=============================================="
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed."
    echo "Please install it from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Heroku CLI found"
echo ""

# Login to Heroku
echo "📝 Logging into Heroku..."
heroku login

# Ask for app name
echo ""
read -p "Enter your Heroku app name (or press Enter for auto-generated): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "Creating Heroku app with auto-generated name..."
    heroku create
else
    echo "Creating Heroku app: $APP_NAME"
    heroku create "$APP_NAME"
fi

# Set buildpack
echo ""
echo "🔧 Setting Python buildpack..."
heroku buildpacks:set heroku/python

# Set environment variables
echo ""
echo "🔐 Setting environment variables..."
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(openssl rand -hex 32)

# Deploy
echo ""
echo "📦 Deploying to Heroku..."
git push heroku main || git push heroku master

# Scale dyno
echo ""
echo "⚡ Scaling web dyno..."
heroku ps:scale web=1

# Open app
echo ""
echo "✅ Deployment complete!"
echo ""
heroku open

echo ""
echo "📊 View logs with: heroku logs --tail"
echo "🔄 Restart app with: heroku restart"
echo "📈 View dashboard: https://dashboard.heroku.com/apps/$(heroku apps:info -j | grep -o '"name":"[^"]*' | cut -d'"' -f4)"

