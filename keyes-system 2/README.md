# The Keyes Company - Home Equity Campaign Dashboard

## Overview

A complete campaign system for The Keyes Company's home equity outreach program. This system includes a dashboard for tracking submissions, an interactive email template with embedded forms, and analytics for understanding client priorities.

## Features

- **Dashboard**: Real-time submission tracking with Keyes branding
- **Test Page**: Live email preview with working form (`/test`)
- **Submissions View**: Full table of all submissions
- **CSV Export**: Download submissions for CRM import
- **API**: JSON endpoint for integrations
- **Keyes Branding**: Complete rebrand with Everglade Green color palette and "You're Home Here" messaging

## Brand Identity

### Colors
- **Primary**: Everglade Green (#114d43) - Deep teal representing Florida's natural beauty
- **Secondary**: Miami Sands (#e8d5c4) - Warm cream/beige accent
- **Dark Accent**: #0d3d35 - Darker teal for gradients

### Tagline
**"You're Home Here"** - The Keyes Company signature

### Logo Style
Script/italic "Keyes" in Georgia serif font with "The" and "Company" in standard weight

## Deployment Options

### Option 1: Render.com (Recommended - Free)

1. Push this folder to a GitHub repository
2. Go to [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Render will auto-detect the `render.yaml` config
6. Click "Create Web Service"
7. Your app will be live at: `https://keyes-dashboard.onrender.com`

### Option 2: Railway.app (Free)

1. Push to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway will auto-detect Python and deploy
6. Get your live URL from the dashboard

### Option 3: Vercel (Free)

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow prompts
4. Your app will be live

### Option 4: PythonAnywhere (Free)

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Create free account
3. Upload files via "Files" tab
4. Set up web app pointing to `app.py`
5. Install requirements: `pip install -r requirements.txt`

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5002

## Routes

- `/` - Dashboard with analytics and email preview
- `/test` - Standalone email preview & test form
- `/submissions` - All submissions table view
- `/api/submissions` - JSON API endpoint
- `/export` - CSV download
- `/api/submit` - Form submission endpoint (POST)

## Environment Variables

- `PORT` - Server port (default: 5002)

## Data Storage

Uses simple JSON file storage (`submissions.json`). For production with high volume, consider upgrading to PostgreSQL or MongoDB.

## Campaign Details

### Email Campaign
- **Subject**: "Your Home Equity Blueprint - The Keyes Company"
- **Focus**: Unlocking $583k-$788k in home equity
- **CTA**: Two-question form embedded in email

### Form Questions
1. **Equity Priority**: Maximize ($788k) vs Speed vs Balance
2. **Next Move**: Multiple goals (buy before sell, downsize, second home, etc.)

### Follow-up Options
- Equity report request
- Expert consultation request
- Phone number collection

## The Keyes Company

Founded in 1926, The Keyes Company is Florida's largest independent real estate firm. Approaching their 100-year anniversary in 2026, they serve South Florida with deep local expertise and a commitment to making clients feel at home.

**Tagline**: "You're Home Here"  
**Website**: keyes.com  
**Heritage**: Nearly 100 years of Florida real estate excellence

## Technical Stack

- **Backend**: Python 3.11 + Flask
- **Frontend**: HTML/CSS (email-safe inline styles)
- **Storage**: JSON file (upgradeable to SQL)
- **Deployment**: Render/Railway/Vercel/PythonAnywhere

## Support

For questions about deployment or customization, refer to the deployment platform's documentation or contact your development team.

---

**Built for The Keyes Company** | 2025

