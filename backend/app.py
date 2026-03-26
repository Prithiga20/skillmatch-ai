from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

CORS(app, origins=["http://localhost:3000", "http://localhost:3001"], supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
JWTManager(app)

from modules.auth import auth_bp
from modules.resume import resume_bp
from modules.jobs import jobs_bp
from modules.match import match_bp
from modules.admin import admin_bp
from modules.enhance import enhance_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(resume_bp, url_prefix="/api/resume")
app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
app.register_blueprint(match_bp, url_prefix="/api/match")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(enhance_bp, url_prefix="/api/enhance")

# Create default admin on startup
from modules.models import users_col
from werkzeug.security import generate_password_hash
from datetime import datetime

if not users_col.find_one({"role": "admin"}):
    users_col.insert_one({
        "name": "Admin",
        "email": "admin@skillmatch.com",
        "password": generate_password_hash("admin123"),
        "role": "admin",
        "created_at": datetime.utcnow(),
    })
    print("Default admin created: admin@skillmatch.com / admin123")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
