# Quick Start Guide - Keyes Campaign System

## What You Have

A complete, rebranded campaign system for The Keyes Company including:

✅ **Dashboard** (`app.py`) - Real-time analytics with Keyes branding  
✅ **Email Template** (`email_template.html`) - Interactive form with Everglade Green design  
✅ **Deployment Config** (`render.yaml`) - Ready for one-click deployment  
✅ **Documentation** - Complete README and deployment guide

## Brand Colors Applied

- **Primary**: Everglade Green (#114d43)
- **Accent**: Miami Sands (#e8d5c4)  
- **Logo**: Italic "Keyes" in Georgia serif font
- **Tagline**: "You're Home Here"

## 3-Minute Deployment

### Option 1: Render.com (Easiest)

```bash
# 1. Create GitHub repo
git init
git add .
git commit -m "Keyes campaign system"
git remote add origin https://github.com/YOUR_USERNAME/keyes-campaign.git
git push -u origin main

# 2. Go to render.com → New Web Service → Connect GitHub
# 3. Select your repo → Render auto-detects everything → Deploy!
# 4. Get your live URL: https://keyes-dashboard.onrender.com
```

### Option 2: Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py

# Visit http://localhost:5002
```

## File Structure

```
keyes-system/
├── app.py                  # Flask application
├── email_template.html     # Campaign email with form
├── requirements.txt        # Python dependencies
├── render.yaml            # Deployment configuration
├── README.md              # Full documentation
├── DEPLOY.md              # Detailed deployment guide
└── QUICKSTART.md          # This file
```

## Routes

Once deployed, you'll have:

- `/` - Dashboard with analytics
- `/test` - Email preview & test form
- `/submissions` - View all submissions
- `/export` - Download CSV
- `/api/submissions` - JSON API
- `/api/submit` - Form submission endpoint (POST)

## Next Steps

1. **Deploy** using Render.com (recommended)
2. **Update** form action URL in `email_template.html` with your live domain
3. **Integrate** with your email platform (HubSpot, Mailchimp, etc.)
4. **Test** the form submission flow
5. **Monitor** submissions via dashboard

## Key Features

### Dashboard
- Real-time submission tracking
- Equity priority breakdown (Maximize vs Speed vs Balance)
- Live email preview
- CSV export for CRM integration

### Email Campaign
- Embedded 2-question form
- Equity range: $583k-$788k
- Multiple goal options (buy before sell, downsize, etc.)
- Optional phone number and expert consultation request

### Data Collection
- Email, first name, last name
- Equity priority preference
- Next move goals
- Phone number (optional)
- Report/expert consultation requests

## Customization

### Update Equity Range
Edit line 22 in `email_template.html`:
```html
<span style="color: #e8d5c4; font-size: 72px;">$583k-$788k</span>
```

### Change Form Action URL
After deployment, update line 49 in `email_template.html`:
```html
<form action="https://YOUR-DOMAIN.com/api/submit" method="POST">
```

### Modify Questions
Edit the form section in `email_template.html` (lines 56-180)

## Support

- **Deployment Issues**: See `DEPLOY.md`
- **Technical Details**: See `README.md`
- **Platform Docs**: 
  - Render: https://render.com/docs
  - Railway: https://docs.railway.app
  - Vercel: https://vercel.com/docs

## Brand Heritage

**The Keyes Company** - Founded 1926, approaching 100-year anniversary in February 2026. Florida's largest independent real estate firm.

---

**Ready to deploy?** Start with Render.com - it's free and takes 3 minutes!

