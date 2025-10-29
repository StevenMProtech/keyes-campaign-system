"""
Behavioral Audience Analyzer
Uses AI vision to analyze pixel tracking screenshots and demographic data
to create targetable audience segments and campaign recommendations
"""

import os
import json
import base64
import requests

def call_openai(messages, model="gpt-4o-mini", temperature=0.7, max_tokens=2000):
    api_key = os.environ.get("OPENAI_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=30)
    response.raise_for_status()
    return response.json()

AUDIENCES_FILE = 'behavioral_audiences.json'


def load_audiences():
    """Load saved behavioral audiences"""
    if os.path.exists(AUDIENCES_FILE):
        with open(AUDIENCES_FILE, 'r') as f:
            return json.load(f)
    return []


def save_audiences(audiences):
    """Save behavioral audiences to file"""
    with open(AUDIENCES_FILE, 'w') as f:
        json.dump(audiences, f, indent=2)


def encode_image_to_base64(image_path):
    """Encode image file to base64 string"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')




def analyze_csv_data(csv_path):
    """
    Analyze visitor journey CSV data using AI
    Returns behavioral insights and patterns
    """
    import csv
    
    # Read CSV file
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        rows = list(csv_reader)
    
    # Get first 100 rows as sample (to avoid token limits)
    sample_rows = rows[:100]
    
    # Convert to text format for AI
    csv_text = "CSV Headers: " + ", ".join(rows[0].keys()) if rows else "Empty CSV"
    csv_text += "\n\nSample Data (first 100 rows):\n"
    for row in sample_rows:
        csv_text += str(row) + "\n"
    
    # Analyze with AI
    prompt = f"""Analyze this visitor journey CSV data and extract behavioral insights:

{csv_text}

Provide a comprehensive analysis in JSON format:
{{
    "total_visitors": "number of unique visitors",
    "avg_pages_per_visit": "average pages viewed",
    "avg_time_on_site": "average time spent",
    "top_pages": ["most visited pages"],
    "conversion_paths": ["common paths to conversion"],
    "drop_off_points": ["where visitors leave"],
    "engagement_level": "high/medium/low",
    "intent_signals": "what behavior indicates intent",
    "behavioral_patterns": "key patterns observed",
    "recommendations": "insights for targeting this audience"
}}

Be specific and data-driven based on the CSV data provided."""

    response = call_openai(
        messages=[
            {"role": "system", "content": "You are an expert data analyst specializing in visitor behavior analysis and audience segmentation."},
            {"role": "user", "content": prompt}
        ], temperature=0.7, max_tokens=2000
    )
    
    # Parse JSON response
    try:
        result = json.loads(response['choices'][0]['message']['content'])
        return result
    except:
        return {"error": "Failed to parse AI response", "raw": response['choices'][0]['message']['content']}

def analyze_audience_screenshots(demographic_image_path, pixel_image_path, audience_name=""):
    """
    Analyze two screenshots using AI vision:
    1. Demographic Data Analytics
    2. Pixel/Behavioral Analytics
    
    Returns comprehensive audience profile with campaign recommendations
    """
    
    # Encode images
    demo_base64 = encode_image_to_base64(demographic_image_path)
    pixel_base64 = encode_image_to_base64(pixel_image_path)
    
    # Create comprehensive prompt
    prompt = f"""You are analyzing website visitor data to create a targetable audience segment for real estate email campaigns.

You have been provided with TWO screenshots:

**Image 1: Demographic Data Analytics**
This shows visitor demographics including:
- Age distribution
- Gender
- Marriage status
- Kids (has children or not)
- Location (City, State, Zip codes)
- Home Owner status
- Income ranges
- Net Worth
- Job Titles
- Department
- Seniority Level

**Image 2: Pixel/Behavioral Analytics**
This shows visitor behavior including:
- Average page views
- Time on site
- Engagement metrics
- Landing pages visited
- Content consumed
- Behavioral patterns

**Your Task:**
Analyze BOTH images carefully and extract ALL visible data. Then create a comprehensive audience profile.

**IMPORTANT INSTRUCTIONS:**
1. Extract EXACT numbers and percentages from the charts
2. Identify the TOP characteristics (highest percentages)
3. Look for behavioral patterns that indicate intent
4. Consider what pages they visited and what that means
5. Think about their pain points and motivations
6. Suggest campaign angles that would resonate

**Return a JSON object with this EXACT structure:**

{{
  "audience_name": "{audience_name if audience_name else 'Suggested name based on data'}",
  "demographics": {{
    "age": "Primary age range with % (e.g., '35-44: 28.41%')",
    "gender": "Primary gender with % (e.g., 'M: 86.27%')",
    "marriage_status": "Primary status with % (e.g., 'True: 97.28%')",
    "has_kids": "Primary value with % (e.g., 'True: 58.15%')",
    "location_top_cities": ["City 1 with %", "City 2 with %", "City 3 with %"],
    "location_top_states": ["State 1 with %", "State 2 with %"],
    "home_owner": "Primary value with % (e.g., 'True: 83.93%')",
    "income_range": "Primary income range with % (e.g., '$75,000 to $99,999: 16.34%')",
    "net_worth": "Primary net worth range with % (e.g., '$25,000 to $49,999: 10.38%')",
    "top_job_titles": ["Job title 1 with %", "Job title 2 with %", "Job title 3 with %"],
    "top_departments": ["Department 1 with %", "Department 2 with %"],
    "seniority_level": "Primary level with % (e.g., 'Staff: 54.18%')"
  }},
  "behavior": {{
    "avg_page_views": "Number from chart",
    "avg_time_on_site": "Time from chart",
    "avg_time_active_onsite": "Time from chart",
    "avg_scroll_depth": "Percentage from chart",
    "top_landing_pages": ["Page 1 with %", "Page 2 with %", "Page 3 with %"],
    "engagement_patterns": "Description of how they interact with the site",
    "intent_signals": "What their behavior indicates about their intentions"
  }},
  "psychographics": {{
    "values": "What they care about based on demographics and behavior",
    "motivations": "What drives them based on pages visited and engagement",
    "pain_points": "Problems they're trying to solve",
    "decision_style": "How they make decisions (analytical, emotional, etc.)"
  }},
  "communication_style": {{
    "tone": "Recommended tone (professional, casual, urgent, etc.)",
    "language": "Language style (data-driven, emotional, storytelling, etc.)",
    "approach": "Best approach (direct, consultative, educational, etc.)"
  }},
  "campaign_recommendations": {{
    "subject_line_angles": ["Angle 1", "Angle 2", "Angle 3"],
    "headline_approaches": ["Approach 1", "Approach 2", "Approach 3"],
    "key_messages": ["Message 1", "Message 2", "Message 3"],
    "cta_suggestions": ["CTA 1", "CTA 2", "CTA 3"],
    "timing_recommendations": "When to send emails based on behavior",
    "content_focus": "What to emphasize in campaigns"
  }},
  "segment_summary": "2-3 sentence summary of who this audience is and why they're valuable"
}}

**CRITICAL:** Return ONLY valid JSON. No markdown, no code blocks, no explanations. Just the JSON object."""

    # Call OpenAI Vision API
    response = call_openai(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{demo_base64}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{pixel_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ], max_tokens=2000, temperature=0.7
    )
    
    # Extract and parse response
    content = response['choices'][0]['message']['content'].strip()
    
    # Remove markdown code blocks if present
    if content.startswith('```'):
        content = content.split('```')[1]
        if content.startswith('json'):
            content = content[4:]
        content = content.strip()
    
    # Parse JSON
    audience_data = json.loads(content)
    
    return audience_data


def create_audience_card(audience_data, demographic_image_path, pixel_image_path):
    """
    Create a saved audience card with images and data
    Returns the audience ID
    """
    audiences = load_audiences()
    
    # Generate unique ID
    import time
    audience_id = f"audience_{int(time.time())}"
    
    # Create audience card
    audience_card = {
        "id": audience_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "demographic_image": demographic_image_path,
        "pixel_image": pixel_image_path,
        **audience_data
    }
    
    audiences.append(audience_card)
    save_audiences(audiences)
    
    return audience_id


def get_audience(audience_id):
    """Get a specific audience by ID"""
    audiences = load_audiences()
    for audience in audiences:
        if audience['id'] == audience_id:
            return audience
    return None


def generate_campaign_for_audience(audience_id):
    """
    Generate a campaign tailored to a behavioral audience
    Uses the audience data to create highly targeted content
    """
    audience = get_audience(audience_id)
    if not audience:
        return None
    
    # Create comprehensive prompt for campaign generation
    prompt = f"""You are creating a highly targeted real estate email campaign for a specific behavioral audience.

**AUDIENCE PROFILE:**

**Demographics:**
- Age: {audience['demographics']['age']}
- Gender: {audience['demographics']['gender']}
- Marriage Status: {audience['demographics']['marriage_status']}
- Has Kids: {audience['demographics']['has_kids']}
- Home Owner: {audience['demographics']['home_owner']}
- Income: {audience['demographics']['income_range']}
- Top Job Titles: {', '.join(audience['demographics']['top_job_titles'][:3])}
- Seniority: {audience['demographics']['seniority_level']}

**Behavior:**
- Avg Page Views: {audience['behavior']['avg_page_views']}
- Avg Time on Site: {audience['behavior']['avg_time_on_site']}
- Top Landing Pages: {', '.join(audience['behavior']['top_landing_pages'][:3])}
- Intent Signals: {audience['behavior']['intent_signals']}

**Psychographics:**
- Values: {audience['psychographics']['values']}
- Motivations: {audience['psychographics']['motivations']}
- Pain Points: {audience['psychographics']['pain_points']}

**Communication Style:**
- Tone: {audience['communication_style']['tone']}
- Language: {audience['communication_style']['language']}
- Approach: {audience['communication_style']['approach']}

**Campaign Recommendations:**
- Subject Line Angles: {', '.join(audience['campaign_recommendations']['subject_line_angles'])}
- Key Messages: {', '.join(audience['campaign_recommendations']['key_messages'])}
- Content Focus: {audience['campaign_recommendations']['content_focus']}

**YOUR TASK:**
Create a complete email campaign that speaks DIRECTLY to this audience based on their actual behavior and demographics.

Apply Harry Dry's 25 copywriting principles:
1. Show transformation
2. Tell their story
3. Use presets (clear options)
4. Personal pronouns
5. Short sentences
6. Conversational tone
7. Clear CTA
8. Social proof
9. Specificity
10. Address objections
... and all others

**Return ONLY valid JSON with this structure:**

{{
  "subject_line": "Personalized subject line using {{{{contact.firstname}}}}",
  "headline": "Compelling headline that speaks to their situation",
  "subheadline": "Supporting subheadline",
  "body_copy": "Full paragraph (100-150 words) that tells their story and shows transformation",
  "cta_button_text": "Clear, action-oriented CTA",
  "callout_box": {{
    "title": "Attention-grabbing callout title",
    "main_text": "Key figure or stat",
    "subtitle": "Supporting text"
  }},
  "form_questions": [
    {{
      "question": "Question 1 text",
      "subtitle": "Optional subtitle",
      "type": "radio",
      "options": [
        {{"label": "Option 1", "description": "Brief description"}},
        {{"label": "Option 2", "description": "Brief description"}},
        {{"label": "Option 3", "description": "Brief description"}},
        {{"label": "Option 4", "description": "Brief description"}}
      ]
    }},
    {{
      "question": "Question 2 text",
      "subtitle": "Optional subtitle",
      "type": "checkbox",
      "options": [
        {{"label": "Option 1"}},
        {{"label": "Option 2"}},
        {{"label": "Option 3"}},
        {{"label": "Option 4"}}
      ]
    }},
    {{
      "question": "Question 3 text",
      "subtitle": "Optional subtitle",
      "type": "radio",
      "options": [
        {{"label": "Option 1"}},
        {{"label": "Option 2"}},
        {{"label": "Option 3"}},
        {{"label": "Option 4"}}
      ]
    }}
  ],
  "explanation": "Why this copy works for THIS specific audience based on their behavior and demographics"
}}"""

    response = call_openai(
        messages=[{"role": "user", "content": prompt}], max_tokens=1500, temperature=0.8
    )
    
    content = response['choices'][0]['message']['content'].strip()
    
    # Remove markdown if present
    if content.startswith('```'):
        content = content.split('```')[1]
        if content.startswith('json'):
            content = content[4:]
        content = content.strip()
    
    return json.loads(content)

