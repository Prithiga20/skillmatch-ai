from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .models import Resume, Job
from .matcher import compute_match_score

enhance_bp = Blueprint("enhance", __name__)

# Skill → Course recommendations mapping
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

# Interview questions per skill
INTERVIEW_QUESTIONS = {
    "python": [
        "What are Python decorators and how do you use them?",
        "Explain the difference between list, tuple, and set.",
        "What is the GIL in Python?",
        "How does memory management work in Python?",
        "What are generators and when would you use them?",
    ],
    "machine learning": [
        "What is the difference between supervised and unsupervised learning?",
        "Explain overfitting and how to prevent it.",
        "What is cross-validation?",
        "Explain the bias-variance tradeoff.",
        "What is gradient descent?",
    ],
    "react": [
        "What is the virtual DOM and how does React use it?",
        "Explain the difference between state and props.",
        "What are React hooks? Name a few commonly used ones.",
        "What is the useEffect hook used for?",
        "How does React handle component re-rendering?",
    ],
    "sql": [
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "Explain normalization and its forms.",
        "What is an index and when should you use one?",
        "What is the difference between WHERE and HAVING?",
        "Explain ACID properties in databases.",
    ],
    "javascript": [
        "What is the difference between == and ===?",
        "Explain closures in JavaScript.",
        "What is event bubbling?",
        "What is the difference between let, var, and const?",
        "Explain promises and async/await.",
    ],
    "java": [
        "What is the difference between JDK, JRE, and JVM?",
        "Explain OOP principles in Java.",
        "What is the difference between abstract class and interface?",
        "What is multithreading in Java?",
        "Explain garbage collection in Java.",
    ],
    "aws": [
        "What is the difference between EC2 and Lambda?",
        "Explain S3 storage classes.",
        "What is VPC and why is it important?",
        "What is Auto Scaling?",
        "Explain the difference between RDS and DynamoDB.",
    ],
    "docker": [
        "What is the difference between a container and a virtual machine?",
        "What is a Dockerfile?",
        "Explain Docker Compose.",
        "What is a Docker image vs a container?",
        "How do you persist data in Docker?",
    ],
}

DEFAULT_QUESTIONS = [
    "Tell me about yourself.",
    "What are your greatest strengths?",
    "Where do you see yourself in 5 years?",
    "Why do you want to work here?",
    "Describe a challenging situation and how you handled it.",
]


@enhance_bp.route("/skill-gap/<int:job_id>", methods=["GET"])
@jwt_required()
def skill_gap(job_id):
    user_id = int(get_jwt_identity())
    resume = Resume.query.filter_by(user_id=user_id).first()
    if not resume or not resume.skills:
        return jsonify({"error": "Upload a resume first"}), 400

    job = Job.query.get_or_404(job_id)
    candidate_skills = {s.strip().lower() for s in resume.skills.split(",") if s.strip()}
    job_skills = {s.strip().lower() for s in job.required_skills.split(",") if s.strip()}

    matched = sorted(candidate_skills & job_skills)
    missing = sorted(job_skills - candidate_skills)

    courses = []
    for skill in missing:
        if skill in COURSE_MAP:
            courses.append({"skill": skill, **COURSE_MAP[skill]})
        else:
            courses.append({"skill": skill, "course": f"Search '{skill}' courses", "platform": "Google", "url": f"https://www.google.com/search?q={skill}+online+course"})

    score = compute_match_score(list(candidate_skills), list(job_skills))

    return jsonify({
        "job_title": job.title,
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "course_recommendations": courses,
    })


@enhance_bp.route("/interview-prep", methods=["GET"])
@jwt_required()
def interview_prep():
    user_id = int(get_jwt_identity())
    resume = Resume.query.filter_by(user_id=user_id).first()

    questions = list(DEFAULT_QUESTIONS)
    skills_used = []

    if resume and resume.skills:
        skills = [s.strip().lower() for s in resume.skills.split(",") if s.strip()]
        for skill in skills:
            if skill in INTERVIEW_QUESTIONS:
                questions.extend(INTERVIEW_QUESTIONS[skill])
                skills_used.append(skill)

    return jsonify({
        "skills_covered": skills_used,
        "questions": list(dict.fromkeys(questions)),  # deduplicate
    })


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
