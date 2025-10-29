from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'submissions.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            email TEXT,
            first_name TEXT,
            last_name TEXT,
            goals TEXT,
            goals_text TEXT,
            wants_equity_report BOOLEAN,
            wants_expert_contact BOOLEAN,
            phone_number TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    total = cursor.execute('SELECT COUNT(*) FROM submissions').fetchone()[0]
    pending = cursor.execute('SELECT COUNT(*) FROM submissions WHERE status = "pending"').fetchone()[0]
    conn.close()
    
    return f"""
    <html>
    <head><title>Howard Hanna - Dashboard</title></head>
    <body style="font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>Howard Hanna - Submissions Dashboard</h1>
        <p>Total Submissions: <strong>{total}</strong></p>
        <p>Pending Review: <strong>{pending}</strong></p>
        <p><a href="/submissions">View All Submissions</a> | <a href="/api/submissions">API Endpoint</a></p>
    </body>
    </html>
    """

@app.route('/api/submit', methods=['POST', 'OPTIONS'])
def submit_form():
    if request.method == 'OPTIONS':
        return '', 200
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get form data
    email = request.form.get('email', '')
    first_name = request.form.get('firstName', '')
    last_name = request.form.get('lastName', '')
    goals = ','.join(request.form.getlist('goals'))
    goals_text = request.form.get('goalsText', '')
    phone_number = request.form.get('phoneNumber', '')
    wants_report = request.form.get('wantsReport') == 'yes'
    wants_expert = request.form.get('wantsExpert') == 'yes'
    
    # Insert into database
    cursor.execute('''
        INSERT INTO submissions 
        (email, first_name, last_name, goals, goals_text, wants_equity_report, wants_expert_contact, phone_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (email, first_name, last_name, goals, goals_text, wants_report, wants_expert, phone_number))
    
    conn.commit()
    conn.close()
    
    # Return thank you page
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thank You - Howard Hanna</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 40px 20px;
                text-align: center;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 60px 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #1a3d3a;
                font-size: 32px;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                font-size: 18px;
                line-height: 1.6;
                margin-bottom: 15px;
            }
            .checkmark {
                font-size: 64px;
                color: #c9a961;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="checkmark">✓</div>
            <h1>Thank You!</h1>
            <p><strong>Your equity plan request has been received.</strong></p>
            <p>A Howard Hanna equity expert will review your goals and contact you shortly with your personalized strategy.</p>
            <p>We're excited to help you make the most of your home equity!</p>
        </div>
    </body>
    </html>
    """

@app.route('/submissions')
def view_submissions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM submissions ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    html = """
    <html>
    <head><title>Submissions</title></head>
    <body style="font-family: Arial; margin: 20px;">
        <h1>All Submissions</h1>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #1a3d3a; color: white;">
                <th>ID</th>
                <th>Timestamp</th>
                <th>Email</th>
                <th>Name</th>
                <th>Goals</th>
                <th>Goals Text</th>
                <th>Phone</th>
                <th>Wants Report</th>
                <th>Wants Expert</th>
            </tr>
    """
    
    for row in rows:
        html += f"""
            <tr>
                <td>{row['id']}</td>
                <td>{row['timestamp']}</td>
                <td>{row['email']}</td>
                <td>{row['first_name']} {row['last_name']}</td>
                <td>{row['goals']}</td>
                <td>{row['goals_text']}</td>
                <td>{row['phone_number']}</td>
                <td>{'Yes' if row['wants_equity_report'] else 'No'}</td>
                <td>{'Yes' if row['wants_expert_contact'] else 'No'}</td>
            </tr>
        """
    
    html += """
        </table>
        <p><a href="/">Back to Dashboard</a></p>
    </body>
    </html>
    """
    
    return html

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM submissions ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    
    submissions = []
    for row in rows:
        submissions.append({
            'id': row['id'],
            'timestamp': row['timestamp'],
            'email': row['email'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'goals': row['goals'],
            'goals_text': row['goals_text'],
            'wants_equity_report': bool(row['wants_equity_report']),
            'wants_expert_contact': bool(row['wants_expert_contact']),
            'phone_number': row['phone_number'],
            'status': row['status']
        })
    
    conn.close()
    return jsonify(submissions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

