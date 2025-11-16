"""
Database Models for Eco-Coach AI
SQLAlchemy ORM models for users and waste logs

This file can be used if you prefer separating models from app.py
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """
    User model for authentication and profile

    Relationships:
    - One user can have many waste logs
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # User preferences (optional for future features)
    location = db.Column(db.String(100), default='General')
    weekly_goal = db.Column(db.Float, default=5.0)  # kg CO2 reduction goal

    # Relationships
    waste_logs = db.relationship('WasteLog', backref='user', lazy='dynamic',
                                cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set user password using werkzeug"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def get_total_co2_saved(self):
        """Calculate total CO2 saved by this user"""
        return sum(log.co2_saved for log in self.waste_logs)

    def get_total_items_logged(self):
        """Get total number of items logged"""
        return self.waste_logs.count()

    def __repr__(self):
        return f'<User {self.username}>'


class WasteLog(db.Model):
    """
    Waste log model with AI-generated disposal instructions

    Each log represents one waste item with:
    - Category classification
    - Disposal instructions from AI
    - Personalized tips
    - CO2 impact calculation
    """
    __tablename__ = 'waste_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Waste item details
    item_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), index=True)  # food, recyclable, hazardous, compostable, landfill
    quantity = db.Column(db.Float, default=1.0)

    # AI-generated content
    disposal_instruction = db.Column(db.Text)
    tip = db.Column(db.Text)

    # Environmental impact
    co2_saved = db.Column(db.Float, default=0.0)  # kg CO2 equivalent

    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convert log to dictionary for JSON API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_name': self.item_name,
            'category': self.category,
            'quantity': self.quantity,
            'disposal_instruction': self.disposal_instruction,
            'tip': self.tip,
            'co2_saved': self.co2_saved,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self):
        return f'<WasteLog {self.item_name} by User {self.user_id}>'


class LocalRule(db.Model):
    """
    Optional: Local recycling rules database

    Can be seeded with location-specific disposal rules
    for common items to enhance AI responses
    """
    __tablename__ = 'local_rules'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False, index=True)
    item_type = db.Column(db.String(100), nullable=False)
    disposal_instruction = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<LocalRule {self.item_type} in {self.location}>'
