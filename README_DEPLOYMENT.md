# Keyes Campaign System - Deployment Package

## 🎯 What's Included

This package contains the complete Keyes Campaign System ready for Heroku deployment:

### Core Application Files
- `app.py` - Main Flask application
- `ai_generator.py` - AI campaign generation engine
- `audience_analyzer.py` - Audience analysis tools
- `html_generator.py` - Email template generator
- `templates/` - HTML templates for all pages
- `uploads/` - Upload directory

### Configuration Files
- `Procfile` - Heroku process configuration
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification
- `.gitignore` - Git ignore rules

### Data Files
- `campaigns.json` - Campaign storage
- `past_clients.json` - Past client segment definitions
- `behavioral_audiences.json` - Behavioral audience data
- `segments.json` - Audience segments
- `market_data.xlsx` - Market statistics by ZIP code

### Documentation
- `HEROKU_DEPLOYMENT.md` - Detailed deployment guide
- `CAMPAIGN_SYSTEM_README.md` - System overview
- `QUICK_START_GUIDE.md` - Quick start guide
- `AI_CAMPAIGN_GENERATOR_DOCUMENTATION.md` - AI generator docs

## 🚀 Quick Deploy (3 Steps)

### Option 1: Automated Script

```bash
cd keyes-system
./deploy_to_heroku.sh
```

### Option 2: Manual Deployment

```bash
# 1. Login to Heroku
heroku login

# 2. Create app
heroku create keyes-campaign-system

# 3. Deploy
git push heroku main
heroku ps:scale web=1
heroku open
```

## 📋 Prerequisites

1. **Heroku Account** - Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI** - Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git** - Ensure Git is installed

## 🎨 Features

### Campaign Management
- AI-powered campaign generation
- Email template builder with drag-and-drop
- Preview and export to HubSpot
- Form builder with custom questions

### Audience Segmentation
- 10 unified past client segments
- Behavioral audience tracking
- CSV/Excel upload for client data
- Analytics dashboard per segment

### Past Client Segments
1. 65+ Not Retired Yet (1,202)
2. 30-45yo Growing Families (490)
3. High-Equity, High-Rate Trapped Movers (512)
4. 65+ All-Cash Owners (432)
5. Large-Home Owners (1,726)
6. Cash Renters / 2020-22 Sellers (333)
7. WARN-List / Job Change (0)
8. High-Intent Website Visitors (0)
9. Equity Comfort Tiers (Dynamic)
10. Young All-Cash Owners (186)

### Analytics
- Demographic breakdowns
- Equity distribution charts
- Age range analysis
- Top ZIP codes
- Average home values and interest rates

## ⚙️ Environment Variables

Set these on Heroku:

```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here
```

## 📊 Post-Deployment

### View Your App
```bash
heroku open
```

### Monitor Logs
```bash
heroku logs --tail
```

### Restart App
```bash
heroku restart
```

## 💾 Data Persistence

⚠️ **Important**: Heroku uses ephemeral storage. Uploaded files are lost on dyno restart.

### Recommended Solutions:
1. **Add Postgres**: `heroku addons:create heroku-postgresql:mini`
2. **Use S3**: Store uploads in Amazon S3
3. **Export regularly**: Download campaign/audience data

## 💰 Pricing

- **Free Tier**: $0/month (sleeps after 30 min inactivity)
- **Hobby Dyno**: $7/month (recommended, no sleep)
- **Postgres Mini**: $5/month (for data persistence)

## 🔧 Troubleshooting

### App Won't Start
```bash
heroku logs --tail
heroku restart
```

### Missing Dependencies
```bash
heroku buildpacks:set heroku/python
git push heroku main
```

### File Upload Issues
- Files are stored temporarily
- Consider adding Postgres or S3 for persistence

## 📞 Support

- **Heroku Docs**: [devcenter.heroku.com](https://devcenter.heroku.com/)
- **Heroku Status**: [status.heroku.com](https://status.heroku.com/)
- **Heroku Support**: Available through dashboard

## 🎉 Success!

Once deployed, your Keyes Campaign System will be live at:
`https://your-app-name.herokuapp.com`

Access the dashboard at:
`https://dashboard.heroku.com/apps/your-app-name`

---

**Built with:** Flask, Python, Pandas, OpenPyXL
**Brand Colors:** Dark Green (#004237), Peachy (#fcbfa7)
**Version:** 1.0.0

