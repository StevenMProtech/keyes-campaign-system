"""
HTML Email Generator for Keyes Campaign System
Generates downloadable HTML files for campaigns
"""

def generate_email_html_content(campaign):
    """Generate complete email HTML content"""
    config = campaign.get('form_config', {})
    
    # Format body copy with proper paragraph breaks
    body_copy = campaign.get('body_copy', 'Your body copy here')
    body_copy_html = format_body_copy(body_copy)
    
    callout_html = generate_callout_html(config)
    form_html = generate_form_html(config)
    
    email_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{campaign.get('name', 'Campaign')}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background-color: #f7f3e5;
        }}
    </style>
</head>
<body>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f7f3e5;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #f7f3e5 0%, #f0ead8 100%); padding: 60px 40px 70px; text-align: center;">
                            <!-- Logo -->
                            <div style="margin-bottom: 35px;">
                                <img src="https://raw.githubusercontent.com/StevenMProtech/Keyes/main/keyes-new-logo.png" alt="Keyes" style="width: 180px; height: auto; display: block; margin: 0 auto;" />
                                <p style="color: #004237; font-size: 10px; margin: 12px 0 0 0; letter-spacing: 3px; text-transform: uppercase; font-weight: 500;">Real Estate</p>
                            </div>
                            
                            <!-- Main Headline -->
                            <h2 style="color: #004237; font-size: 52px; line-height: 1.15; margin: 0 0 25px 0; font-weight: 400; letter-spacing: -0.5px; font-family: Georgia, 'Times New Roman', serif;">
                                {campaign.get('headline', 'Your Headline Here')}
                            </h2>
                            
                            <div style="width: 60px; height: 2px; background: #004237; margin: 0 auto 30px;"></div>
                            
                            <!-- Callout Box -->
                            {callout_html}
                            
                            <p style="color: #004237; font-size: 20px; line-height: 1.4; margin: 25px 0 0 0; font-weight: 700;">
                                {campaign.get('subheadline', 'Your subheadline here')}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <!-- Body Copy -->
                            {body_copy_html}
                            
                            <!-- Form -->
                            <div style="margin-top: 30px;">
                                {form_html}
                            </div>
                            
                            <!-- CTA Button -->
                            <div style="text-align: center; margin-top: 30px;">
                                <a href="#" style="display: inline-block; background-color: #004237; color: #ffffff; padding: 16px 40px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">{campaign.get('cta_text', 'Get Started')}</a>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f7f3e5; padding: 30px; text-align: center;">
                            <p style="color: #666666; font-size: 14px; margin: 0;">The Keyes Company | 49 Years of Excellence | $2.28B Sold Since 1976</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    return email_html


def generate_callout_html(config):
    """Generate callout box HTML"""
    if not config.get('show_callout'):
        return ''
    
    title = config.get('callout_title', '')
    main_text = config.get('callout_main_text', '')
    subtitle = config.get('callout_subtitle', '')
    
    return f'''
    <div style="background: #fefbf9; border: 2px solid #f9e8df; padding: 40px; border-radius: 16px; text-align: center; margin: 0 0 30px 0;">
        <p style="color: #004237; font-size: 20px; font-weight: 600; margin: 0 0 20px 0; letter-spacing: 0.5px;">{title}</p>
        <p style="color: #004237; font-size: 72px; font-weight: 700; margin: 0 0 20px 0; line-height: 0.9; letter-spacing: -2px;">{main_text}</p>
        <p style="color: #666666; font-size: 18px; margin: 0; line-height: 1.4;">{subtitle}</p>
    </div>
    '''


def generate_form_html(config):
    """Generate form HTML"""
    form_html = '<form method="POST" action="#">'
    
    # Question 1 (Radio buttons)
    if config.get('q1_text'):
        form_html += f'''
        <div style="margin-bottom: 30px;">
            <p style="color: #004237; font-size: 18px; font-weight: 600; margin: 0 0 15px 0;">{config.get('q1_text', '')}</p>
            <p style="color: #666666; font-size: 14px; margin: 0 0 20px 0;">{config.get('q1_subtitle', '')}</p>
        '''
        
        for i in range(1, 5):
            label = config.get(f'q1_opt{i}_label', '')
            desc = config.get(f'q1_opt{i}_desc', '')
            if label:
                form_html += f'''
                <div style="background: #f7f3e5; padding: 15px; border-radius: 8px; margin-bottom: 12px;">
                    <input type="radio" name="q1" value="opt{i}" id="q1_opt{i}" style="margin-right: 10px;">
                    <label for="q1_opt{i}" style="color: #004237; font-weight: 600;">{label}</label>
                    <p style="color: #666666; font-size: 13px; margin: 5px 0 0 25px;">{desc}</p>
                </div>
                '''
        
        form_html += '</div>'
    
    # Question 2 (Checkboxes)
    if config.get('q2_text'):
        form_html += f'''
        <div style="margin-bottom: 30px;">
            <p style="color: #004237; font-size: 18px; font-weight: 600; margin: 0 0 15px 0;">{config.get('q2_text', '')}</p>
            <p style="color: #666666; font-size: 14px; margin: 0 0 20px 0;">{config.get('q2_subtitle', '')}</p>
        '''
        
        for i in range(1, 5):
            label = config.get(f'q2_opt{i}', '')
            if label:
                form_html += f'''
                <div style="background: #f7f3e5; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                    <input type="checkbox" name="q2_opt{i}" id="q2_opt{i}" style="margin-right: 10px;">
                    <label for="q2_opt{i}" style="color: #004237; font-weight: 600;">{label}</label>
                </div>
                '''
        
        form_html += '</div>'
    
    # Question 3 (Radio buttons)
    if config.get('q3_text'):
        form_html += f'''
        <div style="margin-bottom: 30px;">
            <p style="color: #004237; font-size: 18px; font-weight: 600; margin: 0 0 15px 0;">{config.get('q3_text', '')}</p>
            <p style="color: #666666; font-size: 14px; margin: 0 0 20px 0;">{config.get('q3_subtitle', '')}</p>
        '''
        
        for i in range(1, 5):
            label = config.get(f'q3_opt{i}', '')
            if label:
                form_html += f'''
                <div style="background: #f7f3e5; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                    <input type="radio" name="q3" value="opt{i}" id="q3_opt{i}" style="margin-right: 10px;">
                    <label for="q3_opt{i}" style="color: #004237; font-weight: 600;">{label}</label>
                </div>
                '''
        
        form_html += '</div>'
    
    form_html += '</form>'
    return form_html



def format_body_copy(body_copy):
    """Format body copy with proper paragraph breaks"""
    if not body_copy:
        return ''
    
    # Split by double newlines (paragraph breaks)
    paragraphs = body_copy.split('\n\n')
    
    # Wrap each paragraph in <p> tags
    formatted_paragraphs = []
    for para in paragraphs:
        # Remove single newlines within paragraphs and strip whitespace
        para = para.replace('\n', ' ').strip()
        if para:
            formatted_paragraphs.append(f'<p style="color: #333333; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">{para}</p>')
    
    return '\n'.join(formatted_paragraphs)

