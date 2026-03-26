# SkillMatch AI

An intelligent job-matching platform that uses AI/NLP to connect job seekers with relevant opportunities based on skill analysis.

---

## Project Structure

```
skillmatch ai/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── modules/
│       ├── models.py           # SQLAlchemy DB models
│       ├── auth.py             # Register / Login endpoints
│       ├── parser.py           # Resume parsing (PDF, DOCX, TXT)
│       ├── resume.py           # Resume upload & profile endpoints
│       ├── jobs.py             # Job CRUD & application endpoints
│       ├── matcher.py          # TF-IDF cosine similarity scoring
│       └── match.py            # Recommendation endpoints
├── frontend/
│   ├── package.json
│   ├── public/index.html
│   └── src/
│       ├── App.js              # Routes & layout
│       ├── App.css             # All styles
│       ├── api.js              # Axios instance with JWT interceptor
│       ├── index.js
│       ├── context/
│       │   └── AuthContext.js  # Global auth state
│       ├── components/
│       │   └── Navbar.js
│       └── pages/
│           ├── Home.js
│           ├── Login.js
│           ├── Register.js
│           ├── SeekerDashboard.js
│           ├── RecruiterDashboard.js
│           └── JobListings.js
└── database/
    └── schema.sql
```

---

## Setup & Running

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your secret keys

# Run the server
python app.py
# Runs on http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm start
# Runs on http://localhost:3000
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user (seeker or recruiter) |
| POST | `/api/auth/login` | Login and receive JWT token |
| POST | `/api/resume/upload` | Upload resume (PDF/DOCX/TXT) |
| GET  | `/api/resume/profile` | Get parsed resume profile |
| GET  | `/api/jobs/` | List all jobs (filterable) |
| POST | `/api/jobs/` | Post a new job (recruiter) |
| GET  | `/api/jobs/<id>` | Get job details |
| DELETE | `/api/jobs/<id>` | Delete a job (recruiter) |
| POST | `/api/jobs/<id>/apply` | Apply for a job (seeker) |
| GET  | `/api/jobs/applications` | Get seeker's applications |
| GET  | `/api/jobs/recruiter/applications` | Get recruiter's applications |
| PATCH | `/api/jobs/applications/<id>/status` | Update application status |
| GET  | `/api/match/recommendations` | AI job recommendations for seeker |
| GET  | `/api/match/candidates/<job_id>` | AI candidate recommendations for recruiter |

---

## How the AI Matching Works

1. When a resume is uploaded, `parser.py` extracts text from PDF/DOCX/TXT files
2. Skills are detected by matching against a curated keyword list using NLP
3. When recommendations are requested, `matcher.py` uses **TF-IDF vectorization** and **cosine similarity** to compute a 0–100 match score between candidate skills and job required skills
4. Results are ranked by score — highest matches appear first

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, React Router v6, Axios |
| Backend | Python 3.11+, Flask 3, Flask-JWT-Extended |
| AI/NLP | scikit-learn (TF-IDF + cosine similarity), pdfminer, python-docx |
| Database | SQLite (dev) / MySQL (prod via SQLAlchemy) |
| Auth | JWT (JSON Web Tokens) + bcrypt password hashing |
