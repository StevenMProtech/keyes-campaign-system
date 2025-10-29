"""
AI Campaign Generator for Keyes Real Estate
Applies all 25 Harry Dry copywriting principles to generate segment-specific campaigns
"""

import json
import os
import requests

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
        "desires": [
            "Clean, fast transaction",
            "Maximum value with minimum exposure",
            "Trusted advisor who understands their wealth",
            "Privacy and discretion"
        ],
        "objections": [
            "Don't want to overpay in commission",
            "Concerned about market timing",
            "Worried about complexity of 1031 exchange",
            "Don't want property sitting on market"
        ],
        "unique_angle": "You paid cash because you value control. Now let's give you control of the timeline too."
    },
    "absentee-instate": {
        "name": "Absentee Owner (In-State)",
        "demographics": "Property investors, 35-65 years old, own 2+ properties in Florida",
        "psychographics": "Analytical, ROI-focused, time-constrained, want passive income",
        "pain_points": [
            "Managing property from distance is exhausting",
            "Worried about property condition deteriorating",
            "Tired of tenant issues and maintenance calls",
            "Want to redeploy capital more efficiently"
        ],
        "desires": [
            "Hands-off transaction process",
            "Quick close to free up capital",
            "Professional management of sale",
            "Clear path to 1031 exchange if needed"
        ],
        "objections": [
            "Don't have time to prep property for sale",
            "Worried about coordinating from afar",
            "Concerned about getting fair market value",
            "Don't want to deal with showings"
        ],
        "unique_angle": "We'll handle everything from here. You don't even need to visit the property."
    },
    "absentee-outstate": {
        "name": "Absentee Owner (Out-of-State)",
        "demographics": "Former Florida residents, retirees who moved, 50-75 years old",
        "psychographics": "Nostalgic but practical, want simplicity, trust local expertise",
        "pain_points": [
            "Can't oversee property from out of state",
            "Worried about getting taken advantage of",
            "Don't know current market conditions",
            "Tired of long-distance property management"
        ],
        "desires": [
            "Trustworthy local expert to handle everything",
            "Fair market value without games",
            "Simple, remote-friendly process",
            "Peace of mind"
        ],
        "objections": [
            "How can I trust someone I can't meet in person?",
            "Is the market good right now?",
            "Will I get a fair price?",
            "Too complicated to sell from afar"
        ],
        "unique_angle": "You trusted us when you lived here. We're still the same team—just with 49 more years of experience."
    },
    "general": {
        "name": "General Past Clients",
        "demographics": "Previous Keyes clients, all ages, homeowners in Florida",
        "psychographics": "Loyal, appreciate relationships, value expertise, life stage transitions",
        "pain_points": [
            "Life has changed since we bought",
            "Home doesn't fit our needs anymore",
            "Want to unlock equity for next chapter",
            "Market feels uncertain"
        ],
        "desires": [
            "Work with someone who knows our history",
            "Smooth transition to next home",
            "Maximize value of current home",
            "Trusted guidance through process"
        ],
        "objections": [
            "Is now the right time to sell?",
            "Can we afford to move up?",
            "What if we can't find the right next home?",
            "Worried about the hassle of moving"
        ],
        "unique_angle": "We helped you find this home. Now let's unlock what it's become."
    },
    "homes-over-$2,000,000": {
        "name": "Luxury Homeowners ($2M+)",
        "demographics": "Ultra high net worth, 45-75 years old, sophisticated buyers",
        "psychographics": "Expect excellence, value discretion, want white-glove service",
        "pain_points": [
            "Don't want property publicly listed",
            "Need privacy and discretion",
            "Worried about unqualified buyers wasting time",
            "Want expert who understands luxury market"
        ],
        "desires": [
            "Off-market opportunities",
            "Exclusive buyer network",
            "Concierge-level service",
            "Maximum value with minimum exposure"
        ],
        "objections": [
            "Will you protect my privacy?",
            "Can you actually find qualified buyers?",
            "What makes you different from other luxury agents?",
            "How long will this take?"
        ],
        "unique_angle": "Our $2.28B in sales gives you access to buyers most agents will never meet."
    }
}

