from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .models import db, Resume, Job
from .matcher import compute_match_score

match_bp = Blueprint("match", __name__)


@match_bp.route("/recommendations", methods=["GET"])
@jwt_required()
def recommend_jobs():
    user_id = int(get_jwt_identity())
    resume = Resume.query.filter_by(user_id=user_id).first()
    if not resume or not resume.skills:
        return jsonify({"error": "Upload a resume first"}), 400

    candidate_skills = [s.strip() for s in resume.skills.split(",") if s.strip()]
    jobs = Job.query.all()

    scored = []
    for job in jobs:
        job_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]
        score = compute_match_score(candidate_skills, job_skills)
        scored.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "required_skills": job_skills,
            "match_score": score,
        })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify(scored[:10])


@match_bp.route("/candidates/<int:job_id>", methods=["GET"])
@jwt_required()
def recommend_candidates(job_id):
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Unauthorized"}), 403

    job = Job.query.get_or_404(job_id)
    job_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]

    resumes = Resume.query.all()
    scored = []
    for resume in resumes:
        if not resume.skills:
            continue
        candidate_skills = [s.strip() for s in resume.skills.split(",") if s.strip()]
        score = compute_match_score(candidate_skills, job_skills)
        scored.append({
            "user_id": resume.user_id,
            "skills": candidate_skills,
            "experience": resume.experience,
            "match_score": score,
        })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify(scored[:20])
