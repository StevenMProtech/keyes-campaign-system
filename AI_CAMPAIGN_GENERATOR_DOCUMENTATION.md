# AI Campaign Generator - Complete Documentation

## Overview

The AI Campaign Generator is a comprehensive system that automatically creates conversion-focused email campaigns using Harry Dry's 25 copywriting principles. It analyzes audience segments and generates personalized content including subject lines, headlines, body copy, callout boxes, and form questions.

## Features

### 1. Segment-Specific Content Generation
- **5 Audience Segments:**
  - All Cash Buyers
  - Absentee Owner (In-State)
  - Absentee Owner (Out-of-State)
  - General Past Clients
  - Homes Over $2,000,000

- **Segment Profiles Include:**
  - Demographics
  - Psychographics
  - Communication Style
  - Pain Points
  - Goals

### 2. Complete Campaign Content
The AI generates:
- Email Subject Line
- Main Headline
- Subheadline
- Body Copy (full paragraph)
- Call-to-Action Button Text
- **Callout Box:**
  - Title
  - Main Text
  - Subtitle
- **Form Question 1 (Radio Buttons):**
  - Question Text
  - Subtitle
  - 4 Options with Labels and Descriptions
- **Form Question 2 (Checkboxes):**
  - Question Text
  - Subtitle
  - 4 Options
- **Form Question 3 (Radio Buttons):**
  - Question Text
  - Subtitle
  - 4 Options
- **Explanation:** Why the copy works (Harry Dry principles applied)

### 3. Harry Dry's 25 Copywriting Principles

The AI applies these principles automatically:

1. **Show transformation** - What changes after they act
2. **Tell their story** - Mirror their situation
3. **Use presets** - Give clear options, don't make them think
4. **Avoid making them think** - Simple, clear choices
5. **Personal pronouns** - You, we, your (not "the client")
6. **Short sentences** - Easy to read and scan
7. **Start with conjunctions** - And, Or, So, But
8. **Avoid jargon** - Plain English
9. **Avoid adjectives** - Show, don't tell
10. **Conversational tone** - Like talking to a friend
11. **Clear call-to-action** - One obvious next step
12. **Social proof** - 49 years, $2.28B sold
13. **Specificity** - Exact numbers, not ranges
14. **Address objections** - "No pressure", "No pitch"
15. **Use contractions** - We're, you're, it's
16. **Active voice** - "We helped you" not "You were helped"
17. **One idea per sentence** - Don't combine thoughts
18. **Use bullets for lists** - Easy to scan
19. **White space** - Let content breathe
20. **Visual hierarchy** - Important info stands out
21. **Personalization** - {{contact.firstname}}
22. **Urgency without pressure** - "Ready now" vs "Just exploring"
23. **Benefits over features** - What they get, not what we do
24. **Emotional connection** - Life changes, family, goals
25. **Respect intelligence** - Don't talk down, especially to sophisticated buyers

## Technical Implementation

### Backend Files

#### 1. `ai_generator.py`
Main AI generation logic with:
- Segment profiles
- Harry Dry principles documentation
- OpenAI GPT-4.1-mini integration
- Campaign content generation function

**Key Functions:**
```python
def generate_campaign_content(segment_id, campaign_name=""):
    """Generate complete campaign content for a specific segment"""
    # Returns full campaign JSON with all fields
```

**API Endpoints:**
- `POST /api/generate-campaign` - Generate campaign content
- `GET /api/segment-profile/<segment_id>` - Get segment profile

#### 2. `app.py`
Flask application with:
- Campaign management routes
- AI generation endpoints
- Template rendering

**Key Routes:**
```python
@app.route('/campaign/new')
def campaign_new():
    """New campaign page with AI generator"""

@app.route('/api/generate-campaign', methods=['POST'])
def api_generate_campaign():
    """AI generation endpoint"""

@app.route('/api/segment-profile/<segment_id>')
def api_segment_profile(segment_id):
    """Segment profile endpoint"""
```

### Frontend Files

#### 1. `templates/campaign_new_complete.html`
Complete campaign creation page with:
- AI Campaign Generator section
- Segment profile viewer
- All form fields (basic + callout box + form questions)
- JavaScript auto-fill logic
- Explanation panel

**Key JavaScript Functions:**
```javascript
function updateSegmentProfile() {
    // Fetches and displays segment profile
}

function generateCampaign() {
    // Calls AI generation API
    // Auto-fills all form fields
    // Shows explanation panel
}
```

### API Response Format

```json
{
  "subject_line": "{{contact.firstname}} — unlock up to $1.2M liquidity fast",
  "headline": "Turn your equity into your next move",
  "subheadline": "Maximize proceeds, keep privacy, and close on your timeline",
  "body_copy": "We get it. You want to move, but you're watching...",
  "cta_button_text": "Show me my options — friendly 20 min chat",
  "callout_box": {
    "title": "Net proceeds you can count on",
    "main_text": "$850K–$1.2M unlocked quickly",
    "subtitle": "What would you do with that cash in hand?"
  },
  "form_questions": [
    {
      "question": "What's next for you?",
      "subtitle": "Pick what fits — we'll send you a plan",
      "type": "radio",
      "options": [
        {
          "label": "Buy before I sell",
          "description": "Secure your next home first"
        },
        {
          "label": "Sell and invest elsewhere",
          "description": "Deploy capital strategically"
        },
        {
          "label": "Consolidate or simplify",
          "description": "Reduce holdings or complexity"
        },
        {
          "label": "Estate or tax planning",
          "description": "Optimize for long-term goals"
        }
      ]
    },
    {
      "question": "What matters most?",
      "subtitle": "Check all that apply",
      "type": "checkbox",
      "options": [
        {"label": "Net proceeds"},
        {"label": "Speed and certainty"},
        {"label": "Privacy"},
        {"label": "Tax efficiency"}
      ]
    },
    {
      "question": "Timeline?",
      "subtitle": "No pressure — helps us help you",
      "type": "radio",
      "options": [
        {"label": "Within 60 days"},
        {"label": "3-6 months"},
        {"label": "6-12 months"},
        {"label": "Exploring options"}
      ]
    }
  ],
  "explanation": "This copy works because it speaks directly to cash buyers..."
}
```

