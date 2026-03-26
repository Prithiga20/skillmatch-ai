from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from bson.objectid import ObjectId
from datetime import datetime
from .models import resumes_col, jobs_col, applications_col, users_col
from .matcher import compute_match_score

enhance_bp = Blueprint("enhance", __name__)

COURSE_MAP = {
    "python": {"course": "Python for Everybody", "platform": "Coursera", "url": "https://www.coursera.org/specializations/python"},
    "machine learning": {"course": "Machine Learning Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction"},
    "deep learning": {"course": "Deep Learning Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/deep-learning"},
    "react": {"course": "React - The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"},
    "javascript": {"course": "JavaScript Algorithms and Data Structures", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"},
    "sql": {"course": "SQL for Data Science", "platform": "Coursera", "url": "https://www.coursera.org/learn/sql-for-data-science"},
    "aws": {"course": "AWS Certified Cloud Practitioner", "platform": "AWS", "url": "https://aws.amazon.com/certification/certified-cloud-practitioner/"},
    "docker": {"course": "Docker & Kubernetes: The Practical Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/"},
    "data analysis": {"course": "Data Analysis with Python", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/"},
    "nlp": {"course": "Natural Language Processing Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/natural-language-processing"},
    "tensorflow": {"course": "TensorFlow Developer Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice"},
    "java": {"course": "Java Programming Masterclass", "platform": "Udemy", "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/"},
    "typescript": {"course": "Understanding TypeScript", "platform": "Udemy", "url": "https://www.udemy.com/course/understanding-typescript/"},
    "devops": {"course": "DevOps Beginners to Advanced", "platform": "Udemy", "url": "https://www.udemy.com/course/decodingdevops/"},
    "kubernetes": {"course": "Kubernetes for the Absolute Beginners", "platform": "Udemy", "url": "https://www.udemy.com/course/learn-kubernetes/"},
    "agile": {"course": "Agile Fundamentals: Including Scrum & Kanban", "platform": "Udemy", "url": "https://www.udemy.com/course/agile-fundamentals-scrum-kanban-scrumban/"},
    "power bi": {"course": "Microsoft Power BI Desktop", "platform": "Udemy", "url": "https://www.udemy.com/course/microsoft-power-bi-up-running-with-power-bi-desktop/"},
    "mongodb": {"course": "MongoDB - The Complete Developer's Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/mongodb-the-complete-developers-guide/"},
    "git": {"course": "Git & GitHub Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/git-and-github-bootcamp/"},
    "flask": {"course": "REST APIs with Flask and Python", "platform": "Udemy", "url": "https://www.udemy.com/course/rest-api-flask-and-python/"},
}

INTERVIEW_QUESTIONS = {
    "python": ["What are Python decorators and how do you use them?", "Explain the difference between list, tuple, and set.", "What is the GIL in Python?", "How does memory management work in Python?", "What are generators and when would you use them?"],
    "machine learning": ["What is the difference between supervised and unsupervised learning?", "Explain overfitting and how to prevent it.", "What is cross-validation?", "Explain the bias-variance tradeoff.", "What is gradient descent?"],
    "react": ["What is the virtual DOM and how does React use it?", "Explain the difference between state and props.", "What are React hooks? Name a few commonly used ones.", "What is the useEffect hook used for?", "How does React handle component re-rendering?"],
    "sql": ["What is the difference between INNER JOIN and LEFT JOIN?", "Explain normalization and its forms.", "What is an index and when should you use one?", "What is the difference between WHERE and HAVING?", "Explain ACID properties in databases."],
    "javascript": ["What is the difference between == and ===?", "Explain closures in JavaScript.", "What is event bubbling?", "What is the difference between let, var, and const?", "Explain promises and async/await."],
    "java": ["What is the difference between JDK, JRE, and JVM?", "Explain OOP principles in Java.", "What is the difference between abstract class and interface?", "What is multithreading in Java?", "Explain garbage collection in Java."],
    "aws": ["What is the difference between EC2 and Lambda?", "Explain S3 storage classes.", "What is VPC and why is it important?", "What is Auto Scaling?", "Explain the difference between RDS and DynamoDB."],
    "docker": ["What is the difference between a container and a virtual machine?", "What is a Dockerfile?", "Explain Docker Compose.", "What is a Docker image vs a container?", "How do you persist data in Docker?"],
}

DEFAULT_QUESTIONS = ["Tell me about yourself.", "What are your greatest strengths?", "Where do you see yourself in 5 years?", "Why do you want to work here?", "Describe a challenging situation and how you handled it."]


@enhance_bp.route("/skill-gap/<job_id>", methods=["GET"])
@jwt_required()
def skill_gap(job_id):
    user_id = get_jwt_identity()
    resume = resumes_col.find_one({"user_id": user_id})
    if not resume or not resume.get("skills"):
        return jsonify({"error": "Upload a resume first"}), 400
    job = jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        return jsonify({"error": "Job not found"}), 404
    candidate_skills = set(resume["skills"]) if isinstance(resume["skills"], list) else {s.strip().lower() for s in resume["skills"].split(",") if s.strip()}
    raw_job_skills = job.get("required_skills", "")
    job_skills = set(raw_job_skills) if isinstance(raw_job_skills, list) else {s.strip().lower() for s in raw_job_skills.split(",") if s.strip()}
    matched = sorted(candidate_skills & job_skills)
    missing = sorted(job_skills - candidate_skills)
    courses = []
    for skill in missing:
        if skill in COURSE_MAP:
            courses.append({"skill": skill, **COURSE_MAP[skill]})
        else:
            courses.append({"skill": skill, "course": f"Search '{skill}' courses", "platform": "Google", "url": f"https://www.google.com/search?q={skill}+online+course"})
    score = compute_match_score(list(candidate_skills), list(job_skills))
    return jsonify({"job_title": job["title"], "match_score": score, "matched_skills": matched, "missing_skills": missing, "course_recommendations": courses})


@enhance_bp.route("/interview-prep", methods=["GET"])
@jwt_required()
def interview_prep():
    user_id = get_jwt_identity()
    resume = resumes_col.find_one({"user_id": user_id})
    questions = list(DEFAULT_QUESTIONS)
    skills_used = []
    if resume and resume.get("skills"):
        skills = resume["skills"] if isinstance(resume["skills"], list) else [s.strip().lower() for s in resume["skills"].split(",") if s.strip()]
        for skill in skills:
            if skill in INTERVIEW_QUESTIONS:
                questions.extend(INTERVIEW_QUESTIONS[skill])
                skills_used.append(skill)
    return jsonify({"skills_covered": skills_used, "questions": list(dict.fromkeys(questions))})


@enhance_bp.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    message = data.get("message", "").lower().strip()
    responses = {
        "resume": "To improve your resume: use action verbs, quantify achievements, tailor it to each job, and keep it to 1-2 pages.",
        "interview": "For interviews: research the company, practice STAR method answers, prepare questions to ask, and dress professionally.",
        "salary": "Research salary ranges on Glassdoor or LinkedIn. Consider your experience, location, and industry when negotiating.",
        "skills": "Focus on in-demand skills like Python, cloud computing, data analysis, and communication. Upload your resume to see your skill gaps.",
        "job search": "Use LinkedIn, Naukri, Indeed, and company career pages. Network actively and tailor your applications.",
        "career": "Set clear career goals, build relevant skills, network with professionals, and seek mentorship in your field.",
        "cover letter": "A good cover letter: addresses the hiring manager by name, highlights 2-3 key achievements, and explains why you want this specific role.",
        "linkedin": "Optimize your LinkedIn: professional photo, compelling headline, detailed experience, and 500+ connections.",
        "rejection": "Rejection is normal. Ask for feedback, improve your application, and keep applying. Persistence is key.",
        "fresher": "As a fresher: build projects, contribute to open source, do internships, and highlight academic achievements.",
    }
    reply = "I can help with: resume tips, interview preparation, salary negotiation, skill development, job search strategies, and career guidance. What would you like to know?"
    for keyword, response in responses.items():
        if keyword in message:
            reply = response
            break
    return jsonify({"reply": reply})


# Feature 6: Resume Score vs Job
@enhance_bp.route("/resume-score/<job_id>", methods=["GET"])
@jwt_required()
def resume_score(job_id):
    user_id = get_jwt_identity()
    resume = resumes_col.find_one({"user_id": user_id})
    if not resume or not resume.get("skills"):
        return jsonify({"error": "Upload a resume first"}), 400
    job = jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        return jsonify({"error": "Job not found"}), 404

    candidate_skills = set(resume["skills"]) if isinstance(resume["skills"], list) else {s.strip().lower() for s in resume["skills"].split(",") if s.strip()}
    raw_job_skills = job.get("required_skills", "")
    job_skills = set(raw_job_skills) if isinstance(raw_job_skills, list) else {s.strip().lower() for s in raw_job_skills.split(",") if s.strip()}

    skill_score = round(compute_match_score(list(candidate_skills), list(job_skills)), 2)
    exp_text = resume.get("experience", "")
    exp_score = 80.0 if "year" in exp_text.lower() else 40.0
    edu_text = resume.get("education", "Not specified")
    edu_score = 90.0 if edu_text != "Not specified" else 50.0
    total = round((skill_score * 0.5) + (exp_score * 0.3) + (edu_score * 0.2), 2)

    return jsonify({
        "job_title": job["title"],
        "total_score": total,
        "breakdown": {
            "skills": {"score": skill_score, "weight": "50%"},
            "experience": {"score": exp_score, "weight": "30%"},
            "education": {"score": edu_score, "weight": "20%"},
        }
    })


# Feature 5: Similar Jobs
@enhance_bp.route("/similar-jobs/<job_id>", methods=["GET"])
def similar_jobs(job_id):
    job = jobs_col.find_one({"_id": ObjectId(job_id)})
    if not job:
        return jsonify([])
    raw_skills = job.get("required_skills", "")
    job_skills = raw_skills if isinstance(raw_skills, list) else [s.strip().lower() for s in raw_skills.split(",") if s.strip()]
    all_jobs = list(jobs_col.find({"_id": {"$ne": ObjectId(job_id)}, "status": {"$ne": "closed"}}))
    scored = []
    for j in all_jobs:
        s = j.get("required_skills", "")
        skills = s if isinstance(s, list) else [x.strip().lower() for x in s.split(",") if x.strip()]
        score = compute_match_score(job_skills, skills)
        if score > 0:
            scored.append({"id": str(j["_id"]), "title": j["title"], "company": j["company"], "location": j.get("location", ""), "match_score": round(score, 2)})
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify(scored[:3])


# Feature 14: Hiring Funnel
@enhance_bp.route("/hiring-funnel/<job_id>", methods=["GET"])
@jwt_required()
def hiring_funnel(job_id):
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Unauthorized"}), 403
    apps = list(applications_col.find({"job_id": job_id}))
    return jsonify({
        "applied": len(apps),
        "shortlisted": len([a for a in apps if a["status"] == "shortlisted"]),
        "rejected": len([a for a in apps if a["status"] == "rejected"]),
    })


# Feature 17: Search History
@enhance_bp.route("/search-history", methods=["GET", "POST", "DELETE"])
@jwt_required()
def search_history():
    user_id = get_jwt_identity()
    user = users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == "GET":
        return jsonify(user.get("search_history", []))

    if request.method == "POST":
        data = request.get_json()
        query = data.get("query", "").strip()
        if query:
            history = user.get("search_history", [])
            if query not in history:
                history.insert(0, query)
                history = history[:10]
            users_col.update_one({"_id": ObjectId(user_id)}, {"$set": {"search_history": history}})
        return jsonify({"message": "Saved"})

    if request.method == "DELETE":
        users_col.update_one({"_id": ObjectId(user_id)}, {"$set": {"search_history": []}})
        return jsonify({"message": "Cleared"})


# Feature 18: Company Profile
@enhance_bp.route("/company-profile", methods=["GET", "POST"])
@jwt_required()
def company_profile():
    claims = get_jwt()
    if claims["role"] != "recruiter":
        return jsonify({"error": "Unauthorized"}), 403
    user_id = get_jwt_identity()

    if request.method == "GET":
        user = users_col.find_one({"_id": ObjectId(user_id)})
        return jsonify(user.get("company_profile", {}))

    data = request.get_json()
    users_col.update_one({"_id": ObjectId(user_id)}, {"$set": {"company_profile": {
        "company_name": data.get("company_name", ""),
        "industry": data.get("industry", ""),
        "website": data.get("website", ""),
        "location": data.get("location", ""),
        "description": data.get("description", ""),
        "updated_at": datetime.utcnow().isoformat(),
    }}})
    return jsonify({"message": "Company profile updated"})
