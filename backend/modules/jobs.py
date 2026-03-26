from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from bson.objectid import ObjectId
from .models import jobs_col, applications_col

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/", methods=["GET"])
def list_jobs():
    skill = request.args.get("skill", "").lower()
    location = request.args.get("location", "").lower()
    query = {"status": {"$ne": "closed"}}
    if skill:
        query["required_skills"] = {"$regex": skill, "$options": "i"}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    jobs = list(jobs_col.find(query).sort("posted_at", -1))
    return jsonify([_serialize(j) for j in jobs])


@jobs_bp.route("/", methods=["POST"])
@jwt_required()
def post_job():
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Only recruiters can post jobs"}), 403

    user_id = get_jwt_identity()
    data = request.get_json()
    result = jobs_col.insert_one({
        "recruiter_id": user_id,
        "title": data["title"],
        "company": data["company"],
        "description": data["description"],
        "required_skills": data["required_skills"],
        "location": data.get("location", ""),
        "experience_required": data.get("experience_required", ""),
        "expiry_date": data.get("expiry_date", ""),
        "status": "open",
        "views": 0,
        "posted_at": datetime.utcnow(),
    })
    job = jobs_col.find_one({"_id": result.inserted_id})
    return jsonify(_serialize(job)), 201


@jobs_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    job = jobs_col.find_one_and_update(
        {"_id": ObjectId(job_id)},
        {"$inc": {"views": 1}},
        return_document=True
    )
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(_serialize(job))


@jobs_bp.route("/<job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    user_id = get_jwt_identity()
    job = jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job["recruiter_id"] != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    jobs_col.delete_one({"_id": ObjectId(job_id)})
    return jsonify({"message": "Job deleted"})


@jobs_bp.route("/<job_id>/toggle-status", methods=["PATCH"])
@jwt_required()
def toggle_status(job_id):
    user_id = get_jwt_identity()
    job = jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job["recruiter_id"] != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    new_status = "closed" if job.get("status", "open") == "open" else "open"
    jobs_col.update_one({"_id": ObjectId(job_id)}, {"$set": {"status": new_status}})
    return jsonify({"status": new_status})


@jobs_bp.route("/<job_id>/apply", methods=["POST"])
@jwt_required()
def apply_job(job_id):
    claims = get_jwt()
    if claims["role"] != "seeker":
        return jsonify({"error": "Only job seekers can apply"}), 403

    job = jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job.get("status") == "closed":
        return jsonify({"error": "This job is closed"}), 400

    user_id = get_jwt_identity()
    if applications_col.find_one({"user_id": user_id, "job_id": job_id}):
        return jsonify({"error": "Already applied"}), 409

    result = applications_col.insert_one({
        "user_id": user_id,
        "job_id": job_id,
        "match_score": 0.0,
        "status": "applied",
        "applied_at": datetime.utcnow(),
    })
    return jsonify({"message": "Applied successfully", "application_id": str(result.inserted_id)}), 201


@jobs_bp.route("/applications", methods=["GET"])
@jwt_required()
def my_applications():
    user_id = get_jwt_identity()
    apps = list(applications_col.find({"user_id": user_id}))
    return jsonify([{
        "application_id": str(a["_id"]),
        "job_id": a["job_id"],
        "status": a["status"],
        "match_score": a["match_score"],
        "applied_at": a["applied_at"].isoformat(),
    } for a in apps])


@jobs_bp.route("/recruiter/applications", methods=["GET"])
@jwt_required()
def recruiter_applications():
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Unauthorized"}), 403

    user_id = get_jwt_identity()
    recruiter_jobs = list(jobs_col.find({"recruiter_id": user_id}))
    job_ids = [str(j["_id"]) for j in recruiter_jobs]
    apps = list(applications_col.find({"job_id": {"$in": job_ids}}))
    return jsonify([{
        "application_id": str(a["_id"]),
        "user_id": a["user_id"],
        "job_id": a["job_id"],
        "status": a["status"],
        "match_score": a["match_score"],
    } for a in apps])


@jobs_bp.route("/applications/<app_id>/status", methods=["PATCH"])
@jwt_required()
def update_status(app_id):
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    applications_col.update_one({"_id": ObjectId(app_id)}, {"$set": {"status": data["status"]}})
    return jsonify({"message": "Status updated"})


def _serialize(job):
    skills = job.get("required_skills", "")
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    return {
        "id": str(job["_id"]),
        "title": job["title"],
        "company": job["company"],
        "description": job["description"],
        "required_skills": skills,
        "location": job.get("location", ""),
        "experience_required": job.get("experience_required", ""),
        "expiry_date": job.get("expiry_date", ""),
        "status": job.get("status", "open"),
        "views": job.get("views", 0),
        "posted_at": job["posted_at"].isoformat(),
    }
