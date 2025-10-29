# Deployment Guide - The Keyes Company Campaign System

## Quick Start (5 Minutes)

The fastest way to get this live is using **Render.com** (completely free, no credit card required).

## Step-by-Step: Render.com Deployment

### 1. Prepare Your Repository

```bash
# If you haven't already, initialize git
git init
git add .
git commit -m "Initial commit - Keyes campaign system"

# Create a GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/keyes-campaign.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Render

1. Go to [https://render.com](https://render.com)
2. Sign up (free account, no credit card needed)
3. Click **"New +"** button in top right
4. Select **"Web Service"**
5. Click **"Connect GitHub"** and authorize Render
6. Select your `keyes-campaign` repository
7. Render will auto-detect the `render.yaml` configuration
8. Click **"Create Web Service"**

### 3. Configuration (Auto-Detected)

Render will automatically use these settings from `render.yaml`:

- **Name**: keyes-dashboard
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Port**: 5002

### 4. Wait for Deployment

- First deployment takes 2-3 minutes
- You'll see build logs in real-time
- Once complete, you'll get a live URL like: `https://keyes-dashboard.onrender.com`

### 5. Test Your Deployment

Visit these URLs (replace with your actual domain):

- `https://keyes-dashboard.onrender.com/` - Main dashboard
- `https://keyes-dashboard.onrender.com/test` - Email test page
- `https://keyes-dashboard.onrender.com/api/submissions` - API endpoint

## Alternative Deployment Options

### Railway.app (Also Free)

1. Go to [https://railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Railway auto-detects Python and deploys
7. Get your URL from the dashboard

**Pros**: Faster cold starts than Render  
**Cons**: $5 free credit (lasts months for low traffic)

### Vercel (Free)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd keyes-system
vercel

# Follow prompts
# Your app will be live at: https://keyes-campaign.vercel.app
```

**Pros**: Lightning-fast CDN, great for static content  
**Cons**: Serverless functions have execution time limits

### PythonAnywhere (Free Tier)

1. Go to [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Create free account
3. Go to **"Files"** tab
4. Upload all files from `keyes-system` folder
5. Go to **"Web"** tab
6. Click **"Add a new web app"**
7. Choose **"Flask"**
8. Point to your `app.py` file
9. In **"Virtualenv"** section, install requirements:
   ```bash
   pip install -r requirements.txt
   ```
10. Reload web app

**Pros**: Always-on, no cold starts  
**Cons**: Limited CPU time on free tier

## Post-Deployment Setup

### 1. Update Email Template Form Action

After deployment, update the form action URL in `email_template.html`:

```html
<!-- Line 49 in email_template.html -->
<form action="https://YOUR-ACTUAL-DOMAIN.com/api/submit" method="POST">
```

Replace `YOUR-ACTUAL-DOMAIN.com` with your live URL.

### 2. Test the Form

1. Visit `/test` route
2. Fill out the form
3. Submit
4. Check `/submissions` to see the data
5. Try `/export` to download CSV

### 3. Integrate with Email Platform

#### For HubSpot:
1. Go to Marketing → Email → Create Email
2. Switch to HTML editor
3. Paste contents of `email_template.html`
4. Update form action URL to your live domain
5. Use HubSpot personalization tokens:
   - `{{ contact.email }}`
   - `{{ contact.firstname }}`
   - `{{ contact.lastname }}`

#### For Mailchimp:
1. Create Campaign → Code Your Own
2. Paste HTML
3. Update form action URL
4. Use merge tags: `*|EMAIL|*`, `*|FNAME|*`, `*|LNAME|*`

#### For ActiveCampaign:
1. Create Campaign → HTML editor
2. Paste HTML
3. Update form action URL
4. Use personalization tags: `%EMAIL%`, `%FIRSTNAME%`, `%LASTNAME%`

## Monitoring & Maintenance

### Check Submissions

- **Dashboard**: `https://your-domain.com/`
- **JSON API**: `https://your-domain.com/api/submissions`
- **CSV Export**: `https://your-domain.com/export`

### Data Backup

Submissions are stored in `submissions.json`. To backup:

1. Download via SFTP/SSH (if available)
2. Or use the `/export` CSV endpoint regularly
3. For production, upgrade to PostgreSQL:
   - Render offers free PostgreSQL
   - Railway offers free PostgreSQL
   - Update `app.py` to use SQLAlchemy

### Scaling Considerations

The current setup uses JSON file storage, which works for:
- Up to ~1,000 submissions
- Low to moderate traffic
- Single server instance

For higher volume:
1. Migrate to PostgreSQL (Render/Railway offer free tier)
2. Add Redis for caching
3. Use Render's auto-scaling

## Troubleshooting

### Issue: Form submissions not saving

**Solution**: Check that the form action URL matches your deployed domain

### Issue: Email template not loading

**Solution**: Verify `email_template.html` is in the same directory as `app.py`

### Issue: 500 Internal Server Error

**Solution**: Check logs in your deployment platform:
- Render: Click "Logs" tab
- Railway: Click "Deployments" → View logs
- Vercel: Check Functions logs

### Issue: Cold starts (Render free tier)

**Solution**: 
- Free tier sleeps after 15 minutes of inactivity
- First request takes ~30 seconds to wake up
- Upgrade to paid tier ($7/month) for always-on

## Security Notes

- No sensitive data is stored (only email, name, preferences)
- CORS is enabled for form submissions
- For production, consider adding:
  - Rate limiting
  - CAPTCHA on forms
  - HTTPS enforcement (automatic on Render/Vercel)
  - Input validation/sanitization

## Custom Domain Setup

### Render.com

1. Go to your service dashboard
2. Click "Settings" → "Custom Domain"
3. Add your domain (e.g., `campaign.keyes.com`)
4. Add CNAME record in your DNS:
   - Name: `campaign`
   - Value: `keyes-dashboard.onrender.com`
5. Wait for SSL certificate (automatic)

### Railway.app

1. Go to project settings
2. Click "Domains"
3. Add custom domain
4. Update DNS CNAME as instructed

## Support Resources

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Flask Docs**: https://flask.palletsprojects.com

---

**Need Help?** Check the deployment platform's documentation or community forums.

