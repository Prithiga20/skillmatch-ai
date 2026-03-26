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
    skill = request.args.get("skill", "").strip().lower()
    resume = resumes_col.find_one({"user_id": user_id})

    questions = list(DEFAULT_QUESTIONS)
    skills_used = []

    if skill:
        # Skill selected manually
        if skill in INTERVIEW_QUESTIONS:
            questions.extend(INTERVIEW_QUESTIONS[skill])
            skills_used = [skill]
        else:
            skills_used = [skill]
    elif resume and resume.get("skills"):
        # Auto from resume
        skills = resume["skills"] if isinstance(resume["skills"], list) else [s.strip().lower() for s in resume["skills"].split(",") if s.strip()]
        for s in skills:
            if s in INTERVIEW_QUESTIONS:
                questions.extend(INTERVIEW_QUESTIONS[s])
                skills_used.append(s)

    return jsonify({
        "skills_covered": skills_used,
        "available_skills": list(INTERVIEW_QUESTIONS.keys()),
        "questions": list(dict.fromkeys(questions))
    })


@enhance_bp.route("/interview-evaluate", methods=["POST"])
@jwt_required()
def interview_evaluate():
    data = request.get_json()
    submissions = data.get("submissions", [])  # [{question, answer, skill}]

    KEYWORDS = {
        "python": ["decorator", "generator", "gil", "list", "tuple", "set", "memory", "lambda", "iterator", "class"],
        "machine learning": ["supervised", "unsupervised", "overfitting", "cross-validation", "gradient", "bias", "variance", "model", "training", "accuracy"],
        "react": ["virtual dom", "state", "props", "hooks", "useeffect", "usestate", "component", "render", "jsx", "lifecycle"],
        "sql": ["join", "index", "normalization", "acid", "where", "having", "primary key", "foreign key", "query", "table"],
        "javascript": ["closure", "promise", "async", "await", "event", "scope", "hoisting", "prototype", "callback", "dom"],
        "java": ["jvm", "oop", "inheritance", "polymorphism", "interface", "abstract", "thread", "garbage", "exception", "collection"],
        "aws": ["ec2", "s3", "lambda", "vpc", "rds", "dynamodb", "iam", "cloudwatch", "auto scaling", "region"],
        "docker": ["container", "image", "dockerfile", "compose", "volume", "network", "registry", "kubernetes", "layer", "daemon"],
    }

    HR_KEYWORDS = ["experience", "team", "challenge", "goal", "strength", "weakness", "achieve", "learn", "work", "project", "skill", "improve", "success", "problem", "solution"]

    results = []
    total_score = 0

    for item in submissions:
        question = item.get("question", "")
        answer = item.get("answer", "").strip()
        skill = item.get("skill", "").lower()
        score = 0
        feedback = []

        if not answer:
            results.append({"question": question, "score": 0, "feedback": "No answer provided.", "grade": "F"})
            continue

        word_count = len(answer.split())

        # Length scoring (max 40)
        if word_count >= 80:
            score += 40
            feedback.append("Excellent answer length.")
        elif word_count >= 40:
            score += 30
            feedback.append("Good answer length.")
        elif word_count >= 15:
            score += 15
            feedback.append("Answer is a bit short. Try to elaborate more.")
        else:
            score += 5
            feedback.append("Answer too brief. Aim for at least 40 words.")

        # Keyword scoring (max 40)
        answer_lower = answer.lower()
        kw_list = KEYWORDS.get(skill, HR_KEYWORDS)
        matched_kw = [k for k in kw_list if k in answer_lower]
        kw_score = min(40, len(matched_kw) * 8)
        score += kw_score
        if matched_kw:
            feedback.append(f"Good use of keywords: {', '.join(matched_kw[:4])}.")
        else:
            feedback.append("Try to include more relevant technical keywords.")

        # Structure scoring (max 20)
        has_structure = any(c in answer for c in [".", ",", ":", "-", "\n"])
        if has_structure and word_count > 20:
            score += 20
            feedback.append("Well-structured answer.")
        else:
            score += 5
            feedback.append("Structure your answer with clear sentences.")

        score = min(100, score)
        grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D" if score >= 30 else "F"
        total_score += score
        results.append({"question": question, "score": score, "grade": grade, "feedback": " ".join(feedback)})

    overall = round(total_score / len(submissions), 1) if submissions else 0
    overall_grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 50 else "D" if overall >= 30 else "F"

    return jsonify({
        "results": results,
        "overall_score": overall,
        "overall_grade": overall_grade,
        "total_questions": len(submissions),
        "answered": len([s for s in submissions if s.get("answer", "").strip()])
    })


