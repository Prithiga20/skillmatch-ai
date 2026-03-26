from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from .models import db, User, Job, Application

admin_bp = Blueprint("admin", __name__)


def require_admin():
    claims = get_jwt()
    if claims["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None


@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    err = require_admin()
    if err:
        return err
    return jsonify({
        "total_users": User.query.count(),
        "total_seekers": User.query.filter_by(role="seeker").count(),
        "total_recruiters": User.query.filter_by(role="recruiter").count(),
        "total_jobs": Job.query.count(),
        "total_applications": Application.query.count(),
    })


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    err = require_admin()
    if err:
        return err
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "created_at": u.created_at.isoformat(),
    } for u in users])


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    err = require_admin()
    if err:
        return err
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"error": "Cannot delete admin"}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


@admin_bp.route("/jobs", methods=["GET"])
@jwt_required()
def list_jobs():
    err = require_admin()
    if err:
        return err
    jobs = Job.query.order_by(Job.posted_at.desc()).all()
    return jsonify([{
        "id": j.id,
        "title": j.title,
        "company": j.company,
        "location": j.location,
        "recruiter_id": j.recruiter_id,
        "posted_at": j.posted_at.isoformat(),
    } for j in jobs])


@admin_bp.route("/jobs/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    err = require_admin()
    if err:
        return err
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted"})


@admin_bp.route("/applications", methods=["GET"])
@jwt_required()
def list_applications():
    err = require_admin()
    if err:
        return err
    apps = Application.query.order_by(Application.applied_at.desc()).all()
    return jsonify([{
        "id": a.id,
        "user_id": a.user_id,
        "job_id": a.job_id,
        "match_score": a.match_score,
        "status": a.status,
        "applied_at": a.applied_at.isoformat(),
    } for a in apps])