# Keyes Company Background
KEYES_BACKGROUND = """
The Keyes Company - Florida's Most Trusted Real Estate Brand
49 years in business | $2.28B sold since 1976
Ranked #1 by volume in South Florida*

What makes us different:
- 49 years of local market expertise
- $2.28B in proven sales results
- Exclusive pre-MLS buyer network
- White-glove concierge service
- In-house mortgage, title, and insurance

Our sister companies:
Berkshire Hathaway HomeServices | $109B sold annually
Seven Gables | $2.28B sold | Since 1976
*2% more than the average broker in the CRMLS
"""


def generate_campaign_content(segment_id, campaign_name="", custom_prompt=""):
    """
    Generate complete campaign content for a specific segment
    using all Harry Dry principles - uses direct API calls instead of OpenAI client
    
    Args:
        segment_id: The segment to target
        campaign_name: Optional campaign name
        custom_prompt: Optional custom instructions from user
    """
    
    # Check if it's a standard segment profile
    if segment_id in SEGMENT_PROFILES:
        profile = SEGMENT_PROFILES[segment_id]
    else:
        # Try to load from behavioral audiences or past clients
        try:
            # Load behavioral audiences
            with open('behavioral_audiences.json', 'r') as f:
                behavioral = json.load(f)
            audience = next((a for a in behavioral if a['id'] == segment_id), None)
            
            if not audience:
                # Try past clients
                with open('past_clients.json', 'r') as f:
                    past_clients = json.load(f)
                audience = next((p for p in past_clients if p['id'] == segment_id), None)
            
            if audience:
                # Convert audience to profile format
                # Extract insights from formula if it's a past client segment
                formula = audience.get('formula', '')
                count = audience.get('count', 0)
                description = audience.get('segment_summary', audience.get('description', ''))
                
                # Generate demographics from formula
                demographics = f"Segment size: {count:,} homeowners. "
                if 'Age' in formula or 'AGE' in formula:
                    demographics += "Age-based targeting. "
                if 'Equity' in formula or 'EQUITY' in formula:
                    demographics += "Equity-focused homeowners. "
                if 'LENGTH_OF_RESIDENCE' in formula:
                    demographics += "Long-term residents. "
                if 'CURRENT_AVM_VALUE' in formula:
                    demographics += "Property value considerations. "
                
                # Generate psychographics from description and formula
                psychographics = description
                if 'Retired' in audience.get('name', '') or 'retirement' in description.lower():
                    psychographics += " Planning for retirement lifestyle changes."
                if 'equity' in description.lower():
                    psychographics += " Focused on maximizing home equity value."
                
                profile = {
                    "name": audience.get('audience_name', audience.get('name', 'Custom Audience')),
                    "demographics": demographics or 'Custom segment',
                    "psychographics": psychographics,
                    "pain_points": [description, "Uncertain about home equity value", "Market timing concerns"],
                    "desires": ["Maximize home value", "Smooth transaction", "Expert guidance"],
                    "objections": ["Market timing concerns", "Transaction complexity", "Commission costs"],
                    "unique_angle": f"{description}. Segment criteria: {formula}. Audience size: {count:,} qualified homeowners."
                }
            else:
                return {"error": f"Segment ID '{segment_id}' not found in behavioral_audiences.json or past_clients.json"}
        except FileNotFoundError as e:
            return {"error": f"File not found: {str(e)}. Make sure past_clients.json exists."}
        except Exception as e:
            return {"error": f"Error loading segment: {str(e)}"}
    
    # Build comprehensive prompt with custom instructions at the very top
    prompt_intro = "You are an expert copywriter for Keyes Real Estate (49 years in business, $2.28B sold since 1976).\n\n"
    
    if custom_prompt:
        prompt_intro += f"""⚠️ CRITICAL OVERRIDE - READ THIS FIRST ⚠️

The user has provided specific custom instructions that MUST take absolute priority over everything else:

"{custom_prompt}"

These instructions override any conflicting guidance below. Follow them exactly while still applying the Harry Dry principles where they don't conflict.

═══════════════════════════════════════════════════════════════

"""
    
    prompt = prompt_intro + f"""
Generate a complete email campaign for {profile['name']} using ALL 25 Harry Dry copywriting principles.

TARGET AUDIENCE PROFILE:
- Demographics: {profile['demographics']}
- Psychographics: {profile['psychographics']}
- Pain Points: {', '.join(profile['pain_points'])}
- Desires: {', '.join(profile['desires'])}
- Objections: {', '.join(profile['objections'])}
- Unique Angle: {profile['unique_angle']}

KEYES COMPANY BACKGROUND:
{KEYES_BACKGROUND}

HARRY DRY'S 25 COPYWRITING PRINCIPLES TO APPLY:
{HARRY_DRY_PRINCIPLES}

CRITICAL REQUIREMENTS:
1. Apply ALL 25 principles - don't skip any
2. Use "you/your" extensively (principle #10)
3. Keep copy conversational and warm (principles #7, #14, #17)
4. Tell a story (principle #20)
5. Differentiate from competition (principles #22, #23)
6. Make it feel personal, not corporate (principles #8, #9)
7. Use contractions naturally (principle #14)
8. Start some sentences with And, But, So (principle #12)
9. Focus on transformation, not features (principle #4)
10. Add warmth to CTA with reassurance (principle #1)

Generate the following fields in valid JSON format:

{{
  "subject": "Email subject line (60 chars max, conversational, benefit-driven)",
  "headline": "Main hero headline (emotional hook, 8-12 words)",
  "subheadline": "Supporting headline (adds context, 12-20 words)",
  "callout_title": "Callout box title (3-5 words, attention-grabbing)",
  "callout_main_text": "Main callout text (equity range or key number, bold and large)",
  "callout_subtitle": "Callout subtitle (question or benefit, 8-12 words)",
  "body_headline": "Body section headline (trust/credibility angle, 8-12 words)",
  "body_copy": "Main body copy (2-3 paragraphs, 150-200 words total, conversational, story-driven, apply all Harry Dry principles)",
  "cta_tagline": "CTA section tagline (action-oriented, 5-8 words)",
  "cta_agent_message": "Personal message from agent (warm, reassuring, 15-25 words)",
  "cta_button_text": "CTA button text (3-5 words, action verb)",
  "q1_text": "Question 1 main text (relates to their priority/pain point)",
  "q1_subtitle": "Question 1 subtitle (adds context or stakes)",
  "q1_opt1_label": "Q1 Option 1 label",
  "q1_opt1_desc": "Q1 Option 1 description",
  "q1_opt2_label": "Q1 Option 2 label",
  "q1_opt2_desc": "Q1 Option 2 description",
  "q1_opt3_label": "Q1 Option 3 label",
  "q1_opt3_desc": "Q1 Option 3 description",
  "q2_text": "Question 2 main text (about their next move/goal)",
  "q2_subtitle": "Question 2 subtitle",
  "q2_opt1": "Q2 Option 1",
  "q2_opt2": "Q2 Option 2",
  "q2_opt3": "Q2 Option 3",
  "q2_opt4": "Q2 Option 4",
  "q2_opt5": "Q2 Option 5",
  "q2_opt6": "Q2 Option 6"
}}

Return ONLY the JSON object, no other text.
"""
    
    # Make API call using requests
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"error": "OpenAI API key not configured"}
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4.1-mini",
                "messages": [
                    {"role": "system", "content": "You are an expert copywriter who applies Harry Dry's principles."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 2000
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return {"error": f"API error: {response.status_code} - {response.text}"}
        
        result = response.json()
        content_text = result['choices'][0]['message']['content'].strip()
        
        # Parse JSON response
        # Remove markdown code blocks if present
        if content_text.startswith('```'):
            content_text = content_text.split('```')[1]
            if content_text.startswith('json'):
                content_text = content_text[4:]
            content_text = content_text.strip()
        
        content = json.loads(content_text)
        return content
        
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def get_segment_profile(segment_id):
    """
    Get the profile data for a specific segment
    """
    return SEGMENT_PROFILES.get(segment_id)