## Usage Instructions

### For Developers

1. **Install Dependencies:**
```bash
cd /home/ubuntu/keyes-system
pip3 install openai
```

2. **Set Environment Variable:**
```bash
export OPENAI_API_KEY="your-api-key"
```

3. **Start Flask Server:**
```bash
PORT=5024 python3.11 app.py
```

4. **Access Application:**
```
http://localhost:5024/campaign/new
```

### For Users

1. **Navigate to New Campaign Page:**
   - Go to Campaign Management
   - Click "+ New Campaign"

2. **Select Target Segment:**
   - Choose from dropdown (All Cash Buyers, Absentee In-State, etc.)
   - Segment profile will appear automatically

3. **Generate Campaign with AI:**
   - Click "Generate Campaign with AI" button
   - Wait 10-15 seconds for generation
   - All fields will auto-fill

4. **Review Generated Content:**
   - Check subject line, headline, body copy
   - Review callout box content
   - Verify form questions and options
   - Read explanation panel

5. **Edit if Needed:**
   - All fields are editable
   - Make any adjustments to match your style
   - Add campaign name

6. **Create Campaign:**
   - Click "Create Campaign" button
   - Campaign will be saved to database

## Testing Results

### Test Case 1: General Past Clients
**Segment Profile:**
- Demographics: Diverse group, 30-70 years old
- Psychographics: Life transitions, growing families
- Communication Style: Warm, relationship-focused

**Generated Content:**
- Subject: "{{contact.firstname}}, you've got $350K+ ready to work for you"
- Headline: "Your home has changed. What's next?"
- Body: Warm, personal, focuses on life changes
- Callout: "Homes moved since 1976" / "$2.28B sold"
- Questions: Life stage focused (upgrade, downsize, relocate)

### Test Case 2: All Cash Buyers
**Segment Profile:**
- Demographics: High net worth, 45-70 years old
- Psychographics: Risk-averse, value privacy
- Communication Style: Direct, data-driven, no fluff

**Generated Content:**
- Subject: "{{contact.firstname}} — unlock up to $1.2M liquidity fast"
- Headline: "Turn your equity into your next move"
- Body: Direct, data-driven, focuses on proceeds and privacy
- Callout: "Net proceeds you can count on" / "$850K–$1.2M unlocked quickly"
- Questions: Financial focused (buy before sell, tax planning, net proceeds)

**Key Observation:** The AI successfully adapts tone, language, and focus based on audience segment!

## Performance Metrics

- **AI Response Time:** 10-15 seconds
- **Fields Auto-Filled:** 30+ fields
- **Success Rate:** 100% (both test cases)
- **User Experience:** Seamless, no manual intervention needed
- **Error Handling:** Graceful fallback with error messages

## Deployment Checklist

- [x] AI generator backend implemented
- [x] OpenAI integration working
- [x] All 5 segment profiles created
- [x] API endpoints functional
- [x] Frontend UI complete
- [x] JavaScript auto-fill working
- [x] Tested with 2 segments (General, All Cash)
- [ ] Test with remaining 3 segments
- [ ] Production environment setup
- [ ] Environment variables configured
- [ ] Error logging implemented
- [ ] User documentation created

## Future Enhancements

1. **Additional Segments:**
   - First-time buyers
   - Investors
   - Luxury sellers

2. **A/B Testing:**
   - Generate multiple variations
   - Track performance metrics

3. **Learning System:**
   - Analyze which campaigns perform best
   - Improve AI prompts based on results

4. **Multi-language Support:**
   - Spanish translations
   - Other languages as needed

5. **Image Generation:**
   - Auto-generate campaign images
   - Match visual style to segment

6. **Email Preview:**
   - Real-time preview of generated email
   - Mobile and desktop views

7. **Campaign Analytics:**
   - Track open rates, click rates
   - Segment performance comparison

## Troubleshooting

### Issue: AI Generation Fails
**Solution:** Check OpenAI API key and internet connection

### Issue: Fields Not Auto-Filling
**Solution:** Check browser console for JavaScript errors

### Issue: Segment Profile Not Showing
**Solution:** Verify segment ID in dropdown matches profile keys

### Issue: Slow Generation
**Solution:** Normal for complex prompts, wait 15-20 seconds

## Support

For questions or issues:
- Check Flask logs: `tail -f nohup.out`
- Check browser console: F12 → Console tab
- Review API response in Network tab

## Credits

- **Harry Dry's Marketing Examples:** https://marketingexamples.com
- **OpenAI GPT-4.1-mini:** AI content generation
- **The Keyes Company:** 49 years of real estate excellence

## License

Proprietary - The Keyes Company

