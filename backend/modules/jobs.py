from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .models import db, Job, Application

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/", methods=["GET"])
def list_jobs():
    skill = request.args.get("skill", "").lower()
    location = request.args.get("location", "").lower()
    query = Job.query
    if skill:
        query = query.filter(Job.required_skills.ilike(f"%{skill}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    jobs = query.order_by(Job.posted_at.desc()).all()
    return jsonify([_serialize(j) for j in jobs])


@jobs_bp.route("/", methods=["POST"])
@jwt_required()
def post_job():
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Only recruiters can post jobs"}), 403

    user_id = int(get_jwt_identity())
    data = request.get_json()
    job = Job(
        recruiter_id=user_id,
        title=data["title"],
        company=data["company"],
        description=data["description"],
        required_skills=data["required_skills"],
        location=data.get("location", ""),
        experience_required=data.get("experience_required", ""),
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(_serialize(job)), 201


@jobs_bp.route("/<int:job_id>", methods=["GET"])
def get_job(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify(_serialize(job))


@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    user_id = int(get_jwt_identity())
    job = Job.query.get_or_404(job_id)
    if job.recruiter_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted"})


@jobs_bp.route("/<int:job_id>/apply", methods=["POST"])
@jwt_required()
def apply_job(job_id):
    claims = get_jwt()
    if claims["role"] != "seeker":
        return jsonify({"error": "Only job seekers can apply"}), 403

    user_id = int(get_jwt_identity())
    existing = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing:
        return jsonify({"error": "Already applied"}), 409

    app = Application(user_id=user_id, job_id=job_id)
    db.session.add(app)
    db.session.commit()
    return jsonify({"message": "Applied successfully", "application_id": app.id}), 201


@jobs_bp.route("/applications", methods=["GET"])
@jwt_required()
def my_applications():
    user_id = int(get_jwt_identity())
    apps = Application.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "application_id": a.id,
        "job_id": a.job_id,
        "status": a.status,
        "match_score": a.match_score,
        "applied_at": a.applied_at.isoformat(),
    } for a in apps])


@jobs_bp.route("/recruiter/applications", methods=["GET"])
@jwt_required()
def recruiter_applications():
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Unauthorized"}), 403

    user_id = int(get_jwt_identity())
    recruiter_jobs = Job.query.filter_by(recruiter_id=user_id).all()
    job_ids = [j.id for j in recruiter_jobs]
    apps = Application.query.filter(Application.job_id.in_(job_ids)).all()
    return jsonify([{
        "application_id": a.id,
        "user_id": a.user_id,
        "job_id": a.job_id,
        "status": a.status,
        "match_score": a.match_score,
    } for a in apps])


@jobs_bp.route("/applications/<int:app_id>/status", methods=["PATCH"])
@jwt_required()
def update_status(app_id):
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Unauthorized"}), 403

    application = Application.query.get_or_404(app_id)
    data = request.get_json()
    application.status = data["status"]
    db.session.commit()
    return jsonify({"message": "Status updated"})


def _serialize(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "required_skills": job.required_skills.split(",") if job.required_skills else [],
        "location": job.location,
        "experience_required": job.experience_required,
        "posted_at": job.posted_at.isoformat(),
    }
