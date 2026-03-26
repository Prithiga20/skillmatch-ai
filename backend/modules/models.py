from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'seeker' or 'recruiter'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resume = db.relationship("Resume", backref="user", uselist=False)
    applications = db.relationship("Application", backref="user")


class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    raw_text = db.Column(db.Text)
    skills = db.Column(db.Text)       # comma-separated
    experience = db.Column(db.Text)
    education = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)  # comma-separated
    location = db.Column(db.String(100))
    experience_required = db.Column(db.String(50))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="job")


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    match_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default="applied")  # applied, shortlisted, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
