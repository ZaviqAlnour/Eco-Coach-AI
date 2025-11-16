"""
Eco-Coach AI - Adaptive Waste Reduction Coach
CS50X Final Project - Main Flask Application

WEEK 1-2 IMPLEMENTATION PLAN:
- Set up Flask app structure
- Implement user authentication (register, login, logout)
- Create database models with SQLAlchemy

WEEK 3-4 IMPLEMENTATION PLAN:
- Build waste logging functionality
- Integrate Bytez API with Qwen3-4B-Instruct-2507
- Create AI prompt templates for disposal instructions

WEEK 5-6 IMPLEMENTATION PLAN:
- Build dashboard with analytics
- Implement Chart.js for visualizations
- Add weekly/monthly metrics calculation

WEEK 7-8 IMPLEMENTATION PLAN:
- Polish UI/UX
- Add error handling and validation
- Testing and deployment preparation
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os
import json
import requests

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ecocoach.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# ========================================
# DATABASE MODELS
# ========================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    waste_logs = db.relationship('WasteLog', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class WasteLog(db.Model):
    __tablename__ = 'waste_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    quantity = db.Column(db.Float, default=1.0)
    disposal_instruction = db.Column(db.Text)
    tip = db.Column(db.Text)
    co2_saved = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'category': self.category,
            'quantity': self.quantity,
            'disposal_instruction': self.disposal_instruction,
            'tip': self.tip,
            'co2_saved': self.co2_saved,
            'timestamp': self.timestamp.isoformat()
        }


# ========================================
# CO2 IMPACT MAP
# ========================================

CO2_IMPACT_MAP = {
    'food': 0.5,
    'vegetables': 0.3,
    'fruit': 0.3,
    'meat': 1.5,
    'dairy': 0.8,
    'bread': 0.4,
    'plastic': 2.0,
    'paper': 0.9,
    'cardboard': 0.7,
    'glass': 0.3,
    'aluminum': 9.0,
    'steel': 1.7,
    'electronics': 5.0,
    'batteries': 3.0,
    'default': 0.5
}

# ========================================
# BYTEZ AI INTEGRATION
# ========================================

def get_ai_waste_analysis(item_name, quantity, user_location="general"):
    prompt = f"""You are an expert environmental coach specializing in waste reduction and recycling.

A user has thrown away: {item_name} (quantity: {quantity})
Location: {user_location}

