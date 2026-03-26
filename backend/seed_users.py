from app import app
from modules.models import db, User
from werkzeug.security import generate_password_hash

users = [
    {"name": "Admin",          "email": "admin@skillmatch.com",     "password": "admin123",     "role": "admin"},
    {"name": "John Recruiter", "email": "recruiter@skillmatch.com", "password": "recruiter123", "role": "recruiter"},
    {"name": "Jane Seeker",    "email": "seeker@skillmatch.com",    "password": "seeker123",    "role": "seeker"},
]

with app.app_context():
    for u in users:
        existing = User.query.filter_by(email=u["email"]).first()
        if existing:
            existing.password = generate_password_hash(u["password"])
            existing.role = u["role"]
            print(f"Updated: {u['email']}")
        else:
            new_user = User(
                name=u["name"],
                email=u["email"],
                password=generate_password_hash(u["password"]),
                role=u["role"],
            )
            db.session.add(new_user)
            print(f"Created: {u['email']}")
    db.session.commit()
    print("\nDone! Login credentials:")
    print("Admin     -> admin@skillmatch.com     / admin123")
    print("Recruiter -> recruiter@skillmatch.com / recruiter123")
    print("Seeker    -> seeker@skillmatch.com    / seeker123")
