from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from modules.models import db
from modules.auth import auth_bp
from modules.resume import resume_bp
from modules.jobs import jobs_bp
from modules.match import match_bp
from modules.admin import admin_bp

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/skillmatch")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 300}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB upload limit

CORS(app, origins=["http://localhost:3000"], supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
JWTManager(app)
db.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(resume_bp, url_prefix="/api/resume")
app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
app.register_blueprint(match_bp, url_prefix="/api/match")
app.register_blueprint(admin_bp, url_prefix="/api/admin")

with app.app_context():
    db.create_all()
    # Create default admin if not exists
    from modules.models import User
    from werkzeug.security import generate_password_hash
    if not User.query.filter_by(role="admin").first():
        admin = User(
            name="Admin",
            email="admin@skillmatch.com",
            password=generate_password_hash("admin123"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin@skillmatch.com / admin123")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
