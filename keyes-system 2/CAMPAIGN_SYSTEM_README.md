# Keyes Multi-Campaign System - Documentation

## Overview

The Keyes campaign system has been enhanced to support **multiple email campaigns** with full CRUD (Create, Read, Update, Delete) capabilities. You can now create, edit, and track multiple campaigns while maintaining your currently deployed campaign.

## Key Features

### 1. **Campaign Management**
- Create new campaigns with custom copy and branding
- Edit existing campaign content (headlines, body copy, CTA text, etc.)
- Change campaign status (Active, Draft, Paused, Archived)
- View all campaigns with real-time statistics
- Preview email templates for each campaign

### 2. **Per-Campaign Tracking**
- All form submissions are automatically linked to their source campaign
- View submissions filtered by campaign
- Export CSV data with campaign attribution
- Track campaign performance with dedicated analytics

### 3. **Campaign Analytics**
- Total submissions per campaign
- Pending submissions count
- Last submission timestamp
- Priority distribution (Maximize, Speed, Balance)

## New Routes

### Campaign Management Pages

| Route | Description |
|-------|-------------|
| `/campaigns` | List all campaigns with stats and quick actions |
| `/campaign/new` | Create a new campaign |
| `/campaign/{campaign_id}` | View campaign details and submissions |
| `/campaign/{campaign_id}/edit` | Edit campaign content and settings |
| `/campaign/{campaign_id}/preview` | Preview campaign email template |

### Updated Routes

| Route | Changes |
|-------|---------|
| `/` | Added "Manage Campaigns" button to Quick Actions |
| `/submissions` | Added "Campaign" column to show which campaign each submission came from |
| `/export` | CSV export now includes "Campaign ID" column |
| `/api/submit` | Now accepts `campaign_id` parameter to track submission source |

## Data Structure

### Campaign Object
```json
{
  "id": "home-equity-2025",
  "name": "Home Equity Strategy 2025",
  "status": "active",
  "created_at": "2025-01-15 10:00:00",
  "updated_at": "2025-01-15 10:00:00",
  "subject": "Unlock Your Home's Hidden Wealth",
  "headline": "Your Fresh Start, Starts Here",
  "subheadline": "Discover how much equity you could unlock...",
  "cta_text": "Get Your Free Equity Strategy",
  "body_copy": "Your home isn't just where you live...",
  "form_fields": {
    "email": true,
    "firstName": true,
    "lastName": true,
    "phoneNumber": true,
    "equity_priority": true,
    "goals": true,
    "wantsReport": true,
    "wantsExpert": true
  },
  "colors": {
    "primary": "#004237",
    "accent": "#fcbfa7",
    "background": "#f7f3e5"
  }
}
```

### Submission Object (Updated)
```json
{
  "id": 1,
  "timestamp": "2025-01-20 14:30:00",
  "campaign_id": "home-equity-2025",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "equity_priority": "maximize",
  "goals": "retirement,investment",
  "goals_text": "Planning for early retirement",
  "phone_number": "555-1234",
  "wants_equity_report": true,
  "wants_expert_contact": true,
  "status": "pending"
}
```

## How to Use

### Creating a New Campaign

1. Navigate to **Dashboard** → **Manage Campaigns**
2. Click **"+ New Campaign"**
3. Fill in the campaign details:
   - Campaign Name (internal use)
   - Email Subject Line
   - Main Headline
   - Subheadline
   - Body Copy
   - Call-to-Action Button Text
   - Campaign Status
4. Click **"Create Campaign"**

### Editing an Existing Campaign

1. Go to **Campaigns** page
2. Find the campaign you want to edit
3. Click **"Edit Campaign"**
4. Update any fields you want to change
5. Click **"Save Changes"**
6. Use **"Preview Email"** to see how it looks

### Tracking Campaign Performance

1. Go to **Campaigns** page to see overview stats for all campaigns
2. Click **"View Details"** on any campaign to see:
   - Total submissions
   - Pending submissions
   - Priority distribution
   - Full list of submissions for that campaign

### Linking Forms to Campaigns

When creating email templates or landing pages, include the campaign ID in the form submission:

**Option 1: Hidden Form Field**
```html
<form action="https://keyes-4pmx.onrender.com/api/submit" method="POST">
  <input type="hidden" name="campaign_id" value="your-campaign-id">
  <!-- other form fields -->
</form>
```

**Option 2: Query Parameter**
```html
<form action="https://keyes-4pmx.onrender.com/api/submit?campaign_id=your-campaign-id" method="POST">
  <!-- form fields -->
</form>
```

If no campaign_id is provided, submissions default to `home-equity-2025` (your current campaign).

## File Structure

```
keyes-system/
├── app.py                          # Main Flask application (updated)
├── campaigns.json                  # Campaign data storage (new)
├── submissions.json                # Submission data storage (existing)
├── email_template.html             # Original email template (existing)
├── static/
│   └── keyes-logo.png             # Keyes logo (existing)
└── CAMPAIGN_SYSTEM_README.md      # This documentation (new)
```

## Deployment

To deploy the updated system:

1. Upload the updated `app.py` to your GitHub repository
2. Upload the new `campaigns.json` file
3. Upload this `CAMPAIGN_SYSTEM_README.md` for reference
4. Render will automatically redeploy with the new features

## Maintaining Your Current Campaign

Your currently deployed campaign (`home-equity-2025`) is preserved in `campaigns.json`. All existing submissions will continue to work, and new submissions from your current email template will be tracked under this campaign.

## Best Practices

1. **Campaign Naming**: Use descriptive names that indicate the campaign's purpose and timeframe
2. **Campaign IDs**: Are auto-generated from campaign names (lowercase, hyphens instead of spaces)
3. **Status Management**: 
   - Use "Draft" for campaigns you're still working on
   - Use "Active" for live campaigns
   - Use "Paused" for temporarily inactive campaigns
   - Use "Archived" for completed campaigns
4. **Testing**: Always preview campaigns before deploying them
5. **Tracking**: Include campaign_id in all email templates and landing pages

## Support

For questions or issues with the campaign system, refer to this documentation or review the code comments in `app.py`.

---

**System Version**: Multi-Campaign v2.0  
**Last Updated**: October 28, 2025  
**Keyes Brand Colors**: Dark Teal (#004237), Coral (#fcbfa7), Cream (#f7f3e5)

