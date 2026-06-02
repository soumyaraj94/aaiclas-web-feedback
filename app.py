import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Import Google Sheets client (will only work if credentials exist)
try:
    from sheets_helper import SheetsClient
    sheets = SheetsClient()
    SHEETS_AVAILABLE = True
except Exception as e:
    print(f"Google Sheets not configured: {e}")
    SHEETS_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

def validate_email(email):
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_mobile(mobile):
    """Validate Indian mobile number (10 digits)"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, mobile) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_feedback():
    try:
        # Get form data
        agent_name = request.form.get('agent_name', '').strip()
        company_name = request.form.get('company_name', '').strip()
        mobile_number = request.form.get('mobile_number', '').strip()
        email = request.form.get('email', '').strip()
        service_rating = request.form.get('service_rating', '').strip()
        feedback = request.form.get('feedback', '').strip()
        remarks = request.form.get('remarks', '').strip()

        # Server-side validation
        errors = {}
        
        if not agent_name:
            errors['agent_name'] = 'Agent Name is required'
        elif len(agent_name) < 2:
            errors['agent_name'] = 'Agent Name must be at least 2 characters'
        
        if not company_name:
            errors['company_name'] = 'Company Name is required'
        elif len(company_name) < 2:
            errors['company_name'] = 'Company Name must be at least 2 characters'
        
        if not mobile_number:
            errors['mobile_number'] = 'Mobile Number is required'
        elif not validate_mobile(mobile_number):
            errors['mobile_number'] = 'Enter a valid 10-digit mobile number'
        
        if not email:
            errors['email'] = 'Email Address is required'
        elif not validate_email(email):
            errors['email'] = 'Enter a valid email address'
        
        if not service_rating:
            errors['service_rating'] = 'Service Rating is required'
        else:
            try:
                rating = int(service_rating)
                if rating < 1 or rating > 5:
                    errors['service_rating'] = 'Rating must be between 1 and 5'
            except ValueError:
                errors['service_rating'] = 'Rating must be a number'
        
        if not feedback:
            errors['feedback'] = 'Your Feedback is required'
        elif len(feedback) < 10:
            errors['feedback'] = 'Feedback must be at least 10 characters'
        
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Prepare data for storage
        # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp = (datetime.now() + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

        data = {
            'timestamp': timestamp,
            'agent_name': agent_name,
            'company_name': company_name,
            'mobile_number': mobile_number,
            'email': email,
            'service_rating': service_rating,
            'feedback': feedback,
            'remarks': remarks
        }
        
        # Store in Google Sheets if available
        if SHEETS_AVAILABLE:
            sheets.add_feedback(data)
        else:
            # For demo purposes, print to console
            print("DEMO MODE: Feedback received:", data)
        
        return jsonify({
            'success': True,
            'message': f'Thank you for your feedback, {agent_name}!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': {'server': f'An error occurred: {str(e)}'}
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
