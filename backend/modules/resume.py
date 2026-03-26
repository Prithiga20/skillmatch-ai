from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .models import db, Resume
from .parser import parse_resume

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims["role"] != "seeker":
        return jsonify({"error": "Only job seekers can upload resumes"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    parsed = parse_resume(file.read(), file.filename)

    resume = Resume.query.filter_by(user_id=user_id).first()
    if not resume:
        resume = Resume(user_id=user_id)
        db.session.add(resume)

    resume.raw_text = parsed["raw_text"]
    resume.skills = ",".join(parsed["skills"])
    resume.experience = parsed["experience"]
    resume.education = parsed["education"]
    db.session.commit()

    return jsonify({
        "skills": parsed["skills"],
        "experience": parsed["experience"],
        "education": parsed["education"],
    })


@resume_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    resume = Resume.query.filter_by(user_id=user_id).first()
    if not resume:
        return jsonify({"error": "No resume found"}), 404

    return jsonify({
        "skills": resume.skills.split(",") if resume.skills else [],
        "experience": resume.experience,
        "education": resume.education,
    })
