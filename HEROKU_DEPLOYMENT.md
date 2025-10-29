# Keyes Campaign System - Heroku Deployment Guide

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Ensure Git is installed on your machine

## Deployment Steps

### 1. Initialize Git Repository (if not already done)

```bash
cd /path/to/keyes-system
git init
git add .
git commit -m "Initial commit - Keyes Campaign System"
```

### 2. Login to Heroku

```bash
heroku login
```

This will open a browser window for authentication.

### 3. Create Heroku App

```bash
heroku create keyes-campaign-system
```

Or use a custom name:

```bash
heroku create your-custom-app-name
```

### 4. Add Buildpack (if needed)

```bash
heroku buildpacks:set heroku/python
```

### 5. Configure Environment Variables

```bash
# Set any environment variables your app needs
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here
```

### 6. Deploy to Heroku

```bash
git push heroku main
```

Or if your branch is named `master`:

```bash
git push heroku master
```

### 7. Scale the Web Dyno

```bash
heroku ps:scale web=1
```

### 8. Open Your App

```bash
heroku open
```

## Post-Deployment

### View Logs

```bash
heroku logs --tail
```

### Restart App

```bash
heroku restart
```

### Run Commands

```bash
heroku run python
```

## File Storage Considerations

⚠️ **Important**: Heroku uses an ephemeral filesystem. Uploaded files (like client data CSVs) will be lost when the dyno restarts.

### Solutions:

1. **Amazon S3**: Store uploaded files in S3
2. **Heroku Postgres**: Store data in a database instead of files
3. **Redis**: Use for temporary data storage

### Recommended: Add Postgres Database

```bash
heroku addons:create heroku-postgresql:mini
```

Then update `app.py` to use PostgreSQL instead of JSON files.

## Custom Domain

### Add Custom Domain

```bash
heroku domains:add www.yourdomain.com
```

### Configure DNS

Add a CNAME record pointing to your Heroku app URL.

## SSL Certificate

Heroku provides free SSL certificates for custom domains:

```bash
heroku certs:auto:enable
```

## Monitoring

### View App Metrics

```bash
heroku ps
heroku logs --tail
```

### Add Monitoring (Optional)

```bash
heroku addons:create papertrail
heroku addons:create newrelic
```

## Troubleshooting

### App Crashes

```bash
heroku logs --tail
heroku restart
```

### Check Dyno Status

```bash
heroku ps
```

### Debug Mode

```bash
heroku config:set DEBUG=True
```

## Updating the App

```bash
git add .
git commit -m "Update description"
git push heroku main
```

## Cost Estimate

- **Hobby Dyno**: $7/month (recommended for production)
- **Free Dyno**: $0/month (sleeps after 30 min of inactivity)
- **Postgres Mini**: $5/month (if using database)

## Support

For issues, contact Heroku support or check:
- [Heroku Dev Center](https://devcenter.heroku.com/)
- [Heroku Status](https://status.heroku.com/)

---

**Your App URL**: `https://your-app-name.herokuapp.com`

**Dashboard**: `https://dashboard.heroku.com/apps/your-app-name`

