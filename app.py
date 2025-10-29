from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import json
import os
from datetime import datetime
from ai_generator import generate_campaign_content, get_segment_profile
from audience_analyzer import analyze_audience_screenshots, create_audience_card, get_audience, load_audiences, generate_campaign_for_audience, analyze_csv_data
from html_generator import generate_email_html_content

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'keyes-campaign-builder-secret-2025')
CORS(app)

# Global authentication check
@app.before_request
def require_authentication():
    """Require authentication for all routes except login"""
    # Allow login page and static files
    if request.endpoint in ['admin_login', 'static']:
        return None
    
    # Check if user is authenticated
    if not session.get('admin_authenticated'):
        return redirect('/admin/login')
    
    return None

SUBMISSIONS_FILE = 'submissions.json'
CAMPAIGNS_FILE = 'campaigns.json'
SEGMENTS_FILE = 'segments.json'
TEMPLATES_FILE = 'email_templates.json'
CURRENT_EMAIL_TEMPLATE = 'email_template.html'

def load_submissions():
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, 'r') as f:
            return json.load(f)
    return []


def load_behavioral_audiences():
    """Load behavioral audiences from database"""
    try:
        with open('behavioral_audiences.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_submissions(submissions):
    with open(SUBMISSIONS_FILE, 'w') as f:
        json.dump(submissions, f, indent=2)

def load_campaigns():
    if os.path.exists(CAMPAIGNS_FILE):
        with open(CAMPAIGNS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_campaigns(campaigns):
    with open(CAMPAIGNS_FILE, 'w') as f:
        json.dump(campaigns, f, indent=2)

def get_campaign(campaign_id):
    campaigns = load_campaigns()
    for campaign in campaigns:
        if campaign['id'] == campaign_id:
            return campaign
    return None

def load_segments():
    if os.path.exists(SEGMENTS_FILE):
        with open(SEGMENTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_segments(segments):
    with open(SEGMENTS_FILE, 'w') as f:
        json.dump(segments, f, indent=2)

def get_segment(segment_id):
    segments = load_segments()
    for segment in segments:
        if segment['id'] == segment_id:
            return segment
    return None

def load_templates():
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_templates(templates):
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(templates, f, indent=2)

def get_template(template_id):
    templates = load_templates()
    for template in templates:
        if template['id'] == template_id:
            return template
    return None

@app.route('/test')
def test_page():
    with open('email_template.html', 'r') as f:
        email_html = f.read()
    return email_html

@app.route('/')
def index():
    submissions = load_submissions()
    total = len(submissions)
    pending = sum(1 for s in submissions if s.get('status') == 'pending')
    maximize = sum(1 for s in submissions if s.get('equity_priority') == 'maximize')
    speed = sum(1 for s in submissions if s.get('equity_priority') == 'speed')
    balance = sum(1 for s in submissions if s.get('equity_priority') == 'balance')
    
    # Load campaigns for dropdown
    campaigns = load_campaigns()
    campaign_options = ""
    for camp in campaigns:
        campaign_options += f'<option value="{camp["id"]}">{camp["name"]}</option>'
    
    # Load email template
    try:
        with open('email_template.html', 'r') as f:
            email_html = f.read()
    except FileNotFoundError:
        email_html = "<!-- Email template not found -->"
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>The Keyes Company Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #1a1a1a;
            min-height: 100vh;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: 350px 1fr;
            height: 100vh;
        }}
        .sidebar {{
            background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
            padding: 30px;
            border-right: 1px solid #333;
            display: flex;
            flex-direction: column;
            width: 350px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: 700;
            color: white;
            margin-bottom: 10px;
        }}
        .logo span {{ color: #fcbfa7; }}
        .tagline {{
            color: #999;
            font-size: 14px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #333;
        }}
        .stat-card {{
            background: rgba(0, 66, 55, 0.15);
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 8px;
            border-left: 3px solid #fcbfa7;
        }}
        .stat-card h3 {{
            color: #999;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .stat-card .number {{
            font-size: 24px;
            font-weight: 700;
            color: #fcbfa7;
            line-height: 1;
        }}
        .stat-card .label {{
            color: #999;
            font-size: 11px;
            margin-top: 3px;
        }}
        .stats-container {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
        }}
        .actions {{
            margin-top: auto;
            padding-top: 20px;
            border-top: 1px solid #333;
            flex-shrink: 0;
        }}
        .actions h3 {{
            color: white;
            font-size: 14px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .btn {{
            display: block;
            padding: 12px 20px;
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin-bottom: 10px;
            text-align: center;
            transition: all 0.2s;
            font-size: 14px;
        }}
        .btn:hover {{ transform: translateX(5px); }}
        .btn.secondary {{
            background: linear-gradient(135deg, #fcbfa7 0%, #f7f3e5 100%);
        }}
        .btn.outline {{
            background: transparent;
            border: 2px solid #004237;
        }}
        .preview {{
            background: #f5f5f5;
            overflow-y: auto;
            padding: 40px 20px;
        }}
        .preview-header {{
            background: white;
            padding: 20px 30px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .preview-header h2 {{
            color: #333;
            font-size: 20px;
        }}
        .preview-header .badge {{
            background: #004237;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .zoom-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .zoom-btn {{
            background: #f0f0f0;
            border: 1px solid #ddd;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .zoom-btn:hover {{
            background: #e0e0e0;
        }}
        .zoom-level {{
            font-size: 12px;
            color: #666;
            min-width: 45px;
            text-align: center;
        }}
        .email-container {{
            max-width: 650px;
            margin: 0 auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        @media (max-width: 1024px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
            .sidebar {{
                border-right: none;
                border-bottom: 1px solid #333;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="sidebar">
            <div class="logo">The <span style="font-style: italic; font-family: Georgia, serif;">Keyes</span> Company</div>
            <div class="tagline">Your Home Equity Campaign Dashboard</div>
            
            <div class="stats-container">
            <div class="stat-card">
                <h3>Total Submissions</h3>
                <div class="number">{total}</div>
                <div class="label">All time</div>
            </div>
            
            <div class="stat-card">
                <h3>Pending Review</h3>
                <div class="number">{pending}</div>
                <div class="label">Needs follow-up</div>
            </div>
            
            <div class="stat-card">
                <h3>Maximize Priority</h3>
                <div class="number">{maximize}</div>
                <div class="label">Want $788k</div>
            </div>
            
            <div class="stat-card">
                <h3>Speed Priority</h3>
                <div class="number">{speed}</div>
                <div class="label">Quick sale</div>
            </div>
            
            <div class="stat-card">
                <h3>Balanced</h3>
                <div class="number">{balance}</div>
                <div class="label">Best of both</div>
            </div>
            </div>
            
            <div class="actions">
                <h3>Quick Actions</h3>
                <a href="/campaign/new" class="btn" style="background: linear-gradient(135deg, #fcbfa7 0%, #fda67a 100%); color: #004237; font-weight: 700;">+ Create New Campaign</a>
                <a href="/audiences" class="btn">Audiences</a>
                <a href="/campaigns" class="btn">Manage Campaigns</a>
                <a href="/submissions" class="btn">View All Submissions</a>
                <a href="/export" class="btn secondary">Export to CSV</a>
                <a href="/api/submissions" class="btn outline">API (JSON)</a>
            </div>
        </div>
        
        <div class="preview">
            <div class="preview-header">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <h2>Live Email Campaign Preview</h2>
                    <select id="campaignSelector" onchange="previewCampaign()" style="padding: 8px 16px; border: 2px solid #004237; border-radius: 6px; font-size: 14px; background: white; cursor: pointer;">
                        <option value="current">Current Email Template</option>
                        {campaign_options}
                    </select>
                    <a href="/template/edit" style="padding: 8px 16px; background: #fcbfa7; color: #004237; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px;">Edit Template</a>
                </div>
                <div class="zoom-controls">
                    <button class="zoom-btn" onclick="zoomOut()">−</button>
                    <span class="zoom-level" id="zoomLevel">100%</span>
                    <button class="zoom-btn" onclick="zoomIn()">+</button>
                    <div class="badge">LIVE & TESTABLE</div>
                </div>
            </div>
            <script>
                let currentZoom = 1.0;
                function zoomIn() {{
                    if (currentZoom < 1.5) {{
                        currentZoom += 0.1;
                        updateZoom();
                    }}
                }}
                function zoomOut() {{
                    if (currentZoom > 0.5) {{
                        currentZoom -= 0.1;
                        updateZoom();
                    }}
                }}
                function updateZoom() {{
                    document.querySelector('.email-container').style.zoom = currentZoom;
                    document.getElementById('zoomLevel').textContent = Math.round(currentZoom * 100) + '%';
                }}
                function previewCampaign() {{
                    const campaignId = document.getElementById('campaignSelector').value;
                    const container = document.querySelector('.email-container');
                    if (campaignId === 'current') {{
                        window.location.reload();
                    }} else {{
                        // Use iframe to preserve formatting
                        container.innerHTML = `<iframe src="/campaign/${{campaignId}}/preview" style="width: 100%; height: 100%; min-height: 800px; border: none; background: white;"></iframe>`;
                    }}
                }}
            </script>
            <div class="email-container">
                {email_html}
            </div>
        </div>
    </div>
</body>
</html>"""

@app.route('/api/submit', methods=['POST', 'OPTIONS'])
def submit_form():
    if request.method == 'OPTIONS':
        return '', 200
    
    submissions = load_submissions()
    
    # Get campaign_id from form or query param, default to home-equity-2025
    campaign_id = request.form.get('campaign_id') or request.args.get('campaign_id', 'home-equity-2025')
    
    new_submission = {
        'id': len(submissions) + 1,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'campaign_id': campaign_id,
        'email': request.form.get('email', ''),
        'first_name': request.form.get('firstName', ''),
        'last_name': request.form.get('lastName', ''),
        'equity_priority': request.form.get('equity_priority', ''),
        'goals': ','.join(request.form.getlist('goals')),
        'goals_text': request.form.get('goalsText', ''),
        'phone_number': request.form.get('phoneNumber', ''),
        'wants_equity_report': request.form.get('wantsReport') == 'yes',
        'wants_expert_contact': request.form.get('wantsExpert') == 'yes',
        'status': 'pending'
    }
    
    submissions.insert(0, new_submission)
    save_submissions(submissions)
    
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You - The Keyes Company</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            background: white;
            padding: 60px 40px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            text-align: center;
        }
        .logo { margin-bottom: 30px; }
        .logo img { width: 180px; height: auto; }
        .checkmark {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 30px;
        }
        .checkmark::after {
            content: "✓";
            font-size: 48px;
            color: white;
            font-weight: bold;
        }
        h1 { color: #004237; font-size: 36px; margin-bottom: 20px; }
        p { color: #666; font-size: 18px; line-height: 1.6; margin-bottom: 15px; }
        .highlight {
            background: rgba(252, 191, 167, 0.1);
            padding: 25px;
            border-radius: 12px;
            margin-top: 30px;
            border-left: 4px solid #fcbfa7;
        }
        .footer { margin-top: 40px; font-size: 14px; color: #999; font-style: italic; }
        .back-btn {
            display: inline-block;
            margin-top: 30px;
            padding: 12px 24px;
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 66, 55, 0.3);
        }
        .zoom-controls {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 8px 12px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            gap: 8px;
            align-items: center;
            z-index: 1000;
        }
        .zoom-btn {
            background: #004237;
            color: white;
            border: none;
            width: 28px;
            height: 28px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        .zoom-btn:hover { background: #003329; transform: scale(1.1); }
        .zoom-level { font-size: 13px; color: #666; font-weight: 600; min-width: 45px; text-align: center; }
    </style>
</head>
<body>
    <div class="zoom-controls">
        <button class="zoom-btn" onclick="zoomOut()">−</button>
        <span class="zoom-level" id="zoomLevel">100%</span>
        <button class="zoom-btn" onclick="zoomIn()">+</button>
    </div>
    <div class="container" id="content">
        <div class="logo"><img src="https://raw.githubusercontent.com/StevenMProtech/Keyes/main/keyes-new-logo.png" alt="Keyes"></div>
        <div class="checkmark"></div>
        <h1>Thank You!</h1>
        <p><strong>Your equity strategy request has been received.</strong></p>
        <p>A Keyes equity expert will review your goals and contact you shortly.</p>
        <div class="highlight">
            <p><strong style="color: #004237; display: block; margin-bottom: 10px;">What's Next?</strong>
            We'll show you how our 4,000+ agent network, exclusive pre-MLS exposure, and nearly 100 years of Florida expertise can help you capture the high end of your equity range.</p>
        </div>
        <div class="footer">Your Fresh Start, Starts Here</div>
        <a href="/" class="back-btn">← Back to Dashboard</a>
    </div>
    <script>
        let zoomLevel = 100;
        function updateZoom() {
            document.getElementById('content').style.transform = `scale(${{zoomLevel / 100}})`;
            document.getElementById('zoomLevel').textContent = zoomLevel + '%';
        }}
        function zoomIn() {{
            if (zoomLevel < 150) {{
                zoomLevel += 10;
                updateZoom();
            }}
        }}
        function zoomOut() {{
            if (zoomLevel > 50) {{
                zoomLevel -= 10;
                updateZoom();
            }}
        }}
    </script>
</body>
</html>"""

@app.route('/template/edit', methods=['GET', 'POST'])
def edit_template():
    """Edit the email template HTML"""
    if request.method == 'POST':
        # Save the template
        new_html = request.form.get('html_content', '')
        
        with open('email_template.html', 'w') as f:
            f.write(new_html)
        
        return '<script>alert("Template saved successfully!"); window.location.href="/template/edit";</script>'
    
    # Load current template
    try:
        with open('email_template.html', 'r') as f:
            current_html = f.read()
    except FileNotFoundError:
        current_html = "<!-- No template found -->"
    
    # Escape for textarea
    import html
    escaped_html = html.escape(current_html)
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Edit Email Template</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .editor-card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        textarea {{
            width: 100%;
            min-height: 500px;
            padding: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            resize: vertical;
        }}
        textarea:focus {{
            outline: none;
            border-color: #004237;
        }}
        .btn-group {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-save {{
            background: #fcbfa7;
            color: #004237;
        }}
        .btn-save:hover {{
            background: #fda67a;
        }}
        .btn-download {{
            background: #004237;
            color: white;
        }}
        .btn-download:hover {{
            background: #003329;
        }}
        .btn-cancel {{
            background: #e0e0e0;
            color: #333;
        }}
        .btn-cancel:hover {{
            background: #d0d0d0;
        }}
        .info {{
            background: #f0f8ff;
            border-left: 4px solid #004237;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/" style="color: white; text-decoration: none; font-size: 24px; opacity: 0.8; transition: opacity 0.3s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">←</a>
            <h1>Email Template Editor</h1>
            <p>Edit the HTML code for your email template</p>
        </div>
        
        <div class="editor-card">
            <div class="info">
                <strong>Note:</strong> This is the master email template (email_template.html). Changes here will affect the preview on the homepage.
            </div>
            
            <form method="POST" id="templateForm">
                <textarea name="html_content" id="htmlContent">{escaped_html}</textarea>
                
                <div class="btn-group">
                    <button type="submit" class="btn btn-save">Save Template</button>
                    <button type="button" class="btn btn-download" onclick="downloadHTML()">Download HTML</button>
                    <a href="/" class="btn btn-cancel">Back to Dashboard</a>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        function downloadHTML() {{
            const htmlContent = document.getElementById('htmlContent').value;
            const blob = new Blob([htmlContent], {{ type: 'text/html' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'email_template.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
"""

@app.route('/submissions')
def view_submissions():
    submissions = load_submissions()
    rows_html = ""
    
    for sub in submissions:
        priority_badge = {
            'maximize': '<span style="background: #004237; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px;">MAXIMIZE</span>',
            'speed': '<span style="background: #fcbfa7; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px;">SPEED</span>',
            'balance': '<span style="background: #666; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px;">BALANCED</span>'
        }.get(sub.get('equity_priority', ''), sub.get('equity_priority', ''))
        
        rows_html += f"""<tr>
            <td>{sub.get('id', '')}</td>
            <td>{sub.get('timestamp', '')}</td>
            <td><span style="background: #f7f3e5; padding: 4px 8px; border-radius: 4px; font-size: 11px; color: #004237;">{sub.get('campaign_id', 'N/A')}</span></td>
            <td><strong>{sub.get('email', '')}</strong></td>
            <td>{sub.get('first_name', '')} {sub.get('last_name', '')}</td>
            <td>{priority_badge}</td>
            <td>{sub.get('goals', '')}</td>
            <td>{sub.get('goals_text', '')}</td>
            <td>{sub.get('phone_number', '')}</td>
            <td>{'✓' if sub.get('wants_equity_report') else '—'}</td>
            <td>{'✓' if sub.get('wants_expert_contact') else '—'}</td>
        </tr>"""
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>All Submissions</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8f5e3 100%);
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header-left {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .logo {{
            font-size: 24px;
            font-weight: 700;
            opacity: 0.95;
        }}
        .logo span {{ color: #fcbfa7; }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header a {{ color: white; text-decoration: none; padding: 10px 20px; background: rgba(255,255,255,0.2); border-radius: 6px; }}
        table {{ width: 100%; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        th {{ background: #004237; color: white; padding: 16px 12px; text-align: left; }}
        td {{ padding: 14px 12px; border-bottom: 1px solid #e0e0e0; }}
        tr:hover {{ background: #f0f8ed; }}
        .zoom-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}
        .zoom-btn {{
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .zoom-btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        .zoom-level {{
            font-size: 12px;
            color: white;
            min-width: 45px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <div class="logo">The <span style="font-style: italic; font-family: Georgia, serif;">Keyes</span> Company</div>
            <h1>All Submissions</h1>
        </div>
        <div style="display: flex; gap: 15px; align-items: center;">
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomOut()">−</button>
                <span class="zoom-level" id="zoomLevel">100%</span>
                <button class="zoom-btn" onclick="zoomIn()">+</button>
            </div>
            <a href="/">← Dashboard</a>
        </div>
    </div>
    <table>
        <tr>
            <th>ID</th><th>Time</th><th>Campaign</th><th>Email</th><th>Name</th><th>Priority</th><th>Goals</th><th>Details</th><th>Phone</th><th>Report</th><th>Call Past Client</th>
        </tr>
        {rows_html if rows_html else '<tr><td colspan="11" style="text-align: center; padding: 60px; color: #999;">No submissions yet</td></tr>'}
    </table>
    <script>
        let currentZoom = 1.0;
        function zoomIn() {{
            if (currentZoom < 1.5) {{
                currentZoom += 0.1;
                updateZoom();
            }}
        }}
        function zoomOut() {{
            if (currentZoom > 0.5) {{
                currentZoom -= 0.1;
                updateZoom();
            }}
        }}
        function updateZoom() {{
            document.querySelector('table').style.zoom = currentZoom;
            document.getElementById('zoomLevel').textContent = Math.round(currentZoom * 100) + '%';
        }}
    </script>
</body>
</html>"""

@app.route('/api/submissions')
def get_submissions():
    return jsonify(load_submissions())

@app.route('/export')
def export_csv():
    submissions = load_submissions()
    csv = "ID,Timestamp,Campaign ID,Email,First Name,Last Name,Equity Priority,Goals,Goals Text,Phone,Wants Report,Wants Expert\n"
    
    for sub in submissions:
        csv += f"{sub.get('id','')},{sub.get('timestamp','')},{sub.get('campaign_id','')},{sub.get('email','')},{sub.get('first_name','')},{sub.get('last_name','')},{sub.get('equity_priority','')},\"{sub.get('goals','')}\",\"{sub.get('goals_text','')}\",{sub.get('phone_number','')},{sub.get('wants_equity_report','')},{sub.get('wants_expert_contact','')}\n"
    
    return Response(csv, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=keyes.csv"})

# Campaign Management Routes
@app.route('/campaigns')
def campaigns_list():
    campaigns = load_campaigns()
    submissions = load_submissions()
    
    # Calculate stats per campaign
    campaign_stats = {}
    for campaign in campaigns:
        campaign_id = campaign['id']
        campaign_submissions = [s for s in submissions if s.get('campaign_id') == campaign_id]
        campaign_stats[campaign_id] = {
            'total': len(campaign_submissions),
            'pending': sum(1 for s in campaign_submissions if s.get('status') == 'pending'),
            'last_submission': campaign_submissions[0]['timestamp'] if campaign_submissions else 'None'
        }
    
    segments = load_segments()
    segment_map = {s['id']: s for s in segments}
    
    campaigns_html = ""
    for campaign in campaigns:
        stats = campaign_stats.get(campaign['id'], {'total': 0, 'pending': 0, 'last_submission': 'None'})
        status_badge = f'<span style="background: {"#004237" if campaign["status"] == "active" else "#fcbfa7"}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; text-transform: uppercase; font-weight: 600;">{campaign["status"]}</span>'
        
        # Get segment info
        segment_id = campaign.get('segment', 'general')
        segment = segment_map.get(segment_id, {'name': 'General', 'icon': '•', 'color': '#fcbfa7'})
        segment_badge = f'<span style="background: {segment["color"]}; color: white; padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600;">{segment["icon"]} {segment["name"]}</span>'
        
        campaigns_html += f"""
        <div style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #fcbfa7;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <h3 style="color: #004237; font-size: 20px; margin-bottom: 8px;">{campaign['name']}</h3>
                    <p style="color: #666; font-size: 14px; margin-bottom: 8px;">ID: {campaign['id']}</p>
                    <div style="margin-bottom: 8px;">{segment_badge}</div>
                    <p style="color: #999; font-size: 12px;">Created: {campaign['created_at']} | Updated: {campaign['updated_at']}</p>
                </div>
                <div>{status_badge}</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; padding: 15px; background: #f7f3e5; border-radius: 8px;">
                <div>
                    <div style="color: #999; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">Total Submissions</div>
                    <div style="color: #004237; font-size: 24px; font-weight: 700;">{stats['total']}</div>
                </div>
                <div>
                    <div style="color: #999; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">Pending</div>
                    <div style="color: #fcbfa7; font-size: 24px; font-weight: 700;">{stats['pending']}</div>
                </div>
                <div>
                    <div style="color: #999; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">Last Submission</div>
                    <div style="color: #666; font-size: 13px; font-weight: 600; margin-top: 8px;">{stats['last_submission']}</div>
                </div>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <a href="/campaign/{campaign['id']}" style="padding: 10px 20px; background: #004237; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">View Details</a>
                <a href="/campaign/{campaign['id']}/edit" style="padding: 10px 20px; background: #fcbfa7; color: #004237; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Edit Campaign</a>
                <a href="/campaign/{campaign['id']}/preview" style="padding: 10px 20px; background: white; color: #004237; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600; border: 2px solid #004237;">Preview Email</a>
                {'' if campaign['id'] == 'home-equity-2025' else f'<a href="/campaign/{campaign["id"]}/delete" onclick="return confirm(&quot;Are you sure you want to delete this campaign? This cannot be undone.&quot;);" style="padding: 10px 20px; background: #dc3545; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Delete</a>'}
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Campaign Management - The Keyes Company</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{ font-size: 32px; }}
        .btn {{
            padding: 12px 24px;
            background: #fcbfa7;
            color: #004237;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            display: inline-block;
            transition: all 0.3s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(252, 191, 167, 0.4);
        }}
        .back-link {{
            color: white;
            text-decoration: none;
            font-size: 14px;
            opacity: 0.9;
            transition: opacity 0.2s;
        }}
        .back-link:hover {{ opacity: 1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Campaign Management</h1>
                <p style="margin-top: 8px; opacity: 0.9;">Create, edit, and track your email campaigns</p>
            </div>
            <div style="display: flex; gap: 15px; align-items: center;">
                <a href="/campaign/new" class="btn">+ New Campaign</a>
                <a href="/" class="back-link">← Dashboard</a>
            </div>
        </div>
        {campaigns_html if campaigns_html else '<div style="background: white; padding: 60px; text-align: center; border-radius: 12px; color: #999;"><p style="font-size: 18px;">No campaigns yet. Create your first campaign to get started!</p></div>'}
    </div>
</body>
</html>"""

@app.route('/campaign/<campaign_id>')
def campaign_detail(campaign_id):
    campaign = get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404
    
    submissions = load_submissions()
    campaign_submissions = [s for s in submissions if s.get('campaign_id') == campaign_id]
    
    rows_html = ""
    for sub in campaign_submissions:
        rows_html += f"""
        <tr>
            <td>{sub.get('id', '')}</td>
            <td>{sub.get('timestamp', '')}</td>
            <td>{sub.get('email', '')}</td>
            <td>{sub.get('first_name', '')} {sub.get('last_name', '')}</td>
            <td>{sub.get('equity_priority', '')}</td>
            <td>{sub.get('goals', '')}</td>
            <td>{sub.get('phone_number', '')}</td>
        </tr>
        """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{campaign['name']} - Campaign Details</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid #fcbfa7;
        }}
        .stat-card h3 {{ color: #999; font-size: 11px; text-transform: uppercase; margin-bottom: 8px; }}
        .stat-card .number {{ color: #004237; font-size: 32px; font-weight: 700; }}
        table {{
            width: 100%;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        th, td {{
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
        }}
        th {{
            background: #004237;
            color: white;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .back-link {{
            color: white;
            text-decoration: none;
            display: inline-block;
            margin-top: 15px;
            opacity: 0.9;
        }}
        .back-link:hover {{ opacity: 1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{campaign['name']}</h1>
            <p style="margin-top: 8px; opacity: 0.9;">Campaign ID: {campaign['id']}</p>
            <p style="margin-top: 4px; font-size: 14px; opacity: 0.8;">Created: {campaign['created_at']} | Updated: {campaign['updated_at']}</p>
            <a href="/campaigns" class="back-link">← Back to Campaigns</a>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total Submissions</h3>
                <div class="number">{len(campaign_submissions)}</div>
            </div>
            <div class="stat-card">
                <h3>Pending</h3>
                <div class="number">{sum(1 for s in campaign_submissions if s.get('status') == 'pending')}</div>
            </div>
            <div class="stat-card">
                <h3>Maximize Priority</h3>
                <div class="number">{sum(1 for s in campaign_submissions if s.get('equity_priority') == 'maximize')}</div>
            </div>
            <div class="stat-card">
                <h3>Speed Priority</h3>
                <div class="number">{sum(1 for s in campaign_submissions if s.get('equity_priority') == 'speed')}</div>
            </div>
        </div>
        
        <table>
            <tr>
                <th>ID</th><th>Time</th><th>Email</th><th>Name</th><th>Priority</th><th>Goals</th><th>Phone</th>
            </tr>
            {rows_html if rows_html else '<tr><td colspan="7" style="text-align: center; padding: 60px; color: #999;">No submissions for this campaign yet</td></tr>'}
        </table>
    </div>
</body>
</html>"""

@app.route('/campaign/<campaign_id>/edit', methods=['GET', 'POST'])
def campaign_edit(campaign_id):
    if request.method == 'POST':
        campaigns = load_campaigns()
        for campaign_index, campaign in enumerate(campaigns):
            if campaign['id'] == campaign_id:
                campaigns[campaign_index]['name'] = request.form.get('name', campaign['name'])
                campaigns[campaign_index]['segment'] = request.form.get('segment', campaign.get('segment', 'general'))
                campaigns[campaign_index]['subject'] = request.form.get('subject', campaign['subject'])
                campaigns[campaign_index]['headline'] = request.form.get('headline', campaign['headline'])
                campaigns[campaign_index]['subheadline'] = request.form.get('subheadline', campaign['subheadline'])
                campaigns[campaign_index]['body_copy'] = request.form.get('body_copy', campaign['body_copy'])
                campaigns[campaign_index]['cta_text'] = request.form.get('cta_text', campaign['cta_text'])
                campaigns[campaign_index]['status'] = request.form.get('status', campaign['status'])
                
                # Save complete form configuration
                campaigns[campaign_index]['form_config'] = {
                    # Callout Box
                    'callout_title': request.form.get('callout_title', ''),
                    'callout_main_text': request.form.get('callout_main_text', ''),
                    'callout_subtitle': request.form.get('callout_subtitle', ''),
                    # Question 1
                    'q1_text': request.form.get('q1_text', ''),
                    'q1_subtitle': request.form.get('q1_subtitle', ''),
                    'q1_opt1_label': request.form.get('q1_opt1_label', ''),
                    'q1_opt1_desc': request.form.get('q1_opt1_desc', ''),
                    'q1_opt1_preselect': request.form.get('q1_opt1_preselect') == 'true',
                    'q1_opt2_label': request.form.get('q1_opt2_label', ''),
                    'q1_opt2_desc': request.form.get('q1_opt2_desc', ''),
                    'q1_opt2_preselect': request.form.get('q1_opt2_preselect') == 'true',
                    'q1_opt3_label': request.form.get('q1_opt3_label', ''),
                    'q1_opt3_desc': request.form.get('q1_opt3_desc', ''),
                    'q1_opt3_preselect': request.form.get('q1_opt3_preselect') == 'true',
                    # Question 2
                    'q2_text': request.form.get('q2_text', ''),
                    'q2_subtitle': request.form.get('q2_subtitle', ''),
                    'q2_opt1': request.form.get('q2_opt1', ''),
                    'q2_opt1_preselect': request.form.get('q2_opt1_preselect') == 'true',
                    'q2_opt2': request.form.get('q2_opt2', ''),
                    'q2_opt2_preselect': request.form.get('q2_opt2_preselect') == 'true',
                    'q2_opt3': request.form.get('q2_opt3', ''),
                    'q2_opt3_preselect': request.form.get('q2_opt3_preselect') == 'true',
                    'q2_opt4': request.form.get('q2_opt4', ''),
                    'q2_opt4_preselect': request.form.get('q2_opt4_preselect') == 'true',
                    'q2_opt5': request.form.get('q2_opt5', ''),
                    'q2_opt5_preselect': request.form.get('q2_opt5_preselect') == 'true',
                    'q2_opt6': request.form.get('q2_opt6', ''),
                    'q2_opt6_preselect': request.form.get('q2_opt6_preselect') == 'true',
                    'q2_text_placeholder': request.form.get('q2_text_placeholder', ''),
                    # Question 3
                    'q3_text': request.form.get('q3_text', ''),
                    'q3_opt1': request.form.get('q3_opt1', ''),
                    'q3_opt1_preselect': request.form.get('q3_opt1_preselect') == 'true',
                    'q3_opt2': request.form.get('q3_opt2', ''),
                    'q3_opt2_preselect': request.form.get('q3_opt2_preselect') == 'true',
                    'q3_phone_placeholder': request.form.get('q3_phone_placeholder', ''),
                    # Submit button
                    'submit_button_text': request.form.get('submit_button_text', ''),
                    'disclaimer_text': request.form.get('disclaimer_text', ''),
                    # Enhanced CTA Section
                    'cta_agent_message': request.form.get('cta_agent_message', ''),
                    'cta_tagline': request.form.get('cta_tagline', ''),
                    'cta_button_text': request.form.get('cta_button_text', 'GET MY EQUITY PLAN'),
                    'cta_agent_photo': request.form.get('cta_agent_photo', '')
                }
                
                # Add options 4-10 for all questions
                for opt_num in range(4, 11):
                    campaigns[campaign_index]['form_config'][f'q1_opt{opt_num}_label'] = request.form.get(f'q1_opt{opt_num}_label', '')
                    campaigns[campaign_index]['form_config'][f'q1_opt{opt_num}_desc'] = request.form.get(f'q1_opt{opt_num}_desc', '')
                    campaigns[campaign_index]['form_config'][f'q1_opt{opt_num}_preselect'] = request.form.get(f'q1_opt{opt_num}_preselect') == 'true'
                    campaigns[campaign_index]['form_config'][f'q2_opt{opt_num}'] = request.form.get(f'q2_opt{opt_num}', '')
                    campaigns[campaign_index]['form_config'][f'q2_opt{opt_num}_preselect'] = request.form.get(f'q2_opt{opt_num}_preselect') == 'true'
                    campaigns[campaign_index]['form_config'][f'q3_opt{opt_num}'] = request.form.get(f'q3_opt{opt_num}', '')
                    campaigns[campaign_index]['form_config'][f'q3_opt{opt_num}_preselect'] = request.form.get(f'q3_opt{opt_num}_preselect') == 'true'
                
                # Save thank you page configuration
                campaigns[campaign_index]['thankyou_config'] = {
                    'headline': request.form.get('thankyou_headline', 'Thank You!'),
                    'message': request.form.get('thankyou_message', ''),
                    'next_steps': request.form.get('thankyou_next_steps', ''),
                    'button_text': request.form.get('thankyou_button_text', ''),
                    'button_link': request.form.get('thankyou_button_link', ''),
                    'redirect_url': request.form.get('thankyou_redirect_url', '')
                }
                
                campaigns[campaign_index]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                save_campaigns(campaigns)
                return f'<script>alert("Campaign saved successfully!"); window.location.href="/campaign/{campaign_id}/preview";</script>'
        return "Campaign not found", 404
    
    campaign = get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Edit Campaign - {campaign['name']}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .form-container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .form-group {{
            margin-bottom: 24px;
        }}
        label {{
            display: block;
            color: #004237;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        input[type="text"], textarea, select {{
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.2s;
        }}
        input[type="text"]:focus, textarea:focus, select:focus {{
            outline: none;
            border-color: #004237;
        }}
        textarea {{
            min-height: 120px;
            resize: vertical;
        }}
        .btn-group {{
            display: flex;
            gap: 12px;
            margin-top: 30px;
        }}
        .btn {{
            padding: 14px 28px;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }}
        .btn-primary {{
            background: #004237;
            color: white;
        }}
        .btn-primary:hover {{
            background: #003329;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 66, 55, 0.3);
        }}
        .btn-secondary {{
            background: #fcbfa7;
            color: #004237;
        }}
        .btn-secondary:hover {{
            background: #faa587;
            transform: translateY(-2px);
        }}
        .btn-cancel {{
            background: #e0e0e0;
            color: #666;
        }}
        .btn-cancel:hover {{
            background: #d0d0d0;
        }}
        .help-text {{
            font-size: 12px;
            color: #999;
            margin-top: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Edit Campaign</h1>
            <p style="margin-top: 8px; opacity: 0.9;">{campaign['name']}</p>
        </div>
        
        <div class="form-container">
            <form method="POST">
                <div class="form-group">
                    <label>Campaign Name</label>
                    <input type="text" name="name" value="{campaign['name']}" required>
                    <div class="help-text">Internal name for this campaign</div>
                </div>
                
                <div class="form-group">
                    <label>Target Segment</label>
                    <select name="segment">
                        <option value="all-cash" {'selected' if campaign.get('segment') == 'all-cash' else ''}>All Cash Buyers</option>
                        <option value="absentee-instate" {'selected' if campaign.get('segment') == 'absentee-instate' else ''}>Absentee Owner (In-State)</option>
                        <option value="absentee-outstate" {'selected' if campaign.get('segment') == 'absentee-outstate' else ''}>Absentee Owner (Out-of-State)</option>
                        <option value="general" {'selected' if campaign.get('segment') == 'general' else ''}>General Past Clients</option>
                    </select>
                    <div class="help-text">Which client segment is this campaign targeting?</div>
                </div>
                
                <div class="form-group">
                    <label>Email Subject Line</label>
                    <input type="text" name="subject" value="{campaign['subject']}" required>
                </div>
                
                <div class="form-group">
                    <label>Main Headline</label>
                    <input type="text" name="headline" value="{campaign['headline']}" required>
                    <div class="help-text">Primary headline shown in the email</div>
                </div>
                
                <div class="form-group">
                    <label>Subheadline</label>
                    <input type="text" name="subheadline" value="{campaign['subheadline']}" required>
                </div>
                
                <div class="form-group">
                    <label>Body Copy</label>
                    <textarea name="body_copy" required>{campaign['body_copy']}</textarea>
                    <div class="help-text">Main content text for the email</div>
                </div>
                
                <div class="form-group">
                    <label>Call-to-Action Button Text</label>
                    <input type="text" name="cta_text" value="{campaign['cta_text']}" required>
                </div>
                
                <hr style="margin: 40px 0; border: none; border-top: 2px solid #f0f0f0;">
                <h3 style="color: #004237; margin-bottom: 20px;">Email Form Builder</h3>
                <p style="color: #666; margin-bottom: 20px; font-size: 14px;">Build your email form with custom questions, options, and pre-selected values</p>
                
                <!-- Callout Box Configuration -->
                <div style="background: #fcbfa7; padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                    <h3 style="color: #004237; margin-bottom: 8px;">Callout Box</h3>
                    <p style="color: #666; font-size: 14px; margin-bottom: 20px;">The highlighted box that appears before the form (e.g., equity range)</p>
                    
                    <div class="form-group">
                        <label>Show Callout Box</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-weight: normal;">
                            <input type="checkbox" name="callout_enabled" value="true" {'checked' if campaign.get('callout_config', {}).get('enabled', True) else ''}>
                            Display callout box in email
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Callout Title</label>
                        <input type="text" name="callout_title" value="{campaign.get('form_config', {}).get('callout_title', 'UNLOCK YOUR EQUITY')}" placeholder="e.g., UNLOCK YOUR EQUITY">
                    </div>
                    
                    <div class="form-group">
                        <label>Callout Main Text</label>
                        <input type="text" name="callout_main_text" value="{campaign.get('form_config', {}).get('callout_main_text', '$150K+')}" placeholder="e.g., $150K+" style="font-size: 18px; font-weight: 600;">
                        <div class="help-text">Large text in the center (e.g., dollar amount or key figure)</div>
                    </div>
                    
                    <div class="form-group">
                        <label>Callout Subtitle</label>
                        <input type="text" name="callout_subtitle" value="{campaign.get('form_config', {}).get('callout_subtitle', 'in potential home equity')}" placeholder="e.g., in potential home equity">
                    </div>
                </div>
                
                <hr style="margin: 40px 0; border: none; border-top: 2px solid #f0f0f0;">
                
                <!-- Question 1: Equity Priority (Radio) -->
                <div style="background: #f7f3e5; padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                    <h4 style="color: #004237; margin-bottom: 16px;">Question 1: Equity Priority (Radio Buttons)</h4>
                    
                    <div class="form-group">
                        <label>Question Text</label>
                        <input type="text" name="q1_text" value="{campaign.get('form_config', {}).get('q1_text', 'How important is reaching the high end of your equity?')}" placeholder="e.g., How important is reaching the high end?">
                    </div>
                    
                    <div class="form-group">
                        <label>Subtitle (optional)</label>
                        <input type="text" name="q1_subtitle" value="{campaign.get('form_config', {}).get('q1_subtitle', '($788k vs. $583k = $205,000 difference)')}" placeholder="e.g., ($788k vs. $583k = $205,000 difference)">
                    </div>
                    
                    <div class="form-group">
                        <label>Option 1 Label</label>
                        <input type="text" name="q1_opt1_label" value="{campaign.get('form_config', {}).get('q1_opt1_label', 'Very important')}">
                        <input type="text" name="q1_opt1_desc" value="{campaign.get('form_config', {}).get('q1_opt1_desc', 'I want every dollar I can get')}" placeholder="Description" style="margin-top: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q1_opt1_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q1_opt1_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Option 2 Label</label>
                        <input type="text" name="q1_opt2_label" value="{campaign.get('form_config', {}).get('q1_opt2_label', 'Speed matters more')}">
                        <input type="text" name="q1_opt2_desc" value="{campaign.get('form_config', {}).get('q1_opt2_desc', 'I need to sell quickly')}" placeholder="Description" style="margin-top: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q1_opt2_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q1_opt2_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Option 3 Label</label>
                        <input type="text" name="q1_opt3_label" value="{campaign.get('form_config', {}).get('q1_opt3_label', 'Both')}">
                        <input type="text" name="q1_opt3_desc" value="{campaign.get('form_config', {}).get('q1_opt3_desc', 'Best price in reasonable timeframe')}" placeholder="Description" style="margin-top: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q1_opt3_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q1_opt3_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Option 4 Label (Optional)</label>
                        <input type="text" name="q1_opt4_label" value="{campaign.get('form_config', {}).get('q1_opt4_label', '')}" placeholder="Leave blank if not needed">
                        <input type="text" name="q1_opt4_desc" value="{campaign.get('form_config', {}).get('q1_opt4_desc', '')}" placeholder="Description" style="margin-top: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q1_opt4_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q1_opt4_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>

                </div>
                
                <!-- Question 2: Goals (Checkboxes) -->
                <div style="background: #f7f3e5; padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                    <h4 style="color: #004237; margin-bottom: 16px;">Question 2: Goals (Checkboxes)</h4>
                    
                    <div class="form-group">
                        <label>Question Text</label>
                        <input type="text" name="q2_text" value="{campaign.get('form_config', {}).get('q2_text', 'What is your next move?')}">
                    </div>
                    
                    <div class="form-group">
                        <label>Subtitle (optional)</label>
                        <input type="text" name="q2_subtitle" value="{campaign.get('form_config', {}).get('q2_subtitle', '(Select all that interest you)')}">
                    </div>
                    
                    <div class="form-group">
                        <label>Option 1</label>
                        <input type="text" name="q2_opt1" value="{campaign.get('form_config', {}).get('q2_opt1', 'Buy my next home BEFORE selling')}">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q2_opt1_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q2_opt1_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Option 2</label>
                        <input type="text" name="q2_opt2" value="{campaign.get('form_config', {}).get('q2_opt2', 'Sell my current home')}">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q2_opt2_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q2_opt2_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Option 3</label>
                        <input type="text" name="q2_opt3" value="{campaign.get('form_config', {}).get('q2_opt3', 'Downsize to a smaller home')}">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q2_opt3_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q2_opt3_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Option 4</label>
                        <input type="text" name="q2_opt4" value="{campaign.get('form_config', {}).get('q2_opt4', 'Purchase a second home or investment property')}">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q2_opt4_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q2_opt4_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>

                    
                    <div class="form-group">
                        <label>Additional Text Field Placeholder</label>
                        <input type="text" name="q2_text_placeholder" value="{campaign.get('form_config', {}).get('q2_text_placeholder', 'Tell us more about your plans (optional)')}">
                    </div>
                </div>
                
                <!-- Question 3: Preferences (Radio) -->
                <div style="background: #f7f3e5; padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                    <h4 style="color: #004237; margin-bottom: 16px;">Question 3: Preferences (Radio Buttons)</h4>
                    
                    <div class="form-group">
                        <label>Question Text</label>
                        <input type="text" name="q3_text" value="{campaign.get('form_config', {}).get('q3_text', 'Would you like us to:')}">
                    </div>
                    
                    <div class="form-group">
                        <label>Option 1</label>
                        <input type="text" name="q3_opt1" value="{campaign.get('form_config', {}).get('q3_opt1', 'Send me a detailed equity report')}">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q3_opt1_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q3_opt1_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Option 2</label>
                        <input type="text" name="q3_opt2" value="{campaign.get('form_config', {}).get('q3_opt2', 'Have a Keyes expert contact me')}">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q3_opt2_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q3_opt2_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Option 3 (Optional)</label>
                        <input type="text" name="q3_opt3" value="{campaign.get('form_config', {}).get('q3_opt3', '')}" placeholder="Leave blank if not needed">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q3_opt3_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q3_opt3_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label>Option 4 (Optional)</label>
                        <input type="text" name="q3_opt4" value="{campaign.get('form_config', {}).get('q3_opt4', '')}" placeholder="Leave blank if not needed">
                        <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; font-weight: normal;">
                            <input type="checkbox" name="q3_opt4_preselect" value="true" {'checked' if campaign.get('form_config', {}).get('q3_opt4_preselect') else ''}>
                            Pre-select this option
                        </label>
                    </div>

                    
                    <div class="form-group">
                        <label>Phone Field Placeholder</label>
                        <input type="text" name="q3_phone_placeholder" value="{campaign.get('form_config', {}).get('q3_phone_placeholder', 'Phone number (optional)')}">
                    </div>
                </div>
                
                <!-- Submit Button -->
                <div style="background: #f7f3e5; padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                    <h4 style="color: #004237; margin-bottom: 16px;">Submit Button</h4>
                    
                    <div class="form-group">
                        <label>Button Text</label>
                        <input type="text" name="submit_button_text" value="{campaign.get('form_config', {}).get('submit_button_text', 'GET MY BLUEPRINT')}">
                    </div>
                    
                    <div class="form-group">
                        <label>Disclaimer Text (below button)</label>
                        <textarea name="disclaimer_text" style="min-height: 60px;">{campaign.get('form_config', {}).get('disclaimer_text', 'By submitting, you agree to be contacted by The Keyes Company regarding your home equity.')}</textarea>
                    </div>
                </div>
                
                <!-- Enhanced CTA Section -->
                <div style="background: #f7f3e5; padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                    <h4 style="color: #004237; margin-bottom: 16px;">Enhanced CTA Section</h4>
                    <p style="color: #666; font-size: 14px; margin-bottom: 20px;">Personal, reassuring call-to-action that appears after form questions</p>
                    
                    <div class="form-group">
                        <label>Agent Message</label>
                        <input type="text" name="cta_agent_message" value="{campaign.get('form_config', {}).get('cta_agent_message', 'We will create your custom equity plan in 24 hours')}">
                        <div class="help-text">Personal message from the agent/team (will be shown twice - in checkbox and below photo)</div>
                    </div>
                    
                    <div class="form-group">
                        <label>CTA Tagline</label>
                        <input type="text" name="cta_tagline" value="{campaign.get('form_config', {}).get('cta_tagline', 'No sales pitch, just expert guidance')}">
                        <div class="help-text">Italic tagline that removes friction (shown below agent photo)</div>
                    </div>
                    
                    <div class="form-group">
                        <label>CTA Button Text</label>
                        <input type="text" name="cta_button_text" value="{campaign.get('form_config', {}).get('cta_button_text', 'GET MY EQUITY PLAN')}">
                        <div class="help-text">Large button text (will be displayed in all caps)</div>
                    </div>
                    
                    <div class="form-group">
                        <label>Agent Photo URL</label>
                        <input type="text" name="cta_agent_photo" value="{campaign.get('form_config', {}).get('cta_agent_photo', '')}" placeholder="e.g., https://example.com/agent-photo.jpg">
                        <div class="help-text">URL to agent photo (leave blank for default). Image should be square, at least 200x200px.</div>
                    </div>
                </div>
                
                <hr style="margin: 40px 0; border: none; border-top: 2px solid #f0f0f0;">
                
                <!-- Thank You Page Configuration -->
                <div style="background: #f7f3e5; padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                    <h4 style="color: #004237; margin-bottom: 16px;">Thank You Page</h4>
                    <p style="color: #666; font-size: 14px; margin-bottom: 20px;">Customize what users see after submitting the form</p>
                    
                    <div class="form-group">
                        <label>Thank You Headline</label>
                        <input type="text" name="thankyou_headline" value="{campaign.get('thankyou_config', {}).get('headline', 'Thank You!')}">
                    </div>
                    
                    <div class="form-group">
                        <label>Thank You Message</label>
                        <textarea name="thankyou_message" style="min-height: 80px;">{campaign.get('thankyou_config', {}).get('message', "We've received your information and will be in touch soon.")}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Next Steps Text (Optional)</label>
                        <textarea name="thankyou_next_steps" style="min-height: 60px;" placeholder="e.g., Check your email for your personalized equity report">{campaign.get('thankyou_config', {}).get('next_steps', '')}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Button Text (Optional)</label>
                        <input type="text" name="thankyou_button_text" value="{campaign.get('thankyou_config', {}).get('button_text', '')}" placeholder="e.g., Return to Dashboard">
                    </div>
                    
                    <div class="form-group">
                        <label>Button Link (Optional)</label>
                        <input type="text" name="thankyou_button_link" value="{campaign.get('thankyou_config', {}).get('button_link', '')}" placeholder="e.g., https://keyes.com">
                    </div>
                    
                    <div class="form-group">
                        <label>Auto-Redirect URL (Optional)</label>
                        <input type="text" name="thankyou_redirect_url" value="{campaign.get('thankyou_config', {}).get('redirect_url', '')}" placeholder="Leave blank for no redirect">
                        <small style="color: #666; font-size: 12px; display: block; margin-top: 4px;">If set, page will redirect after 3 seconds</small>
                    </div>
                </div>
                
                <hr style="margin: 40px 0; border: none; border-top: 2px solid #f0f0f0;">
                
                <div class="form-group">
                    <label>Campaign Status</label>
                    <select name="status">
                        <option value="active" {"selected" if campaign["status"] == "active" else ""}>Active</option>
                        <option value="draft" {"selected" if campaign["status"] == "draft" else ""}>Draft</option>
                        <option value="paused" {"selected" if campaign["status"] == "paused" else ""}>Paused</option>
                        <option value="archived" {"selected" if campaign["status"] == "archived" else ""}>Archived</option>
                    </select>
                </div>
                
                <div class="btn-group">
                    <button type="submit" class="btn btn-primary">Save Form Configuration</button>
                    <a href="/campaign/{campaign_id}/generate-email" class="btn" style="background: #fcbfa7; color: #004237;" onclick="return confirm('This will generate email_template.html with your form configuration. Continue?');">Generate Email HTML</a>
                    <a href="/campaign/{campaign_id}/preview" class="btn btn-secondary" target="_blank">Preview Current Email</a>
                    <a href="/campaign/{campaign_id}/download-html" class="btn" style="background: #004237; color: white;">Download HTML</a>
                    <a href="/campaigns" class="btn btn-cancel">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>"""

@app.route('/campaign/<campaign_id>/preview')
def campaign_preview(campaign_id):
    campaign = get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404
    
    # Use the same email generation logic as generate-email route
    # This ensures preview shows exactly what will be generated
    config = campaign.get('form_config', {})
    
    # Format body copy with proper paragraphs
    body_paragraphs = ''
    if campaign.get('body_copy'):
        paras = [p.strip() for p in campaign['body_copy'].split('\n\n') if p.strip()]
        body_paragraphs = ''.join([f'<p style="font-size: 17px; line-height: 1.7; margin: 0 0 20px 0; color: #555555;">{para}</p>' for para in paras])
    
    # If no form config exists, show basic email
    if not config:
        return f'''<!DOCTYPE html>
<html>
<body style="padding: 40px; font-family: Arial;">
<h1>{campaign['headline']}</h1>
<p>{campaign['subheadline']}</p>
<p>{campaign['body_copy']}</p>
<p style="color: #999; margin-top: 40px;">No form configured yet. Edit this campaign to build the form.</p>
</body>
</html>'''
    
    # Build form HTML from config (same logic as generate-email)
    # Q1 HTML
    q1_html = f'''<div style="margin-bottom: 40px;">
        <p style="font-size: 18px; margin: 0 0 8px 0; color: #004237; font-weight: 700; text-align: center;">{config.get('q1_text', '')}</p>
        <p style="font-size: 14px; margin: 0 0 25px 0; color: #777777; text-align: center;">{config.get('q1_subtitle', '')}</p>
        '''
    
    for i in range(1, 11):  # Support up to 10 options
        label = config.get(f'q1_opt{i}_label', '')
        if label:
            desc = config.get(f'q1_opt{i}_desc', '')
            checked = 'checked' if config.get(f'q1_opt{i}_preselect') else ''
            border_color = '#fcbfa7' if checked else '#e0e0e0'
            q1_html += f'''<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 12px;">
                <tr>
                    <td style="padding: 15px; background: #f7f3e5; border: 2px solid {border_color}; border-radius: 8px;">
                        <input type="radio" name="equity_priority" value="opt{i}" {checked} style="margin-right: 12px;">
                        <label style="cursor: pointer; display: inline;">
                            <strong style="color: #004237; font-size: 15px;">{label}</strong><br>
                            <span style="color: #666; font-size: 13px;">{desc}</span>
                        </label>
                    </td>
                </tr>
            </table>'''
    
    q1_html += '</div>'
    
    # Q2 HTML (checkboxes)
    q2_html = f'''<div style="margin-bottom: 40px;">
        <p style="font-size: 18px; margin: 0 0 8px 0; color: #004237; font-weight: 700; text-align: center;">{config.get('q2_text', '')}</p>
        <p style="font-size: 14px; margin: 0 0 25px 0; color: #777777; text-align: center;">{config.get('q2_subtitle', '')}</p>
        '''
    
    for i in range(1, 11):  # Support up to 10 options
        opt_text = config.get(f'q2_opt{i}', '')
        if opt_text:
            checked = 'checked' if config.get(f'q2_opt{i}_preselect') else ''
            q2_html += f'''<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 12px;">
                <tr>
                    <td style="padding: 15px; background: #f7f3e5; border: 2px solid #e0e0e0; border-radius: 8px;">
                        <input type="checkbox" name="goals" value="{opt_text}" {checked} style="margin-right: 12px;">
                        <label style="color: #004237; font-size: 14px; font-weight: 500;">{opt_text}</label>
                    </td>
                </tr>
            </table>'''
    
    q2_html += f'''<textarea name="goals_text" placeholder="{config.get('q2_text_placeholder', '')}" style="width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; margin-top: 12px;"></textarea>
    </div>'''
    
    # Q3 HTML
    q3_html = f'''<div style="margin-bottom: 30px;">
        <p style="font-size: 18px; margin: 0 0 25px 0; color: #004237; font-weight: 700; text-align: center;">{config.get('q3_text', '')}</p>
        '''
    
    for i in [1, 2]:
        opt_text = config.get(f'q3_opt{i}', '')
        if opt_text:
            checked = 'checked' if config.get(f'q3_opt{i}_preselect') else ''
            border_color = '#fcbfa7' if checked else '#e0e0e0'
            q3_html += f'''<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 12px;">
                <tr>
                    <td style="padding: 15px; background: #f7f3e5; border: 2px solid {border_color}; border-radius: 8px;">
                        <input type="radio" name="contact_preference" value="opt{i}" {checked} style="margin-right: 12px;">
                        <label style="color: #004237; font-size: 14px; font-weight: 500;">{opt_text}</label>
                    </td>
                </tr>
            </table>'''
    
    q3_html += f'''<input type="tel" name="phone_number" placeholder="{config.get('q3_phone_placeholder', '')}" style="width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; margin-top: 20px;">
    </div>'''
    
    # Callout box HTML
    callout_html = ''
    if config.get('show_callout'):
        callout_html = f'''<tr>
                        <td style="padding: 0 45px 30px;">
                            <div style="background: linear-gradient(135deg, #fcbfa7 0%, #fda67a 100%); padding: 30px; border-radius: 12px; text-align: center;">
                                <p style="font-size: 14px; color: #004237; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin: 0 0 12px 0;">{config.get('callout_title', '')}</p>
                                <p style="font-size: 36px; color: #004237; font-weight: 700; margin: 0 0 8px 0; line-height: 1;">{config.get('callout_main_text', '')}</p>
                                <p style="font-size: 14px; color: #004237; margin: 0;">{config.get('callout_subtitle', '')}</p>
                            </div>
                        </td>
                    </tr>'''
    
    # Complete email
    email_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{campaign['subject']}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f7f3e5;">
    <div style="background: #004237; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center;">
        <a href="/campaigns" style="color: white; text-decoration: none; font-size: 14px; font-weight: 600;">← Back to Campaigns</a>
        <div style="display: flex; gap: 12px;">
            <a href="/campaign/{campaign['id']}/edit" style="background: #e0e0e0; color: #004237; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">Edit</a>
            <a href="/campaign/{campaign['id']}/generate-email" style="background: #fcbfa7; color: #004237; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">Download HTML</a>
            <button onclick="copyToClipboard()" style="background: #004237; color: white; padding: 8px 16px; border: 2px solid white; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer;">Copy HTML</button>
        </div>
    </div>
    <script>
    function copyToClipboard() {{
        const emailContent = document.querySelector('table[width="600"]').outerHTML;
        const fullHTML = `<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>{campaign['subject']}</title>\n</head>\n<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f7f3e5;">\n    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f7f3e5;">\n        <tr>\n            <td align="center" style="padding: 30px 20px;">\n                ${{emailContent}}\n            </td>\n        </tr>\n    </table>\n</body>\n</html>`;
        navigator.clipboard.writeText(fullHTML).then(() => {{
            alert('HTML copied to clipboard! Ready to paste into HubSpot.');
        }}).catch(err => {{
            alert('Failed to copy: ' + err);
        }});
    }}
    </script>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f7f3e5;">
        <tr>
            <td align="center" style="padding: 30px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; max-width: 600px; box-shadow: 0 8px 24px rgba(0,66,55,0.15); border-radius: 12px; overflow: hidden;">
                    <!-- Header with Hero Image Style -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #f7f3e5 0%, #f0ead8 100%); padding: 60px 40px 70px; text-align: center; position: relative;">
                            <!-- Logo -->
                            <div style="margin-bottom: 35px;">
                                <img src="https://raw.githubusercontent.com/StevenMProtech/Keyes/main/keyes-new-logo.png" alt="Keyes" style="width: 180px; height: auto; display: block; margin: 0 auto;" />
                                <p style="color: #004237; font-size: 10px; margin: 12px 0 0 0; letter-spacing: 3px; text-transform: uppercase; font-weight: 500;">Real Estate</p>
                            </div>
                            
                            <!-- Main Headline -->
                            <h2 style="color: #004237; font-size: 52px; line-height: 1.15; margin: 0 0 25px 0; font-weight: 400; letter-spacing: -0.5px; font-family: Georgia, 'Times New Roman', serif;">
                                {campaign['headline']}
                            </h2>
                            
                            <div style="width: 60px; height: 2px; background: #004237; margin: 0 auto 30px;"></div>
                            
                            <!-- Callout Box in Header -->
                            <div style="background: #fefbf9; border: 2px solid #f9e8df; padding: 40px; border-radius: 16px; margin: 0 0 30px 0;">
                                <p style="font-size: 20px; color: #004237; font-weight: 600; letter-spacing: 0.5px; margin: 0 0 20px 0;">{config.get('callout_title', '')}</p>
                                <p style="font-size: 72px; color: #004237; font-weight: 700; margin: 0 0 20px 0; line-height: 0.9; letter-spacing: -2px;">{config.get('callout_main_text', '')}</p>
                                <p style="font-size: 18px; color: #666666; margin: 0; line-height: 1.4;">{config.get('callout_subtitle', '')}</p>
                            </div>
                            
                            <p style="color: #004237; font-size: 20px; line-height: 1.4; margin: 25px 0 0 0; font-weight: 700;">
                                {campaign.get('subheadline', '')}
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 20px 45px 30px;">
                            <!-- Body Headline -->
                            <h3 style="color: #004237; font-size: 36px; line-height: 1.3; margin: 0 0 30px 0; font-weight: 700;">{campaign.get('body_headline', '')}</h3>
                            
                            <!-- Body Paragraphs -->
                            {body_paragraphs}
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding: 0 45px 50px;">
                            <div style="background: #ffffff; border: 2px solid #004237; padding: 40px 35px; border-radius: 12px;">
                                {q1_html}
                                {q2_html}
                                
                                    <!-- Enhanced CTA Section -->
                                    <div style="padding: 30px 0; text-align: center; border-top: 1px solid #e0e0e0; margin-top: 30px;">
                                        <!-- Checkbox Option -->
                                        <label style="display: flex; align-items: flex-start; gap: 15px; text-align: left; cursor: pointer; margin-bottom: 40px;">
                                            <input type="checkbox" name="follow_up" value="yes" checked style="width: 24px; height: 24px; margin-top: 2px; accent-color: #004237;">
                                            <div>
                                                <p style="font-size: 20px; font-weight: 600; color: #004237; margin: 0;">Have a Keyes expert follow up with me</p>
                                            </div>
                                        </label>
                                        
                                        <!-- Large CTA Button -->
                                        <button type="submit" style="background: #004237; color: white; padding: 20px 60px; border: none; border-radius: 8px; font-size: 18px; font-weight: 700; cursor: pointer; letter-spacing: 1.5px; box-shadow: 0 4px 12px rgba(0,66,55,0.3); transition: all 0.3s; margin-bottom: {'40px' if config.get('cta_agent_photo', '').strip() else '0'};">{config.get('cta_button_text', 'GET MY EQUITY PLAN')}</button>
                                        
                                        {('<!-- Agent Photo --><img src="' + config.get('cta_agent_photo', '') + '" alt="Keyes Expert" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin-bottom: 20px;"><!-- Agent Message --><p style="font-size: 17px; color: #333; margin: 0 0 8px 0; font-weight: 500;">' + config.get('cta_agent_message', 'We will create your custom equity plan in 24 hours') + '</p><p style="font-size: 15px; color: #666; margin: 0; font-style: italic;">' + config.get('cta_tagline', 'No sales pitch, just expert guidance') + '</p>') if config.get('cta_agent_photo', '').strip() else ''}
                                    </div>
                                
                                <p style="font-size: 11px; color: #999; text-align: center; margin: 20px 0 0 0; line-height: 1.5;">{config.get('disclaimer_text', '')}</p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Why Us Section -->
                    <tr>
                        <td style="background: #004237; padding: 50px 45px; color: white;">
                            <h3 style="font-size: 32px; font-weight: 300; font-style: italic; margin: 0 0 35px 0; text-align: center;">Why Us:</h3>
                            
                            <div style="text-align: left; max-width: 500px; margin: 0 auto;">
                                <div style="margin-bottom: 25px;">
                                    <p style="font-size: 18px; font-weight: 700; margin: 0 0 8px 0;">98 Years of Trust:</p>
                                    <p style="font-size: 15px; opacity: 0.9; margin: 0; line-height: 1.6;">Florida's most experienced brokerage with nearly a century of market expertise.</p>
                                </div>
                                
                                <div style="margin-bottom: 25px;">
                                    <p style="font-size: 18px; font-weight: 700; margin: 0 0 8px 0;">4,000+ Agent Network:</p>
                                    <p style="font-size: 15px; opacity: 0.9; margin: 0; line-height: 1.6;">Maximum exposure for your property across our extensive network.</p>
                                </div>
                                
                                <div>
                                    <p style="font-size: 18px; font-weight: 700; margin: 0 0 8px 0;">Exclusive Pre-MLS Access:</p>
                                    <p style="font-size: 15px; opacity: 0.9; margin: 0; line-height: 1.6;">Get first look at properties before they hit the public market.</p>
                                </div>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #f7f3e5; padding: 30px; text-align: center;">
                            <p style="color: #666; font-size: 12px; margin: 0;">© 2025 The Keyes Company. All rights reserved.</p>
                            <p style="color: #999; font-size: 11px; margin: 8px 0 0 0;">98 Years of Trust | 4,000+ Realtors®</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
    
    return email_html

@app.route('/campaign/<campaign_id>/generate-email')
def generate_email(campaign_id):
    campaign = get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404
    
    config = campaign.get('form_config', {})
    
    # Determine which option is pre-selected for Q1
    q1_checked = ''
    if config.get('q1_opt1_preselect'):
        q1_checked = 'checked="checked"' if config.get('q1_opt1_preselect') else ''
        q1_value = 'maximize'
    elif config.get('q1_opt2_preselect'):
        q1_checked = 'checked="checked"'
        q1_value = 'speed'
    elif config.get('q1_opt3_preselect'):
        q1_checked = 'checked="checked"'
        q1_value = 'balance'
    else:
        q1_value = ''
    
    # Build Q1 HTML
    q1_html = f'''<div style="margin-bottom: 40px;">
                        <p style="font-size: 18px; margin: 0 0 8px 0; color: #004237; font-weight: 700; text-align: center;">{config.get('q1_text', 'How important is reaching the high end of your equity?')}</p>
                        <p style="font-size: 14px; margin: 0 0 25px 0; color: #777777; text-align: center;">{config.get('q1_subtitle', '')}</p>
                        
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td style="padding: 15px; background: #f7f3e5; border: 2px solid {'#fcbfa7' if config.get('q1_opt1_preselect') else '#e0e0e0'}; border-radius: 8px; margin-bottom: 12px; cursor: pointer;">
                                    <input type="radio" name="equity_priority" value="maximize" id="maximize" {'checked' if config.get('q1_opt1_preselect') else ''} style="margin-right: 12px;">
                                    <label for="maximize" style="cursor: pointer; display: inline;">
                                        <strong style="color: #004237; font-size: 15px;">{config.get('q1_opt1_label', 'Very important')}</strong><br>
                                        <span style="color: #666; font-size: 13px;">{config.get('q1_opt1_desc', 'I want every dollar I can get')}</span>
                                    </label>
                                </td>
                            </tr>
                        </table>
                        <div style="height: 12px;"></div>
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td style="padding: 15px; background: #f7f3e5; border: 2px solid {'#fcbfa7' if config.get('q1_opt2_preselect') else '#e0e0e0'}; border-radius: 8px; margin-bottom: 12px; cursor: pointer;">
                                    <input type="radio" name="equity_priority" value="speed" id="speed" {'checked' if config.get('q1_opt2_preselect') else ''} style="margin-right: 12px;">
                                    <label for="speed" style="cursor: pointer; display: inline;">
                                        <strong style="color: #004237; font-size: 15px;">{config.get('q1_opt2_label', 'Speed matters more')}</strong><br>
                                        <span style="color: #666; font-size: 13px;">{config.get('q1_opt2_desc', 'I need to sell quickly')}</span>
                                    </label>
                                </td>
                            </tr>
                        </table>
                        <div style="height: 12px;"></div>
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td style="padding: 15px; background: #f7f3e5; border: 2px solid {'#fcbfa7' if config.get('q1_opt3_preselect') else '#e0e0e0'}; border-radius: 8px; cursor: pointer;">
                                    <input type="radio" name="equity_priority" value="balance" id="balance" {'checked' if config.get('q1_opt3_preselect') else ''} style="margin-right: 12px;">
                                    <label for="balance" style="cursor: pointer; display: inline;">
                                        <strong style="color: #004237; font-size: 15px;">{config.get('q1_opt3_label', 'Both')}</strong><br>
                                        <span style="color: #666; font-size: 13px;">{config.get('q1_opt3_desc', 'Best price in reasonable timeframe')}</span>
                                    </label>
                                </td>
                            </tr>
                        </table>
                    </div>'''
    
    # Build Q2 HTML (checkboxes)
    q2_options = []
    for i in range(1, 11):  # Support up to 10 options
        opt_text = config.get(f'q2_opt{i}', '')
        if opt_text:
            is_checked = 'checked' if config.get(f'q2_opt{i}_preselect') else ''
            q2_options.append(f'''<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 12px;">
                                <tr>
                                    <td style="padding: 15px; background: #f7f3e5; border: 2px solid #e0e0e0; border-radius: 8px;">
                                        <input type="checkbox" name="goals" value="{opt_text.lower().replace(' ', '_')}" {is_checked} style="margin-right: 12px;">
                                        <label style="color: #004237; font-size: 14px; font-weight: 500;">{opt_text}</label>
                                    </td>
                                </tr>
                            </table>''')
    
    q2_html = f'''<div style="margin-bottom: 40px;">
                        <p style="font-size: 18px; margin: 0 0 8px 0; color: #004237; font-weight: 700; text-align: center;">{config.get('q2_text', "What's your next move?")}</p>
                        <p style="font-size: 14px; margin: 0 0 25px 0; color: #777777; text-align: center;">{config.get('q2_subtitle', '(Select all that interest you)')}</p>
                        
                        {''.join(q2_options)}
                        
                        <textarea name="goals_text" placeholder="{config.get('q2_text_placeholder', 'Tell us more about your plans (optional)')}" style="width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; font-family: inherit; min-height: 80px; margin-top: 12px;"></textarea>
                    </div>'''
    
    # Build Q3 HTML (radio)
    q3_html = f'''<div style="margin-bottom: 30px;">
                        <p style="font-size: 18px; margin: 0 0 25px 0; color: #004237; font-weight: 700; text-align: center;">{config.get('q3_text', 'Would you like us to:')}</p>
                        
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 12px;">
                            <tr>
                                <td style="padding: 15px; background: #f7f3e5; border: 2px solid {'#fcbfa7' if config.get('q3_opt1_preselect') else '#e0e0e0'}; border-radius: 8px;">
                                    <input type="radio" name="contact_preference" value="report" id="report" {'checked' if config.get('q3_opt1_preselect') else ''} style="margin-right: 12px;">
                                    <label for="report" style="color: #004237; font-size: 14px; font-weight: 500;">{config.get('q3_opt1', 'Send me a detailed equity report')}</label>
                                </td>
                            </tr>
                        </table>
                        
                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td style="padding: 15px; background: #f7f3e5; border: 2px solid {'#fcbfa7' if config.get('q3_opt2_preselect') else '#e0e0e0'}; border-radius: 8px;">
                                    <input type="radio" name="contact_preference" value="expert" id="expert" {'checked' if config.get('q3_opt2_preselect') else ''} style="margin-right: 12px;">
                                    <label for="expert" style="color: #004237; font-size: 14px; font-weight: 500;">{config.get('q3_opt2', 'Have a Keyes expert contact me')}</label>
                                </td>
                            </tr>
                        </table>
                        
                        <input type="tel" name="phone_number" placeholder="{config.get('q3_phone_placeholder', 'Phone number (optional)')}" style="width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; margin-top: 20px;">
                    </div>'''
    
    # Generate complete email HTML
    email_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{campaign['subject']} - The Keyes Company</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f7f3e5;">
    <div style="background: #004237; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center;">
        <a href="/campaigns" style="color: white; text-decoration: none; font-size: 14px; font-weight: 600;">← Back to Campaigns</a>
        <div style="display: flex; gap: 12px;">
            <a href="/campaign/{campaign['id']}/edit" style="background: #e0e0e0; color: #004237; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">Edit</a>
            <a href="/campaign/{campaign['id']}/generate-email" style="background: #fcbfa7; color: #004237; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">Download HTML</a>
            <button onclick="copyToClipboard()" style="background: #004237; color: white; padding: 8px 16px; border: 2px solid white; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer;">Copy HTML</button>
        </div>
    </div>
    <script>
    function copyToClipboard() {{
        const emailContent = document.querySelector('table[width="600"]').outerHTML;
        const fullHTML = `<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>{campaign['subject']}</title>\n</head>\n<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f7f3e5;">\n    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f7f3e5;">\n        <tr>\n            <td align="center" style="padding: 30px 20px;">\n                ${{emailContent}}\n            </td>\n        </tr>\n    </table>\n</body>\n</html>`;
        navigator.clipboard.writeText(fullHTML).then(() => {{
            alert('HTML copied to clipboard! Ready to paste into HubSpot.');
        }}).catch(err => {{
            alert('Failed to copy: ' + err);
        }});
    }}
    </script>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f7f3e5;">
        <tr>
            <td align="center" style="padding: 30px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; max-width: 600px; box-shadow: 0 8px 24px rgba(0,66,55,0.15); border-radius: 12px; overflow: hidden;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #f7f3e5 0%, #f0ead8 100%); padding: 60px 40px; text-align: center;">
                            <h2 style="color: #004237; font-size: 42px; line-height: 1.2; margin: 0 0 25px 0; font-weight: 300;">
                                {campaign['headline']}
                            </h2>
                            <p style="color: #666; font-size: 18px; margin: 0;">{campaign['subheadline']}</p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 20px 45px 30px;">
                            <!-- Body Headline -->
                            <h3 style="color: #004237; font-size: 36px; line-height: 1.3; margin: 0 0 30px 0; font-weight: 700;">{campaign.get('body_headline', '')}</h3>
                            
                            <!-- Body Paragraphs -->
                            {body_paragraphs}
                        </td>
                    </tr>

                    <!-- FORM START -->
                    <tr>
                        <td style="padding: 0 45px 50px;">
                            <form action="https://keyes-4pmx.onrender.com/api/submit" method="POST" style="margin: 0;">
                                <input type="hidden" name="campaign_id" value="{campaign['id']}">
                                <input type="hidden" name="email" value="{{{{ contact.email }}}}">
                                <input type="hidden" name="firstName" value="{{{{ contact.firstname }}}}">
                                <input type="hidden" name="lastName" value="{{{{ contact.lastname }}}}">
                                
                                <div style="background: #ffffff; border: 2px solid #004237; padding: 40px 35px; border-radius: 12px;">
                                    
                                    {q1_html}
                                    
                                    {q2_html}
                                    
                                    <!-- Enhanced CTA Section -->
                                    <div style="padding: 30px 0; text-align: center; border-top: 1px solid #e0e0e0; margin-top: 30px;">
                                        <!-- Checkbox Option -->
                                        <label style="display: flex; align-items: flex-start; gap: 15px; text-align: left; cursor: pointer; margin-bottom: 40px;">
                                            <input type="checkbox" name="follow_up" value="yes" checked style="width: 24px; height: 24px; margin-top: 2px; accent-color: #004237;">
                                            <div>
                                                <p style="font-size: 20px; font-weight: 600; color: #004237; margin: 0;">Have a Keyes expert follow up with me</p>
                                            </div>
                                        </label>
                                        
                                        <!-- Large CTA Button -->
                                        <button type="submit" style="background: #004237; color: white; padding: 20px 60px; border: none; border-radius: 8px; font-size: 18px; font-weight: 700; cursor: pointer; letter-spacing: 1.5px; box-shadow: 0 4px 12px rgba(0,66,55,0.3); transition: all 0.3s; margin-bottom: {'40px' if config.get('cta_agent_photo', '').strip() else '0'};">{config.get('cta_button_text', 'GET MY EQUITY PLAN')}</button>
                                        
                                        {('<!-- Agent Photo --><img src="' + config.get('cta_agent_photo', '') + '" alt="Keyes Expert" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin-bottom: 20px;"><!-- Agent Message --><p style="font-size: 17px; color: #333; margin: 0 0 8px 0; font-weight: 500;">' + config.get('cta_agent_message', 'We will create your custom equity plan in 24 hours') + '</p><p style="font-size: 15px; color: #666; margin: 0; font-style: italic;">' + config.get('cta_tagline', 'No sales pitch, just expert guidance') + '</p>') if config.get('cta_agent_photo', '').strip() else ''}
                                    </div>
                                    
                                    <p style="font-size: 11px; color: #999; text-align: center; margin: 20px 0 0 0; line-height: 1.5;">{config.get('disclaimer_text', 'By submitting, you agree to be contacted by The Keyes Company regarding your home equity.')}</p>
                                </div>
                            </form>
                        </td>
                    </tr>
                    
                    <!-- Why Us Section -->
                    <tr>
                        <td style="background: #004237; padding: 50px 45px; color: white;">
                            <h3 style="font-size: 32px; font-weight: 300; font-style: italic; margin: 0 0 35px 0; text-align: center;">Why Us:</h3>
                            
                            <div style="text-align: left; max-width: 500px; margin: 0 auto;">
                                <div style="margin-bottom: 25px;">
                                    <p style="font-size: 18px; font-weight: 700; margin: 0 0 8px 0;">98 Years of Trust:</p>
                                    <p style="font-size: 15px; opacity: 0.9; margin: 0; line-height: 1.6;">Florida's most experienced brokerage with nearly a century of market expertise.</p>
                                </div>
                                
                                <div style="margin-bottom: 25px;">
                                    <p style="font-size: 18px; font-weight: 700; margin: 0 0 8px 0;">4,000+ Agent Network:</p>
                                    <p style="font-size: 15px; opacity: 0.9; margin: 0; line-height: 1.6;">Maximum exposure for your property across our extensive network.</p>
                                </div>
                                
                                <div>
                                    <p style="font-size: 18px; font-weight: 700; margin: 0 0 8px 0;">Exclusive Pre-MLS Access:</p>
                                    <p style="font-size: 15px; opacity: 0.9; margin: 0; line-height: 1.6;">Sell faster and for more with our exclusive buyer network.</p>
                                </div>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #f7f3e5; padding: 30px; text-align: center;">
                            <p style="color: #666; font-size: 12px; margin: 0;">© 2025 The Keyes Company. All rights reserved.</p>
                            <p style="color: #999; font-size: 11px; margin: 8px 0 0 0;">98 Years of Trust | 4,000+ Realtors®</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
    
    # Save to email_template.html
    with open('email_template.html', 'w') as f:
        f.write(email_html)
    
    return '<script>alert("Email HTML generated successfully! Check email_template.html"); window.location.href="/campaign/' + campaign_id + '/edit";</script>'

@app.route('/campaign/<campaign_id>/download-html')
def download_campaign_html(campaign_id):
    """Generate and download campaign HTML file"""
    campaign = get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404
    
    from flask import make_response
    
    # Generate the email HTML
    email_html = generate_email_html_content(campaign)
    
    # Create response with download headers
    response = make_response(email_html)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=campaign_{campaign_id}.html'
    
    return response

@app.route('/campaign/new', methods=['GET', 'POST'])
def campaign_new():
    # Get segment from query param for pre-selection
    default_segment = request.args.get('segment', 'general')
    
    if request.method == 'POST':
        campaigns = load_campaigns()
        
        # Generate campaign ID from name
        campaign_name = request.form.get('name', '')
        campaign_id = campaign_name.lower().replace(' ', '-').replace('_', '-')
        
        # Check if ID already exists
        if any(c['id'] == campaign_id for c in campaigns):
            return '<script>alert("Campaign ID already exists. Please use a different name."); window.history.back();</script>'
        
        new_campaign = {
            'id': campaign_id,
            'name': campaign_name,
            'segment': request.form.get('segment', 'general'),
            'status': request.form.get('status', 'draft'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'subject': request.form.get('subject', ''),
            'headline': request.form.get('headline', ''),
            'subheadline': request.form.get('subheadline', ''),
            'body_headline': request.form.get('body_headline', ''),
            'cta_text': request.form.get('cta_text', 'Get Started'),
            'body_copy': request.form.get('body_copy', ''),
            'form_config': {
                'show_callout': True,  # Always show callout box
                'callout_title': request.form.get('callout_title', ''),
                'callout_main_text': request.form.get('callout_main_text', ''),
                'callout_subtitle': request.form.get('callout_subtitle', ''),
                'cta_agent_message': request.form.get('cta_agent_message', ''),
                'cta_tagline': request.form.get('cta_tagline', ''),
                'cta_button_text': request.form.get('cta_button_text', 'GET MY EQUITY PLAN'),
                'cta_agent_photo': request.form.get('cta_agent_photo', ''),
                'q1_text': request.form.get('q1_text', ''),
                'q1_subtitle': request.form.get('q1_subtitle', ''),
                'q1_opt1_label': request.form.get('q1_opt1_label', ''),
                'q1_opt1_desc': request.form.get('q1_opt1_desc', ''),
                'q1_opt2_label': request.form.get('q1_opt2_label', ''),
                'q1_opt2_desc': request.form.get('q1_opt2_desc', ''),
                'q1_opt3_label': request.form.get('q1_opt3_label', ''),
                'q1_opt3_desc': request.form.get('q1_opt3_desc', ''),
                'q1_opt4_label': request.form.get('q1_opt4_label', ''),
                'q1_opt4_desc': request.form.get('q1_opt4_desc', ''),
                'q2_text': request.form.get('q2_text', ''),
                'q2_subtitle': request.form.get('q2_subtitle', ''),
                'q2_opt1': request.form.get('q2_opt1', ''),
                'q2_opt2': request.form.get('q2_opt2', ''),
                'q2_opt3': request.form.get('q2_opt3', ''),
                'q2_opt4': request.form.get('q2_opt4', ''),
                'q3_text': request.form.get('q3_text', ''),
                'q3_subtitle': request.form.get('q3_subtitle', ''),
                'q3_opt1': request.form.get('q3_opt1', ''),
                'q3_opt2': request.form.get('q3_opt2', ''),
                'q3_opt3': request.form.get('q3_opt3', ''),
                'q3_opt4': request.form.get('q3_opt4', '')
            },
            'form_fields': {
                'email': True,
                'firstName': True,
                'lastName': True,
                'phoneNumber': True,
                'equity_priority': True,
                'goals': True,
                'wantsReport': True,
                'wantsExpert': True
            },
            'colors': {
                'primary': '#004237',
                'accent': '#fcbfa7',
                'background': '#f7f3e5'
            }
        }
        
        campaigns.append(new_campaign)
        save_campaigns(campaigns)
        return f'<script>alert("Campaign created successfully!"); window.location.href="/campaign/{campaign_id}/preview";</script>'
    
    # Load behavioral audiences from database
    behavioral_audiences = load_behavioral_audiences()
    
    # Load past client segments
    try:
        with open('past_clients.json', 'r') as f:
            past_client_segments = json.load(f)
    except:
        past_client_segments = []
    
    # Load template and replace placeholders
    with open('templates/campaign_new_complete.html', 'r') as f:
        html = f.read()
    
    # Build past client segments options HTML
    past_client_options_html = ""
    if past_client_segments:
        past_client_options_html = '<option disabled>──────────────────────────</option>\n'
        past_client_options_html += '<option disabled style="font-weight: 600;">PAST CLIENT SEGMENTS</option>\n'
        for seg in past_client_segments:
            selected = 'selected' if default_segment == seg['id'] else ''
            past_client_options_html += f'<option value="{seg["id"]}" {selected}>{seg["name"]}</option>\n'
    
    # Build behavioral audiences options HTML
    behavioral_options_html = ""
    if behavioral_audiences:
        behavioral_options_html = '<option disabled>──────────────────────────</option>\n'
        behavioral_options_html += '<option disabled style="font-weight: 600;">BEHAVIORAL AUDIENCES</option>\n'
        for aud in behavioral_audiences:
            selected = 'selected' if default_segment == aud['id'] else ''
            behavioral_options_html += f'<option value="{aud["id"]}" {selected}>{aud.get("audience_name", aud.get("name", "Unnamed"))}</option>\n'
    
    # Replace segment selection placeholders
    html = html.replace('{{SELECTED_ALL_CASH}}', 'selected' if default_segment == 'all-cash' else '')
    html = html.replace('{{SELECTED_ABSENTEE_INSTATE}}', 'selected' if default_segment == 'absentee-instate' else '')
    html = html.replace('{{SELECTED_ABSENTEE_OUTSTATE}}', 'selected' if default_segment == 'absentee-outstate' else '')
    html = html.replace('{{SELECTED_GENERAL}}', 'selected' if default_segment == 'general' else '')
    html = html.replace('{{SELECTED_LUXURY}}', 'selected' if default_segment == 'homes-over-$2,000,000' else '')
    
    # Inject past client segments and behavioral audiences before </select>
    all_audiences_html = past_client_options_html + behavioral_options_html
    html = html.replace('</select>', all_audiences_html + '</select>')
    
    return html

# Segments Management Routes
@app.route('/segments')
def segments_dashboard():
    segments = load_segments()
    campaigns = load_campaigns()
    submissions = load_submissions()
    
    # Calculate stats per segment
    segment_stats = {}
    for segment in segments:
        segment_id = segment['id']
        segment_campaigns = [c for c in campaigns if c.get('segment') == segment_id]
        segment_submissions = [s for s in submissions if any(c['id'] == s.get('campaign_id') for c in segment_campaigns)]
        
        segment_stats[segment_id] = {
            'campaigns': len(segment_campaigns),
            'submissions': len(segment_submissions),
            'active_campaigns': sum(1 for c in segment_campaigns if c.get('status') == 'active')
        }
    
    segments_html = ""
    for segment in segments:
        stats = segment_stats.get(segment['id'], {'campaigns': 0, 'submissions': 0, 'active_campaigns': 0})
        
        segments_html += f"""
        <div style="background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid {segment['color']};">
            <div style="display: flex; align-items: start; gap: 20px; margin-bottom: 20px;">
                <div style="font-size: 48px; line-height: 1;">{segment['icon']}</div>
                <div style="flex: 1;">
                    <h3 style="color: #004237; font-size: 22px; margin-bottom: 8px;">{segment['name']}</h3>
                    <p style="color: #666; font-size: 14px; line-height: 1.5;">{segment['description']}</p>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; padding: 20px; background: #f7f3e5; border-radius: 8px; margin-bottom: 20px;">
                <div>
                    <div style="color: #999; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">Total Campaigns</div>
                    <div style="color: #004237; font-size: 28px; font-weight: 700;">{stats['campaigns']}</div>
                </div>
                <div>
                    <div style="color: #999; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">Active Campaigns</div>
                    <div style="color: {segment['color']}; font-size: 28px; font-weight: 700;">{stats['active_campaigns']}</div>
                </div>
                <div>
                    <div style="color: #999; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">Total Submissions</div>
                    <div style="color: #fcbfa7; font-size: 28px; font-weight: 700;">{stats['submissions']}</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 12px;">
                <a href="/segments/{segment['id']}" style="display: inline-block; padding: 12px 24px; background: {segment['color']}; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; transition: all 0.3s;">View Campaigns</a>
                <a href="/segments/{segment['id']}/edit" style="display: inline-block; padding: 12px 24px; background: #fcbfa7; color: #004237; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px;">Edit Segment</a>
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Past Client Segments - The Keyes Company</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .header h1 {{ font-size: 36px; margin-bottom: 12px; }}
        .header p {{ font-size: 16px; opacity: 0.9; line-height: 1.5; }}
        .segments-grid {{
            display: grid;
            gap: 24px;
            margin-top: 30px;
        }}
        .back-link {{
            display: inline-block;
            margin-top: 20px;
            color: white;
            text-decoration: none;
            opacity: 0.9;
            transition: opacity 0.2s;
        }}
        .back-link:hover {{ opacity: 1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Past Client Segments</h1>
            <p>Target specific client groups with personalized campaigns. Track performance across different market segments to optimize your outreach strategy.</p>
            <div style="margin-top: 20px;">
                <a href="/segments/new" style="display: inline-block; padding: 12px 24px; background: #fcbfa7; color: #004237; text-decoration: none; border-radius: 6px; font-weight: 600; margin-right: 12px;">+ New Segment</a>
                <a href="/" class="back-link">← Back to Dashboard</a>
            </div>
        </div>
        
        <div class="segments-grid">
            {segments_html}
        </div>
    </div>
</body>
</html>"""

@app.route('/campaign/<campaign_id>/delete')
def campaign_delete(campaign_id):
    # Protect initial template
    if campaign_id == 'home-equity-2025':
        return '<script>alert("Cannot delete the initial template campaign."); window.location.href="/campaigns";</script>'
    
    campaigns = load_campaigns()
    campaigns = [c for c in campaigns if c['id'] != campaign_id]
    save_campaigns(campaigns)
    return '<script>alert("Campaign deleted successfully!"); window.location.href="/campaigns";</script>'

@app.route('/segments/<segment_id>')
def segment_campaigns(segment_id):
    segment = get_segment(segment_id)
    if not segment:
        return "Segment not found", 404
    
    campaigns = load_campaigns()
    segment_campaigns = [c for c in campaigns if c.get('segment') == segment_id]
    submissions = load_submissions()
    
    campaigns_html = ""
    for campaign in segment_campaigns:
        campaign_submissions = [s for s in submissions if s.get('campaign_id') == campaign['id']]
        status_badge = f'<span style="background: {"#004237" if campaign["status"] == "active" else "#fcbfa7"}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; text-transform: uppercase; font-weight: 600;">{campaign["status"]}</span>'
        
        campaigns_html += f"""
        <div style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid {segment['color']};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <h3 style="color: #004237; font-size: 20px; margin-bottom: 8px;">{campaign['name']}</h3>
                    <p style="color: #666; font-size: 14px; margin-bottom: 8px;">ID: {campaign['id']}</p>
                    <p style="color: #999; font-size: 12px;">Created: {campaign['created_at']} | Updated: {campaign['updated_at']}</p>
                </div>
                <div>{status_badge}</div>
            </div>
            
            <div style="background: rgba({int(segment['color'][1:3], 16)}, {int(segment['color'][3:5], 16)}, {int(segment['color'][5:7], 16)}, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 24px;">{segment['icon']}</span>
                    <div>
                        <div style="font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 2px;">Targeting Segment</div>
                        <div style="font-size: 14px; color: #004237; font-weight: 600;">{segment['name']}</div>
                    </div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px;">
                <div style="background: #f7f3e5; padding: 15px; border-radius: 8px;">
                    <div style="color: #999; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">Total Submissions</div>
                    <div style="color: #004237; font-size: 24px; font-weight: 700;">{len(campaign_submissions)}</div>
                </div>
                <div style="background: #f7f3e5; padding: 15px; border-radius: 8px;">
                    <div style="color: #999; font-size: 11px; text-transform: uppercase; margin-bottom: 4px;">Pending</div>
                    <div style="color: #fcbfa7; font-size: 24px; font-weight: 700;">{sum(1 for s in campaign_submissions if s.get('status') == 'pending')}</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <a href="/campaign/{campaign['id']}" style="padding: 10px 20px; background: #004237; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">View Details</a>
                <a href="/campaign/{campaign['id']}/edit" style="padding: 10px 20px; background: #fcbfa7; color: #004237; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Edit Campaign</a>
                <a href="/campaign/{campaign['id']}/preview" style="padding: 10px 20px; background: white; color: #004237; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600; border: 2px solid #004237;">Preview Email</a>
                {'' if campaign['id'] == 'home-equity-2025' else f'<a href="/campaign/{campaign["id"]}/delete" onclick="return confirm(&quot;Are you sure you want to delete this campaign? This cannot be undone.&quot;);" style="padding: 10px 20px; background: #dc3545; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Delete</a>'}
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{segment['name']} Campaigns - The Keyes Company</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, {segment['color']} 0%, #003329 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .header-icon {{ font-size: 64px; line-height: 1; }}
        .header h1 {{ font-size: 32px; margin-bottom: 8px; }}
        .header p {{ font-size: 15px; opacity: 0.9; line-height: 1.5; }}
        .back-link {{
            display: inline-block;
            margin-top: 15px;
            color: white;
            text-decoration: none;
            opacity: 0.9;
            transition: opacity 0.2s;
        }}
        .back-link:hover {{ opacity: 1; }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            background: white;
            color: {segment['color']};
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 20px;
            transition: all 0.3s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255,255,255,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-icon">{segment['icon']}</div>
            <div style="flex: 1;">
                <h1>{segment['name']}</h1>
                <p>{segment['description']}</p>
                <a href="/segments" class="back-link">← Back to Segments</a>
                <a href="/campaign/new?segment={segment_id}" class="btn">+ New Campaign for this Segment</a>
            </div>
        </div>
        
        {campaigns_html if campaigns_html else '<div style="background: white; padding: 60px; text-align: center; border-radius: 12px; color: #999;"><p style="font-size: 18px;">No campaigns for this segment yet. Create your first campaign to get started!</p></div>'}
    </div>
</body>
</html>"""

# Email Template Management Routes
# Template routes removed - confusing feature

# Segment Management Routes
@app.route('/segments/<segment_id>/edit', methods=['GET', 'POST'])
def segment_edit(segment_id):
    if request.method == 'POST':
        segments = load_segments()
        for i, seg in enumerate(segments):
            if seg['id'] == segment_id:
                segments[i]['name'] = request.form.get('name', seg['name'])
                segments[i]['description'] = request.form.get('description', seg['description'])
                segments[i]['color'] = request.form.get('color', seg['color'])
                save_segments(segments)
                return '<script>alert("Segment updated successfully!"); window.location.href="/segments";</script>'
        return "Segment not found", 404
    
    segment = get_segment(segment_id)
    if not segment:
        return "Segment not found", 404
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Edit Segment - The Keyes Company</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .form-container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .form-group {{
            margin-bottom: 24px;
        }}
        label {{
            display: block;
            color: #004237;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        input, textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
        }}
        textarea {{ min-height: 100px; }}
        .btn {{
            padding: 14px 28px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            margin-right: 12px;
        }}
        .btn-primary {{
            background: #004237;
            color: white;
        }}
        .btn-cancel {{
            background: #e0e0e0;
            color: #666;
            text-decoration: none;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Edit Segment: {segment['name']}</h1>
        </div>
        <div class="form-container">
            <form method="POST">
                <div class="form-group">
                    <label>Segment Name</label>
                    <input type="text" name="name" value="{segment['name']}" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" required>{segment['description']}</textarea>
                </div>
                <div class="form-group">
                    <label>Color (Keyes brand colors only)</label>
                    <select name="color" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 6px;">
                        <option value="#004237" {'selected' if segment['color'] == '#004237' else ''}>Keyes Green (#004237)</option>
                        <option value="#fcbfa7" {'selected' if segment['color'] == '#fcbfa7' else ''}>Keyes Coral (#fcbfa7)</option>
                        <option value="#f7f3e5" {'selected' if segment['color'] == '#f7f3e5' else ''}>Keyes Cream (#f7f3e5)</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Save Changes</button>
                <a href="/segments" class="btn btn-cancel">Cancel</a>
            </form>
        </div>
    </div>
</body>
</html>'''

@app.route('/segments/new', methods=['GET', 'POST'])
def segment_new():
    if request.method == 'POST':
        segments = load_segments()
        
        segment_name = request.form.get('name', '')
        segment_id = segment_name.lower().replace(' ', '-')
        
        if any(s['id'] == segment_id for s in segments):
            return '<script>alert("Segment ID already exists."); window.history.back();</script>'
        
        new_segment = {
            'id': segment_id,
            'name': segment_name,
            'description': request.form.get('description', ''),
            'color': request.form.get('color', '#004237'),
            'icon': '$'
        }
        
        segments.append(new_segment)
        save_segments(segments)
        return '<script>alert("Segment created successfully!"); window.location.href="/segments";</script>'
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>New Segment - The Keyes Company</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }
        .form-container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .form-group {
            margin-bottom: 24px;
        }
        label {
            display: block;
            color: #004237;
            font-weight: 600;
            margin-bottom: 8px;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
        }
        textarea { min-height: 100px; }
        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            margin-right: 12px;
        }
        .btn-primary {
            background: #004237;
            color: white;
        }
        .btn-cancel {
            background: #e0e0e0;
            color: #666;
            text-decoration: none;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Create New Segment</h1>
        </div>
        <div class="form-container">
            <form method="POST">
                <div class="form-group">
                    <label>Segment Name</label>
                    <input type="text" name="name" required placeholder="e.g., High Net Worth Clients">
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" required placeholder="Describe this client segment..."></textarea>
                </div>
                <div class="form-group">
                    <label>Color (Keyes brand colors only)</label>
                    <select name="color">
                        <option value="#004237">Keyes Green (#004237)</option>
                        <option value="#fcbfa7">Keyes Coral (#fcbfa7)</option>
                        <option value="#f7f3e5">Keyes Cream (#f7f3e5)</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Create Segment</button>
                <a href="/segments" class="btn btn-cancel">Cancel</a>
            </form>
        </div>
    </div>
</body>
</html>'''

@app.route('/api/generate-campaign', methods=['POST'])
def api_generate_campaign():
    """API endpoint to generate campaign content using AI"""
    data = request.json
    segment_id = data.get('segment_id')
    campaign_name = data.get('campaign_name', '')
    custom_prompt = data.get('custom_prompt', '')
    
    if not segment_id:
        return jsonify({"error": "segment_id is required"}), 400
    
    # Generate content using AI
    content = generate_campaign_content(segment_id, campaign_name, custom_prompt)
    
    if "error" in content:
        return jsonify(content), 500
    
    return jsonify(content)

@app.route('/api/segment-profile/<segment_id>')
def api_segment_profile(segment_id):
    """Get detailed profile for a segment"""
    profile = get_segment_profile(segment_id)
    if profile:
        return jsonify(profile)
    return jsonify({"error": "Segment not found"}), 404



@app.route('/audiences/<audience_id>/edit')
def edit_audience(audience_id):
    """Edit an existing audience (static or behavioral)"""
    # Check if it's a behavioral audience
    behavioral_audiences = load_behavioral_audiences()
    audience = next((a for a in behavioral_audiences if a['id'] == audience_id), None)
    is_behavioral = audience is not None
    
    # If not behavioral, check static segments
    if not audience:
        from ai_generator import get_segment_profile
        profile = get_segment_profile(audience_id)
        if profile:
            # Convert static segment to audience format
            segments = load_segments()
            seg = next((s for s in segments if s['id'] == audience_id), None)
            if seg:
                audience = {
                    'id': audience_id,
                    'audience_name': profile['name'],
                    'segment_summary': seg.get('description', ''),
                    'demographics': profile.get('demographics', ''),
                    'psychographics': profile.get('psychographics', ''),
                    'behavior': profile.get('pain_points', ''),
                    'communication_style': profile.get('communication_style', '')
                }
    
    if not audience:
        return "Audience not found", 404
    
    # Load the edit template with pre-filled data
    with open('templates/audience_edit.html', 'r') as f:
        template = f.read()
    
    # Replace placeholders with audience data
    template = template.replace('{{AUDIENCE_ID}}', audience.get('id', audience_id))
    template = template.replace('{{AUDIENCE_NAME}}', audience.get('audience_name', ''))
    template = template.replace('{{DEMOGRAPHICS}}', str(audience.get('demographics', '')))
    template = template.replace('{{PSYCHOGRAPHICS}}', str(audience.get('psychographics', '')))
    template = template.replace('{{BEHAVIOR}}', str(audience.get('behavior', '')))
    template = template.replace('{{COMMUNICATION_STYLE}}', str(audience.get('communication_style', '')))
    template = template.replace('{{SEGMENT_SUMMARY}}', audience.get('segment_summary', ''))
    template = template.replace('{{IS_STATIC}}', 'true' if not is_behavioral else 'false')
    
    return template

@app.route('/audiences/<audience_id>/delete')
def delete_audience(audience_id):
    """Delete a behavioral audience"""
    audiences = load_behavioral_audiences()
    audiences = [a for a in audiences if a['id'] != audience_id]
    
    # Save updated list
    with open('behavioral_audiences.json', 'w') as f:
        json.dump(audiences, f, indent=2)
    
    return redirect('/audiences')

@app.route('/api/update-audience', methods=['POST'])
def api_update_audience():
    """API endpoint to update an audience"""
    try:
        data = request.json
        audience_id = data.get('audience_id')
        
        audiences = load_behavioral_audiences()
        
        # Find and update the audience
        for i, aud in enumerate(audiences):
            if aud['id'] == audience_id:
                # Update fields
                aud['audience_name'] = data.get('audience_name', aud['audience_name'])
                aud['segment_summary'] = data.get('segment_summary', aud.get('segment_summary', ''))
                
                # Update demographics if provided
                if 'demographics' in data:
                    aud['demographics'] = data['demographics']
                
                # Update psychographics if provided
                if 'psychographics' in data:
                    aud['psychographics'] = data['psychographics']
                
                # Update behavior if provided
                if 'behavior' in data:
                    aud['behavior'] = data['behavior']
                
                # Update communication style if provided
                if 'communication_style' in data:
                    aud['communication_style'] = data['communication_style']
                
                audiences[i] = aud
                break
        
        # Save updated list
        with open('behavioral_audiences.json', 'w') as f:
            json.dump(audiences, f, indent=2)
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/audiences/new')
def audience_builder():
    """Multi-method Audience Builder page"""
    with open('templates/audience_builder_complete.html', 'r') as f:
        return f.read()

@app.route('/audiences')
def audiences_list():
    """List all audiences (static + behavioral)"""
    segments = load_segments()
    behavioral_audiences = load_behavioral_audiences()
    
    # Build static segments cards
    static_cards = ""
    for seg in segments:
        static_cards += f"""
        <div class="campaign-card">
            <div class="campaign-header">
                <h3>{seg['name']}</h3>
                <span class="badge" style="background: {seg['color']}; color: white;">Static Segment</span>
            </div>
            <p style="color: #666; margin: 12px 0;">{seg['description']}</p>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px;">
                <a href="/campaign/new?segment={seg['id']}" style="padding: 10px 20px; background: #004237; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Generate Campaign</a>
                <a href="/audiences/{seg['id']}/edit" style="padding: 10px 20px; background: #fcbfa7; color: #004237; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Edit</a>
                <button onclick="if(confirm('Delete this audience?')) {{ fetch('/api/delete-audience', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ audience_id: '{seg['id']}' }}) }}).then(() => location.reload()); }}" style="padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">Delete</button>
            </div>
        </div>
        """
    
    # Build behavioral audiences cards
    behavioral_cards = ""
    for aud in behavioral_audiences:
        behavioral_cards += f"""
        <div class="campaign-card">
            <div class="campaign-header">
                <h3>{aud['audience_name']}</h3>
                <span class="badge" style="background: #fcbfa7; color: #004237;">Behavioral Audience</span>
            </div>
            <p style="color: #666; margin: 12px 0;">{aud.get('segment_summary', 'Custom behavioral audience')}</p>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px;">
                <a href="/campaign/new?segment={aud['id']}" style="padding: 10px 20px; background: #004237; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Generate Campaign</a>
                <a href="/audiences/{aud['id']}/edit" style="padding: 10px 20px; background: #fcbfa7; color: #004237; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Edit</a>
                <a href="/audiences/{aud['id']}/delete" onclick="return confirm('Are you sure you want to delete this audience?')" style="padding: 10px 20px; background: #dc3545; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Delete</a>
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Audiences - The Keyes Company</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{ font-size: 32px; }}
        .header p {{ margin-top: 8px; opacity: 0.9; }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .tab {{
            padding: 12px 24px;
            background: transparent;
            color: #666;
            text-decoration: none;
            border-bottom: 3px solid transparent;
            font-weight: 600;
            transition: all 0.3s;
            cursor: pointer;
        }}
        .tab:hover {{ color: #004237; }}
        .tab.active {{
            color: #004237;
            border-bottom-color: #fcbfa7;
        }}
        .btn-create {{
            background: #fcbfa7;
            color: #004237;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 15px;
            transition: all 0.3s;
        }}
        .btn-create:hover {{ background: #fda67a; }}
        .section-title {{
            font-size: 20px;
            color: #004237;
            margin: 30px 0 15px 0;
            font-weight: 600;
        }}
        .campaign-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s;
        }}
        .campaign-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.12); transform: translateY(-2px); }}
        .campaign-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .campaign-header h3 {{ color: #004237; font-size: 20px; }}
        .badge {{
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="display: flex; align-items: center; gap: 20px;">
                <a href="/" style="color: white; text-decoration: none; font-size: 24px; opacity: 0.8; transition: opacity 0.3s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">←</a>
                <div>
                    <h1>Audiences</h1>
                    <p>Manage your static segments and behavioral audiences</p>
                </div>
            </div>
            <a href="/audiences/new" class="btn-create">+ Create New Audience</a>
        </div>
        
        <div class="tabs">
            <a href="/audiences" class="tab active">All Audiences</a>
            <a href="/audiences/past-clients" class="tab">Past Client</a>
        </div>
        
        <h2 class="section-title">Static Segments</h2>
        {static_cards}
        
        <h2 class="section-title">Behavioral Audiences</h2>
        {behavioral_cards if behavioral_cards else '<p style="text-align: center; color: #999; padding: 40px; background: white; border-radius: 12px;">No behavioral audiences yet. <a href="/audiences/new" style="color: #004237; font-weight: 600;">Create your first one!</a></p>'}
    </div>
</body>
</html>
"""


@app.route('/audiences/past-clients')
def past_clients():
    """Past Client page with 10 unified segments"""
    from storage import list_files_in_spaces
    
    # Load past client segments
    with open('past_clients.json', 'r') as f:
        segments = json.load(f)
    
    # Get uploaded files from Spaces
    files = list_files_in_spaces()
    
    # Build files table
    files_html = ""
    for file in files:
        size_mb = file['size'] / (1024 * 1024)
        date = file['last_modified'].strftime('%Y-%m-%d %H:%M')
        files_html += f'''
        <tr>
            <td><input type="checkbox" name="selected_files" value="{file['key']}" class="file-checkbox"></td>
            <td>{file['filename']}</td>
            <td>{size_mb:.2f} MB</td>
            <td>{date}</td>
        </tr>
        '''
    
    if not files_html:
        files_html = '<tr><td colspan="4" style="text-align: center; color: #999; padding: 20px;">No files uploaded yet. Upload a CSV file above to get started.</td></tr>'
    
    # Build segment cards
    segment_cards = ""
    for seg in segments:
        # Handle subtiers for Equity Comfort Tiers
        subtiers_html = ""
        if 'subtiers' in seg:
            subtiers_html = '<div style="margin-top: 16px; padding: 16px; background: #f9f9f9; border-radius: 8px;">'
            subtiers_html += '<p style="font-size: 13px; font-weight: 600; color: #004237; margin-bottom: 12px;">Sub-Tiers:</p>'
            for subtier in seg['subtiers']:
                subtiers_html += f'<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;"><div style="width: 12px; height: 12px; border-radius: 50%; background: {subtier["color"]}"></div><span style="font-size: 13px; color: #666;"><strong>{subtier["name"]}:</strong> {subtier["formula"]}</span></div>'
            subtiers_html += '</div>'
        
        segment_cards += f"""
        <div class="campaign-card">
            <div class="campaign-header">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 20px; height: 20px; border-radius: 4px; background: {seg['color']}"></div>
                    <h3>{seg['name']}</h3>
                </div>
                <span class="badge" style="background: {seg['color']}; color: white;">Count: {seg['count']}</span>
            </div>
            <p style="color: #666; margin: 12px 0; line-height: 1.6;">{seg['description']}</p>
            <div style="background: #f7f3e5; padding: 12px; border-radius: 6px; margin: 12px 0;">
                <p style="font-size: 13px; color: #666; font-family: 'Courier New', monospace;"><strong>Formula:</strong> {seg['formula']}</p>
            </div>
            {subtiers_html}
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px;">
                <a href="/campaign/new?segment={seg['id']}" style="padding: 10px 20px; background: #004237; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Generate Campaign</a>
                <a href="/audiences/past-clients/{seg['id']}/analytics" style="padding: 10px 20px; background: #fcbfa7; color: #004237; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">View Analytics</a>
                <a href="/audiences/past-clients/{seg['id']}/edit" style="padding: 10px 20px; background: #006652; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">Edit Segment</a>
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Past Client Segments - The Keyes Company</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{ font-size: 32px; }}
        .header p {{ margin-top: 8px; opacity: 0.9; }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .tab {{
            padding: 12px 24px;
            background: transparent;
            color: #666;
            text-decoration: none;
            border-bottom: 3px solid transparent;
            font-weight: 600;
            transition: all 0.3s;
            cursor: pointer;
        }}
        .tab:hover {{ color: #004237; }}
        .tab.active {{
            color: #004237;
            border-bottom-color: #fcbfa7;
        }}
        .campaign-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s;
        }}
        .campaign-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.12); transform: translateY(-2px); }}
        .campaign-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .campaign-header h3 {{ color: #004237; font-size: 20px; }}
        .badge {{
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}
        .info-box {{
            background: #fefbf9;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            color: #004237;
            border: 2px solid #f0e6d8;
        }}
        .info-box h3 {{ margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="display: flex; align-items: center; gap: 20px;">
                <a href="/" style="color: white; text-decoration: none; font-size: 24px; opacity: 0.8; transition: opacity 0.3s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">←</a>
                <div>
                    <h1>Past Client Segments</h1>
                    <p>10 unified segments for targeting past clients with precision</p>
                </div>
            </div>
        </div>
        
        <div class="tabs">
            <a href="/audiences" class="tab">All Audiences</a>
            <a href="/audiences/past-clients" class="tab active">Past Client</a>
        </div>
        
        <div class="info-box">
            <h3>File Management</h3>
            <p style="margin-bottom: 16px;">Upload client data files to use for segment calculations. Manage file selection when editing or creating segments.</p>
            
            <form action="/admin/upload-files" method="post" enctype="multipart/form-data" style="margin-bottom: 20px;" onsubmit="document.getElementById('uploadBtn').disabled=true; document.getElementById('uploadBtn').innerText='Uploading...'; return true;">
                <input type="file" name="files" accept=".csv,.xlsx,.xls" multiple required style="padding: 8px; border: 2px solid #004237; border-radius: 6px; background: white;">
                <button type="submit" id="uploadBtn" style="padding: 10px 24px; background: #004237; color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; margin-left: 10px;">Upload Files</button>
            </form>
            
            <div style="margin-top: 16px;">
                <a href="/audiences/past-clients/new" style="padding: 10px 24px; background: #fcbfa7; color: #004237; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block;">Create New Segment</a>
            </div>
        </div>
        
        {segment_cards}
    </div>
</body>
</html>
"""



@app.route('/admin/fix-segment-ids')
def fix_segment_ids():
    """One-time migration to fix segment IDs in past_clients.json"""
    import json
    import uuid
    
    try:
        with open('past_clients.json', 'r') as f:
            segments = json.load(f)
        
        fixed_count = 0
        for seg in segments:
            # If ID looks like a name (has spaces or is too long), generate a new one
            if ' ' in seg.get('id', '') or len(seg.get('id', '')) > 20:
                old_id = seg['id']
                seg['id'] = str(uuid.uuid4())[:8]
                fixed_count += 1
                print(f"Fixed: {old_id} -> {seg['id']}")
        
        # Save back
        with open('past_clients.json', 'w') as f:
            json.dump(segments, f, indent=2)
        
        return f'<script>alert("Fixed {fixed_count} segment IDs!"); window.location.href="/audiences/past-clients";</script>'
    
    except Exception as e:
        return f'<script>alert("Error: {str(e)}"); window.history.back();</script>'

@app.route('/audiences/past-clients/new', methods=['GET', 'POST'])
def create_past_client_segment():
    """Create a new past client segment"""
    import json
    from formula_evaluator import validate_formula, get_available_fields
    from storage import list_files_in_spaces
    import uuid
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        formula = request.form.get('formula', '').strip()
        color = request.form.get('color', '#004237').strip()
        selected_files = request.form.getlist('selected_files')
        
        # Validate
        if not name or not description or not formula:
            return '<script>alert("All fields are required"); window.history.back();</script>'
        
        # Validate formula
        validation = validate_formula(formula)
        if not validation['valid']:
            return f'<script>alert("Invalid formula: {validation["message"]}"); window.history.back();</script>'
        
        # Load existing segments
        with open('past_clients.json', 'r') as f:
            segments = json.load(f)
        
        # Create new segment
        new_segment = {
            'id': str(uuid.uuid4())[:8],
            'name': name,
            'description': description,
            'formula': formula,
            'color': color,
            'count': 0,
            'selected_files': selected_files
        }
        
        # Calculate count if files selected
        if selected_files:
            import pandas as pd
            from storage import download_file_from_spaces
            from formula_evaluator import evaluate_formula
            import os
            
            try:
                # Download and merge selected files
                dfs = []
                for file_key in selected_files:
                    local_path = f'/tmp/{file_key.split("/")[-1]}'
                    result = download_file_from_spaces(file_key, local_path)
                    if result['success']:
                        if local_path.endswith('.csv'):
                            df = pd.read_csv(local_path)
                        else:
                            df = pd.read_excel(local_path)
                        dfs.append(df)
                        os.remove(local_path)
                
                merged_df = pd.concat(dfs, ignore_index=True)
                
                # Prepare data
                if 'AGE' in merged_df.columns:
                    merged_df['AGE'] = pd.to_numeric(merged_df['AGE'], errors='coerce')
                if 'CURRENT_SALE_MTG_1_LOAN_AMOUNT' in merged_df.columns:
                    merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'] = pd.to_numeric(merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'], errors='coerce').fillna(0)
                if 'CURRENT_AVM_VALUE' in merged_df.columns:
                    merged_df['CURRENT_AVM_VALUE'] = pd.to_numeric(merged_df['CURRENT_AVM_VALUE'], errors='coerce')
                if 'CURRENT_SALE_MTG_1_INT_RATE' in merged_df.columns:
                    merged_df['CURRENT_SALE_MTG_1_INT_RATE'] = pd.to_numeric(merged_df['CURRENT_SALE_MTG_1_INT_RATE'], errors='coerce')
                if 'LENGTH_OF_RESIDENCE' in merged_df.columns:
                    merged_df['LENGTH_OF_RESIDENCE'] = pd.to_numeric(merged_df['LENGTH_OF_RESIDENCE'], errors='coerce')
                if 'SUM_BUILDING_SQFT' in merged_df.columns:
                    merged_df['SUM_BUILDING_SQFT'] = pd.to_numeric(merged_df['SUM_BUILDING_SQFT'], errors='coerce')
                
                merged_df['EQUITY'] = merged_df['CURRENT_AVM_VALUE'] - merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT']
                merged_df['MEDIAN_HOME_PRICE'] = 500000
                merged_df['MEDIAN_SQFT'] = 2000
                if 'CURRENT_SALE_RECORDING_DATE' in merged_df.columns:
                    merged_df['SALE_YEAR'] = pd.to_datetime(merged_df['CURRENT_SALE_RECORDING_DATE'], errors='coerce').dt.year
                merged_df['EQUITY_COMFORT_SCORE'] = merged_df['EQUITY'] / merged_df['MEDIAN_HOME_PRICE']
                
                # Calculate count
                count = evaluate_formula(merged_df, formula)
                new_segment['count'] = count
                
            except Exception as e:
                return f'<script>alert("Error calculating count: {str(e)}"); window.history.back();</script>'
        
        # Add to segments
        segments.append(new_segment)
        
        # Save
        with open('past_clients.json', 'w') as f:
            json.dump(segments, f, indent=2)
        
        return f'<script>alert("Segment created successfully! Count: {new_segment["count"]}"); window.location.href="/audiences/past-clients";</script>'
    
    # GET request - show creation form
    files = list_files_in_spaces()
    fields = get_available_fields()
    
    # Build fields HTML
    fields_html = ""
    for field in fields:
        fields_html += f'<div style="margin-bottom: 8px;"><strong>{field["name"]}</strong> ({field["type"]}): {field["description"]}</div>'
    
    # Build files list
    files_html = ""
    for file in files:
        size_mb = file['size'] / (1024 * 1024)
        date = file['last_modified'].strftime('%Y-%m-%d %H:%M')
        files_html += f'''
        <tr>
            <td><input type="checkbox" name="selected_files" value="{file['key']}"></td>
            <td>{file['filename']}</td>
            <td>{size_mb:.2f} MB</td>
            <td>{date}</td>
        </tr>
        '''
    
    if not files_html:
        files_html = '<tr><td colspan="4" style="text-align: center; padding: 20px; color: #999;">No files uploaded. Go to Past Clients page to upload files.</td></tr>'
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Create New Segment</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .form-group {{
            margin-bottom: 24px;
        }}
        label {{
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #004237;
        }}
        input[type="text"], textarea, input[type="color"] {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }}
        input[type="text"]:focus, textarea:focus {{
            outline: none;
            border-color: #004237;
        }}
        textarea {{
            font-family: 'Courier New', monospace;
            min-height: 100px;
            resize: vertical;
        }}
        .help-box {{
            background: #f0f8ff;
            border-left: 4px solid #004237;
            padding: 16px;
            border-radius: 8px;
            margin-top: 12px;
        }}
        .help-box h4 {{
            color: #004237;
            margin-bottom: 12px;
        }}
        .field-list {{
            font-size: 13px;
            color: #666;
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/audiences/past-clients" style="color: white; text-decoration: none; font-size: 24px; opacity: 0.8; transition: opacity 0.3s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">←</a>
            <h1>Create New Segment</h1>
            <p>Define a new audience segment with custom formula and data files</p>
        </div>
        
        <form method="POST">
            <div class="card">
                <div class="form-group">
                    <label for="name">Segment Name</label>
                    <input type="text" id="name" name="name" required placeholder="e.g., High Equity Seniors">
                </div>
                
                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" name="description" rows="2" required placeholder="Brief description of this segment"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="formula">Formula</label>
                    <textarea id="formula" name="formula" rows="4" required placeholder="e.g., Age >= 60 and Equity >= 200000"></textarea>
                    <div class="help-box">
                        <h4>Formula Syntax</h4>
                        <p style="margin-bottom: 12px;">Use logical operators: <code>and</code>, <code>or</code>, <code>>=</code>, <code><=</code>, <code>!=</code></p>
                        <p style="margin-bottom: 12px;"><strong>Example:</strong> <code>Age >= 60 and Equity >= 200000</code></p>
                        <p style="margin-bottom: 12px;"><strong>BETWEEN syntax:</strong> <code>Age BETWEEN 30 AND 45</code></p>
                        <div class="field-list">
                            <h4 style="margin-top: 16px; margin-bottom: 8px;">Available Fields:</h4>
                            {fields_html}
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="color">Segment Color</label>
                    <input type="color" id="color" name="color" value="#004237">
                </div>
            </div>
            
            <div class="card">
                <h2 style="color: #004237; margin-bottom: 20px;">Data Files</h2>
                <p style="margin-bottom: 16px; color: #666;">Select which files to use for calculating this segment's count.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
                    <thead>
                        <tr style="background: #f0e6d8;">
                            <th style="padding: 10px; text-align: left; width: 50px;">Use</th>
                            <th style="padding: 10px; text-align: left;">Filename</th>
                            <th style="padding: 10px; text-align: left; width: 120px;">Size</th>
                            <th style="padding: 10px; text-align: left; width: 180px;">Uploaded</th>
                        </tr>
                    </thead>
                    <tbody>
                        {files_html}
                    </tbody>
                </table>
                
                <div style="display: flex; gap: 10px;">
                    <button type="submit" style="padding: 12px 24px; background: #fcbfa7; color: #004237; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px;">Create Segment</button>
                    <a href="/audiences/past-clients" style="padding: 12px 24px; background: #e0e0e0; color: #333; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">Cancel</a>
                </div>
            </div>
        </form>
    </div>
</body>
</html>
"""

@app.route('/audiences/past-clients/<segment_id>/edit', methods=['GET', 'POST'])
def edit_past_client_segment(segment_id):
    """Edit a past client segment formula"""
    import json
    from formula_evaluator import validate_formula, get_available_fields
    from storage import list_files_in_spaces
    
    # Load segments
    with open('past_clients.json', 'r') as f:
        segments = json.load(f)
    
    segment = next((s for s in segments if s['id'] == segment_id), None)
    if not segment:
        return "Segment not found", 404
    
    # Get uploaded files
    files = list_files_in_spaces()
    
    # Get currently selected files for this segment (if stored)
    selected_file_keys = segment.get('selected_files', [])
    
    if request.method == 'POST':
        # Always save AND recalculate with one button
        # First save the formula changes
        new_formula = request.form.get('formula', '').strip()
        new_name = request.form.get('name', '').strip()
        new_description = request.form.get('description', '').strip()
        
        # Validate formula
        validation = validate_formula(new_formula)
        if not validation['valid']:
            return f'<script>alert("Invalid formula: {validation["message"]}"); window.history.back();</script>'
        
        # Update segment
        segment['formula'] = new_formula
        if new_name:
            segment['name'] = new_name
        if new_description:
            segment['description'] = new_description
        
        # Then recalculate with selected files
        selected_files = request.form.getlist('selected_files')
        if selected_files:
            # Store selected files in segment
            segment['selected_files'] = selected_files
            
            # Trigger recalculation
            import pandas as pd
            from storage import download_file_from_spaces
            from formula_evaluator import evaluate_formula
            import os
            
            try:
                # Download and merge selected files
                dfs = []
                for file_key in selected_files:
                    local_path = f'/tmp/{file_key.split("/")[-1]}'
                    result = download_file_from_spaces(file_key, local_path)
                    if result['success']:
                        if local_path.endswith('.csv'):
                            df = pd.read_csv(local_path)
                        else:
                            df = pd.read_excel(local_path)
                        dfs.append(df)
                        os.remove(local_path)
                
                merged_df = pd.concat(dfs, ignore_index=True)
                
                # Prepare data
                if 'AGE' in merged_df.columns:
                    merged_df['AGE'] = pd.to_numeric(merged_df['AGE'], errors='coerce')
                if 'CURRENT_SALE_MTG_1_LOAN_AMOUNT' in merged_df.columns:
                    merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'] = pd.to_numeric(merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'], errors='coerce').fillna(0)
                if 'CURRENT_AVM_VALUE' in merged_df.columns:
                    merged_df['CURRENT_AVM_VALUE'] = pd.to_numeric(merged_df['CURRENT_AVM_VALUE'], errors='coerce')
                if 'CURRENT_SALE_MTG_1_INT_RATE' in merged_df.columns:
                    merged_df['CURRENT_SALE_MTG_1_INT_RATE'] = pd.to_numeric(merged_df['CURRENT_SALE_MTG_1_INT_RATE'], errors='coerce')
                if 'LENGTH_OF_RESIDENCE' in merged_df.columns:
                    merged_df['LENGTH_OF_RESIDENCE'] = pd.to_numeric(merged_df['LENGTH_OF_RESIDENCE'], errors='coerce')
                if 'SUM_BUILDING_SQFT' in merged_df.columns:
                    merged_df['SUM_BUILDING_SQFT'] = pd.to_numeric(merged_df['SUM_BUILDING_SQFT'], errors='coerce')
                
                merged_df['EQUITY'] = merged_df['CURRENT_AVM_VALUE'] - merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT']
                merged_df['MEDIAN_HOME_PRICE'] = 500000
                merged_df['MEDIAN_SQFT'] = 2000
                if 'CURRENT_SALE_RECORDING_DATE' in merged_df.columns:
                    merged_df['SALE_YEAR'] = pd.to_datetime(merged_df['CURRENT_SALE_RECORDING_DATE'], errors='coerce').dt.year
                merged_df['EQUITY_COMFORT_SCORE'] = merged_df['EQUITY'] / merged_df['MEDIAN_HOME_PRICE']
                
                # Calculate count
                formula = segment.get('formula', '')
                if formula:
                    count = evaluate_formula(merged_df, formula)
                else:
                    count = 0
                segment['count'] = count
                
                # Save
                with open('past_clients.json', 'w') as f:
                    json.dump(segments, f, indent=2)
                
                return f'<script>alert("Segment saved and recalculated! Count: {count} from {len(merged_df)} records"); window.location.href="/audiences/past-clients";</script>'
            
            except Exception as e:
                return f'<script>alert("Error: {str(e)}"); window.history.back();</script>'
        else:
            # No files selected, just save
            with open('past_clients.json', 'w') as f:
                json.dump(segments, f, indent=2)
            
            return '<script>alert("Segment saved successfully!"); window.location.href="/audiences/past-clients";</script>'
    
    # GET request - show edit form
    fields = get_available_fields()
    fields_html = ""
    for field in fields:
        fields_html += f'<div style="margin-bottom: 8px;"><strong>{field["name"]}</strong> ({field["type"]}): {field["description"]}</div>'
    
    # Build files list with checkboxes
    files_html = ""
    for file in files:
        size_mb = file['size'] / (1024 * 1024)
        date = file['last_modified'].strftime('%Y-%m-%d %H:%M')
        checked = 'checked' if file['key'] in selected_file_keys else ''
        files_html += f'''
        <tr>
            <td><input type="checkbox" name="selected_files" value="{file['key']}" {checked}></td>
            <td>{file['filename']}</td>
            <td>{size_mb:.2f} MB</td>
            <td>{date}</td>
        </tr>
        '''
    
    if not files_html:
        files_html = '<tr><td colspan="4" style="text-align: center; padding: 20px; color: #999;">No files uploaded. Go to Past Clients page to upload files.</td></tr>'
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Edit Segment: {segment['name']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .form-group {{
            margin-bottom: 24px;
        }}
        label {{
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #004237;
        }}
        input[type="text"], textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }}
        input[type="text"]:focus, textarea:focus {{
            outline: none;
            border-color: #004237;
        }}
        textarea {{
            font-family: 'Courier New', monospace;
            min-height: 100px;
            resize: vertical;
        }}
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }}
        .btn-primary {{
            background: #004237;
            color: white;
        }}
        .btn-primary:hover {{
            background: #003329;
        }}
        .btn-secondary {{
            background: #fcbfa7;
            color: #004237;
            margin-left: 10px;
        }}
        .btn-secondary:hover {{
            background: #fda67a;
        }}
        .help-box {{
            background: #f0f8ff;
            border-left: 4px solid #004237;
            padding: 16px;
            border-radius: 8px;
            margin-top: 12px;
        }}
        .help-box h4 {{
            color: #004237;
            margin-bottom: 12px;
        }}
        .field-list {{
            font-size: 13px;
            color: #666;
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/audiences/past-clients" style="color: white; text-decoration: none; font-size: 24px; opacity: 0.8; transition: opacity 0.3s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">←</a>
            <h1>Edit Segment</h1>
            <p>Modify the formula and settings for this audience segment</p>
        </div>
        
        <form method="POST">
            <div class="card">
                <div class="form-group">
                    <label for="name">Segment Name</label>
                    <input type="text" id="name" name="name" value="{segment['name']}" required>
                </div>
                
                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" name="description" rows="2" required>{segment['description']}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="formula">Formula</label>
                    <textarea id="formula" name="formula" rows="4" required>{segment['formula']}</textarea>
                    <div class="help-box">
                        <h4>Formula Syntax</h4>
                        <p style="margin-bottom: 12px;">Use logical operators: <code>and</code>, <code>or</code>, <code>>=</code>, <code><=</code>, <code>!=</code></p>
                        <p style="margin-bottom: 12px;"><strong>Example:</strong> <code>Age >= 60 and Equity >= 200000</code></p>
                        <p style="margin-bottom: 12px;"><strong>BETWEEN syntax:</strong> <code>Age BETWEEN 30 AND 45</code></p>
                        <div class="field-list">
                            <h4 style="margin-top: 16px; margin-bottom: 8px;">Available Fields:</h4>
                            {fields_html}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- File Management Section -->
            <div class="card">
                <h2 style="color: #004237; margin-bottom: 20px;">Data Files</h2>
                <p style="margin-bottom: 16px; color: #666;">Select which files to use for this segment. The count will be recalculated when you save.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
                    <thead>
                        <tr style="background: #f0e6d8;">
                            <th style="padding: 10px; text-align: left; width: 50px;">Use</th>
                            <th style="padding: 10px; text-align: left;">Filename</th>
                            <th style="padding: 10px; text-align: left; width: 120px;">Size</th>
                            <th style="padding: 10px; text-align: left; width: 180px;">Uploaded</th>
                        </tr>
                    </thead>
                    <tbody>
                        {files_html}
                    </tbody>
                </table>
                
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button type="submit" style="padding: 12px 24px; background: #fcbfa7; color: #004237; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px;">Save & Recalculate</button>
                    <a href="/audiences/past-clients" style="padding: 12px 24px; background: #e0e0e0; color: #333; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">Cancel</a>
                    <span style="margin-left: auto; font-size: 13px; color: #666;">Current count: <strong>{segment.get('count', 0)}</strong></span>
                </div>
            </div>
        </form>
    </div>
</body>
</html>
"""


@app.route('/audiences/past-clients/<segment_id>/analytics')
def past_client_analytics(segment_id):
    """Analytics page for a specific past client segment"""
    import pandas as pd
    import json
    
    # Load segment info
    with open('past_clients.json', 'r') as f:
        segments = json.load(f)
    
    segment = next((s for s in segments if s['id'] == segment_id), None)
    if not segment:
        return "Segment not found", 404
    
    # Load client data
    try:
        df = pd.read_csv('uploaded_client_data.csv')
        
        # Clean data
        df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce')
        df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'] = pd.to_numeric(df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'], errors='coerce').fillna(0)
        df['CURRENT_AVM_VALUE'] = pd.to_numeric(df['CURRENT_AVM_VALUE'], errors='coerce')
        df['CURRENT_SALE_MTG_1_INT_RATE'] = pd.to_numeric(df['CURRENT_SALE_MTG_1_INT_RATE'], errors='coerce')
        df['LENGTH_OF_RESIDENCE'] = pd.to_numeric(df['LENGTH_OF_RESIDENCE'], errors='coerce')
        df['SUM_BUILDING_SQFT'] = pd.to_numeric(df['SUM_BUILDING_SQFT'], errors='coerce')
        df['EQUITY'] = df['CURRENT_AVM_VALUE'] - df['CURRENT_SALE_MTG_1_LOAN_AMOUNT']
        
        # Filter to segment
        if segment_id == '65-not-retired':
            segment_df = df[df['AGE'] >= 60]
        elif segment_id == 'growing-families':
            segment_df = df[(df['LENGTH_OF_RESIDENCE'] >= 6) & (df['AGE'] >= 30) & (df['AGE'] <= 45)]
        elif segment_id == 'trapped-movers':
            segment_df = df[(df['EQUITY'] >= 200000) & (df['CURRENT_SALE_MTG_1_INT_RATE'] >= 6.5)]
        elif segment_id == 'all-cash-seniors':
            segment_df = df[(df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'] == 0) & (df['AGE'] >= 65)]
        elif segment_id == 'large-home-owners':
            segment_df = df[df['SUM_BUILDING_SQFT'] >= 2500]
        elif segment_id == 'cash-renters':
            df['SALE_YEAR'] = pd.to_datetime(df['CURRENT_SALE_RECORDING_DATE'], errors='coerce').dt.year
            segment_df = df[(df['SALE_YEAR'] >= 2020) & (df['SALE_YEAR'] <= 2022)]
        elif segment_id == 'young-cash-owners':
            segment_df = df[(df['AGE'] < 45) & (df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'] == 0)]
        else:
            segment_df = df
        
        # Calculate analytics
        total_count = len(segment_df)
        avg_age = segment_df['AGE'].mean()
        avg_equity = segment_df['EQUITY'].mean()
        avg_home_value = segment_df['CURRENT_AVM_VALUE'].mean()
        avg_mortgage = segment_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'].mean()
        avg_rate = segment_df['CURRENT_SALE_MTG_1_INT_RATE'].mean()
        
        # Top ZIPs
        top_zips = segment_df['ZIP'].value_counts().head(5).to_dict()
        
        # Age distribution
        age_ranges = {
            '< 30': len(segment_df[segment_df['AGE'] < 30]),
            '30-45': len(segment_df[(segment_df['AGE'] >= 30) & (segment_df['AGE'] < 45)]),
            '45-60': len(segment_df[(segment_df['AGE'] >= 45) & (segment_df['AGE'] < 60)]),
            '60-75': len(segment_df[(segment_df['AGE'] >= 60) & (segment_df['AGE'] < 75)]),
            '75+': len(segment_df[segment_df['AGE'] >= 75])
        }
        
        # Equity distribution
        equity_ranges = {
            '< $100K': len(segment_df[segment_df['EQUITY'] < 100000]),
            '$100K-$200K': len(segment_df[(segment_df['EQUITY'] >= 100000) & (segment_df['EQUITY'] < 200000)]),
            '$200K-$300K': len(segment_df[(segment_df['EQUITY'] >= 200000) & (segment_df['EQUITY'] < 300000)]),
            '$300K-$500K': len(segment_df[(segment_df['EQUITY'] >= 300000) & (segment_df['EQUITY'] < 500000)]),
            '$500K+': len(segment_df[segment_df['EQUITY'] >= 500000])
        }
        
    except Exception as e:
        return f"Error loading data: {e}", 500
    
    # Build analytics HTML
    top_zips_html = ''.join([f'<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e0e0e0;"><span>{zip_code}</span><span style="font-weight: 600;">{count}</span></div>' for zip_code, count in top_zips.items()])
    
    age_chart_html = ''.join([f'<div style="margin-bottom: 12px;"><div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span style="font-size: 13px;">{range_name}</span><span style="font-size: 13px; font-weight: 600;">{count}</span></div><div style="width: 100%; height: 20px; background: #f0e6d8; border-radius: 4px; overflow: hidden;"><div style="width: {(count/total_count*100) if total_count > 0 else 0}%; height: 100%; background: #004237;"></div></div></div>' for range_name, count in age_ranges.items()])
    
    equity_chart_html = ''.join([f'<div style="margin-bottom: 12px;"><div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span style="font-size: 13px;">{range_name}</span><span style="font-size: 13px; font-weight: 600;">{count}</span></div><div style="width: 100%; height: 20px; background: #f0e6d8; border-radius: 4px; overflow: hidden;"><div style="width: {(count/total_count*100) if total_count > 0 else 0}%; height: 100%; background: {segment["color"]}"></div></div></div>' for range_name, count in equity_ranges.items()])
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{segment['name']} Analytics - The Keyes Company</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 8px; }}
        .header p {{ opacity: 0.9; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .stat-card h3 {{ font-size: 14px; color: #666; margin-bottom: 8px; text-transform: uppercase; }}
        .stat-card .value {{ font-size: 32px; font-weight: 700; color: #004237; }}
        .chart-card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }}
        .chart-card h2 {{ font-size: 20px; color: #004237; margin-bottom: 20px; }}
        .back-link {{
            display: inline-block;
            color: white;
            text-decoration: none;
            font-size: 24px;
            opacity: 0.8;
            transition: opacity 0.3s;
            margin-bottom: 16px;
        }}
        .back-link:hover {{ opacity: 1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/audiences/past-clients" class="back-link">←</a>
            <h1>{segment['name']}</h1>
            <p>{segment['description']}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Count</h3>
                <div class="value">{total_count:,}</div>
            </div>
            <div class="stat-card">
                <h3>Avg Age</h3>
                <div class="value">{avg_age:.0f}</div>
            </div>
            <div class="stat-card">
                <h3>Avg Equity</h3>
                <div class="value">${avg_equity:,.0f}</div>
            </div>
            <div class="stat-card">
                <h3>Avg Home Value</h3>
                <div class="value">${avg_home_value:,.0f}</div>
            </div>
            <div class="stat-card">
                <h3>Avg Mortgage</h3>
                <div class="value">${avg_mortgage:,.0f}</div>
            </div>
            <div class="stat-card">
                <h3>Avg Interest Rate</h3>
                <div class="value">{avg_rate:.2f}%</div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <div class="chart-card">
                <h2>Age Distribution</h2>
                {age_chart_html}
            </div>
            
            <div class="chart-card">
                <h2>Equity Distribution</h2>
                {equity_chart_html}
            </div>
        </div>
        
        <div class="chart-card">
            <h2>Top 5 ZIP Codes</h2>
            {top_zips_html}
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/campaign/new?segment={segment_id}" style="padding: 14px 32px; background: #004237; color: white; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; display: inline-block;">Generate Campaign for This Segment</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/api/upload-client-data', methods=['POST'])
def upload_client_data():
    """Process uploaded client data CSV/Excel and calculate segment counts"""
    try:
        import pandas as pd
        from datetime import datetime
        from storage import upload_file_to_spaces
        import io
        
        client_file = request.files.get('client_file')
        if not client_file:
            return '<script>alert("No file uploaded"); window.location.href="/audiences/past-clients";</script>'
        
        # Read file content once
        filename = client_file.filename
        file_content = client_file.read()
        
        # Upload to DigitalOcean Spaces for secure storage
        file_stream = io.BytesIO(file_content)
        upload_result = upload_file_to_spaces(file_stream, filename)
        
        if not upload_result['success']:
            return f'<script>alert("Upload failed: {upload_result["message"]}"); window.location.href="/audiences/past-clients";</script>'
        
        # Also save locally for processing (temporary)
        filepath = f'uploaded_client_data.{filename.split(".")[-1]}'
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        # Read file based on extension
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Load past client segments
        with open('past_clients.json', 'r') as f:
            segments = json.load(f)
        
        # Clean and prepare data
        # Convert numeric columns
        if 'AGE' in df.columns:
            df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce')
        if 'CURRENT_SALE_MTG_1_LOAN_AMOUNT' in df.columns:
            df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'] = pd.to_numeric(df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'], errors='coerce').fillna(0)
        if 'CURRENT_AVM_VALUE' in df.columns:
            df['CURRENT_AVM_VALUE'] = pd.to_numeric(df['CURRENT_AVM_VALUE'], errors='coerce')
        if 'CURRENT_SALE_MTG_1_INT_RATE' in df.columns:
            df['CURRENT_SALE_MTG_1_INT_RATE'] = pd.to_numeric(df['CURRENT_SALE_MTG_1_INT_RATE'], errors='coerce')
        if 'LENGTH_OF_RESIDENCE' in df.columns:
            df['LENGTH_OF_RESIDENCE'] = pd.to_numeric(df['LENGTH_OF_RESIDENCE'], errors='coerce')
        if 'SUM_BUILDING_SQFT' in df.columns:
            df['SUM_BUILDING_SQFT'] = pd.to_numeric(df['SUM_BUILDING_SQFT'], errors='coerce')
        
        # Calculate equity
        df['EQUITY'] = df['CURRENT_AVM_VALUE'] - df['CURRENT_SALE_MTG_1_LOAN_AMOUNT']
        
        # Load market data for median values
        try:
            market_df = pd.read_excel('market_data.xlsx')
            # Create ZIP to median mapping if available
            if 'ZIP' in df.columns and 'ZIP' in market_df.columns:
                zip_medians = market_df.set_index('ZIP')['MedianHomePrice'].to_dict() if 'MedianHomePrice' in market_df.columns else {}
                df['MEDIAN_HOME_PRICE'] = df['ZIP'].map(zip_medians)
        except:
            df['MEDIAN_HOME_PRICE'] = 500000  # Default fallback
        
        # Calculate counts for each segment using dynamic formula evaluation
        from formula_evaluator import evaluate_formula
        
        # Add calculated columns
        df['MEDIAN_SQFT'] = 2000  # Default median SQFT
        if 'CURRENT_SALE_RECORDING_DATE' in df.columns:
            df['SALE_YEAR'] = pd.to_datetime(df['CURRENT_SALE_RECORDING_DATE'], errors='coerce').dt.year
        df['EQUITY_COMFORT_SCORE'] = df['EQUITY'] / df['MEDIAN_HOME_PRICE']
        
        for seg in segments:
            try:
                formula = seg.get('formula', '')
                if formula:
                    count = evaluate_formula(df, formula)
                else:
                    count = 0
                seg['count'] = count
            except Exception as e:
                print(f"Error calculating {seg['id']}: {e}")
                import traceback
                traceback.print_exc()
                seg['count'] = 0
        
        # Save updated counts
        with open('past_clients.json', 'w') as f:
            json.dump(segments, f, indent=2)
        
        return '<script>alert("Client data processed successfully!"); window.location.href="/audiences/past-clients";</script>'
    
    except Exception as e:
        return f'<script>alert("Error processing file: {str(e)}"); window.location.href="/audiences/past-clients";</script>'

@app.route('/api/recalculate-segment', methods=['POST'])
def recalculate_segment():
    """Recalculate a single segment using selected files"""
    try:
        import pandas as pd
        from storage import download_file_from_spaces
        from formula_evaluator import evaluate_formula
        import json
        import os
        
        segment_id = request.form.get('segment_id')
        selected_files = request.form.getlist('selected_files')
        
        if not segment_id or not selected_files:
            return '<script>alert("Missing segment ID or files"); window.location.href="/audiences/past-clients";</script>'
        
        # Download and merge all selected files
        dfs = []
        for file_key in selected_files:
            local_path = f'/tmp/{file_key.split("/")[-1]}'
            result = download_file_from_spaces(file_key, local_path)
            
            if result['success']:
                if local_path.endswith('.csv'):
                    df = pd.read_csv(local_path)
                else:
                    df = pd.read_excel(local_path)
                dfs.append(df)
                os.remove(local_path)  # Clean up
        
        # Merge all dataframes
        merged_df = pd.concat(dfs, ignore_index=True)
        
        # Prepare data (same as upload handler)
        if 'AGE' in merged_df.columns:
            merged_df['AGE'] = pd.to_numeric(merged_df['AGE'], errors='coerce')
        if 'CURRENT_SALE_MTG_1_LOAN_AMOUNT' in merged_df.columns:
            merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'] = pd.to_numeric(merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'], errors='coerce').fillna(0)
        if 'CURRENT_AVM_VALUE' in merged_df.columns:
            merged_df['CURRENT_AVM_VALUE'] = pd.to_numeric(merged_df['CURRENT_AVM_VALUE'], errors='coerce')
        if 'CURRENT_SALE_MTG_1_INT_RATE' in merged_df.columns:
            merged_df['CURRENT_SALE_MTG_1_INT_RATE'] = pd.to_numeric(merged_df['CURRENT_SALE_MTG_1_INT_RATE'], errors='coerce')
        if 'LENGTH_OF_RESIDENCE' in merged_df.columns:
            merged_df['LENGTH_OF_RESIDENCE'] = pd.to_numeric(merged_df['LENGTH_OF_RESIDENCE'], errors='coerce')
        if 'SUM_BUILDING_SQFT' in merged_df.columns:
            merged_df['SUM_BUILDING_SQFT'] = pd.to_numeric(merged_df['SUM_BUILDING_SQFT'], errors='coerce')
        
        merged_df['EQUITY'] = merged_df['CURRENT_AVM_VALUE'] - merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT']
        merged_df['MEDIAN_HOME_PRICE'] = 500000
        merged_df['MEDIAN_SQFT'] = 2000
        
        if 'CURRENT_SALE_RECORDING_DATE' in merged_df.columns:
            merged_df['SALE_YEAR'] = pd.to_datetime(merged_df['CURRENT_SALE_RECORDING_DATE'], errors='coerce').dt.year
        merged_df['EQUITY_COMFORT_SCORE'] = merged_df['EQUITY'] / merged_df['MEDIAN_HOME_PRICE']
        
        # Load segments
        with open('past_clients.json', 'r') as f:
            segments = json.load(f)
        
        # Find and update only the specified segment
        segment = next((s for s in segments if s['id'] == segment_id), None)
        if not segment:
            return '<script>alert("Segment not found"); window.location.href="/audiences/past-clients";</script>'
        
        # Calculate count for this segment only
        try:
            formula = segment.get('formula', '')
            if formula:
                count = evaluate_formula(merged_df, formula)
            else:
                count = 0
            segment['count'] = count
        except Exception as e:
            return f'<script>alert("Error calculating segment: {str(e)}"); window.location.href="/audiences/past-clients";</script>'
        
        # Save updated segments
        with open('past_clients.json', 'w') as f:
            json.dump(segments, f, indent=2)
        
        return f'<script>alert("Segment \\"{segment["name"]}\\" recalculated! New count: {count} from {len(merged_df)} total records"); window.location.href="/audiences/past-clients";</script>'
    
    except Exception as e:
        return f'<script>alert("Error: {str(e)}"); window.location.href="/audiences/past-clients";</script>'

@app.route('/api/manage-files')
def manage_files():
    """View and manage uploaded files in DigitalOcean Spaces"""
    from storage import list_files_in_spaces, delete_file_from_spaces
    
    # Handle delete request
    if request.args.get('delete'):
        key = request.args.get('delete')
        result = delete_file_from_spaces(key)
        return jsonify(result)
    
    # List all uploaded files
    files = list_files_in_spaces()
    
    return jsonify({
        'success': True,
        'files': files
    })

@app.route('/api/analyze-audience', methods=['POST'])
@app.route('/api/create-audience-upload', methods=['POST'])
def api_analyze_audience():
    """API endpoint to analyze audience from screenshots and/or CSV"""
    try:
        # Get uploaded files
        demo_file = request.files.get('demographic_image')
        pixel_file = request.files.get('pixel_image')
        csv_file = request.files.get('csv_file')
        audience_name = request.form.get('audience_name', '')
        notes = request.form.get('notes', '')
        
        print(f"DEBUG: demo_file={demo_file}, pixel_file={pixel_file}, csv_file={csv_file}")
        print(f"DEBUG: demo_file.filename={getattr(demo_file, 'filename', None)}")
        print(f"DEBUG: pixel_file.filename={getattr(pixel_file, 'filename', None)}")
        print(f"DEBUG: csv_file.filename={getattr(csv_file, 'filename', None)}")
        print(f"DEBUG: audience_name={audience_name}")
        print(f"DEBUG: request.files keys={list(request.files.keys())}")
        print(f"DEBUG: request.form keys={list(request.form.keys())}")
        
        # At least one file is required (check filename not empty string)
        has_demo = demo_file and demo_file.filename and demo_file.filename.strip() != ''
        has_pixel = pixel_file and pixel_file.filename and pixel_file.filename.strip() != ''
        has_csv = csv_file and csv_file.filename and csv_file.filename.strip() != ''
        
        print(f"DEBUG: has_demo={has_demo}, has_pixel={has_pixel}, has_csv={has_csv}")
        
        if not has_demo and not has_pixel and not has_csv:
            return jsonify({"error": "At least one file (image or CSV) is required"}), 400
        
        # Save uploaded files temporarily
        import os
        import time
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = int(time.time())
        demo_path = None
        pixel_path = None
        csv_path = None
        
        if demo_file:
            demo_path = os.path.join(upload_dir, f'demo_{timestamp}.png')
            demo_file.save(demo_path)
        
        if pixel_file:
            pixel_path = os.path.join(upload_dir, f'pixel_{timestamp}.png')
            pixel_file.save(pixel_path)
        
        if csv_file:
            csv_path = os.path.join(upload_dir, f'journey_{timestamp}.csv')
            csv_file.save(csv_path)
        
        # Analyze with AI
        audience_data = {}
        
        # Analyze images if provided
        if demo_path and pixel_path:
            audience_data = analyze_audience_screenshots(demo_path, pixel_path, audience_name)
        elif demo_path or pixel_path:
            # Handle single image case - just extract what we can
            audience_data = {"audience_name": audience_name, "demographics": {}, "behavior": {}}
        else:
            # No images provided - initialize with basic structure
            audience_data = {
                "audience_name": audience_name,
                "demographics": {},
                "behavior": {},
                "csv_only": True
            }
        
        # Analyze CSV if provided
        if csv_path:
            csv_insights = analyze_csv_data(csv_path)
            # Merge CSV insights into audience_data
            if 'behavior' not in audience_data:
                audience_data['behavior'] = {}
            audience_data['behavior'].update(csv_insights)
            audience_data['csv_analyzed'] = True
        
        # Add notes if provided
        if notes:
            audience_data['additional_notes'] = notes
        
        if "error" in audience_data:
            return jsonify(audience_data), 500
        
        # Create audience card
        audience_id = create_audience_card(audience_data, demo_path, pixel_path)
        
        # Add audience_id to response
        audience_data['audience_id'] = audience_id
        
        return jsonify({"success": True, "audience_id": audience_id})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



@app.route('/api/preview-audience-campaign')
def preview_audience_campaign():
    """Generate a preview of campaign copy for an audience without creating a campaign"""
    audience_id = request.args.get('audience_id')
    if not audience_id:
        return jsonify({'error': 'Missing audience_id'}), 400
    
    try:
        # Generate campaign content using AI
        from ai_generator import generate_campaign_content
        result = generate_campaign_content(audience_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Admin Panel Routes

# Simple authentication decorator
def require_admin_password(f):
    """Decorator to require admin password for protected routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not session.get('admin_authenticated'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'keyes2025')
        
        if password == admin_password:
            session['admin_authenticated'] = True
            return redirect('/admin')
        else:
            return '<script>alert("Invalid password"); window.location.href="/admin/login";</script>'
    
    return """<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        h1 { color: #004237; margin-bottom: 24px; text-align: center; }
        input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 16px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #004237;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        button:hover { background: #003329; }
    </style>
</head>
<body>
    <div class="login-box">
        <img src="https://raw.githubusercontent.com/StevenMProtech/Keyes/main/keyes-new-logo.png" alt="Keyes Logo" style="width: 200px; display: block; margin: 0 auto 24px auto;">
        <h1>Campaign Manager Login</h1>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter admin password" required autofocus>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/admin/logout')
def admin_logout():
    """Logout from admin panel"""
    session.pop('admin_authenticated', None)
    return redirect('/')

@app.route('/admin')
@require_admin_password
def admin_panel():
    """Admin panel for file and segment management"""
    from storage import list_files_in_spaces
    import json
    
    # Get uploaded files from Spaces
    files = list_files_in_spaces()
    
    # Get current segments
    with open('past_clients.json', 'r') as f:
        segments = json.load(f)
    
    # Build files table
    files_html = ""
    for file in files:
        size_mb = file['size'] / (1024 * 1024)
        date = file['last_modified'].strftime('%Y-%m-%d %H:%M')
        files_html += f"""
        <tr>
            <td><input type="checkbox" name="selected_files" value="{file['key']}" class="file-checkbox"></td>
            <td>{file['filename']}</td>
            <td>{size_mb:.2f} MB</td>
            <td>{date}</td>
            <td>
                <button onclick="deleteFile('{file['key']}')" style="padding: 6px 12px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">Delete</button>
            </td>
        </tr>
        """
    
    if not files_html:
        files_html = '<tr><td colspan="5" style="text-align: center; color: #999;">No files uploaded yet</td></tr>'
    
    # Build segments table
    segments_html = ""
    for seg in segments:
        segments_html += f"""
        <tr>
            <td><strong>{seg['name']}</strong></td>
            <td style="font-family: monospace; font-size: 12px;">{seg['formula']}</td>
            <td>{seg.get('count', 0)}</td>
            <td>
                <a href="/audiences/past-clients/{seg['id']}/edit" style="padding: 6px 12px; background: #006652; color: white; text-decoration: none; border-radius: 4px; font-size: 13px;">Edit</a>
                <button onclick="deleteSegment('{seg['id']}')" style="padding: 6px 12px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 8px;">Delete</button>
            </td>
        </tr>
        """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - Keyes Campaign Manager</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        h2 {{ color: #004237; margin-bottom: 20px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #f7f3e5;
            font-weight: 600;
            color: #004237;
        }}
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }}
        .btn-primary {{ background: #004237; color: white; }}
        .btn-primary:hover {{ background: #003329; }}
        .btn-secondary {{ background: #fcbfa7; color: #004237; margin-left: 10px; }}
        .btn-danger {{ background: #dc3545; color: white; margin-left: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Admin Panel</h1>
                <p>Manage files and audience segments</p>
            </div>
            <div>
                <a href="/" class="btn btn-secondary">Back to App</a>
                <a href="/admin/logout" class="btn btn-danger">Logout</a>
            </div>
        </div>
        
        <!-- File Management -->
        <div class="card">
            <h2>📁 File Management</h2>
            <div style="margin-bottom: 20px;">
                <form action="/admin/upload-files" method="POST" enctype="multipart/form-data" style="display: inline-block;">
                    <input type="file" name="files" multiple accept=".csv,.xlsx" style="margin-right: 10px;">
                    <button type="submit" class="btn btn-primary">Upload Files</button>
                </form>
            </div>
            
            <form id="analyzeForm" action="/admin/analyze-selected" method="POST">
                <table>
                    <thead>
                        <tr>
                            <th width="50">Select</th>
                            <th>Filename</th>
                            <th width="120">Size</th>
                            <th width="180">Upload Date</th>
                            <th width="100">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {files_html}
                    </tbody>
                </table>
                
                <div style="margin-top: 20px;">
                    <button type="submit" class="btn btn-primary">Analyze Selected Files</button>
                    <span style="margin-left: 16px; color: #666; font-size: 14px;">Select one or more files to merge and calculate segment counts</span>
                </div>
            </form>
        </div>
        
        <!-- Segment Management -->
        <div class="card">
            <h2>👥 Segment Management</h2>
            <div style="margin-bottom: 20px;">
                <a href="/admin/create-segment" class="btn btn-primary">+ Create New Segment</a>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Segment Name</th>
                        <th>Formula</th>
                        <th width="100">Count</th>
                        <th width="150">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {segments_html}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        function deleteFile(key) {{
            if (confirm('Are you sure you want to delete this file?')) {{
                fetch('/admin/delete-file?key=' + encodeURIComponent(key), {{method: 'POST'}})
                    .then(r => r.json())
                    .then(data => {{
                        if (data.success) {{
                            alert('File deleted successfully');
                            window.location.reload();
                        }} else {{
                            alert('Error: ' + data.message);
                        }}
                    }});
            }}
        }}
        
        function deleteSegment(segmentId) {{
            if (confirm('Are you sure you want to delete this segment?')) {{
                fetch('/admin/delete-segment?id=' + segmentId, {{method: 'POST'}})
                    .then(r => r.json())
                    .then(data => {{
                        if (data.success) {{
                            alert('Segment deleted successfully');
                            window.location.reload();
                        }} else {{
                            alert('Error: ' + data.message);
                        }}
                    }});
            }}
        }}
    </script>
</body>
</html>
"""

@app.route('/admin/upload-files', methods=['POST'])
@require_admin_password
def admin_upload_files():
    """Upload multiple files to DigitalOcean Spaces"""
    from storage import upload_file_to_spaces
    import io
    
    files = request.files.getlist('files')
    if not files:
        return '<script>alert("No files selected"); window.location.href="/admin";</script>'
    
    uploaded_count = 0
    for file in files:
        if file.filename:
            file_content = file.read()
            file_stream = io.BytesIO(file_content)
            result = upload_file_to_spaces(file_stream, file.filename)
            if result['success']:
                uploaded_count += 1
    
    return f'<script>alert("{uploaded_count} file(s) uploaded successfully"); window.location.href="/admin";</script>'

@app.route('/admin/delete-file', methods=['POST'])
@require_admin_password
def admin_delete_file():
    """Delete a file from DigitalOcean Spaces"""
    from storage import delete_file_from_spaces
    
    key = request.args.get('key')
    result = delete_file_from_spaces(key)
    return jsonify(result)

@app.route('/admin/delete-segment', methods=['POST'])
@require_admin_password
def admin_delete_segment():
    """Delete a past client segment"""
    import json
    
    segment_id = request.args.get('id')
    
    with open('past_clients.json', 'r') as f:
        segments = json.load(f)
    
    segments = [s for s in segments if s['id'] != segment_id]
    
    with open('past_clients.json', 'w') as f:
        json.dump(segments, f, indent=2)
    
    return jsonify({'success': True, 'message': 'Segment deleted'})

@app.route('/admin/create-segment', methods=['GET', 'POST'])
@require_admin_password
def admin_create_segment():
    """Create a new past client segment"""
    import json
    from formula_evaluator import validate_formula, get_available_fields
    
    if request.method == 'POST':
        segment_id = request.form.get('id', '').strip().lower().replace(' ', '-')
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        formula = request.form.get('formula', '').strip()
        color = request.form.get('color', '#004237').strip()
        
        # Validate
        if not all([segment_id, name, description, formula]):
            return '<script>alert("All fields are required"); window.history.back();</script>'
        
        validation = validate_formula(formula)
        if not validation['valid']:
            return f'<script>alert("Invalid formula: {validation["message"]}"); window.history.back();</script>'
        
        # Load existing segments
        with open('past_clients.json', 'r') as f:
            segments = json.load(f)
        
        # Check for duplicate ID
        if any(s['id'] == segment_id for s in segments):
            return '<script>alert("Segment ID already exists"); window.history.back();</script>'
        
        # Add new segment
        new_segment = {
            'id': segment_id,
            'name': name,
            'description': description,
            'formula': formula,
            'color': color,
            'count': 0
        }
        segments.append(new_segment)
        
        # Save
        with open('past_clients.json', 'w') as f:
            json.dump(segments, f, indent=2)
        
        return '<script>alert("Segment created successfully"); window.location.href="/admin";</script>'
    
    # GET - show form
    fields = get_available_fields()
    fields_html = ""
    for field in fields:
        fields_html += f'<div style="margin-bottom: 8px;"><strong>{field["name"]}</strong> ({field["type"]}): {field["description"]}</div>'
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Create New Segment</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f7f3e5;
            padding: 40px 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #004237 0%, #003329 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; font-weight: 600; margin-bottom: 8px; color: #004237; }}
        input[type="text"], textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
        }}
        textarea {{ font-family: 'Courier New', monospace; min-height: 100px; }}
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-primary {{ background: #004237; color: white; }}
        .btn-secondary {{ background: #fcbfa7; color: #004237; margin-left: 10px; }}
        .help-box {{
            background: #f0f8ff;
            border-left: 4px solid #004237;
            padding: 16px;
            border-radius: 8px;
            margin-top: 12px;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Create New Segment</h1>
            <p>Define a new audience segment with custom formula</p>
        </div>
        
        <div class="card">
            <form method="POST">
                <div class="form-group">
                    <label>Segment ID (lowercase, no spaces)</label>
                    <input type="text" name="id" placeholder="e.g., high-value-seniors" required>
                </div>
                
                <div class="form-group">
                    <label>Segment Name</label>
                    <input type="text" name="name" placeholder="e.g., High-Value Seniors" required>
                </div>
                
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" rows="2" placeholder="Brief description of this segment" required></textarea>
                </div>
                
                <div class="form-group">
                    <label>Formula</label>
                    <textarea name="formula" rows="4" placeholder="e.g., Age >= 65 and Equity >= 500000" required></textarea>
                    <div class="help-box">
                        <strong>Available Fields:</strong>
                        <div style="margin-top: 8px;">{fields_html}</div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Color (hex code)</label>
                    <input type="text" name="color" value="#004237" placeholder="#004237">
                </div>
                
                <div>
                    <button type="submit" class="btn btn-primary">Create Segment</button>
                    <a href="/admin" class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/admin/analyze-selected', methods=['POST'])
@require_admin_password
def admin_analyze_selected():
    """Analyze selected files and calculate segment counts"""
    from storage import download_file_from_spaces
    from formula_evaluator import evaluate_formula
    import pandas as pd
    import json
    import os
    
    selected_files = request.form.getlist('selected_files')
    if not selected_files:
        return '<script>alert("No files selected"); window.location.href="/admin";</script>'
    
    try:
        # Download and merge all selected files
        dfs = []
        for file_key in selected_files:
            local_path = f'/tmp/{file_key.split("/")[-1]}'
            result = download_file_from_spaces(file_key, local_path)
            
            if result['success']:
                if local_path.endswith('.csv'):
                    df = pd.read_csv(local_path)
                else:
                    df = pd.read_excel(local_path)
                dfs.append(df)
                os.remove(local_path)  # Clean up
        
        # Merge all dataframes
        merged_df = pd.concat(dfs, ignore_index=True)
        
        # Prepare data (same as upload handler)
        if 'AGE' in merged_df.columns:
            merged_df['AGE'] = pd.to_numeric(merged_df['AGE'], errors='coerce')
        if 'CURRENT_SALE_MTG_1_LOAN_AMOUNT' in merged_df.columns:
            merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'] = pd.to_numeric(merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT'], errors='coerce').fillna(0)
        if 'CURRENT_AVM_VALUE' in merged_df.columns:
            merged_df['CURRENT_AVM_VALUE'] = pd.to_numeric(merged_df['CURRENT_AVM_VALUE'], errors='coerce')
        if 'CURRENT_SALE_MTG_1_INT_RATE' in merged_df.columns:
            merged_df['CURRENT_SALE_MTG_1_INT_RATE'] = pd.to_numeric(merged_df['CURRENT_SALE_MTG_1_INT_RATE'], errors='coerce')
        if 'LENGTH_OF_RESIDENCE' in merged_df.columns:
            merged_df['LENGTH_OF_RESIDENCE'] = pd.to_numeric(merged_df['LENGTH_OF_RESIDENCE'], errors='coerce')
        if 'SUM_BUILDING_SQFT' in merged_df.columns:
            merged_df['SUM_BUILDING_SQFT'] = pd.to_numeric(merged_df['SUM_BUILDING_SQFT'], errors='coerce')
        
        merged_df['EQUITY'] = merged_df['CURRENT_AVM_VALUE'] - merged_df['CURRENT_SALE_MTG_1_LOAN_AMOUNT']
        merged_df['MEDIAN_HOME_PRICE'] = 500000
        merged_df['MEDIAN_SQFT'] = 2000
        
        if 'CURRENT_SALE_RECORDING_DATE' in merged_df.columns:
            merged_df['SALE_YEAR'] = pd.to_datetime(merged_df['CURRENT_SALE_RECORDING_DATE'], errors='coerce').dt.year
        merged_df['EQUITY_COMFORT_SCORE'] = merged_df['EQUITY'] / merged_df['MEDIAN_HOME_PRICE']
        
        # Calculate counts for all segments
        with open('past_clients.json', 'r') as f:
            segments = json.load(f)
        
        for seg in segments:
            try:
                formula = seg.get('formula', '')
                if formula:
                    count = evaluate_formula(merged_df, formula)
                else:
                    count = 0
                seg['count'] = count
            except Exception as e:
                print(f"Error calculating {seg['id']}: {e}")
                seg['count'] = 0
        
        # Save updated counts
        with open('past_clients.json', 'w') as f:
            json.dump(segments, f, indent=2)
        
        return f'<script>alert("Analysis complete! {len(merged_df)} total records processed from {len(selected_files)} file(s)"); window.location.href="/admin";</script>'
    
    except Exception as e:
        return f'<script>alert("Error: {str(e)}"); window.location.href="/admin";</script>'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5022))
    app.run(host='0.0.0.0', port=port, debug=False)
