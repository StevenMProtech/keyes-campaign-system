# Deploy Updated Keyes System to Render

## Quick Deploy Instructions

Your Keyes campaign system is ready to deploy with all the latest updates including the proper logo and fixed routes.

### Option 1: Connect to Existing Render Service (Recommended)

Since you already have `keyes-4pmx.onrender.com` running, you need to update it:

1. **Go to your Render dashboard**: https://dashboard.render.com/

2. **Find your service** `keyes-4pmx`

3. **Connect to Git** (if not already connected):
   - Click on your service
   - Go to "Settings"
   - Under "Build & Deploy", connect your GitHub/GitLab repo
   - OR use "Manual Deploy" option below

4. **Push this code to your connected repo**:
   ```bash
   cd /path/to/keyes-system
   git remote add origin YOUR_REPO_URL
   git push -u origin master
   ```

5. **Render will auto-deploy** when it detects the push

### Option 2: Manual Deploy (If No Git Connected)

1. **Download the complete system**:
   - Get the `keyes-COMPLETE-SYSTEM.tar.gz` file
   - Extract it locally

2. **Go to Render Dashboard**:
   - Navigate to your `keyes-4pmx` service
   - Click "Manual Deploy" → "Deploy latest commit"
   - OR delete and recreate the service with new files

3. **Upload via Render's interface**:
   - Some services allow file upload
   - Check your service settings

### Option 3: Create New Render Service

If you want to start fresh:

1. **Push to GitHub** (create new repo):
   ```bash
   # On your local machine after downloading the files
   cd keyes-system
   git remote add origin https://github.com/YOUR_USERNAME/keyes-campaign.git
   git push -u origin master
   ```

2. **Create new Render service**:
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render will detect `render.yaml` and configure automatically
   - Click "Create Web Service"

3. **Service will deploy automatically**

### What's Fixed in This Update

✅ Actual Keyes logo (embedded base64 in email, image file for dashboard)  
✅ Correct brand colors (#004237 teal, #fcbfa7 coral, #f7f3e5 cream)  
✅ Cream/beige header background so green logo shows  
✅ `/submissions` route working  
✅ Dashboard logo updated  
✅ All routes functional  

### Verify Deployment

After deploying, test these URLs:

- `https://keyes-4pmx.onrender.com/` - Dashboard (should show logo)
- `https://keyes-4pmx.onrender.com/submissions` - Submissions page (should work now)
- `https://keyes-4pmx.onrender.com/test` - Email preview
- `https://keyes-4pmx.onrender.com/export` - CSV export

### Files Included

```
keyes-system/
├── app.py                    # Flask application (updated logo)
├── email_template.html       # Email with embedded logo
├── requirements.txt          # Python dependencies
├── render.yaml              # Render configuration
├── static/
│   └── keyes-logo.png       # Logo for dashboard
├── README.md                # Documentation
├── DEPLOY.md                # Deployment guide
└── QUICKSTART.md            # Quick start guide
```

### Troubleshooting

**If deployment fails:**

1. Check Render logs for errors
2. Verify `requirements.txt` has all dependencies
3. Ensure `render.yaml` is properly configured
4. Check that Python version matches (3.11)

**If logo doesn't show:**

1. Clear browser cache
2. Check that `static/keyes-logo.png` exists
3. Verify Flask is serving static files

**If submissions page still shows "Not Found":**

1. Verify the updated `app.py` was deployed
2. Check Render logs for route registration
3. Restart the service manually

### Support

If you encounter issues:
- Check Render's build logs
- Verify all files were uploaded
- Ensure environment variables are set (if any)
- Try manual redeploy from Render dashboard

---

**Ready to deploy!** Choose your preferred method above and your Keyes campaign system will be live with all the latest updates.

