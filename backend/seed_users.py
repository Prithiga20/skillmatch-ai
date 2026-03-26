from modules.models import users_col
from werkzeug.security import generate_password_hash
from datetime import datetime

# Clear all existing users
users_col.delete_many({})
print("Cleared existing users")

users = [
    {"name": "Admin",          "email": "admin@skillmatch.com",     "password": "admin123",     "role": "admin"},
    {"name": "John Recruiter", "email": "recruiter@skillmatch.com", "password": "recruiter123", "role": "recruiter"},
    {"name": "Jane Seeker",    "email": "seeker@skillmatch.com",    "password": "seeker123",    "role": "seeker"},
]

for u in users:
    existing = users_col.find_one({"email": u["email"]})
    if existing:
        users_col.update_one({"email": u["email"]}, {"$set": {"password": generate_password_hash(u["password"]), "role": u["role"]}})
        print(f"Updated: {u['email']}")
    else:
        users_col.insert_one({"name": u["name"], "email": u["email"], "password": generate_password_hash(u["password"]), "role": u["role"], "created_at": datetime.utcnow()})
        print(f"Created: {u['email']}")

print("\nDone!")
print("Admin     -> admin@skillmatch.com     / admin123")
print("Recruiter -> recruiter@skillmatch.com / recruiter123")
print("Seeker    -> seeker@skillmatch.com    / seeker123")
