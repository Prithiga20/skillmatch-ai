from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from bson.objectid import ObjectId
from .models import resumes_col, jobs_col
from .matcher import compute_match_score

match_bp = Blueprint("match", __name__)


@match_bp.route("/recommendations", methods=["GET"])
@jwt_required()
def recommend_jobs():
    user_id = get_jwt_identity()
    resume = resumes_col.find_one({"user_id": user_id})
    if not resume or not resume.get("skills"):
        return jsonify({"error": "Upload a resume first"}), 400

    candidate_skills = resume["skills"] if isinstance(resume["skills"], list) else [s.strip() for s in resume["skills"].split(",") if s.strip()]
    jobs = list(jobs_col.find())

    scored = []
    for job in jobs:
        skills = job.get("required_skills", "")
        job_skills = skills if isinstance(skills, list) else [s.strip() for s in skills.split(",") if s.strip()]
        score = compute_match_score(candidate_skills, job_skills)
        scored.append({
            "id": str(job["_id"]),
            "title": job["title"],
            "company": job["company"],
            "location": job.get("location", ""),
            "required_skills": job_skills,
            "match_score": score,
        })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify(scored[:10])


@match_bp.route("/candidates/<job_id>", methods=["GET"])
@jwt_required()
def recommend_candidates(job_id):
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Unauthorized"}), 403

    job = jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        return jsonify({"error": "Job not found"}), 404

    skills = job.get("required_skills", "")
    job_skills = skills if isinstance(skills, list) else [s.strip() for s in skills.split(",") if s.strip()]

    resumes = list(resumes_col.find())
    scored = []
    for resume in resumes:
        if not resume.get("skills"):
            continue
        candidate_skills = resume["skills"] if isinstance(resume["skills"], list) else [s.strip() for s in resume["skills"].split(",") if s.strip()]
        score = compute_match_score(candidate_skills, job_skills)
        scored.append({
            "user_id": resume["user_id"],
            "skills": candidate_skills,
            "experience": resume.get("experience", ""),
            "match_score": score,
        })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify(scored[:20])
