from app import app
from modules.models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    existing = User.query.filter_by(email="admin@skillmatch.com").first()
    if existing:
        existing.password = generate_password_hash("admin123")
        existing.role = "admin"
        db.session.commit()
        print("Admin password reset: admin@skillmatch.com / admin123")
    else:
        admin = User(
            name="Admin",
            email="admin@skillmatch.com",
            password=generate_password_hash("admin123"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created: admin@skillmatch.com / admin123")