Please respond in JSON only with fields:
category, disposal_instruction, tip, estimated_weight_kg
"""
    api_key = os.environ.get('BYTEZ_API_KEY')
    if not api_key:
        return get_mock_ai_response(item_name, quantity)

    api_url = "https://api.bytez.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen3-4b-instruct-2507",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        ai_content = result['choices'][0]['message']['content'].strip()
        if ai_content.startswith('```'):
            lines = ai_content.split('\n')
            ai_content = '\n'.join(lines[1:-1])
        ai_data = json.loads(ai_content)
    except Exception:
        return get_mock_ai_response(item_name, quantity)

    category = ai_data.get('category', 'default').lower()
    weight = ai_data.get('estimated_weight_kg', 0.5) * quantity
    co2_rate = CO2_IMPACT_MAP.get(category, CO2_IMPACT_MAP['default'])
    for key in CO2_IMPACT_MAP:
        if key in item_name.lower() or key in category.lower():
            co2_rate = CO2_IMPACT_MAP[key]
            break
    co2_saved = round(weight * co2_rate, 2)

    return {
        'category': ai_data.get('category', 'other'),
        'disposal_instruction': ai_data.get('disposal_instruction', 'Please recycle responsibly.'),
        'tip': ai_data.get('tip', 'Reduce, reuse, recycle.'),
        'co2_saved': co2_saved
    }


def get_mock_ai_response(item_name, quantity):
    item_lower = item_name.lower()
    if any(word in item_lower for word in ['food', 'meat', 'vegetable', 'fruit', 'bread', 'dairy']):
        category = 'food'
        instruction = f"Compost {item_name} if possible. Otherwise, dispose in food waste bin."
        tip = f"Plan meals to reduce {item_name} waste."
    elif any(word in item_lower for word in ['plastic', 'bottle', 'container']):
        category = 'recyclable'
        instruction = f"Rinse {item_name}, remove labels, place in recycling bin."
        tip = f"Use reusable alternatives instead of {item_name}."
    elif any(word in item_lower for word in ['paper', 'cardboard', 'box']):
        category = 'recyclable'
        instruction = f"Flatten {item_name} and recycle paper components."
        tip = "Go digital to reduce paper waste."
    elif any(word in item_lower for word in ['battery', 'electronic']):
        category = 'hazardous'
        instruction = f"Take {item_name} to hazardous waste collection center."
        tip = "Use rechargeable alternatives."
    else:
        category = 'other'
        instruction = f"Dispose of {item_name} in regular waste."
        tip = "Check if it can be reused, donated, or repaired."
    co2_rate = CO2_IMPACT_MAP.get(category, 0.5)
    co2_saved = round(quantity * 0.5 * co2_rate, 2)
    return {'category': category, 'disposal_instruction': instruction, 'tip': tip, 'co2_saved': co2_saved}

# ========================================
# AUTH DECORATOR
# ========================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ========================================
# ROUTES
# ========================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username exists.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email registered.', 'danger')
            return redirect(url_for('register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Login now.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    recent_logs = WasteLog.query.filter_by(user_id=user_id).order_by(WasteLog.timestamp.desc()).limit(10).all()
    all_logs = WasteLog.query.filter_by(user_id=user_id).all()
    total_items = len(all_logs)
    total_co2_saved = sum(log.co2_saved for log in all_logs)
    category_counts = {}
    for log in all_logs:
        cat = log.category or 'other'
        category_counts[cat] = category_counts.get(cat, 0) + 1
    weekly_data = get_weekly_trend(user_id)
    return render_template('dashboard.html',
                           recent_logs=recent_logs,
                           total_items=total_items,
                           total_co2_saved=round(total_co2_saved, 2),
                           category_counts=category_counts,
                           weekly_data=weekly_data)

# Log waste
@app.route('/log-waste', methods=['GET', 'POST'])
@login_required
def log_waste():
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        quantity = float(request.form.get('quantity', 1.0))
        if not item_name:
            flash('Enter an item name.', 'danger')
            return redirect(url_for('log_waste'))
        try:
            ai_result = get_ai_waste_analysis(item_name, quantity)
            log = WasteLog(user_id=session['user_id'],
                           item_name=item_name,
                           category=ai_result['category'],
                           quantity=quantity,
                           disposal_instruction=ai_result['disposal_instruction'],
                           tip=ai_result['tip'],
                           co2_saved=ai_result['co2_saved'])
            db.session.add(log)
            db.session.commit()
            flash('Waste logged!', 'success')
            return redirect(url_for('view_log', log_id=log.id))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('log_waste'))
    return render_template('log_waste.html')

@app.route('/log/<int:log_id>')
@login_required
def view_log(log_id):
    log = WasteLog.query.get_or_404(log_id)
    if log.user_id != session['user_id']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('view_log.html', log=log)

# History route (fixed)
@app.route('/history')
@login_required
def history():
    user_id = session['user_id']
    logs = WasteLog.query.filter_by(user_id=user_id).order_by(WasteLog.timestamp.desc()).all()
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    recent_logs_count = len([log for log in logs if log.timestamp > one_week_ago])
    return render_template('history.html', logs=logs, recent_logs_count=recent_logs_count)

# API endpoints
@app.route('/api/weekly-stats')
@login_required
def api_weekly_stats():
    user_id = session['user_id']
    weekly_data = get_weekly_trend(user_id, weeks=8)
    return jsonify(weekly_data)

@app.route('/api/category-breakdown')
@login_required
def api_category_breakdown():
    user_id = session['user_id']
    logs = WasteLog.query.filter_by(user_id=user_id).all()
    category_data = {}
    for log in logs:
        cat = log.category or 'other'
        category_data[cat] = category_data.get(cat, 0) + 1
    return jsonify(category_data)

# Helper
def get_weekly_trend(user_id, weeks=4):
    now = datetime.utcnow()
    weekly_stats = []
    for i in range(weeks):
        week_start = now - timedelta(days=(i+1)*7)
        week_end = now - timedelta(days=i*7)
        logs = WasteLog.query.filter(
            WasteLog.user_id == user_id,
            WasteLog.timestamp >= week_start,
            WasteLog.timestamp < week_end
        ).all()
        total_items = len(logs)
        total_co2 = sum(log.co2_saved for log in logs)
        weekly_stats.insert(0, {
            'week': f'Week {weeks-i}',
            'items': total_items,
            'co2_saved': round(total_co2, 2)
        })
    return weekly_stats

# DB init
def init_db():
    with app.app_context():
        db.create_all()
        print("DB tables created!")

# Run app
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
