"""
AI Campaign Generator for Keyes Real Estate
Applies all 25 Harry Dry copywriting principles to generate segment-specific campaigns
"""

from openai import OpenAI
import json
import os

client = OpenAI()

# All 25 Harry Dry Principles
HARRY_DRY_PRINCIPLES = """
1. Add warmth to CTA (face image, name, reassurance - "friendly tour, not a sales pitch")
2. Don't use adjectives if possible
3. Don't make the client think - presets are best when segmenting
4. Don't show a logo, show the transformation
5. Tease the content in ads
6. Show the product in action
7. Make the copy shorter
8. Don't write AT the readers
9. Use your customers' words
10. Load up on personal pronouns (you, your, we)
11. Don't worry about grammar
12. Start sentences with conjunctions (And, But, So)
13. Don't persuade - let the reader be persuaded
14. Use contractions (we'll, you've, it's)
15. Don't imitate
16. Ditch the thesaurus
17. Empathize
18. Respect the competition
19. Don't try too hard
20. Tell stories
21. Read it aloud
22. Differentiate through contrast (point at status quo)
23. Invent a new category (no competitors)
24. Go all-in on one niche or feature
25. Positioning needs a story behind it
"""

# Segment Analysis Data
SEGMENT_PROFILES = {
    "all-cash": {
        "name": "All Cash Buyers",
        "demographics": "High net worth individuals, 45-70 years old, financially sophisticated",
        "psychographics": "Risk-averse, value privacy, appreciate discretion, want efficiency",
        "pain_points": [
            "Worried about market timing for next move",
            "Concerned about tax implications of selling",
            "Want to maximize equity without hassle",
            "Need liquidity for next opportunity"
        ],
        "motivations": [
            "Unlock equity for next investment",
            "Downsize or upgrade lifestyle",
            "Relocate for family or retirement",
            "Portfolio rebalancing"
        ],
        "communication_style": "Direct, data-driven, no fluff, respect their intelligence",
        "decision_factors": ["Speed of transaction", "Net proceeds", "Privacy", "Convenience"]
    },
    "absentee-instate": {
        "name": "Absentee Owner (In-State)",
        "demographics": "Property investors, 35-65 years old, own 2+ properties in Florida",
        "psychographics": "Business-minded, ROI-focused, time-constrained, strategic thinkers",
        "pain_points": [
            "Managing properties from a distance is exhausting",
            "Maintenance costs eating into returns",
            "Market conditions changing, unsure if should hold or sell",
            "Property manager issues or vacancy concerns"
        ],
        "motivations": [
            "Optimize portfolio performance",
            "1031 exchange into better property",
            "Cash out appreciated assets",
            "Reduce management headaches"
        ],
        "communication_style": "Business-focused, numbers-driven, appreciate options and scenarios",
        "decision_factors": ["ROI comparison", "Tax strategy", "Market timing", "Ease of transaction"]
    },
    "absentee-outstate": {
        "name": "Absentee Owner (Out-of-State)",
        "demographics": "Out-of-state investors or former residents, 40-70 years old",
        "psychographics": "Nostalgic about Florida, concerned about distance, want local expertise",
        "pain_points": [
            "Can't oversee property from out of state",
            "Worried about getting fair market value from afar",
            "Hurricane/insurance concerns growing",
            "Don't know current market conditions"
        ],
        "motivations": [
            "Simplify life by selling distant property",
            "Capitalize on Florida market appreciation",
            "Reduce risk exposure",
            "Consolidate assets closer to home"
        ],
        "communication_style": "Need reassurance, want local market expertise, appreciate transparency",
        "decision_factors": ["Trust in local expertise", "Market data", "Simplified process", "Fair pricing"]
    },
    "general": {
        "name": "General Past Clients",
        "demographics": "Diverse group, 30-70 years old, various financial situations",
        "psychographics": "Life transitions, growing families, career changes, lifestyle shifts",
        "pain_points": [
            "Life changed since last purchase",
            "Outgrew current home or need to downsize",
            "Job relocation or family needs",
            "Equity built up but not sure what to do"
        ],
        "motivations": [
            "Adapt home to current life stage",
            "Move closer to family or work",
            "Upgrade or downsize",
            "Take advantage of equity growth"
        ],
        "communication_style": "Warm, relationship-focused, appreciate personal touch and guidance",
        "decision_factors": ["Trust from past relationship", "Life fit", "Financial sense", "Timing flexibility"]
    },
    "homes-over-$2,000,000": {
        "name": "Homes Over $2,000,000",
        "demographics": "Ultra high net worth, 50-75 years old, sophisticated buyers",
        "psychographics": "Expect white-glove service, value discretion, want exclusive opportunities",
        "pain_points": [
            "Standard marketing won't work for luxury properties",
            "Need global buyer reach, not just local",
            "Privacy is paramount",
            "Want broker who understands luxury market nuances"
        ],
        "motivations": [
            "Upgrade to even higher-end property",
            "Consolidate multiple properties",
            "Lifestyle change (yacht, travel, second home)",
            "Estate planning considerations"
        ],
        "communication_style": "Sophisticated, expects expertise, values relationships and track record",
        "decision_factors": ["Broker's luxury market expertise", "Global reach", "Discretion", "Track record with high-value sales"]
    }
}

