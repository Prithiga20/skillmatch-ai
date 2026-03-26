from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import users_col, str_id

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    role = data.get("role", "seeker")

    if role == "admin":
        return jsonify({"error": "Admin accounts cannot be self-registered"}), 403
    if users_col.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already registered"}), 409

    result = users_col.insert_one({
        "name": data["name"],
        "email": data["email"],
        "password": generate_password_hash(data["password"]),
        "role": role,
        "created_at": datetime.utcnow(),
    })
    user_id = str(result.inserted_id)
    token = create_access_token(identity=user_id, additional_claims={"role": role})
    return jsonify({"token": token, "user": {"id": user_id, "name": data["name"], "role": role}}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = users_col.find_one({"email": data["email"]})
    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    user_id = str(user["_id"])
    token = create_access_token(identity=user_id, additional_claims={"role": user["role"]})
    return jsonify({"token": token, "user": {"id": user_id, "name": user["name"], "role": user["role"]}})
