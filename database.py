"""
Database models for SecureAI
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UserSession(db.Model):
    """Store anonymous user sessions"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Store risk assessments
    password_strength = db.Column(db.String(20))
    phishing_awareness = db.Column(db.String(20))
    overall_risk_score = db.Column(db.Integer)

class RiskAssessment(db.Model):
    """Store risk assessment results"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)