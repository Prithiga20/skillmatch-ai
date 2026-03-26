from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from bson.objectid import ObjectId
from .models import resumes_col
from .parser import parse_resume

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()
    claims = get_jwt()
    if claims["role"] != "seeker":
        return jsonify({"error": "Only job seekers can upload resumes"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    parsed = parse_resume(file.read(), file.filename)

    resumes_col.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "raw_text": parsed["raw_text"],
            "skills": parsed["skills"],
            "experience": parsed["experience"],
            "education": parsed["education"],
            "uploaded_at": datetime.utcnow(),
        }},
        upsert=True,
    )

    return jsonify({
        "skills": parsed["skills"],
        "experience": parsed["experience"],
        "education": parsed["education"],
    })


@resume_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    resume = resumes_col.find_one({"user_id": user_id})
    if not resume:
        return jsonify({"error": "No resume found"}), 404

    return jsonify({
        "skills": resume.get("skills", []),
        "experience": resume.get("experience", ""),
        "education": resume.get("education", ""),
    })
