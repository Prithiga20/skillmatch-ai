from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from bson.objectid import ObjectId
from .models import users_col, jobs_col, applications_col

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
        "total_users": users_col.count_documents({}),
        "total_seekers": users_col.count_documents({"role": "seeker"}),
        "total_recruiters": users_col.count_documents({"role": "recruiter"}),
        "total_jobs": jobs_col.count_documents({}),
        "total_applications": applications_col.count_documents({}),
    })


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    err = require_admin()
    if err:
        return err
    users = list(users_col.find().sort("created_at", -1))
    return jsonify([{
        "id": str(u["_id"]),
        "name": u["name"],
        "email": u["email"],
        "role": u["role"],
        "created_at": u["created_at"].isoformat(),
    } for u in users])


@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    err = require_admin()
    if err:
        return err
    user = users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user["role"] == "admin":
        return jsonify({"error": "Cannot delete admin"}), 400
    users_col.delete_one({"_id": ObjectId(user_id)})
    return jsonify({"message": "User deleted"})


@admin_bp.route("/jobs", methods=["GET"])
@jwt_required()
def list_jobs():
    err = require_admin()
    if err:
        return err
    jobs = list(jobs_col.find().sort("posted_at", -1))
    return jsonify([{
        "id": str(j["_id"]),
        "title": j["title"],
        "company": j["company"],
        "location": j.get("location", ""),
        "recruiter_id": j["recruiter_id"],
        "posted_at": j["posted_at"].isoformat(),
    } for j in jobs])


@admin_bp.route("/jobs/<job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    err = require_admin()
    if err:
        return err
    jobs_col.delete_one({"_id": ObjectId(job_id)})
    return jsonify({"message": "Job deleted"})


@admin_bp.route("/applications", methods=["GET"])
@jwt_required()
def list_applications():
    err = require_admin()
    if err:
        return err
    apps = list(applications_col.find().sort("applied_at", -1))
    return jsonify([{
        "id": str(a["_id"]),
        "user_id": a["user_id"],
        "job_id": a["job_id"],
        "match_score": a["match_score"],
        "status": a["status"],
        "applied_at": a["applied_at"].isoformat(),
    } for a in apps])
