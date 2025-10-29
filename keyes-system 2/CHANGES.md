# Rebranding Changes - MetroBrokers to The Keyes Company

## Summary

Complete rebrand of the past client campaign system from MetroBrokers to The Keyes Company, including visual identity, messaging, and technical updates.

## Brand Identity Changes

### Logo & Name
- **Before**: "metrobrokers" (lowercase, orange accent)
- **After**: "The *Keyes* Company" (italic Keyes in Georgia serif font, cream accent)

### Tagline
- **Before**: "Expect Better"
- **After**: "You're Home Here"

### Campaign Name
- **Before**: "Next Chapter Campaign"
- **After**: "Your Home Equity Campaign"

### Color Palette

| Element | MetroBrokers | The Keyes Company |
|---------|--------------|-------------------|
| Primary | #5a9f3e (Green) | #114d43 (Everglade Green) |
| Dark Accent | #4a8533 | #0d3d35 (Dark Teal) |
| Secondary | #f7931e (Orange) | #e8d5c4 (Miami Sands) |
| Light Accent | #e67e00 | #d4c0af (Light Sand) |

## File-by-File Changes

### app.py
- Updated all "MetroBrokers" references to "The Keyes Company"
- Changed color scheme throughout dashboard
- Updated logo HTML to include italic styling for "Keyes"
- Modified tagline from "Next Chapter Campaign Dashboard" to "Your Home Equity Campaign Dashboard"
- Fixed file paths to use relative paths instead of absolute paths

### email_template.html
- Rebranded header with new logo and colors
- Changed headline from "Planning your next chapter? Expect Better" to "Ready to unlock your home equity? You're Home Here"
- Updated "Together, We're Better" to "The Keyes Difference"
- Applied Everglade Green gradient to header background
- Changed all button and accent colors to match Keyes palette
- Updated form action URL placeholder from metrobrokers to keyes

### render.yaml
- Changed service name from "metrobrokers-dashboard" to "keyes-dashboard"
- Updated all references in configuration

### README.md
- Completely rewritten with Keyes Company information
- Added brand heritage section (founded 1926, 100-year anniversary 2026)
- Updated all examples and URLs to use "keyes" instead of "metrobrokers"
- Added Keyes color palette documentation
- Included "You're Home Here" tagline throughout

### DEPLOY.md
- New deployment guide written specifically for Keyes system
- Updated all example URLs and repository names
- Added Keyes-specific customization instructions
- Updated form action URL examples

## Visual Design Changes

### Dashboard
- **Sidebar Background**: Maintained dark theme but updated accent colors
- **Stat Cards**: Changed from green (#5a9f3e) to Everglade Green (#114d43)
- **Buttons**: Updated gradient from green/orange to teal/cream
- **Logo**: Changed to "The *Keyes* Company" with italic styling

### Email Template
- **Header**: Deep teal gradient background (Everglade Green)
- **Logo Text**: Cream/sand color (#e8d5c4) for "Keyes"
- **CTA Buttons**: Everglade Green with hover effects
- **Form Elements**: Teal accents on radio buttons and checkboxes
- **Overall Tone**: More sophisticated, heritage-focused

## Messaging Changes

### Key Phrases Updated

| Original | New |
|----------|-----|
| "Planning your next chapter?" | "Ready to unlock your home equity?" |
| "Expect Better" | "You're Home Here" |
| "Together, We're Better" | "The Keyes Difference" |
| "MetroBrokers Real Estate" | "The Keyes Company Real Estate" |

### Maintained Elements
- Equity range: $583k-$788k (kept same)
- Two-question form structure
- Goal options (buy before sell, downsize, etc.)
- Submission tracking functionality
- CSV export capability

## Technical Improvements

### Path Handling
- Fixed hardcoded `/home/ubuntu/` paths
- Implemented relative path resolution
- Made system portable across different environments

### Deployment
- Updated render.yaml for Keyes branding
- Maintained compatibility with all deployment platforms
- No changes to core Flask functionality

## Brand Personality Shift

### MetroBrokers
- Modern, energetic
- Bold green and orange
- "Expect Better" - aspirational
- Contemporary feel

### The Keyes Company
- Heritage, established
- Sophisticated teal and cream
- "You're Home Here" - welcoming, personal
- Classic Florida elegance
- Nearly 100 years of trust

## Files Added

- `QUICKSTART.md` - Quick deployment guide
- `CHANGES.md` - This file
- Brand assets saved during research

## Files Modified

- `app.py` - Complete rebrand
- `email_template.html` - Complete rebrand
- `render.yaml` - Updated configuration
- `README.md` - Rewritten for Keyes
- `DEPLOY.md` - Rewritten for Keyes
- `requirements.txt` - No changes (same dependencies)

## Testing Notes

- Dashboard renders correctly with new branding
- Email template displays properly in browser
- Form submission endpoint maintains same API
- CSV export functionality unchanged
- All routes functional

## Migration Path

For existing MetroBrokers deployments:

1. Backup existing `submissions.json` data
2. Deploy Keyes system to new URL
3. Update email campaign form action URLs
4. Test submission flow
5. Import historical data if needed
6. Redirect old URLs (optional)

## Brand Compliance

All changes align with The Keyes Company's official rebrand (November 2024):
- ✅ Everglade Green primary color
- ✅ Miami Sands accent color
- ✅ "You're Home Here" tagline
- ✅ Script/italic Keyes logo style
- ✅ Florida heritage messaging
- ✅ Sophisticated, welcoming tone

---

**Rebrand completed**: October 27, 2025  
**Source system**: MetroBrokers Past Client Campaign  
**Target brand**: The Keyes Company  
**Status**: Ready for deployment