# Example email from Harry Dry PDF
EXAMPLE_EMAIL = """
Subject Line: Mike — you've got $488K sitting in your house

Mike,

We helped you buy at $500K.
Today it's worth $850K.

Most brokers will get you that. We get you 2% more*.
That's $17,000 more in your pocket.

What could you do with an extra $17K?
• Cover moving costs and still have $10K left
• Bigger down payment on your next place
• Upgrade something in your new home
• Just keep it

What's next for you?
(Pick what fits — we'll send you a plan)
☐ Buy my next home before selling
☐ Sell and move on
☐ Downsize
☐ Buy a second home or investment
☐ Relocate
☐ Something else

[Show Me My Options]
[picture] Michael Chen | 20 min, no pitch

Why we get 2% more:
• SG Refresh: We stage your home at no cost. First impressions drive value.
• Global reach: JamesEdition connects your home to qualified luxury buyers worldwide.
• 49 years of relationships: We know the buyers before they're looking.

"She's handled over 13 transactions for me. Always attentive, fantastic negotiator."
— Client since 2005

Seven Gables | $2.28B sold | Since 1976
*2% more than the average broker in the CRMLS
"""


def generate_campaign_content(segment_id, campaign_name="", custom_prompt=""):
    """
    Generate complete campaign content for a specific segment
    using all Harry Dry principles
    
    Args:
        segment_id: The segment to target
        campaign_name: Optional campaign name
        custom_prompt: Optional custom instructions from user
    """
    
    # Try to load from hardcoded profiles first
    if segment_id in SEGMENT_PROFILES:
        profile = SEGMENT_PROFILES[segment_id]
    else:
        # Try behavioral_audiences.json
        try:
            with open('behavioral_audiences.json', 'r') as f:
                behavioral = json.load(f)
            audience = next((b for b in behavioral if b['id'] == segment_id), None)
            
            if not audience:
                # Try past_clients.json
                with open('past_clients.json', 'r') as f:
                    past_clients = json.load(f)
                audience = next((p for p in past_clients if p['id'] == segment_id), None)
            
            if audience:
                # Convert to profile format
                formula = audience.get('formula', '')
                count = audience.get('count', 0)
                description = audience.get('segment_summary', audience.get('description', ''))
                
                # Generate demographics from formula
                demographics = f"Segment size: {count:,} homeowners. "
                if 'Age' in formula or 'AGE' in formula:
                    demographics += "Age-based targeting. "
                if 'Equity' in formula or 'EQUITY' in formula:
                    demographics += "Equity-focused homeowners. "
                
                profile = {
                    "name": audience.get('audience_name', audience.get('name', 'Custom Audience')),
                    "demographics": demographics or 'Custom segment',
                    "psychographics": description,
                    "pain_points": [description, "Uncertain about home equity value"],
                    "motivations": ["Maximize home value", "Expert guidance"],
                    "communication_style": "Direct, benefit-focused",
                    "decision_factors": ["Market timing", "Transaction ease", "Trust"]
                }
            else:
                return {"error": f"Segment ID '{segment_id}' not found"}
        except FileNotFoundError as e:
            return {"error": f"File not found: {str(e)}"}
        except Exception as e:
            return {"error": f"Error loading segment: {str(e)}"}
    
    # Add custom prompt if provided
    custom_instructions = ""
    if custom_prompt:
        custom_instructions = f"\n\n**CRITICAL: CUSTOM INSTRUCTIONS FROM USER (HIGHEST PRIORITY):**\n{custom_prompt}\n\nYou MUST follow these custom instructions exactly. They override the default segment profile where there's a conflict. Still apply Harry Dry's principles, but adapt the copy to match these specific instructions.\n"
    
    # Build comprehensive prompt with custom instructions at the very top
    prompt_intro = "You are an expert copywriter for Keyes Real Estate (49 years in business, $2.28B sold since 1976).\n\n"
    
    if custom_prompt:
        prompt_intro += f"""⚠️ CRITICAL OVERRIDE - READ THIS FIRST ⚠️

The user has provided specific custom instructions that MUST take absolute priority over everything else:

\"{custom_prompt}\"

You MUST generate ALL copy (headline, body, questions, options) specifically for this exact situation. Ignore the default segment profile if it conflicts. The custom instructions describe the REAL audience you're writing for.

═══════════════════════════════════════════════════════════════

"""
    
    prompt = prompt_intro + f"""Generate a complete email campaign for this audience:

SEGMENT: {profile['name']}
DEMOGRAPHICS: {profile['demographics']}
PSYCHOGRAPHICS: {profile['psychographics']}
PAIN POINTS: {', '.join(profile['pain_points'])}
MOTIVATIONS: {', '.join(profile['motivations'])}
COMMUNICATION STYLE: {profile['communication_style']}
DECISION FACTORS: {', '.join(profile['decision_factors'])}

Apply ALL 25 Harry Dry Principles:
{HARRY_DRY_PRINCIPLES}

Study this example email that perfectly applies these principles:
{EXAMPLE_EMAIL}

Generate campaign content in this EXACT JSON format:
{{
  "campaign_name": "Short descriptive campaign name (e.g., 'Spring 2025 Luxury Equity' or 'Q2 Cash Buyer Outreach')",
  "subject_line": "Personalized subject with specific benefit (use merge tags like {{{{contact.firstname}}}}, include numbers)",
  "headline": "Main headline (short, transformation-focused, conversational)",
  "subheadline": "Supporting headline (builds on main headline, adds context)",
  "body_headline": "Bold headline for body section (e.g., '98 Years of Trust. Your Equity, Maximized.')",
  "body_copy": "MAXIMUM 2 sentences ONLY. Use contractions. Personal pronouns. Tell their story. Make it conversational. Keep total under 40 words. Wrap key insights (numbers, dollar amounts, important phrases) in <strong style='color: #004237;'>text</strong> tags for bold green highlighting.",
  "callout_box": {{
    "title": "Clear benefit statement",
    "main_text": "Big number or transformation (e.g., $583k–$788k)",
    "subtitle": "Emotional hook question or statement"
  }},
  "cta_button_text": "Action-oriented button text (warm, specific, e.g., 'GET MY EQUITY PLAN')",
  "cta_agent_message": "Personal reassuring message from agent (e.g., 'Sarah will create your custom equity plan in 24 hours')",
  "cta_tagline": "Italic tagline that removes friction (e.g., 'No sales pitch, just expert guidance')",
  "form_questions": [
    {{
      "question": "What's next for you?",
      "subtitle": "Pick what fits — we'll send you a plan",
      "type": "radio",
      "options": [
        {{"label": "Option 1", "description": "Brief description"}},
        {{"label": "Option 2", "description": "Brief description"}},
        {{"label": "Option 3", "description": "Brief description"}},
        {{"label": "Option 4", "description": "Brief description"}}
      ]
    }},
    {{
      "question": "What matters most to you?",
      "subtitle": "Check all that apply",
      "type": "checkbox",
      "options": [
        {{"label": "Option 1", "description": "Brief description"}},
        {{"label": "Option 2", "description": "Brief description"}},
        {{"label": "Option 3", "description": "Brief description"}},
        {{"label": "Option 4", "description": "Brief description"}}
      ]
    }},
    {{
      "question": "When are you thinking about this?",
      "subtitle": "No pressure — just helps us help you",
      "type": "radio",
      "options": [
        {{"label": "Option 1", "description": "Brief description"}},
        {{"label": "Option 2", "description": "Brief description"}},
        {{"label": "Option 3", "description": "Brief description"}},
        {{"label": "Option 4", "description": "Brief description"}}
      ]
    }}
  ],
  "why_section": {{
    "title": "Why we get better results:",
    "points": [
      "Point 1 with specific benefit",
      "Point 2 with specific benefit",
      "Point 3 with specific benefit"
    ]
  }},
  "testimonial": "One sentence testimonial from real client",
  "explanation": "2-3 paragraphs explaining: (1) Why this copy works for this segment, (2) Which Harry Dry principles were applied and how, (3) What makes this different from generic real estate copy"
}}

IMPORTANT:
- Use HubSpot merge tags: {{{{contact.firstname}}}}, {{{{contact.lastname}}}}, {{{{contact.email}}}}
- Make it sound like it's from a real person, not a company
- Every line must earn its space
- Read-aloud test quality
- Show transformation, not process
- Don't make them think - use clear presets
- Warm CTA with reassurance
- Specific numbers and benefits for this segment
- Tell THEIR story, not yours
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert copywriter who specializes in applying Harry Dry's principles to real estate marketing. You generate conversion-focused, segment-specific email campaigns."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        content = json.loads(response.choices[0].message.content)
        return content
        
    except Exception as e:
        return {"error": str(e)}


def get_segment_profile(segment_id):
    """Get detailed profile for a segment (static or behavioral)"""
    # Check static segments first
    if segment_id in SEGMENT_PROFILES:
        return SEGMENT_PROFILES[segment_id]
    
    # Check behavioral audiences
    try:
        import json
        with open('data/audiences.json', 'r') as f:
            audiences = json.load(f)
        
        for aud in audiences:
            if aud['id'] == segment_id:
                # Convert behavioral audience to segment profile format
                return {
                    "name": aud['audience_name'],
                    "demographics": aud.get('demographics', 'Custom behavioral audience'),
                    "psychographics": aud.get('psychographics', aud.get('segment_summary', '')),
                    "communication_style": aud.get('communication_style', 'Personalized based on behavior')
                }
    except:
        pass
    
    return None