@enhance_bp.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    message = data.get("message", "").lower().strip()

    RULES = [
        # Resume
        (["resume", "cv", "curriculum"], "📄 Resume Tips:\n• Use strong action verbs (Led, Built, Improved, Achieved)\n• Quantify achievements — e.g. 'Increased sales by 30%'\n• Tailor your resume for each job description\n• Keep it to 1–2 pages max\n• Use a clean, ATS-friendly format\n• Add a strong summary at the top"),
        (["cover letter", "covering letter"], "✉️ Cover Letter Tips:\n• Address the hiring manager by name if possible\n• Open with a strong hook — why you want THIS role\n• Highlight 2–3 key achievements relevant to the job\n• Keep it under 1 page\n• End with a confident call to action"),
        # Interview
        (["interview", "prepare for interview", "interview tips"], "🎯 Interview Preparation:\n• Research the company — mission, products, recent news\n• Practice STAR method (Situation, Task, Action, Result)\n• Prepare 5 questions to ask the interviewer\n• Dress professionally and arrive early\n• Practice common questions: strengths, weaknesses, goals\n• Use our Interview Prep module for skill-based practice!"),
        (["star method", "star technique"], "⭐ STAR Method:\n• Situation — Set the context\n• Task — Describe your responsibility\n• Action — Explain what YOU did specifically\n• Result — Share the measurable outcome\n\nExample: 'I led a team of 4 (S), tasked with reducing load time (T), I optimized queries (A), resulting in 40% faster performance (R).'"),
        # Salary
        (["salary", "negotiate", "pay", "compensation", "ctc"], "💰 Salary Negotiation:\n• Research market rates on Glassdoor, LinkedIn, Levels.fyi\n• Never give a number first — ask for their range\n• Anchor high — you can always come down\n• Consider the full package: bonus, equity, benefits\n• Practice your pitch: 'Based on my experience and market data, I'm targeting X'\n• It's always okay to ask for time to consider an offer"),
        # Skills
        (["skill", "learn", "upskill", "course", "certification"], "🚀 Skill Development:\n• Top in-demand skills: Python, SQL, React, AWS, Docker, ML\n• Use free platforms: freeCodeCamp, Coursera, edX, YouTube\n• Build real projects — employers value portfolios\n• Get certified: AWS, Google, Microsoft certs add credibility\n• Use our Skill Gap Analyzer to find what you're missing!"),
        (["python"], "🐍 Python Career Tips:\n• Python is #1 for Data Science, ML, Backend, Automation\n• Learn: basics → OOP → libraries (pandas, numpy, flask)\n• Build projects: web scraper, data dashboard, REST API\n• Top certifications: PCEP, PCAP (Python Institute)"),
        (["data science", "machine learning", "ai", "artificial intelligence"], "🤖 Data Science / ML Path:\n• Learn: Python → Statistics → pandas/numpy → sklearn → Deep Learning\n• Key tools: Jupyter, TensorFlow, PyTorch, Tableau\n• Build a portfolio: Kaggle competitions, GitHub projects\n• Roles: Data Analyst → Data Scientist → ML Engineer"),
        # Job Search
        (["job search", "find job", "job hunt", "apply", "application"], "🔍 Job Search Strategy:\n• Use: LinkedIn, Indeed, Naukri, Glassdoor, AngelList\n• Apply to 10–15 jobs/week for best results\n• Customize your resume for each application\n• Follow up after 1 week if no response\n• Network — 70% of jobs are filled through connections\n• Use SkillMatch AI to find jobs matching your skills!"),
        (["linkedin", "linked in", "profile"], "💼 LinkedIn Optimization:\n• Professional headshot (increases views by 14x)\n• Headline: 'Role | Skills | Value' not just your job title\n• Write a compelling About section (first 3 lines matter most)\n• Add all skills and get endorsements\n• Post content weekly to increase visibility\n• Connect with recruiters in your target companies"),
        (["network", "networking"], "🤝 Networking Tips:\n• Attend industry meetups, hackathons, webinars\n• Connect with alumni from your college on LinkedIn\n• Send personalized connection requests (not generic)\n• Offer value before asking for favors\n• Informational interviews are powerful — just ask!"),
        # Career
        (["career change", "switch career", "career switch"], "🔄 Career Change Tips:\n• Identify transferable skills from your current role\n• Take online courses to bridge skill gaps\n• Build a portfolio in the new field\n• Start with freelance/side projects to gain experience\n• Network with people already in your target field\n• Be patient — career transitions take 6–12 months typically"),
        (["career", "growth", "promotion", "career path"], "📈 Career Growth:\n• Set clear 1-year and 5-year goals\n• Ask for feedback regularly from your manager\n• Take on stretch assignments beyond your role\n• Build both technical and soft skills\n• Find a mentor in your field\n• Document your achievements for performance reviews"),
        (["fresher", "fresh graduate", "entry level", "no experience", "beginner"], "🎓 Fresher Career Tips:\n• Build projects and put them on GitHub\n• Contribute to open source projects\n• Do internships — even unpaid ones build experience\n• Highlight academic projects and achievements\n• Get 1–2 certifications in your field\n• Apply broadly — your first job doesn't have to be perfect"),
        # Wellbeing
        (["rejection", "rejected", "failed", "not selected"], "💪 Dealing with Rejection:\n• Rejection is a normal part of job searching — everyone faces it\n• Ask for feedback when possible\n• Review and improve your resume/interview skills\n• Keep a consistent application routine\n• Celebrate small wins — every interview is practice\n• Most people apply to 50–100 jobs before landing one"),
        (["stress", "anxiety", "burnout", "overwhelm"], "🧘 Managing Job Search Stress:\n• Set a daily limit — apply to 5 jobs, then stop\n• Take breaks and maintain hobbies\n• Talk to friends, family, or a mentor\n• Exercise regularly — it helps with anxiety\n• Remember: job searching is a skill that improves with practice\n• You WILL find the right opportunity!"),
        (["remote", "work from home", "wfh", "hybrid"], "🏠 Remote Work Tips:\n• Highlight remote-friendly skills: communication, self-management\n• Use: Remote.co, We Work Remotely, FlexJobs\n• Set up a professional home workspace\n• Be proactive in communication with remote teams\n• Time zone flexibility is a big plus for global roles"),
        (["freelance", "freelancing", "gig"], "💻 Freelancing Tips:\n• Start on: Upwork, Fiverr, Toptal, Freelancer\n• Build a strong portfolio with 3–5 sample projects\n• Set competitive rates initially to build reviews\n• Specialize in a niche — generalists earn less\n• Always have a contract and milestone-based payments"),
    ]

    reply = None
    for keywords, response in RULES:
        if any(kw in message for kw in keywords):
            reply = response
            break

    if not reply:
        # Greeting detection
        if any(g in message for g in ["hi", "hello", "hey", "good morning", "good evening", "howdy"]):
            reply = "👋 Hello! I'm your Career Guidance Assistant. I can help you with:\n\n• 📄 Resume & Cover Letter Tips\n• 🎯 Interview Preparation\n• 💰 Salary Negotiation\n• 🚀 Skill Development\n• 🔍 Job Search Strategies\n• 📈 Career Growth\n\nWhat would you like help with today?"
        elif any(t in message for t in ["thank", "thanks", "great", "awesome", "helpful"]):
            reply = "😊 You're welcome! Feel free to ask anything else. Good luck with your career journey! 🚀"
        else:
            reply = "🤔 I'm not sure about that specific query. I can help with:\n\n• Resume tips\n• Interview preparation\n• Salary negotiation\n• Skill development\n• Job search strategies\n• Career guidance\n• Networking tips\n• Fresher advice\n\nTry asking something like 'How do I improve my resume?' or 'Interview tips'"

    return jsonify({"reply": reply, "suggestions": [
        "Resume tips", "Interview advice", "Salary negotiation",
        "Skill development", "Job search", "Career growth", "Fresher tips", "Networking"
    ]})


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
